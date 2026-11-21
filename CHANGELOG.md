# Historia zmian

## Zmiany robocze (bez wydania szablonu)

- Dodano izolowany test pełnego przebiegu CLI oraz kontrolę braku niezamierzonej publikacji MSC.
- Migrator odrzuca niespójne rejestry schematu 2 zamiast zwracać fałszywe `ALREADY_V2`.
- Oddzielono numer schematu danych od numeru rewizji szablonu. Starsze metadane pozostają obsługiwane.
- Numer `0.1.0` oznacza roboczą rewizję szablonu, nie dowodzi istnienia tagu ani GitHub Release.

Nie ma potwierdzonej historii wydań szablonu 1.x ani 2.x. Nie odtwarzamy fikcyjnych wydań.
