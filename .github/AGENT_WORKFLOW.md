# Procedura agentów ARC

**Zakres:** nadrzędny [AGENTS.md](../AGENTS.md). Procedura nie nadaje dodatkowych uprawnień do hostów, prywatnych repozytoriów, badań i publikacji.

## A. Rozpoznanie i Definition of Ready

Przed rozpoczęciem odczytaj rzeczywisty `main` i SHA, wszystkie PR (również drafty), Issues, lease, `program.json`, `PROJECT_STATE.yaml`, `portfolio/*.json`, [ARCHITECTURE](../ARCHITECTURE.md), zależności i istniejące testy. Zidentyfikuj globalne ID MSC, kanoniczne repozytorium i tryb `local`/`external` oraz ewentualny pierwotny projekt. Nie twórz nowego PR, gdy istnieje zadanie o tym samym celu. Przy zmianach rejestru sprawdź, czy nie utrwala on informacji o prywatnych projektach w publicznym repozytorium.

Zapisz w istniejącym Issue lub PR: cel, mierzalne kryteria akceptacji, base SHA, właściciela, zakres, ryzyko R0–R3, uprawnienia i plan walidacji. Brak zgody na ujawnienie informacji lub migrację jest blokadą, a nie brakującym szczegółem technicznym.

## B. Implementacja i testy

Działaj możliwie małą, odwracalną zmianą. Nie duplikuj zewnętrznych manuskryptów, kodu `app-*`/`lib-*`, dowodów ani rejestrów; lokalny kanoniczny manuskrypt ARC jest dozwolony. `snapshot_sha` oznacza historyczną migawkę; `audit-live` jest odczytem aktualnego zdalnego HEAD, a brak dostępu jest `UNAVAILABLE`. Nie przepinaj SNAPSHOT automatycznie, nawet gdy zdalna gałąź jest nowsza.

Wykonaj offline `python scripts/validate_repository.py --phase scaffold`, `python scripts/validate_documentation.py`, `python scripts/validate_pages.py`, `python -m unittest discover -s tests -v` i, jeśli dotyczy publicznego katalogu, `python scripts/build_public_catalog.py`. Dokumentuj dokładny SHA, polecenia, środowisko i wyniki. Nie deklaruj `PASS` dla `NOT_RUN` ani `UNAVAILABLE`. Nie uruchamiaj niezaufanego kodu na stałym runnerze; nie uruchamiaj prywatnego `audit-live` w publicznym CI.

## C. Recenzja, merge i wydanie

Przed merge sprawdź diff, CI, granice prywatności i integralność metadanych na finalnym SHA. Niezależne review jest opcjonalne, nie wymaga się `APPROVED` od drugiej osoby. Przestrzegaj pozostałych aktywnych reguł. Po scaleniu sprawdź `main` i wyniki testów.

Wydanie publicznego katalogu to **osobna czynność**. W `pages/` mogą znaleźć się tylko zasoby z `config/pages-policy.json`, po sprawdzeniu tekstów, danych, obrazów, linków, renderowanego HTML, widoczności i praw do ujawnienia. Nigdy nie publikuj `docs/`, `.github/`, instrukcji agentowych ani informacji redakcyjnych. Prywatne repo nie zapewnia prywatnej strony. Nie twórz workflow automatycznie publikującego z merge.

## D. Odbiór, blokady i sprzątanie

Definition of Done: kryteria zostały potwierdzone na aktualnym SHA, właściwe dokumenty i dowody są zgodne, przegląd techniczny ukończony, wymagane uprawnienia spełnione i właściwy etap integracji zweryfikowany. Merge, aktualny audit-live, reproducibility, publikacja witryny i publikacja manuskryptu mają **osobne** statusy. Zapisz blokady i punkt wznowienia w istniejącym Issue. Usuwaj wyłącznie własne, zweryfikowane jako zbędne zasoby; nie likwiduj nieznanych worktree, gałęzi ani projektów.
