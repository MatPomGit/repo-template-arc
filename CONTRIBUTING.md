# Zasady współpracy

Proponuj zmiany rejestrów z odnośnikiem do kanonicznego repozytorium, sprawdzonym właścicielem manuskryptu i weryfikowalnym SHA. Zmiany na gałęziach wymagają niezależnego przeglądu, walidacji lokalnej i zgodności z limitem WIP Research Autopilot. Nie twórz drugiego wpisu manuskryptu w innym programie; użyj `related` i linku do właściciela.

## Autorstwo i środowisko testowe

Mateusz Pomianek jest co najmniej jednym z autorów programu w `CITATION.cff`; opcjonalnych współautorów dopisuje się po potwierdzeniu rzeczywistego wkładu. Autorzy repozytorium ARC nie są automatycznie autorami wszystkich manuskryptów w repozytoriach podrzędnych.

Publiczne repozytoria mogą używać GitHub-hosted runners do bezpiecznego, izolowanego CI. Nie udostępniaj sekretów, danych prywatnych ani poświadczeń do submodułów w kodzie niezaufanych PR. `audit-live` prywatnych źródeł należy wykonywać oddzielnie. Uwzględniaj limity i zatwierdzenie ewentualnych wydatków.
