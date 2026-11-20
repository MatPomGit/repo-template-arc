# Granice portfolio i odpowiedzialności

`arc-*` utrzymuje linie badawcze i rejestry: `areas/index.json`, `portfolio/projects.json`, `portfolio/papers.json`, `portfolio/dependencies.json`. Własność pojedynczego manuskryptu, protokołu i analizy pozostaje w kanonicznym `msc-*` lub starszym repozytorium z udokumentowaną migracją. `app-*` i `lib-*` zachowują własne wersjonowane źródła i kontrakty.

Jedna publikacja ma jedno `owner_project_id`, a przypisania innych programów służą wyłącznie jako `related`. ARC może odsyłać do submodułów, lecz nie może zastąpić zamrożonych gitlinków bieżącym SHA podczas reprodukcji. Zmiany nazw i repozytoriów wymagają mapy kompatybilności i decyzji właściciela.

Nie twórz równoległej bazy tych samych projektów w dokumentacji. Dane o stanie odczytuj z rejestrów, dokumenty mają wyjaśniać ich kontrakty. Publiczne strony korzystają wyłącznie z zatwierdzonych metadanych i nie mogą zdradzać nazw prywatnych projektów.
