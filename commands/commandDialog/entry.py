import adsk.core
import os
from ...lib import fusion360utils as futil
from ... import config
from .logic import CommandLogic

app = adsk.core.Application.get()
ui = app.userInterface
logic = CommandLogic(app)

CMD_ID = f'{config.COMPANY_NAME}_{config.ADDIN_NAME}_cmdDivvalog'
CMD_NAME = 'uzyj wtyczki'
CMD_Description = ''
IS_PROMOTED = True
WORKSPACE_ID = 'FusionSolidEnvironment'
PANEL_ID = 'SketchPanel'
COMMAND_BESIDE_ID = 'ScriptsManagerCommand'
ICON_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', '')

def start():
    cmd_def = ui.commandDefinitions.addButtonDefinition(CMD_ID, CMD_NAME, CMD_Description, ICON_FOLDER)
    logic.add_handler(cmd_def.commandCreated, command_created)
    workspace = ui.workspaces.itemById(WORKSPACE_ID)
    panel = workspace.toolbarPanels.itemById(PANEL_ID)
    control = panel.controls.addCommand(cmd_def, COMMAND_BESIDE_ID, False)
    control.isPromoted = IS_PROMOTED

def stop():
    logic.remove_handlers()
    workspace = ui.workspaces.itemById(WORKSPACE_ID)
    panel = workspace.toolbarPanels.itemById(PANEL_ID)
    command_control = panel.controls.itemById(CMD_ID)
    command_definition = ui.commandDefinitions.itemById(CMD_ID)
    if command_control:
        command_control.deleteMe()
    if command_definition:
        command_definition.deleteMe()

def command_created(args: adsk.core.CommandCreatedEventArgs):
    logic.create_command_inputs(args.command)
    logic.add_handler(args.command.execute, logic.execute)
    logic.add_handler(args.command.inputChanged, logic.input_changed)
    logic.add_handler(args.command.validateInputs, logic.validate_inputs)
    logic.add_handler(args.command.destroy, logic.destroy)
