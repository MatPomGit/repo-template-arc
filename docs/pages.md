# Zasady publicznego portalu GitHub Pages

**GitHub Pages publikuje wyłącznie `pages/`, nigdy `docs/`.** `docs/` zawiera dokumenty techniczne, polityki, analizy bezpieczeństwa i instrukcje agentów. Źródło witryny w `mkdocs.yml` to `docs_dir: pages`, a katalog budowania to `site/`.

## Jawna lista zasobów

Każdy plik HTML, Markdown, CSS, JavaScript, obraz i inne dopuszczone rozszerzenie w `pages/` musi mieć wpis w `config/pages-policy.json`. `scripts/validate_pages.py` sprawdza allowlistę, granice ścieżek, symlinki, niezatwierdzoną konfigurację budowania i wybrane niedopuszczalne treści. `scripts/build_public_catalog.py` zapisuje tylko `pages/projects.md`, wybierając jawne, publiczne i zatwierdzone projekty. Nie kopiuj nigdy `portfolio/`, `docs/`, `.github/`, `AGENTS.md` ani prywatnego wyniku `audit-live`.

## Treść i widoczność

Na stronie **nigdy** nie umieszczaj poleceń do agenta AI, promptów, notatek redakcyjnych, komunikatów dla autora, `TODO`, `REPLACE`, opisów organizacji pracy agenta ani porad o wspomaganiu prowadzenia repozytorium. Publiczny język ma być neutralny naukowo i skierowany do odbiorców spoza zespołu.

**Prywatne repozytorium nie gwarantuje prywatności GitHub Pages.** Przed włączeniem witryny sprawdź rzeczywiste ustawienia widoczności, uprawnienia, domenę, plany kosztowe i wygenerowane pliki. Jeśli wymagana poufność nie może być zapewniona, zrezygnuj z publikacji.

**Zabroniony jest tryb `Deploy from a branch` z `main:/docs` lub root repo.** Samo `mkdocs.yml` nie uniemożliwia ujawnienia tych źródeł przez ustawienia GitHub. Możliwe jest wyłącznie osobno autoryzowane wydanie wygenerowanego `site/` z dokładnie zatwierdzonych materiałów, np. przez kontrolowany artefakt GitHub Actions lub dedykowaną gałąź zawierającą tylko treści publiczne.

Przed każdą publikacją: kontrola wszystkich plików i metadanych obrazów, praw i źródeł, linków, wygenerowanego HTML, prywatności, rzeczywistego stanu repozytorium oraz niezależna recenzja finalnego SHA. Skan statyczny nie zastępuje oceny redakcyjnej i prawnej. Bez osobnej zgody właściciela nie dodawaj workflow automatycznie publikującego na merge.
