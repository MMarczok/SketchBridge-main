# wtyczka - Fusion 360 Add-in

Wtyczka do **Fusion 360** do automatycznego łączenia luźnych punktów w szkicach.

## 📋 Informacje

- **Nazwa**: wtyczka
- **Typ**: Fusion 360 Add-in
- **Funkcja**: Łączenie punktów szkicu w automatyczny lub ręczny sposób
- **Autor**: M. Marczok
- **Wersja**: 1.0.0
- **GitHub**: [github.com/MMarczok/SketchBridge-main](https://github.com/MMarczok/SketchBridge-main)

## 🚀 Instalacja

1. Pobierz pliki z GitHub
2. Umieść folder w katalogu add-ins Fusion 360
3. Restart Fusion 360
4. **Tools** → **Add-ins** → zaznacz "wtyczka"

## 📖 Jak używać

### 1. Otwórz szkic
- Otwórz istniejący szkic w Fusion 360
- Będą tam luźne punkty do połączenia

### 2. Uruchom wtyczkę
- Kliknij przycisk **"uzyj wtyczki"** w panelu Sketch (górny pasek)
- Pojawi się okno dialogowe

### 3. Wybierz tryb połączenia

Masz **3 opcje**:

#### **Join (domyślnie)**
- Łączy punkty za pomocą vinculum (ograniczenia zbieżności)
- Wszystkie znalezione punkty w odległości są automatycznie połączone

#### **Fill**
- Łączy punkty linią
- Tworzy linie między bliskimi punktami

#### **Table Select** ⭐
- Pokazuje **tabelkę** ze wszystkimi potencjalnymi połączeniami
- Możesz wybrać które połączyć
- **Ważne**: Jeśli okno jest puste, zmień **rozmiar okna** (pociągnij krawędź) - tabela się pojawi
- Zaznacz checkboxy obok połączeń które chcesz
- Kliknij **"Create Connections"** lub zamknij okno

### 4. Ustawienia

| Ustawienie | Opis |
|-----------|------|
| **Max Connection Distance** | Maksymalna odległość między punktami do połączenia (domyślnie 0.2) |
| **Join Type** | Rodzaj połączenia: Join, Fill, Table Select |
| **Manual Accept Connections** | Jeśli zaznaczysz - każde połączenie trzeba zatwierdzić osobno |

## ✨ Funkcje

✅ Automatyczne łączenie luźnych punktów  
✅ Trzy tryby pracy (Join, Fill, Table Select)  
✅ Ręczny wybór połączeń w trybie Table Select  
✅ Uniknięcie połączeń które już istnieją  
✅ Integracja z Fusion 360  

## 🎯 Przykład użycia

1. Otwórz szkic z luźnymi punktami
2. Ustaw **Max Connection Distance** na 0.5 (np.)
3. Wybierz **"Table Select"**
4. Zmień rozmiar okna dialogowego (jeśli trzeba)
5. Zaznacz punkty które chcesz połączyć
6. Zamknij okno - połączenia się tworzą automatycznie
7. Gotowe! 🎉

## 🐛 Rozwiązywanie problemów

### Okno z tabelką jest puste
- **Rozwiązanie**: Zmień rozmiar okna! Pociągnij krawędź okna dialogowego, a tabela się pojawi

### Nie znaleziono połączeń
- Zmniejsz **Max Connection Distance** lub sprawdź czy punkty są rzeczywiście blisko siebie

### Wtyczka się nie włącza
- Sprawdź czy folder jest w poprawnym miejscu
- Restart Fusion 360
- **Tools** → **Add-ins** → wyłącz i włącz wtyczkę

## 📁 Struktura projektu

```
wtyczka/
├── README.md                 # Ta plik
├── wtyczka.py              # Główny plik wtyczki
├── wtyczka.manifest        # Manifest wtyczki
├── config.py               # Konfiguracja
├── commands/
│   └── commandDialog/
│       ├── entry.py        # Punkt wejścia
│       ├── logic.py        # Logika połączania
│       ├── help_palette.html
│       └── resources/      # Ikony
└── lib/
    └── fusion360utils/     # Utility funkcje
```

## 📝 Licencja

MIT License

## 👤 Autor

**M. Marczok**  
Email: m.marczok@panova.pl

---

Jeśli masz pytania lub znalazłeś błąd - zgłoś issue na GitHub! 🙏
