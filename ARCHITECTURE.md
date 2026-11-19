# Architektura programu ARC

`arc-*` pełni funkcję portalu naukowego i rejestru źródeł dowodów. `msc-*` jest właścicielem hipotez, protokołów, analiz, danych referencyjnych i manuskryptów, a `app-*` i `lib-*` dostarczają niezależne oprogramowanie. Duże istniejące projekty nie wymagają natychmiastowego przemianowania na `msc-*`.

```text
ARC (strategia, rejestry, publiczny katalog)
  |-- areas/index.json                dziedziny/linie naukowe
  |-- portfolio/projects.json         kanoniczne badania i ich SHA
  |-- portfolio/papers.json           artykuły i jeden właściciel
  |-- portfolio/dependencies.json     aparatura, dane, app/lib
  |-- docs/projects.md                tylko publicznie zatwierdzone wpisy
  +-- [opcjonalne git submodules]     źródła projektów, nie kopie
          |-- msc-*                  nauka i strony badań
          +-- starsze repo           migracja kontrolowana
```

**Niezmiennik:** jedna pozycja artykułu -> jeden `owner_project_id` -> jedno kanoniczne repozytorium. Wieloprogramowe powiązania to tagi i `related`, nie duplikaty.

**Główne programy:** `arc-neuro` (w tym `ndd/`), `arc-ai`, `arc-xr`, `arc-robo`. Nie tworzyć `arc-ndd` ani `arc-eye`. Eye tracking jest rodziną metod i narzędzi.

**Dwa widoki SHA:** `snapshot_sha` służy do odtwarzania i wersjonowania indeksu; `remote_head_sha` jest odczytywany na żywo przez narzędzie audytu i nie zastępuje automatycznie snapshotu. Nie porównywać daty `README.md` z rzeczywistym stanem zdalnego repo.

**Sprzęt:** indeks zawiera tylko `equipment_id`, `contract_path`, `validation_status`; prawdziwe kontrakty i identyfikatory fizyczne pozostają w kanonicznym katalogu Research Autopilot. Nie utożsamiać standardowego Quest 3 z urządzeniem do śledzenia wzroku.
