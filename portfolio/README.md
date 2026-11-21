# Kanoniczne rejestry programu

- `projects.json`: lista niezależnych projektów, także istniejących pod dawnymi nazwami. Pola każdego wpisu: `id`, `title`, `repository`, `url`, `role` (`primary`/`related`), `primary_program`, `line`, `status`, `visibility`, `public_listing`, `default_branch`, `snapshot_sha`, `pages_url`, `submodule_path`.
- `papers.json` (obowiązujący schemat v1): `id`, `title`, `owner_project_id`, `canonical_repository`, `manuscript_path`, `stage`, `doi`, `preprint_url`, `preregistration_url`. Pole `owner_project_id` jest wymagane wyłącznie przez walidator v1 i wskazuje zewnętrzny projekt. Docelowy schemat v2 zastępuje tę regułę właścicielem `local` lub `external` bez fikcyjnego projektu.
- `dependencies.json`: grupy `tools`, `equipment`, `datasets`. Rekord zawiera `project_id`, `ref` i — zależnie od kategorii — wersję/commit, `equipment_id`, `contract_path` albo manifest/checksum. Brak duplikacji kontraktów aparatury.
- `areas/index.json`: lista `lines` z `id`, `title`, `description`. W ARC Neuro należy rozważyć `ndd`, `affect`, `cognition`, `social`, `psychometrics`; nie robić z NDD piątego ARC.

**Etap wdrożenia:** ten commit dokumentuje model hybrydowy, lecz aktywny rejestr i walidator nadal mają `schema_version: 1`. Rekordy `local` zapisuj dopiero po wdrożeniu i przetestowaniu schematu v2. Nie obchodź walidatora i nie dodawaj sztucznych projektów w `projects.json`.

**Publiczne strony** powstają wyłącznie z projektów `public_listing=true`, `visibility=public` i potwierdzoną witryną HTTPS. Repo prywatne nie powinny być indeksowane publicznie bez wyraźnej decyzji.
