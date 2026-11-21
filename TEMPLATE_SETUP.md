# Konfiguracja szablonu programu ARC (rewizja robocza 0.1.0)

Dla migracji programu zastosuj [procedurę v1 → v2](docs/migrations/schema-v2.md) z exact SHA i bez automatycznego przenoszenia źródeł. Dla nowego repozytorium preferuj `scripts/init_arc.py` zamiast ręcznych edycji wielu plików. Generator i `scripts/new_manuscript.py` domyślnie działają w trybie dry-run; zapis wymaga jawnego `--apply`. Oba są przeznaczone do pracy w zatwierdzonym lokalnym checkout, bez uruchamiania kodu z nieznanych źródeł.

1. Utwórz repozytorium `arc-neuro`, `arc-ai`, `arc-xr` lub `arc-robo` (po sprawdzeniu, czy już istnieje); wybierz prywatność. Skopiuj wszystkie pliki bez historii źródłowej.
2. W `program.json` ustaw `repository_visibility: public` albo `private` oraz kanoniczne `repository_full_name` zgodne z GitHub zgodnie z rzeczywistą widocznością GitHub, nazwę programu, właściciela, zakres i politykę publicznej witryny. Repozytorium pozostające `unconfigured` nie może rejestrować badań. Zastąp pola `REPLACE` w README, AGENTS, RESEARCH, PROJECT_STATE i docs. W `CITATION.cff` zachowaj Mateusza Pomianka jako autora podstawowego, a opcjonalnych współautorów dopisz po potwierdzeniu wkładu. Ustal odpowiednią licencję w LICENSE, nie przyznawaj jej automatycznie.
3. W `areas/index.json` zarejestruj linie (np. w ARC Neuro: ndd, affect, cognition, social, psychometrics), a w `portfolio/projects.json` zarejestruj tylko rzeczywiście istniejące **zewnętrzne** projekty `msc-*` lub historyczne o statusie `primary`/`related`. Dla lokalnego manuskryptu nie dodawaj fikcyjnego projektu.
4. Każdy artykuł w `portfolio/papers.json` ma **jednego** właściciela kanonicznego: lokalne ARC albo zewnętrzny projekt. Schemat v2 rozróżnia te tryby bez fikcyjnego właściciela projektu. Ustaw `manuscript_root: manuscripts` dla nowych ARC; podczas kontrolowanej migracji można zachować `papers/` z katalogami linii badawczych przez `manuscript_root: papers`. Zależności w `portfolio/dependencies.json` wskazują sprzęt i narzędzia przez ID, bez dublowania kart urządzeń i kodu aplikacji.
5. Git submodule nie jest obowiązkowy. Jeśli program ma fizycznie pobierać repozytorium podrzędne, wykonaj świadomie `git submodule add <URL> <sciezka>`, zapisz `submodule_path` i commit SHA w rejestrze. Następnie użytkownik pobiera program jednym `python scripts/bootstrap.py --mode reproduce` albo `git clone --recurse-submodules`.
6. W trybie `audit-live` wykonaj zdalną weryfikację każdego projektu zamiast ufać historycznym SHA z submodułów. Przypięte commity aktualizuj dopiero oddzielnym PR po testach; nie zmieniaj snapshotu historycznych eksperymentów.
7. Uruchom `python scripts/validate_repository.py --phase scaffold --repo-full-name <owner/arc-programme>` dla skonfigurowanego ARC, `python scripts/validate_documentation.py`, `python scripts/validate_pages.py`, `python -m unittest discover -s tests -v` i generację katalogu `python scripts/build_public_catalog.py`. Generator zapisuje tylko `pages/projects.md`, nigdy dokumentację `docs/`. Po wygenerowaniu ponownie sprawdź treść, listę dozwolonych plików i poprawność katalogu. Publikacja wymaga osobnej zgody i przeglądu realnie wygenerowanej witryny.
8. Tryb `--phase publish` sprawdza wybrane blokady redakcyjne, ale nie stanowi potwierdzenia etycznego ani naukowego i nie uruchamia zdalnej publikacji. Włączenie `is_template` w GitHub wymaga praw administracyjnych.

Zewnętrznie potwierdzona tożsamość GitHub (w CI: `GITHUB_REPOSITORY`) musi zgadzać się z `program.json:repository_full_name`. Bez takiej informacji walidator kontroluje tylko spójność deklaracji; dla lokalnego manuskryptu weryfikuje `commit_sha` i `blob_sha` względem dostępnej historii Git. Wynik `UNAVAILABLE` wymaga pełniejszego checkoutu, a brak przypiętego SHA oznacza `NOT_RUN`, nie dowód odtwarzalności. Pola `paper_id` i `project_id` są wzajemnie wykluczające i nigdy nie mają wartości `null`.

W publicznym ARC przed dodaniem lokalnego TeX, planu lub protokołu potwierdź prawo i zgodę na upublicznienie **samego pliku w repozytorium i historii Git**. Wyłączenie katalogu Pages albo `public_listing: false` nie ukrywa zawartości publicznego repozytorium.

Szablon ma być niewielki. Lokalny kanoniczny manuskrypt oraz jego plan mogą należeć do ARC; zewnętrzne MSC zachowują własne źródła. Biblioteki i aplikacje pozostają w `lib-*` i `app-*`; surowe dane w autoryzowanych magazynach.

## Dokumentacja projektu i polityka strony

`ARCHITECTURE.md` opisuje kanoniczny model ARC, a `docs/architecture/` rzeczywiste przepływy danych i zależności. `docs/adr/` dokumentuje istotne decyzje techniczne, `docs/security/` model zagrożeń, a `GOVERNANCE.md` role i bramki odpowiedzialności. Przy rozwoju projektu aktualizuj te dokumenty wraz z rejestrami `portfolio/`; szczegółowe metody, kod i artefakty należą do właściwych `msc-*`, `app-*` i `lib-*`. Zobacz [standard i limity znaków](docs/documentation.md).

**Dla stron GitHub Pages zawsze wybieraj oddzielne `pages/`**. Nie publikuj `docs/`, `AGENTS.md`, procedur wewnętrznych, statusów roboczych ani komentarzy dla agentów i autora. Dla prywatnych repozytoriów osobno sprawdź widoczność witryny; nie zakładaj, że pozostanie prywatna. Zakaz trybu `Deploy from a branch` wskazującego `main:/docs` lub korzeń repo. Zewnętrzne uruchomienie jest osobną decyzją właściciela. Nie dodawaj `CONTRIBUTING.md`.

## Autorstwo i współpraca

Mateusz Pomianek pozostaje co najmniej jednym z autorów każdego repozytorium programu `arc-*` utworzonego z tego szablonu. Dodatkowych współautorów można dopisywać po potwierdzeniu wkładu, afiliacji i kolejności; autorstwo repozytorium programu nie zastępuje niezależnych decyzji o autorach manuskryptów w `msc-*`. Nie zamieniaj autora podstawowego na placeholder lub inne nazwisko. Nie utożsamiaj autorstwa z własnością praw ani autorem konkretnego commita.

## Runner i bezpieczeństwo CI

Dla publicznych repozytoriów dopuszcza się GitHub-hosted runners, np. `ubuntu-latest`, do bezpiecznych, izolowanych testów struktury i rejestrów. Nie jest wymagany stały runner lokalny. W przypadku repozytoriów prywatnych najpierw ustal zasady poufności, koszty i zakres dostępu. Nigdy nie przekazuj prywatnych tokenów ani danych uczestników do PR z niezaufanych forków. `audit-live` prywatnych źródeł przeprowadza się oddzielnie, po autoryzacji; respektuj zero dodatkowych wydatków bez zgody. Zaplanowane zabezpieczenia opisuje [audyt](reviews/2026-11-19-template-audit.md).

## Kontrola widoczności i CI

Szablon rozpoczyna się od `repository_visibility: unconfigured`. Dopiero po weryfikacji ustawień nowego repozytorium wpisz `public` lub `private`. Nie wpisuj żadnych informacji o prywatnych projektach do publicznego ARC, nawet z `public_listing: false`, gdyż cała historia Git jest jawna. W publicznych repozytoriach izolowany `pull_request` workflow sprawdza strukturę i testy z `--repo-visibility public`, a w prywatnych automatyczny job jest pomijany. Bieżące SHA prywatnych projektów przechowuj wyłącznie w prywatnym rejestrze Research Autopilot. Strona Pages i `publish` pozostają osobnymi bramkami.

## GitHub Pages oraz wydania programu

Portal programu opisuje badania odbiorcy zewnętrznemu i korzysta wyłącznie z zatwierdzonego `pages/`. Przestrzegaj [wytycznych Pages ARC](docs/pages.md), odrębnej listy plików, kontroli końcowego HTML, prywatności rekordów i osobnej zgody na deployment. Nie publikuj `docs/`, kart urządzeń, prywatnych manuskryptów, promptów i informacji o agentach. Brak zatwierdzonych publicznych projektów nie uprawnia do stworzenia fikcyjnego katalogu.

Wersjonowane [wydania ARC](docs/releases.md) dotyczą **migawek rejestru i pakietów odtwarzalności**, nie artykułów MSC ani oprogramowania APP/LIB. Rozdziel `VERSION` programu od `template_version`; nie myl `--phase publish` z autoryzacją GitHub Release. Każdy artefakt i wynik kontroli powiąż z exact SHA, dowodami pochodzenia, prawami i odrębnym zatwierdzeniem właściciela. Nie dodawaj automatycznych workflow wydawniczych do wzorca.
