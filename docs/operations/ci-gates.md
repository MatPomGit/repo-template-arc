# Kontrola CI i bramki PR programu ARC

Program ARC uruchamia izolowany workflow GitHub-hosted dla publicznych repozytoriów na zdarzeniach pull_request i push do main. Checkout działa na dokładnym HEAD SHA, bez utrwalania poświadczeń, bez submodułów i LFS, z uprawnieniami contents: read. Prywatne repozytoria nie uruchamiają tego joba automatycznie i wymagają oddzielnej polityki dostępu i kosztów.

Wymagany wynik techniczny przed merge:
- arc-program-contract: PASS, zerowe findings, kontrola widoczności repozytorium;
- walidacja katalogu pages, dokumentacji, SHA oraz deterministyczności;
- testy E2E generatorów, walidacja study.yaml i schematów, kontrola testów negatywnych;
- kompilacja wygenerowanego `main.tex` przez `latexmk` na izolowanym runnerze;
- MkDocs build --strict i audyt całego HTML.

Przed merge sprawdź pozytywny wynik CI, diff i bezpieczeństwo finalnego exact SHA. Niezależne review jest opcjonalne, bez obowiązkowego `APPROVED`. W aktywnym ruleset `main` (ID `27653249`) wymagany jest PR z zerem zatwierdzeń oraz **check `offline-arc-validation`** z GitHub Actions (`integration_id=15368`). [CI na dokładnym SHA `746cb2fd`](https://github.com/MatPomGit/repo-template-arc/actions/runs/44899712577) zakończyło się sukcesem. Reguła ma `do_not_enforce_on_create=true`: nadal należy wykonać negatywny test blokady merge przy brakującym lub błędnym checku i odnotować jego wynik. Nie utożsamiaj samej konfiguracji rulesetu z wykonanym testem negatywnym.

Samo scalenie PR nie upoważnia do publikacji GitHub Pages, artykułów, wyników eksperymentalnych, archiwum danych ani Release. Publikacja pozostaje osobnym zadaniem z kontrolą uprawnień i zakresu ujawnienia. Nie uruchamia się niezaufanego kodu na stałym runnerze HomeServer.

E4.0 B1: walidator `study.yaml` odrzuca dowiązania w każdym komponencie ścieżki, a ponowne użycie generatora wymaga zgodności rejestru i planu. Zapis wieloplikowy jest odwracalny przy zwykłych błędach procesu z jawnym `ROLLBACK_INCOMPLETE` przy nieudanym przywróceniu; **nie** stanowi transakcji atomowej względem awarii zasilania ani równoległych zmian innych procesów.
