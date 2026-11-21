# Architektura szczegółowa programu ARC

[ARCHITECTURE.md](../../ARCHITECTURE.md) jest krótkim, kanonicznym opisem granic programu. Ten katalog służy do dokumentowania **istniejących** przepływów, zależności i odtwarzalności bez powielania rejestrów.

- [Portfolio i zależności](portfolio-boundaries.md): odpowiedzialność `arc-*`, `msc-*`, `app-*`, `lib-*`.
- [Przepływy danych](data-flow.md): rejestry, audyt live, publiczny katalog oraz granice ujawnienia.
- [Reprodukowanie](reproducibility.md): snapshot, remote HEAD, gitlink i pochodzenie wyników.
- [ADR](../adr/README.md): uzasadnienia decyzji o architekturze i poufności.

**Status szablonu:** brak skonfigurowanych badań i rzeczywistych projektów. Dla programu rozwijanego z tego szablonu każdą zmianę opisuj na podstawie aktualnych faktów, SHA i rzeczywistych dowodów. Dokument nie zastępuje protokołu należącego do kanonicznego właściciela: lokalnego ARC albo zewnętrznego `msc-*`.
