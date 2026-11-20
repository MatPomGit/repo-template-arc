# Runbook programu ARC

**Stan:** szablon. Nie zakłada się skonfigurowanej infrastruktury ani prywatnego dostępu.

1. Sprawdź `program.json`, `PROJECT_STATE.yaml` i aktualny commit. Przed zapisem rejestrów zweryfikuj ich właścicieli, brak prywatnych metadanych w repo publicznym i statusy naukowe.
2. Wykonaj izolowane testy statyczne i jednostkowe. Nie inicjuj submodułów lub zewnętrznego `audit-live` bez potrzeby i uprawnienia.
3. W trybie `reproduce` odtwarzaj przypięte gitlinki i snapshoty, nie aktualizuj ich automatycznie do HEAD.
4. W trybie `audit-live` sprawdzaj tylko aktualny zdalny stan przy posiadanych uprawnieniach. Nie zapisuj tokenów w repo, logu ani adresach URL.
5. Przy publicznym katalogu wywołaj `python scripts/build_public_catalog.py`, `python scripts/validate_pages.py` i przejrzyj realnie wygenerowany HTML. Publikacja wymaga osobnego zatwierdzenia.
6. Dla awarii, migracji lub rollbacku zachowaj przed zmianą kopię rejestrów, SHA i mapę dawnych URI, sprawdź statusy powiązanych projektów i nie przerywaj cudzych obliczeń.

**NOT_RUN** oznacza brak testu; wynik statyczny nie jest dowodem dostępu do prywatnych repozytoriów, reprodukcji ani poprawnego renderu Pages. Źródła: [REPRODUCIBILITY.md](../../REPRODUCIBILITY.md), [submoduły](../submodules.md), [polityka Pages](../pages.md).
