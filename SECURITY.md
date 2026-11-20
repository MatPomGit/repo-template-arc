# Bezpieczeństwo i poufność programu ARC

**Status szablonu:** brak skonfigurowanego prywatnego kanału przyjmowania zgłoszeń. Właściciel projektu powinien ustalić rzeczywisty, obsługiwany kanał przed udostępnieniem usług lub zbieraniem danych. Nie podawaj fikcyjnego adresu ani nie obiecuj czasu odpowiedzi.

## Zasoby i granice

ARC jest rejestrem projektów i dowodów, a nie magazynem danych osobowych. Rejestry mogą zawierać odnośniki do prywatnych repozytoriów, SHA, sprzętu i wewnętrznych źródeł; **w publicznym ARC nie wolno przechowywać nawet nazw prywatnych projektów**, niezależnie od `public_listing`. GitHub Pages może być publiczne mimo prywatności repozytorium, a historia Git jest często trwale dostępna po publikacji.

Nigdy nie umieszczaj w Git, logach, dokumentacji publicznej ani plikach `.gitmodules`: tokenów, kluczy, danych uczestników, surowych EEG/wideo/gaze, danych zdrowotnych, prywatnych ścieżek dostępu i zastrzeżonych materiałów. Kanoniczne kontrakty aparatury są w uprawnionym katalogu, a nie kopiowane do publicznego portalu.

## Dostęp, testy i reakcja

Niezaufane PR i zależności uruchamiaj tylko w izolacji, bez sekretów i na nieuprzywilejowanych runnerach. `audit-live` prywatnych źródeł wymaga osobnych uprawnień; brak dostępu oznacza `UNAVAILABLE`. Nie modyfikuj produkcji, reguł dostępu ani historii Git bez zgody. Podejrzenia wycieku kieruj prywatnie do upoważnionego właściciela, nie do publicznego Issue.

Powiązane instrukcje: [model zagrożeń](docs/security/threat-model.md), [reagowanie na incydenty](docs/security/incident-response.md), [ADR granic publikacji](docs/adr/0002-publication-boundaries.md) i [polityka Pages](docs/pages.md). Przed publikacją sprawdź prawa, widoczność, kompletne zasoby HTML i zgodę właściciela.
