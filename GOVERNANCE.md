# Zarządzanie programem badawczym ARC

Program ARC zarządza **portfelem publikacji** i może prowadzić lokalne źródła naukowe, ale nie przejmuje treści cudzych projektów. Właściciel naukowy odpowiada za zakres programu, akceptację przypisania projektu i publikację publicznych metadanych. Zewnętrzne `msc-*` zachowują odpowiedzialność za swoje hipotezy, protokoły, wyniki, prawa i manuskrypty. W przypadku pracy lokalnej odpowiada za nie kanoniczny właściciel ARC.

Zmianę rejestru dopuszczaj tylko po potwierdzeniu kanonicznego właściciela, aktualnej wersji, zakresu i stanu dowodu. Każda publikacja ma jednego właściciela; referencje innych ARC oznaczaj `related`. W publicznym repozytorium zabronione są wpisy wskazujące prywatne projekty, nawet gdy `public_listing` jest wyłączone.

## Uprawnienia, recenzje i publikacja

Research Autopilot, jeśli dostępny i uprawniony, zarządza kolejką, leasingiem i limitem WIP. Zmiany wymagają uprawnień, przeglądu technicznego i testów finalnego SHA adekwatnych do ryzyka R0–R3 z [AGENTS.md](AGENTS.md). Niezależne review może być wykonane, ale nie jest obowiązkową bramką merge. Własnej kontroli nie przedstawiaj jako niezależnej.

Migracje historii, przenoszenie projektów, ujawnienie prywatnych metadanych, wydania i GitHub Pages wymagają oddzielnego zatwierdzenia i możliwości wycofania. Scalenie PR nie oznacza publikacji. Decyzje architektoniczne przechowuje [ADR](docs/adr/README.md), natomiast stan i źródła faktów pozostają w `portfolio/`, `program.json` i `RESEARCH.md`. Nie utrzymuj równoległych rejestrów.

Zasady ochrony danych: [SECURITY.md](SECURITY.md); zachowanie: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md); publikacja: [docs/pages.md](docs/pages.md).
