# ARC — REPLACE_PROGRAM_NAME

**Rodzaj repozytorium:** program naukowy `arc-*`  
**Program:** `arc-REPLACE`  
**Wersja szablonu:** `2.0.0`  
**Autor podstawowy:** Mateusz Pomianek; dodatkowi współautorzy po potwierdzeniu wkładu  
**Stan naukowy:** indeks planowany, bez potwierdzonych wyników empirycznych

## Misja i granice programu

Zastąp ten akapit zwięzłym opisem pytań naukowych, kryterium przypisania manuskryptu i odrębności od innych ARC. Dostępne programy nadrzędne: **ARC Neuro, ARC AI, ARC XR, ARC Robo**. NDD to linia w Neuro, a nie osobny program. Okulometria jest metodą, nie piątym programem.

## Katalog badań

Rejestr kanonicznych projektów jest w [`portfolio/projects.json`](portfolio/projects.json), artykułów w [`portfolio/papers.json`](portfolio/papers.json), zależności w [`portfolio/dependencies.json`](portfolio/dependencies.json). ARC może prowadzić lokalne kanoniczne manuskrypty w `manuscripts/MSC-*/`, a dla zewnętrznych `msc-*`/repozytoriów historycznych utrzymuje referencje i zależności. Nie przechowuje duplikatów cudzych źródeł. Starsze repozytoria mogą być wskazywane pod obecną nazwą do czasu kontrolowanej migracji.

[Publiczny katalog projektów](pages/projects.md) jest generowany z pozycji jawnie zatwierdzonych do publikacji. Program ARC nie jest repozytorium surowych danych uczestników ani pakietem aplikacji.

## Generatory ARC i manuskryptów

Nowy program inicjalizuje się poprzez `python scripts/init_arc.py --programme arc-neuro --repository OWNER/arc-neuro --title "Nazwa" --owner "Autor" --scope "Zakres naukowy" --visibility public --area ndd`. Komenda **domyślnie nie zapisuje plików**; po przeglądzie dodaj `--apply`. Skrypt nie przyznaje zgody na publikację.

Lokalny manuskrypt tworzy `python scripts/new_manuscript.py --id MSC-ADHD-P01 --title "Tytuł" --area ndd --study-type empirical`. Również wymaga `--apply`; tworzy `main.tex`, `study.yaml`, `references.bib` i aktualizuje kanoniczny rejestr. Walidacja planu: `python scripts/validate_study.py --path manuscripts/MSC-ADHD-P01/study.yaml --paper-id MSC-ADHD-P01`. Zależności walidacji: `pip install -r requirements-research.txt`.

## Uruchomienie

```bash
python scripts/validate_repository.py --phase scaffold
python scripts/validate_documentation.py
python scripts/validate_pages.py
# Po izolowanym zbudowaniu MkDocs: python scripts/validate_site.py
python -m unittest discover -s tests -v
python scripts/build_public_catalog.py
# Jeśli skonfigurowano submoduły, pobierz przypięte wersje:
python scripts/bootstrap.py --mode reproduce
# Gdy potrzebujesz analizy bieżącego portfolio, sprawdź aktualne gałęzie zdalne:
python scripts/bootstrap.py --mode audit-live
```

Weryfikacja `audit-live` **nie zmienia** przypiętych commitów i nie uruchamia kodu projektów podrzędnych. Brak dostępu do prywatnego repozytorium daje `UNAVAILABLE`, nie `PASS`.

## Audyt i plan napraw

Zobacz [niezależny audyt szablonu ARC z 2026-11-19](reviews/2026-11-19-template-audit.md), zawierający priorytety P0–P2 i test akceptacyjny. Publiczne repozytoria mogą korzystać z istniejących izolowanych kontroli CI, bez sekretów i bez dostępu do prywatnych projektów; wynik testu nie jest zgodą na publikację.

## Architektura i bezpieczeństwo

[Kontrole CI i wymagane bramki PR](docs/operations/ci-gates.md) dokumentują różnicę między PASS testów, uprawnionym review i rzeczywistą ochroną gałęzi.


[Architektura](ARCHITECTURE.md), [zarządzanie](GOVERNANCE.md), [model zagrożeń](docs/security/threat-model.md), [decyzje ADR](docs/adr/README.md), [standard dokumentacji](docs/documentation.md), [polityka GitHub Pages](docs/pages.md), [wydania programu](docs/releases.md) i [wsparcie](SUPPORT.md). Nie twórz osobnego `CONTRIBUTING.md`.

## Otwartość

Strona programu: **NOT_CONFIGURED**. Strony indywidualnych projektów znajdują się w odpowiednich repozytoriach. Architektura: [ARCHITECTURE.md](ARCHITECTURE.md). Zasady badań: [RESEARCH.md](RESEARCH.md). Reprodukowanie wersji: [REPRODUCIBILITY.md](REPRODUCIBILITY.md). Kryteria publikacji: [docs/publication-policy.md](docs/publication-policy.md).

Nie publikować prywatnych nazw, danych ani wewnętrznych ścieżek bez zgody właściciela. Plik `LICENSE` pozostaje nieaktywnym szablonem do chwili wyboru właściwej licencji.
