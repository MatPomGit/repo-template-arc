# Migracja programów ARC v1 do v2

Migracja dotyczy kanonicznych rejestrów programu i nie powoduje przenoszenia plików TeX, pobierania cudzych repozytoriów ani zmiany autorstwa. **Zmieniany jest wyłącznie `schema_version` (1 → 2); `template_version` zachowuje istniejącą wartość SemVer, ponieważ opisuje pochodzenie szablonu, a nie schemat danych.** Gdy stan źródeł jest niejednoznaczny, operacja ma zostać zablokowana.

## Procedura operacyjna

1. Zakończ kolidujące PR źródłowe, zweryfikuj aktualny HEAD i wykonaj migawkę projektu. Narzędzia v2, schematy, testy i dokumentację przenoś w osobnym zatwierdzonym PR, bez przepisywania historii.
2. `python scripts/migrate_arc.py --mode inventory` zwraca listę zastanych lokalnych plików `main.tex` i liczbę rekordów. Nie zapisuje plików.
3. `python scripts/migrate_arc.py --mode plan --repository MatPomGit/arc-neuro --map /private/map.json` sprawdza źródła i mapę artykułów. Dla prostego rejestru v1 z pracami wyłącznie zewnętrznymi `--map` można pominąć. Wymagany status planu to `READY`.
4. Po potwierdzeniu właścicieli, identyfikatorów, dowodów i widoczności wykonaj w czystym checkout `python scripts/migrate_arc.py --mode apply --repository MatPomGit/arc-neuro --map /private/map.json --expected-sha FULL_40_HEX_SHA`. Jeżeli program publiczny zawiera lokalne źródła, wymagane jest ponadto `--confirm-public-sources`.
5. Porównaj liczbę artykułów, sumy źródeł, wersje, zależności i ścieżki przed/po. Uruchom walidację rejestrów, YAML, testy i recenzję E3/E4 na dokładnym SHA. Dopiero następnie otwórz PR.

Mapa ma postać:

`{"schema_version":1,"articles":{"MSC-CR-P05":{"mode":"external","research_state":"active"}},"sources":{"manuscripts/MSC-CR-P06/main.tex":{"mode":"local","title":"Zweryfikowany tytuł","area":"ndd","research_state":"planned","publication_stage":"concept"}}}`

Dla źródłowego wpisu v1 z jednoznacznym `owner_project_id`, zgodnym repozytorium i stanem `concept` przyjmowana jest własność zewnętrzna i stan naukowy `planned`. Inne etapy wymagają jawnego `research_state`. Statusy zgłoszenia, akceptacji i publikacji zachowują wymagania dowodowe. Zgoda na upublicznienie artykułu nigdy nie powstaje automatycznie: nowe rekordy otrzymują `public_listing=false` i brak publicznego opisu.

Lokalny plik `main.tex` niewpisany w v1 wymaga mapy `sources` z rzeczywistym tytułem, linią badań i ID MSC. Jeśli lokalny plik jest jedynie pomocniczym planem artykułu kanonicznego w zewnętrznym MSC, odnotuj przy odpowiednim wpisie `articles` znacznik `local_source_role: noncanonical_plan`. Taki plik nie zmienia właściciela. Nazwy typu `slot-NNN` należy najpierw jawnie zmapować i przemianować w oddzielnym PR. Samo podanie nowego ID nie zmieni lokalizacji TeX.

W obrębie jednego ARC nie mogą współistnieć dwa aktywne katalogi źródłowe `papers/` i `manuscripts/` bez uprzedniej normalizacji. Dopuszczona jest struktura `papers/<area>/<MSC-ID>/main.tex` i nowa `manuscripts/<MSC-ID>/main.tex`.

## Spójność rejestru i dowodów

Wpis każdej zależności zawiera dokładnie jeden niepusty identyfikator `paper_id` albo `project_id`. Drugi klucz musi być nieobecny, nie `null`. Lokalny `commit_sha` wiąże ścieżkę `main.tex` z historycznym drzewem Git, a `blob_sha` sprawdza konkretną zawartość. Brak wskazanego SHA oznacza `NOT_RUN`; brak obiektu w checkout oznacza `UNAVAILABLE`, nie `PASS`. Tożsamość repozytorium należy porównać z zewnętrznie potwierdzonym `GITHUB_REPOSITORY` (CLI: `--repo-full-name`).

## Ograniczenia bezpieczeństwa

Tryby `inventory` i `plan` są read-only. `apply` wymaga exact SHA oraz czystego drzewa plików śledzonych przez Git. Zapis obejmuje pięć plików konfiguracyjnych/rejestrowych. Po zapisie narzędzie waliduje program; przy błędzie podejmuje próbę przywrócenia oryginałów. Nie zastępuje to kopii zapasowej oraz możliwości powrotu do SHA źródłowego. Nie uruchamiaj `apply` bez zweryfikowania aktualnej widoczności repozytorium i praw do ujawnienia samych plików w historii Git.

Migrator nie uruchamia Pages, nie tworzy Release, nie nadaje DOI ani nie scala PR. Weryfikacja globalnej unikalności MSC między programami wymaga dodatkowego odczytu portfolio Research Autopilot.
