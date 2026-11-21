# ARC — szablon programu badawczego

**Typ:** program ARC (`arc-*`)  
**Rewizja szablonu:** `0.1.0` | **Schemat rejestrów:** `2`

ARC służy do organizacji interdyscyplinarnych programów badawczych, ich projektów, manuskryptów i zależności. Każda praca ma jedno kanoniczne źródło i odrębny identyfikator MSC. Program może utrzymywać własne manuskrypty albo wskazywać zewnętrzne projekty, bez duplikowania dokumentacji naukowej.

## Zakres badań

Zakres programu wynika z jego głównych pytań naukowych, a nie wyłącznie z zastosowanej aparatury czy oprogramowania. Programy ARC obejmują neuronaukę i psychoinformatykę, rzeczywistość rozszerzoną, robotykę oraz metody sztucznej inteligencji.

## Programy i projekty

Indeks projektów znajduje się w [rejestrze projektów](portfolio/projects.json), a indeks manuskryptów w [rejestrze artykułów](portfolio/papers.json). [Rejestr zależności](portfolio/dependencies.json) wiąże badania z wykorzystywanymi narzędziami i zasobami. Metadane rozróżniają stan naukowy pracy i etap jej publikacji.

Publiczny portal programu, jeśli został uruchomiony, korzysta wyłącznie z wydzielonego katalogu [Pages](pages/index.md). Zatwierdzone pozycje katalogu są powiązane z oryginalnymi repozytoriami. Grafiki identyfikujące program i poszczególne projekty mogą występować w publicznym portalu, jeżeli zostały udostępnione i zatwierdzone.

## Metody i odtwarzalność

W [opisie badań](RESEARCH.md) określono ich zakres i główne założenia. [Odtwarzalność](REPRODUCIBILITY.md) opisuje relacje między źródłami, wersjami i dowodami. [Architektura](ARCHITECTURE.md) przedstawia granice odpowiedzialności programu, a [polityka danych](docs/data-policy.md) sposób traktowania zasobów badawczych.

Wpis w katalogu nie stanowi potwierdzenia przeprowadzenia eksperymentu ani opublikowania wyników. Stan badań i dowody są przechowywane w repozytorium kanonicznym danej pracy.

## Informacje o repozytorium

Repozytorium stanowi szablon struktury programów ARC. Szczegółowe informacje o konfiguracji znajdują się w [dokumentacji technicznej](TEMPLATE_SETUP.md), a warunki rozpowszechniania w [licencji](LICENSE).
