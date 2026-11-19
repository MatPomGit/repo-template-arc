# Konfiguracja ARC Template v1.0.0

1. Utwórz repozytorium `arc-neuro`, `arc-ai`, `arc-xr` lub `arc-robo` (po sprawdzeniu, czy już istnieje); wybierz prywatność. Skopiuj wszystkie pliki bez historii źródłowej.
2. W `program.json` ustaw rzeczywistą nazwę programu, właściciela, zakres i politykę publicznej witryny. Zastąp pola `REPLACE` w README, AGENTS, RESEARCH, PROJECT_STATE i docs. W `CITATION.cff` zachowaj Mateusza Pomianka jako autora podstawowego, a opcjonalnych współautorów dopisz po potwierdzeniu wkładu. Ustal odpowiednią licencję w LICENSE, nie przyznawaj jej automatycznie.
3. W `areas/index.json` zarejestruj linie (np. w ARC Neuro: ndd, affect, cognition, social, psychometrics), a w `portfolio/projects.json` dodaj kanoniczne projekty `msc-*` lub dotychczasowe repozytoria o statusie `primary`/`related`.
4. Każdy artykuł w `portfolio/papers.json` ma **jednego** właściciela projektu. Zależności w `portfolio/dependencies.json` wskazują sprzęt i narzędzia przez ID, bez dublowania kart urządzeń i kodu aplikacji.
5. Git submodule nie jest obowiązkowy. Jeśli program ma fizycznie pobierać repozytorium podrzędne, wykonaj świadomie `git submodule add <URL> <sciezka>`, zapisz `submodule_path` i commit SHA w rejestrze. Następnie użytkownik pobiera program jednym `python scripts/bootstrap.py --mode reproduce` albo `git clone --recurse-submodules`.
6. W trybie `audit-live` wykonaj zdalną weryfikację każdego projektu zamiast ufać historycznym SHA z submodułów. Przypięte commity aktualizuj dopiero oddzielnym PR po testach; nie zmieniaj snapshotu historycznych eksperymentów.
7. Uruchom walidację `python scripts/validate_repository.py --phase scaffold`, testy `python -m unittest discover -s tests -v` i generację katalogu `python scripts/build_public_catalog.py`. Publikację strony poprzedź niezależnym przeglądem treści.
8. Tryb `--phase publish` sprawdza wybrane blokady redakcyjne, ale nie stanowi potwierdzenia etycznego ani naukowego i nie uruchamia zdalnej publikacji. Włączenie `is_template` w GitHub wymaga praw administracyjnych.

Szablon ma być niewielki. Katalogi protokołów, eksperymentów, manuskryptów i analiz należą do repozytoriów `msc-*`; biblioteki i aplikacje do `lib-*` i `app-*`.

## Autorstwo i współpraca

Mateusz Pomianek pozostaje co najmniej jednym z autorów każdego repozytorium programu `arc-*` utworzonego z tego szablonu. Dodatkowych współautorów można dopisywać po potwierdzeniu wkładu, afiliacji i kolejności; autorstwo repozytorium programu nie zastępuje niezależnych decyzji o autorach manuskryptów w `msc-*`. Nie zamieniaj autora podstawowego na placeholder lub inne nazwisko. Nie utożsamiaj autorstwa z własnością praw ani autorem konkretnego commita.

## Runner i bezpieczeństwo CI

Dla publicznych repozytoriów dopuszcza się GitHub-hosted runners, np. `ubuntu-latest`, do bezpiecznych, izolowanych testów struktury i rejestrów. Nie jest wymagany stały runner lokalny. W przypadku repozytoriów prywatnych najpierw ustal zasady poufności, koszty i zakres dostępu. Nigdy nie przekazuj prywatnych tokenów ani danych uczestników do PR z niezaufanych forków. `audit-live` prywatnych źródeł przeprowadza się oddzielnie, po autoryzacji; respektuj zero dodatkowych wydatków bez zgody. Zaplanowane zabezpieczenia opisuje [audyt](reviews/2026-11-19-template-audit.md).
