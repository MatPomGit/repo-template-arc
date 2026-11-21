# Polityka automatyzacji ARC

Publiczne repozytoria `arc-*` **mogą korzystać z GitHub-hosted runners** (np. `ubuntu-latest`) do krótkiej, izolowanej walidacji plików, rejestrów i testów na `pull_request` oraz `push`. Użycie stałych runnerów HomeServer/Andromeda nie jest wymagane dla podstawowego CI. Dla repo prywatnych należy osobno ocenić koszt, poufność i dostęp.

Podstawowy CI jest dostępny jako `.github/workflows/arc-contract-tests.yml` i uruchamia się tylko dla publicznych repozytoriów na izolowanym runnerze. Sprawdza `python scripts/validate_repository.py --phase scaffold` i `python -m unittest discover -s tests -v`, w tym kompilację wygenerowanego `main.tex` przez `latexmk`, bez sekretów i bez kontaktu z prywatnymi źródłami. Walidacja deterministyczności `pages/projects.md`, limitów znaków dokumentacji oraz granic publicznej witryny działa offline w CI. **To nie jest workflow publikacyjny** ani niezależna recenzja wygenerowanego HTML; udostępnienie Pages wymaga osobnej decyzji.

W workflowach używaj minimalnego `GITHUB_TOKEN` (`permissions: contents: read`). Nie uruchamiaj kodu obcych forków przez uprzywilejowane `pull_request_target`, nie przekazuj sekretów do niezaufanych PR i nie uruchamiaj ich kodu na stałych zaufanych runnerach. `audit-live` wymagający poświadczeń do prywatnych repozytoriów jest osobnym zadaniem z autoryzacją i bez automatycznego przenoszenia wyników do Pages.

Każda zmiana kontroli wymaga exact SHA, przeglądu uprawnień, zgodności z WIP Research Autopilot i **zero dodatkowych kosztów bez zgody**. Wydania, przenoszenie projektów i publikacja Pages wymagają osobnej zgody.
