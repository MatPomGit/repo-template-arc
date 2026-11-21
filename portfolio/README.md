# Kanoniczne rejestry programu ARC (v2)

`portfolio/papers.json` jest jedynym **edytowalnym lokalnym rejestrem artykułów ARC**. Zawiera: identyfikator MSC, tytuł, linię badawczą, `research_state`, `publication_stage`, `relation`, `owner`, `manuscript`, `study_plan`, zgodę na umieszczenie w katalogu, DOI, odnośniki i `stage_evidence`. Status naukowy i etap publikacji są oddzielne.

- `owner.mode=local`: kanoniczne źródło LaTeX znajduje się w tym ARC, `owner.project_id=null`; nie rejestruj fikcyjnego `msc-*`.
- `owner.mode=external`: `project_id` wskazuje projekt z `portfolio/projects.json`, a `owner.repository` musi odpowiadać jego repozytorium. Lokalny plan nie jest kopią kanonicznego manuskryptu.
- `relation=related`: niezależny program wskazuje pozycję innego właściciela. Globalną unikalność ID kontroluje Research Autopilot.
- `portfolio/dependencies.json`: każda zależność w `tools`, `equipment` lub `datasets` wskazuje **dokładnie jedno** z `paper_id` albo `project_id`. Bez duplikowania kodu i kart aparatury.
- `areas/index.json`: lista zdefiniowanych linii programu. Same metody (np. eye tracking) nie stanowią osobnych ARC.

`PROJECT_STATE.yaml` przechowuje stan operacyjny i kontrolne liczniki zgodne z rejestrami. Stare v1 obsługuje walidator kompatybilności; przejście wymaga migratora (faza C). Nie twórz osobnego ręcznie utrzymywanego `manuscript_register.md` ani `publication_register.md`.

Publiczna strona jest niezależną, dopuszczaną projekcją `pages/`. `public_listing=true` nie zastępuje zgody na wdrożenie. Publiczne ARC nie może zawierać prywatnych metadanych nawet poza Pages.

Schematy: [program](../schemas/program.v2.schema.json), [projekty](../schemas/projects.v2.schema.json), [artykuły](../schemas/papers.v2.schema.json), [zależności](../schemas/dependencies.v2.schema.json).
