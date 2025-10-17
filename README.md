# Pokročilá Kalkulačka - PySide6

Kompletní kalkulátor naprogramovaný v PySide6 s pokročilými funkcemi a zabezpečením.

## Funkce

### Základní funkce
- ✅ Sčítání, odčítání, násobení, dělení
- ✅ Zadávání čísel tlačítky
- ✅ Editace textového pole
- ✅ Desetinná čísla
- ✅ Ochrana proti více desetinným tečkám
- ✅ Ochrana proti dělení nulou
- ✅ Výpis historie operací
- ✅ Přenos předchozích operací/výsledků

### Bonusové funkce
- ✅ Závorky a priorita operací
- ✅ Převody číselných soustav:
  - Dvojková (binární)
  - Osmičková (oktální)
  - Šestnáctková (hexadecimální)
  - Římské číslice (I-MMMCMXCIX)
  - Libovolná soustava (2-36)
  - Operace v jiných soustavách
- ✅ Trigonometrické funkce:
  - sin, cos, tan
  - Přepínání stupně/radiány
- ✅ Logaritmické a exponenciální:
  - log(x), ln(x), exp(x)
  - Mocniny (x²)
  - π konstanta
- ✅ Výpočet procent

### Bezpečnost
- ✅ Validace vstupu
- ✅ Sanitizace výrazů
- ✅ Omezené jmenné prostory (žádné __import__, eval)
- ✅ Ochrana proti code injection
- ✅ Kontrola NaN/Inf výsledků

## Instalace

```bash
# Nainstalovat závislosti
pip3 install -r requirements.txt

# Spustit kalkulátor
python3 calculator.py
```

## Testování

```bash
# Spustit testy
python3 test_calculator.py
```

## Struktura projektu

```
/home/rydloj/Projects/Skola/
├── calculator.py         # Hlavní aplikace
├── test_calculator.py    # Unit testy
├── requirements.txt      # Závislosti
└── README.md            # Dokumentace
```

## Použití

### Hlavní kalkulátor
1. Zadejte čísla pomocí tlačítek nebo textového pole
2. Použijte operátory: +, -, *, /, ()
3. Stiskněte "=" nebo Enter pro výpočet
4. "C" vymaže displej

### Pokročilé funkce
- **sin/cos/tan**: Vloží funkci, např. `sin(30)`
- **log/ln/exp**: Logaritmy a exponenciály
- **x²**: Umocní aktuální výraz na druhou
- **π**: Vloží hodnotu π
- **Degrees/Radians**: Přepne režim úhlů

### Převodník soustav
1. Vyberte kartu "Base Converter"
2. Zadejte číslo
3. Vyberte zdrojovou a cílovou soustavu
4. Klikněte "Convert"

### Historie
1. Vyberte kartu "History"
2. Dvoj-kliknutím na záznam vyberte expresi nebo výsledek
3. "Clear History" vymaže historii

## Bezpečnostní opatření

### Validace vstupu
- Kontrola více desetinných teček
- Validace výrazů před vyhodnocením
- Kontrola dělení nulou

### Omezený běhový prostor
- Pouze povolené funkce (math module)
- Žádný přístup k __builtins__
- Žádné nebezpečné operace (os, sys, eval, exec)

### Kontrola výsledků
- Detekce NaN (Not a Number)
- Detekce Inf (Infinity)
- Ošetření chybových stavů

## Testování

Projektu obsahuje kompletní test suite:
- Základní operace
- Desetinná čísla
- Závorky a priorita
- Trigonometrie
- Logaritmy
- Převody soustav
- Římské číslice
- Bezpečnostní testy
- Edge cases

## Vývojové poznámky

### Architektura
- **NumberBaseConverter**: Převody číselných soustav
- **ExpressionEvaluator**: Bezpečné vyhodnocení výrazů
- **HistoryManager**: Správa historie výpočtů
- **CalculatorUI**: Grafické rozhraní (PySide6)

### Zabezpečení eval()
Používáme `eval()` s omezeným namespace:
```python
safe_dict = {
    'sin': math.sin, 'cos': math.cos,
    # ... pouze povolené funkce
    '__builtins__': {}  # zakázané vestavěné funkce
}
result = eval(expr, safe_dict, {})
```

## Licence

Akademický projekt - Školní úkol

## Autor

Vytvořeno s pomocí Claude Code
