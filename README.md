# ARC — REPLACE_PROGRAM_NAME

**Rodzaj repozytorium:** program naukowy `arc-*`  
**Program:** `arc-REPLACE`  
**Wersja szablonu:** `1.0.0`  
**Autor podstawowy:** Mateusz Pomianek; dodatkowi współautorzy po potwierdzeniu wkładu  
**Stan naukowy:** indeks planowany, bez potwierdzonych wyników empirycznych

## Misja i granice programu

Zastąp ten akapit zwięzłym opisem pytań naukowych, kryterium przypisania manuskryptu i odrębności od innych ARC. Dostępne programy nadrzędne: **ARC Neuro, ARC AI, ARC XR, ARC Robo**. NDD to linia w Neuro, a nie osobny program. Okulometria jest metodą, nie piątym programem.

## Katalog badań

Rejestr kanonicznych projektów jest w [`portfolio/projects.json`](portfolio/projects.json), artykułów w [`portfolio/papers.json`](portfolio/papers.json), zależności w [`portfolio/dependencies.json`](portfolio/dependencies.json). Projekt `msc-*` ma własny protokół, manuskrypt, dane referencyjne i GitHub Pages; ARC utrzymuje tylko odnośniki oraz metadane zależności. Starsze repozytoria mogą być wskazywane pod obecną nazwą do czasu kontrolowanej migracji.

[Publiczny katalog projektów](docs/projects.md) jest generowany z pozycji jawnie zatwierdzonych do publikacji. Program ARC nie jest repozytorium surowych danych uczestników ani pakietem aplikacji.

## Uruchomienie

```bash
python scripts/validate_repository.py --phase scaffold
python -m unittest discover -s tests -v
python scripts/build_public_catalog.py
# Jeśli skonfigurowano submoduły, pobierz przypięte wersje:
python scripts/bootstrap.py --mode reproduce
# Gdy potrzebujesz analizy bieżącego portfolio, sprawdź aktualne gałęzie zdalne:
python scripts/bootstrap.py --mode audit-live
```

Weryfikacja `audit-live` **nie zmienia** przypiętych commitów i nie uruchamia kodu projektów podrzędnych. Brak dostępu do prywatnego repozytorium daje `UNAVAILABLE`, nie `PASS`.

## Audyt i plan napraw

Zobacz [niezależny audyt szablonu ARC z 2026-11-19](reviews/2026-11-19-template-audit.md), zawierający priorytety P0–P2 i test akceptacyjny. Publiczne repozytoria mogą używać GitHub-hosted runners do bezpiecznych, izolowanych kontroli CI; nie oznacza to, że szablon już ma workflow.

## Otwartość

Strona programu: **NOT_CONFIGURED**. Strony indywidualnych projektów znajdują się w odpowiednich repozytoriach. Architektura: [ARCHITECTURE.md](ARCHITECTURE.md). Zasady badań: [RESEARCH.md](RESEARCH.md). Reprodukowanie wersji: [REPRODUCIBILITY.md](REPRODUCIBILITY.md). Kryteria publikacji: [docs/publication-policy.md](docs/publication-policy.md).

Nie publikować prywatnych nazw, danych ani wewnętrznych ścieżek bez zgody właściciela. Plik `LICENSE` pozostaje nieaktywnym szablonem do chwili wyboru właściwej licencji.
