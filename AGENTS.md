# Obowiązujące zasady agentów dla programu ARC

Czytaj po kolei: `program.json`, `PROJECT_STATE.yaml`, `RESEARCH.md`, `ARCHITECTURE.md`, `portfolio/projects.json`, `portfolio/papers.json`, `portfolio/dependencies.json`, `docs/governance.md`.

1. To repozytorium **indeksuje** badania; nie kopiuj manuskryptów, wyników pomiarów, kodu `app-*` ani `lib-*`.
2. Każdy manuskrypt ma jedno repozytorium kanoniczne i jedno `project_id`; odnośniki między programami są `related`, nie drugą kopią.
3. Przed audytem aktualnego programu wykonaj `python scripts/bootstrap.py --mode audit-live` z uwierzytelnionym dostępem do repozytoriów. Raportuj `CURRENT`, `STALE` i `UNAVAILABLE` osobno. Nie opieraj aktualnej recenzji wyłącznie na starym gitlinku.
4. Przed odtworzeniem wyników użyj przypiętego commitu i manifestu eksperymentu (`--mode reproduce`). Nigdy nie zastępuj zamrożonego SNAPSHOT aktualnym `main` podczas analizy historycznej.
5. Nie czytaj ani nie publikuj danych osobowych, surowych EEG/wideo/eye tracking. Źródłem kontraktów sprzętu jest Research Autopilot `catalog/equipment/` i `docs/equipment/`, a sieci `homeserver-infra/docs/infrastructure/network/`.
6. Rozróżniaj `planned`, `source_written`, `tested`, `hardware_verified`, `submitted`, `published`; nie wymyślaj DOI, etyki, statystyk, potwierdzenia uploadu OSF ani dostępności urządzeń.
7. Dla każdego PR zachowuj exact SHA, audyt, limity WIP i bramki właścicielskie. Nie uruchamiaj niezweryfikowanych PR na stałych runnerach HomeServer/Andromeda; nie wprowadzaj dodatkowych kosztów.
8. Automatyzacje publikowania GitHub Pages, przenoszenia projektów i zmian uprawnień wymagają oddzielnej zgody. Nie twórz drugiego schedulera poza Research Autopilot.
9. Repozytoria prywatne podlegają kontroli dostępu; GitHub App jest planowanym ograniczonym odczytem, nie należy zakładać wdrożonego, nieograniczonego brokera.
10. Nie kasuj ani nie archiwizuj historycznych repozytoriów bez mapy odwołań i potwierdzenia właściciela.

11. Mateusz Pomianek musi pozostać co najmniej jednym z autorów w `CITATION.cff` i metadanych repozytorium programu; dodatkowych współautorów wolno dodawać po potwierdzeniu wkładu. Nie nadpisuj automatycznie autorstwa niezależnych prac w `msc-*`.
12. Dla repozytoriów publicznych bezpieczne, izolowane kontrole CI **mogą** korzystać z GitHub-hosted runners. Sekrety, prywatny `audit-live` i kod niezaufanych PR muszą pozostawać poza uprzywilejowanymi środowiskami. Nie traktuj dokumentacji zaplanowanego CI jako dowodu wykonania testów.
