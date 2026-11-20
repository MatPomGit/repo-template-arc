# Runbook programu ARC

**Stan:** szablon. Nie zakłada się skonfigurowanej infrastruktury ani prywatnego dostępu.

1. Sprawdź `program.json`, `PROJECT_STATE.yaml` i aktualny commit. Przed zapisem rejestrów zweryfikuj ich właścicieli, brak prywatnych metadanych w repo publicznym i statusy naukowe.
2. Wykonaj izolowane testy statyczne i jednostkowe. Nie inicjuj submodułów lub zewnętrznego `audit-live` bez potrzeby i uprawnienia.
3. W trybie `reproduce` odtwarzaj przypięte gitlinki i snapshoty, nie aktualizuj ich automatycznie do HEAD.
4. W trybie `audit-live` sprawdzaj tylko aktualny zdalny stan przy posiadanych uprawnieniach. Nie zapisuj tokenów w repo, logu ani adresach URL.
5. Przy publicznym katalogu wywołaj `python scripts/build_public_catalog.py`, `python scripts/validate_pages.py` i przejrzyj realnie wygenerowany HTML. Publikacja wymaga osobnego zatwierdzenia.
6. Dla awarii, migracji lub rollbacku zachowaj przed zmianą kopię rejestrów, SHA i mapę dawnych URI, sprawdź statusy powiązanych projektów i nie przerywaj cudzych obliczeń.

**NOT_RUN** oznacza brak testu; wynik statyczny nie jest dowodem dostępu do prywatnych repozytoriów, reprodukcji ani poprawnego renderu Pages. Źródła: [REPRODUCIBILITY.md](../../REPRODUCIBILITY.md), [submoduły](../submodules.md), [polityka Pages](../pages.md).

## Bramka ochrony gałęzi `main`

Przed scaleniem zmian R2/R3 właściciel administracyjny GitHub powinien włączyć w rulesecie docelowej gałęzi: **Require a pull request before merging**, niezależną recenzję zgodną z rolami oraz **Require status checks to pass** dla joba `offline-arc-validation` (workflow `ARC research contract`). Należy zweryfikować źródło GitHub App i identyfikator statusu przed zapisaniem wymaganej kontroli. Stały bypass administratora należy wyłączyć albo ograniczyć do jawnej, audytowanej sytuacji awaryjnej. Dodatkowo nie wolno wykonywać push bezpośrednio do `main`.

**Stan przeglądu E3.0/E4.0 (2026-11-20):** aktywny ruleset `27653249` miał tylko `deletion` i `non_fast_forward`, z `bypass_mode: always`. Niniejszy plik **nie zmienia konfiguracji GitHub**. Do zamknięcia bramki konieczna jest rzeczywista zmiana w ustawieniach repozytorium i ponowny odczyt reguł. Zielony CI bez obowiązkowego status check nie wystarcza do ochrony gałęzi.
