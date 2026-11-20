# Model zagrożeń programu ARC

**Ocena: NOT_ASSESSED.** Poniższy rejestr obszarów nie stanowi dowodu działania zabezpieczeń.

| Powierzchnia | Zagrożenie | Minimalna kontrola |
| --- | --- | --- |
| Publiczne repo ARC | Ujawnienie nazwy prywatnego projektu mimo `public_listing:false` | Odrzucenie prywatnych wpisów już w rejestrach |
| GitHub Pages | Kopia `docs/`, promptów, dokumentów roboczych, obrazów z metadanymi | `pages/`, jawna allowlista, kontrola treści i renderu |
| `audit-live` | Wycieki tokenów lub metadanych prywatnego repo | Odrębna tożsamość, minimalny dostęp, bez publicznego CI |
| Submoduły | Niezaufany kod, wykradzione credentials | Pinned gitlink, izolacja, kontrola URI i uprawnień |
| Dane i dowody | Błędny SHA, duplikaty, fikcyjne DOI | Zgodność z kanonicznym źródłem i niezależny przegląd |
| Aparatura | Błędne przypisanie urządzenia lub jego walidacji | `equipment_id`, wersja kontraktu, test sprzętowy źródła |
| Publikacja | Naruszenie praw, etyki i polityki wydawcy | Decyzja właściciela i osobna weryfikacja |

Przed konfiguracją rzeczywistego programu uzupełnij zasoby, granice zaufania, prawdopodobieństwo, skutek, właściciela ryzyka, kontrolę i test na dokładnym SHA. Brak dowodu oznacz `NOT_RUN` lub `UNAVAILABLE`, nie `PASS`.

Zobacz [SECURITY.md](../../SECURITY.md), [przepływy](../architecture/data-flow.md) i [ADR](../adr/0002-publication-boundaries.md).
