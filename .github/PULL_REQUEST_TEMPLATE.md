## Zakres, wynik i ryzyko R0–R3

- Program / linia badawcza:
- Kanoniczne repozytoria, których dotyczy PR:
- Identyfikatory MSC, których dotyczy zmiana:
- Tryb właściciela (`local` / `external`) i kanoniczne repozytorium:
- Czy zmienia właściciela manuskryptu? (tak/nie)
- Czy ujawnia wpis publicznie? (tak/nie)

## Weryfikacja

- [ ] Sprawdzono aktualne remote HEAD/SHA i pochodzenie danych.
- [ ] Wykonano `python scripts/validate_repository.py --phase scaffold`.
- [ ] Wykonano `python -m unittest discover -s tests -v`.
- [ ] Potwierdzono brak prywatnych odnośników i niezatwierdzonych zasobów w `pages/`.
- [ ] Wykonano `python scripts/validate_documentation.py` i `python scripts/validate_pages.py`.
- [ ] Sprawdzono zmiany architektury/ADR, źródłowy SHA i granice publikacji.
- [ ] Wpisano ograniczenia, recenzję i plan wycofania.
