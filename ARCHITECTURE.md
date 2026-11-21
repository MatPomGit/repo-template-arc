# Architektura programu ARC

`arc-*` jest programem badawczym, rejestrem źródeł dowodów i **może być kanonicznym właścicielem lokalnych manuskryptów**. Projekty zewnętrzne `msc-*` zachowują własne hipotezy, protokoły, analizy i manuskrypty; `app-*` i `lib-*` dostarczają niezależne oprogramowanie. Duże istniejące projekty nie wymagają natychmiastowego przemianowania na `msc-*`.

```text
ARC (strategia, rejestry, publiczny katalog)
  |-- areas/index.json                dziedziny/linie naukowe
  |-- portfolio/projects.json         kanoniczne badania i ich SHA
  |-- portfolio/papers.json           artykuły i jeden właściciel
  |-- portfolio/dependencies.json     aparatura, dane, app/lib
  |-- manuscripts/MSC-.../             opcjonalne lokalne źródła TeX
  |-- pages/projects.md               tylko publicznie zatwierdzone wpisy
  +-- [opcjonalne git submodules]     źródła projektów, nie kopie
          |-- msc-*                  nauka i strony badań
          +-- starsze repo           migracja kontrolowana
```

**Granice publikacji:** `docs/` przechowuje dokumentację techniczną, bezpieczeństwa i decyzji architektonicznych; nigdy nie jest źródłem Pages. `pages/` zawiera wyłącznie przeglądnięte materiały dla odbiorców, z jawną listą dopuszczenia. [Architektura szczegółowa](docs/architecture/README.md), [ADR](docs/adr/README.md) i [model zagrożeń](docs/security/threat-model.md) nie są automatycznie publiczne.

**Niezmiennik:** jeden globalny identyfikator MSC -> jedno kanoniczne repozytorium (`local` ARC albo `external` MSC) -> dokładnie jeden właściciel. Dla lokalnego manuskryptu nie twórz fikcyjnego `owner_project_id`. Wieloprogramowe powiązania to tagi i `related`, nie duplikaty.

**Główne programy:** `arc-neuro` (w tym `ndd/`), `arc-ai`, `arc-xr`, `arc-robo`. Nie tworzyć `arc-ndd` ani `arc-eye`. Eye tracking jest rodziną metod i narzędzi.

**Dwa widoki SHA:** `snapshot_sha` służy do odtwarzania i wersjonowania indeksu; `remote_head_sha` jest odczytywany na żywo przez narzędzie audytu i nie zastępuje automatycznie snapshotu. Nie porównywać daty `README.md` z rzeczywistym stanem zdalnego repo.

**Sprzęt:** indeks zawiera tylko `equipment_id`, `contract_path`, `validation_status`; prawdziwe kontrakty i identyfikatory fizyczne pozostają w prywatnym repozytorium `devices`; Research Autopilot korzysta z referencji. Nie utożsamiać standardowego Quest 3 z urządzeniem do śledzenia wzroku.
