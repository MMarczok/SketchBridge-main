import adsk.core, adsk.fusion, adsk.cam, traceback
from ...lib import fusion360utils as futil
import os
from ... import config

class CommandLogic:
    def __init__(self, app):
        self.app = app
        self.ui = app.userInterface
        self.handlers = []
        self.PALETTE_ID = config.sample_palette_id
        self.PALETTE_URL = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'help_palette.html')
        self.PALETTE_URL = self.PALETTE_URL.replace('\\', '/')
        self.CONNECTION_PALETTE_ID = f'{config.COMPANY_NAME}_{config.ADDIN_NAME}_connection_palette'
        self.connection_palette = None
        self.potential_connections = []

    def add_handler(self, event, method):
        handler = futil.add_handler(event, method)
        self.handlers.append(handler)

    def remove_handlers(self):
        self.handlers = []

    def create_command_inputs(self, command):
        inputs = command.commandInputs
        defaultUnits = self.app.activeProduct.unitsManager.defaultLengthUnits
        inputs.addValueInput('max_distance', 'Max Connection Distance', defaultUnits, adsk.core.ValueInput.createByReal(0.2))
        dropDownInput = inputs.addDropDownCommandInput('join_type', 'Join Type', adsk.core.DropDownStyles.TextListDropDownStyle)
        dropDownList = dropDownInput.listItems
        dropDownList.add('Join', True)
        dropDownList.add('Fill', False)
        dropDownList.add('Table Select', False)
        inputs.addBoolValueInput('manual_accept', 'Manual Accept Connections', True)
        helppath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'help_icon', '')
        self.help = inputs.addBoolValueInput('help', 'Help', False, helppath)

    def execute(self, args):
        inputs = args.command.commandInputs
        max_distance_input = inputs.itemById('max_distance')
        join_type_input = inputs.itemById('join_type')
        manual_accept_input = inputs.itemById('manual_accept')
        
        
        max_distance = max_distance_input.value
        join_type = join_type_input.selectedItem.name
        manual_accept = manual_accept_input.value

        try:
            design = adsk.fusion.Design.cast(self.app.activeProduct)
            skt = adsk.fusion.Sketch.cast(self.app.activeEditObject)
            sketchCurves = skt.sketchCurves

            points_to_connect = self.identify_points_to_connect(skt.sketchPoints, sketchCurves)
            self.ui.messageBox(f'Found {len(points_to_connect)} points to connect.', 'Debug')
            
            if join_type == 'Table Select':
                self.show_connection_table(points_to_connect, max_distance, skt)
                return
            
            self.connect_points(points_to_connect, max_distance, join_type, manual_accept)
            self.ui.messageBox(f'Operation completed. Checked {len(skt.sketchPoints)} points, attempted to connect {len(points_to_connect)} points.', 'Results')

        except Exception as e:
            self.ui.messageBox('Error:\n{}'.format(traceback.format_exc()))

    def identify_points_to_connect(self, points, curves):
        points_to_connect = []
        for point in points:
            if self.is_point_connected_to_one_curve_only(point, curves):
                points_to_connect.append(point)
                self.ui.messageBox(f'Point to connect: ({point.geometry.x}, {point.geometry.y})', 'Debug')
        return points_to_connect

    def is_point_connected_to_one_curve_only(self, point, curves):
        connection_count = 0
        for curve in curves:
            if curve.startSketchPoint == point or curve.endSketchPoint == point:
                connection_count += 1
        return connection_count == 1

    def are_points_already_connected(self, point1, point2, sketchCurves):
        for curve in sketchCurves:
            start_point = curve.startSketchPoint.geometry
            end_point = curve.endSketchPoint.geometry
            if (start_point.isEqualTo(point1) and end_point.isEqualTo(point2)) or (start_point.isEqualTo(point2) and end_point.isEqualTo(point1)):
                return True
        
        skt = adsk.fusion.Sketch.cast(self.app.activeEditObject)
        geomConstraints = skt.geometricConstraints
        for constraint in geomConstraints:
            if constraint.objectType == adsk.fusion.CoincidentConstraint.classType():
                if (constraint.point.geometry.isEqualTo(point1) and constraint.entity.geometry.isEqualTo(point2)) or \
                   (constraint.point.geometry.isEqualTo(point2) and constraint.entity.geometry.isEqualTo(point1)):
                    return True
        return False

    def connect_points(self, points, max_distance, join_type, manual_accept):
        skt = adsk.fusion.Sketch.cast(self.app.activeEditObject)
        if not skt:
            self.ui.messageBox('No active sketch selected.')
            return

        remaining_points = points.copy()
        connections_to_accept = []

        while remaining_points:
            point1 = remaining_points.pop(0)
            for point2 in list(remaining_points):
                if point1.geometry.distanceTo(point2.geometry) < max_distance:
                    if point1.geometry.isEqualTo(point2.geometry):
                        continue
                    if manual_accept:
                        connections_to_accept.append((point1, point2))
                    else:
                        if join_type == 'Join':
                            geomConstraints = skt.geometricConstraints
                            if not self.are_points_already_connected(point1.geometry, point2.geometry, skt.sketchCurves):
                                try:
                                    geomConstraints.addCoincident(point1, point2)
                                except RuntimeError as e:
                                    self.ui.messageBox(f'Failed to add constraint: {e}')
                        elif join_type == 'Fill':
                            if not self.are_points_already_connected(point1.geometry, point2.geometry, skt.sketchCurves):
                                skt.sketchCurves.sketchLines.addByTwoPoints(point1, point2)
                        remaining_points.remove(point2)
        
        if manual_accept:
            self.accept_connections(connections_to_accept, join_type)

    def highlight_points(self, points):
        app = adsk.core.Application.get()
        design = adsk.fusion.Design.cast(app.activeProduct)
        root_comp = design.rootComponent
        custom_graphics = root_comp.customGraphicsGroups.add()
        
        marker_bodies = []
        coords_list = []
        
        for point in points:
            coords_list.extend([point.geometry.x, point.geometry.y, point.geometry.z])
        
        coords = adsk.fusion.CustomGraphicsCoordinates.create(coords_list)
        point_indices = list(range(len(points)))
        point_set = custom_graphics.addPointSet(coords, point_indices, 
                                                adsk.fusion.CustomGraphicsPointTypes.UserDefinedCustomGraphicsPointType,
                                                'TestPoint.png')
        marker_bodies.append(point_set)
        
        return marker_bodies

    def accept_connections(self, connections, join_type):
        skt = adsk.fusion.Sketch.cast(self.app.activeEditObject)
        if not skt:
            self.ui.messageBox('No active sketch selected.')
            return

        highlighted_bodies = self.highlight_points([point for conn in connections for point in conn])

        for connection in connections:
            point1, point2 = connection
            response = self.ui.messageBox(
                f'Connect points ({point1.geometry.x}, {point1.geometry.y}) and ({point2.geometry.x}, {point2.geometry.y})?', 
                'Accept Connection', 
                adsk.core.MessageBoxButtonTypes.YesNoButtonType, 
                adsk.core.MessageBoxIconTypes.QuestionIconType
            )
            if response == adsk.core.DialogResults.DialogYes:
                if join_type == 'Join':
                    geomConstraints = skt.geometricConstraints
                    if not self.are_points_already_connected(point1.geometry, point2.geometry, skt.sketchCurves):
                        try:
                            geomConstraints.addCoincident(point1, point2)
                        except RuntimeError as e:
                            self.ui.messageBox(f'Failed to add constraint: {e}')
                elif join_type == 'Fill':
                    if not self.are_points_already_connected(point1.geometry, point2.geometry, skt.sketchCurves):
                        skt.sketchCurves.sketchLines.addByTwoPoints(point1, point2)

        # Remove temporary objects after accepting connections
        for body in highlighted_bodies:
            body.deleteMe()

    def destroy(self, args):
        futil.log('Command Destroy Event')
        self.remove_handlers()

    def input_changed(self, args):
        changedInput = args.input
        if (changedInput.id == 'help'):
            # Creating palette
            self.palette = self.ui.palettes.itemById(self.PALETTE_ID)
            if not self.palette: 
                self.palette = self.ui.palettes.add(self.PALETTE_ID, 'wtyczka Help', self.PALETTE_URL, False, True, True, 600, 500, True)
                #self.palette.setPosition(800, 400)
                self.palette.isVisible = True
                futil.add_handler(self.palette.closed, self.palette_closed)

    def palette_closed(self, args: adsk.core.UserInterfaceGeneralEventArgs):
        global _handlers
        _handlers = []
        palette = self.ui.palettes.itemById(self.PALETTE_ID)
        # Delete the Palette
        if palette:
            palette.deleteMe()

    def validate_inputs(self, args):
        inputs = args.inputs
        max_distance_input = inputs.itemById('max_distance')

        max_distance = max_distance_input.value
        args.areInputsValid = max_distance >= 0

    def show_connection_table(self, points, max_distance, sketch):
        # Find all potential connections
        potential_connections = []
        remaining_points = points.copy()
        
        while remaining_points:
            point1 = remaining_points.pop(0)
            for point2 in list(remaining_points):
                if point1.geometry.distanceTo(point2.geometry) < max_distance:
                    if not self.are_points_already_connected(point1.geometry, point2.geometry, sketch.sketchCurves):
                        potential_connections.append((point1, point2))
        
        if not potential_connections:
            self.ui.messageBox('No potential connections found within the specified distance.', 'No Connections')
            return
        
        self.potential_connections = potential_connections
        
        # Create HTML table
        html_content = self.generate_connection_table_html(potential_connections, len(potential_connections))
        
        # Create temporary HTML file
        table_html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'connection_table.html')
        try:
            with open(table_html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
        except Exception as e:
            self.ui.messageBox(f'Error writing HTML: {str(e)}', 'Error')
            return
        
        # Convert path to proper file:// URL format for Windows
        import pathlib
        file_path = pathlib.Path(table_html_path).as_uri()
        
        self.connection_palette = self.ui.palettes.add(self.CONNECTION_PALETTE_ID, 'Select Connections', file_path, False, True, True, 800, 600, True)
        self.connection_palette.isVisible = True
        futil.add_handler(self.connection_palette.closed, self.connection_palette_closed)

    def generate_connection_table_html(self, connections, num_connections):
        # Build table rows
        rows_html = ""
        for i, (point1, point2) in enumerate(connections):
            distance = point1.geometry.distanceTo(point2.geometry)
            p1x = point1.geometry.x
            p1y = point1.geometry.y
            p2x = point2.geometry.x
            p2y = point2.geometry.y
            rows_html += '<tr><td><input type="checkbox" checked value="' + str(i) + '"></td><td>' + f'{p1x:.2f},{p1y:.2f}' + '</td><td>' + f'{p2x:.2f},{p2y:.2f}' + '</td><td>' + f'{distance:.3f}' + '</td></tr>'
        
        html = '''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>wtyczka Connections</title>
<style>
body { font-family: Arial, sans-serif; padding: 15px; margin: 0; background: white; }
h3 { margin-top: 0; color: #333; }
table { width: 100%; border-collapse: collapse; background: white; }
th { background-color: #4CAF50; color: white; padding: 10px; text-align: left; }
td { padding: 8px; border-bottom: 1px solid #ddd; }
tr:hover { background-color: #f5f5f5; }
input { cursor: pointer; }
button { padding: 10px 15px; margin: 10px 5px 10px 0; font-size: 14px; cursor: pointer; border: 1px solid #999; }
.btn-connect { background-color: #4CAF50; color: white; border: none; }
.btn-cancel { background-color: #f44336; color: white; border: none; }
.info { color: #666; font-size: 12px; margin: 10px 0; }
</style>
</head>
<body>
<h3>Found ''' + str(num_connections) + ''' Connections</h3>
<p class="info">Checked connections will be created. Uncheck any you want to skip.</p>
<table>
<tr><th>Create</th><th>Point 1 (X, Y)</th><th>Point 2 (X, Y)</th><th>Distance</th></tr>
''' + rows_html + '''
</table>
<button class="btn-connect" onclick="closeWindow()">Create Connections</button>
<button class="btn-cancel" onclick="cancelWindow()">Cancel</button>
<script>
function closeWindow() {
    window.close();
}
function cancelWindow() {
    window.close();
}
</script>
</body>
</html>'''
        return html
    def connection_palette_closed(self, args):
        # Connect all the found connections when palette closes
        skt = adsk.fusion.Sketch.cast(self.app.activeEditObject)
        if not skt:
            return
        
        # Connect all potential connections that were found
        num_connections = len(self.potential_connections)
        self.connect_selected_connections(list(range(num_connections)))
        
        # Clean up
        if self.connection_palette:
            self.connection_palette.deleteMe()
            self.connection_palette = None
        
        # Remove temporary HTML file
        table_html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'connection_table.html')
        if os.path.exists(table_html_path):
            try:
                os.remove(table_html_path)
            except:
                pass
        
        # Show result
        self.ui.messageBox(f'Successfully created {num_connections} connections.', 'Complete')

    def connect_selected_connections(self, selected_indices):
        skt = adsk.fusion.Sketch.cast(self.app.activeEditObject)
        if not skt:
            return
        
        for index in selected_indices:
            if index < len(self.potential_connections):
                point1, point2 = self.potential_connections[index]
                
                # Add coincident constraint (Join)
                geomConstraints = skt.geometricConstraints
                try:
                    geomConstraints.addCoincident(point1, point2)
                except RuntimeError as e:
                    self.ui.messageBox(f'Failed to connect points: {e}')

