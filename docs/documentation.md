# Standard dokumentacji i limity objętości ARC

**Jedno źródło prawdy:** `portfolio/*.json` i `program.json` przechowują metadane, `ARCHITECTURE.md` opisuje kontekst systemu, `docs/architecture/` szczegóły, `docs/adr/` uzasadnienia decyzji, `SECURITY.md` kanał zgłaszania podatności, `docs/security/` zagrożenia, a `GOVERNANCE.md` kompetencje. `docs/` nie jest źródłem witryny publicznej; `pages/` zawiera wyłącznie zatwierdzoną projekcję.

## Budżety

Automatycznym źródłem jest [config/documentation-policy.json](../config/documentation-policy.json). Liczymy **znaki Unicode**, wraz ze spacjami i końcami wierszy, nie bajty UTF-8.

| Dokument | Limit znaków |
| --- | ---: |
| `AGENTS.md`, `README.md`, `ARCHITECTURE.md` | 12 000 |
| `SECURITY.md`, procedura agentów, runbook | 10 000 |
| `CODE_OF_CONDUCT.md`, `SUPPORT.md`, pojedynczy ADR | 6 000–6 500 |
| `GOVERNANCE.md` | 7 000 |
| Rozdziały architektury i bezpieczeństwa | 8 500 |
| Publiczna strona `pages/**/*.md` | 6 000 |
| Pozostałe `docs/**/*.md` | 10 000 |

Kontrole `python scripts/validate_documentation.py` i `python scripts/validate_pages.py` są częścią CI. Przekroczenie limitu to `FAIL` z liczbą znaków i ścieżką. Nie skracaj kluczowych dowodów lub zapisów naukowych tylko dla osiągnięcia limitu. W razie przepełnienia wyeliminuj powtórzenia, przenieś szczegóły do właściwego istniejącego dokumentu albo utwórz jeden uzasadniony aneks z odnośnikiem, zamiast automatycznie zwiększać limit.

## Aktualizacja wraz z rozwojem programu

**Scaffold:** stan deklarowany odróżnia plan od wykonania. Brak projektów i wyników jest stanem normalnym.

**Pierwszy projekt lub publikacja:** zaktualizuj kanoniczne rejestry, zakres, jeden identyfikator właściciela i stan dowodów; dokumentacja wyjaśnia zmiany i granice, nie powiela listy projektów.

**Pierwszy audyt live lub submoduł:** dokumentuj uprawnienia, zamrożony snapshot, metody reprodukcji i rzeczywistą kontrolę integracji. Brak dostępu nie daje `PASS`.

**Pierwsza strona Pages:** użyj odrębnego `pages/`, zatwierdź każdy plik i zewnętrzną widoczność, usuń instrukcje agentowe, uwagi redakcyjne i wewnętrzne metadane. Najpierw przegląd, potem osobna autoryzacja publikacji.

**Przed wydaniem:** potwierdź licencję, bezpieczeństwo, prawa do treści, aktualność SHA, statusy artykułów, wygenerowany katalog i wynik testów. Przed zmianą każdej polityki zachowaj dokładny SHA i decyzję review.
