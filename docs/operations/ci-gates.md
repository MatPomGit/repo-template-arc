# Kontrola CI i bramki PR programu ARC

Program ARC uruchamia izolowany workflow GitHub-hosted dla publicznych repozytoriów na zdarzeniach pull_request i push do main. Checkout działa na dokładnym HEAD SHA, bez utrwalania poświadczeń, bez submodułów i LFS, z uprawnieniami contents: read. Prywatne repozytoria nie uruchamiają tego joba automatycznie i wymagają oddzielnej polityki dostępu i kosztów.

Wymagany wynik techniczny przed merge:
- arc-program-contract: PASS, zerowe findings, kontrola widoczności repozytorium;
- walidacja katalogu pages, dokumentacji, SHA oraz deterministyczności;
- testy E2E generatorów, walidacja study.yaml i schematów, kontrola testów negatywnych;
- kompilacja wygenerowanego `main.tex` przez `latexmk` na izolowanym runnerze;
- MkDocs build --strict i audyt całego HTML.

Przed merge sprawdź pozytywny wynik CI, diff i bezpieczeństwo finalnego exact SHA. Niezależne review jest opcjonalne, bez obowiązkowego `APPROVED`. W `main-branch-ruleset` (ID `27653249`) wymagany powinien być check GitHub Actions `offline-arc-validation`, bez obowiązkowych zatwierdzeń recenzenta. **Nie traktuj zapisu w dokumentacji jako dowodu konfiguracji GitHub:** odczytaj aktywne `rules[].parameters.required_status_checks` z API bezpośrednio przed oceną ochrony `main`. Pusta lista oznacza `CI_NOT_ENFORCED`, nawet gdy GitHub Actions kończą się `success`. Aktualnie występuje regresja konfiguracji śledzona w [Issue #9](https://github.com/MatPomGit/repo-template-arc/issues/9). Po przywróceniu wymogu przeprowadź negatywny test blokady scalenia dla brakującego lub błędnego checku; raportuj wyłącznie faktycznie sprawdzony przypadek.

Samo scalenie PR nie upoważnia do publikacji GitHub Pages, artykułów, wyników eksperymentalnych, archiwum danych ani Release. Publikacja pozostaje osobnym zadaniem z kontrolą uprawnień i zakresu ujawnienia. Nie uruchamia się niezaufanego kodu na stałym runnerze HomeServer.

E4.0 B1: walidator `study.yaml` odrzuca dowiązania w każdym komponencie ścieżki, a ponowne użycie generatora wymaga zgodności rejestru i planu. Zapis wieloplikowy jest odwracalny przy zwykłych błędach procesu z jawnym `ROLLBACK_INCOMPLETE` przy nieudanym przywróceniu; **nie** stanowi transakcji atomowej względem awarii zasilania ani równoległych zmian innych procesów.
