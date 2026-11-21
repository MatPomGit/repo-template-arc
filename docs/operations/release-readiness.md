# ARC Template 2.0.0: kontrole fazy E

Szablon posiada kontrakt `template_version: 2.0.0`. Plik `VERSION` dotyczy niezależnego **wydania programu badawczego**, a nie automatycznego nadania nowego numeru szablonowi. Nie przestawiaj `VERSION` na 2.0.0 tylko po to, by zgadzał się z numerem schematu. Samo CI nie wykonuje GitHub Release.

## E1. Pełny przebieg funkcjonalny

`python -m unittest discover -s tests -p 'test_lifecycle_cli.py' -v` uruchamia realne polecenia w tymczasowej kopii szablonu, bez sieci, publikacji, danych uczestników ani działań na repozytoriach produkcyjnych. Kontroluje:

- `init_arc.py` i `new_manuscript.py`: domyślny dry-run bez zmian oraz jawny `--apply`.
- Walidację nowego ARC, `study.yaml`, autorstwa i zarejestrowanego lokalnego MSC.
- Publiczny i prywatny wariant repozytorium oraz brak niezatwierdzonych artykułów w `pages/`.
- Powtarzalność generatora katalogu, ponowne uruchomienie generatora, blokadę ponownej inicjalizacji.
- Odrzucanie niekompletnych rejestrów, które jedynie deklarują `schema_version: 2`; brak fałszywego `ALREADY_V2`.

## E2. Migracje istniejących programów

Pilotaż `arc-xr` służy do sprawdzenia rzeczywistych plików i zgodności MSC. Pozostałe migracje ARC wymagają osobnego rejestru źródeł, rzeczywistej historii SHA oraz zatwierdzonych PR. Migrator nie przenosi automatycznie źródeł LaTeX; testy wersji v1→v2 muszą potwierdzić, że wyniki badań, statusy zgłoszeń, DOI i uprawnienia nie są wytwarzane sztucznie.

## E3. Bramki wydania i dowody

Przed formalnym oznaczeniem wydania szablonu:

1. Potwierdź ostateczny exact HEAD SHA, pełny diff i bazę gałęzi.
2. Wymagaj zielonych testów kontraktów, E2E, schematów, katalogów i HTML; dołącz odnośniki do właściwych jobów.
3. Zweryfikuj niezależną recenzję E3.0/E4.0 i dowody powiązane z tym samym SHA.
4. Sprawdź rzeczywiste, serwerowo egzekwowane wymagane checki i review w ruleset `main`. Brak tych reguł oznacza `GATE_UNENFORCED` i status HOLD, nawet przy zielonym CI.
5. Przygotuj odpowiednią wersję, wpis do `CHANGELOG.md`, identyfikację zakresu artefaktu i dopuszczalnych treści. Release, tag, Pages i dystrybucja wymagają odrębnej decyzji.

## E4. Werdykty

`PASS` dotyczy tylko zakończonej kontroli na konkretnym SHA. `NOT_RUN` i `UNAVAILABLE` nie oznaczają PASS. Szablon może mieć zrealizowane testy E1, ale nadal pozostawać w stanie `RELEASE_HOLD` do czasu potwierdzenia E2 i E3. Nie nadaje to uprawnień do publikacji prac ani uruchomienia kosztownych usług.
