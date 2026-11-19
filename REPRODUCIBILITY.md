# Odtwarzalność i aktualność

| Tryb | Definicja | Działanie |
| --- | --- | --- |
| `reproduce` | Migawka historycznego eksperymentu | inicjalizacja submodułów przy ich **przypiętych** SHA |
| `audit-live` | Bieżący stan programu badawczego | `git ls-remote` dla zarejestrowanych gałęzi źródłowych; bez zmian w checkoutach |

Przypisanie wersji: `program commit -> project snapshot SHA -> manuscript source -> app/lib version@SHA -> equipment_id/contract_version -> dataset manifest/checksum -> wynik/DOI`.

`STALE` oznacza tylko nowszy zdalny commit; to nie dowodzi błędu ani nieważności historycznego eksperymentu. `UNAVAILABLE` oznacza brak podstaw do pełnego aktualnego audytu. Automatyzacja może zgłosić PR aktualizacyjny po testach, ale nie przepina samodzielnie danych z trwającego eksperymentu.

Dla programów otwartych publikuj wyłącznie przefiltrowany katalog i publiczne informacje. GitHub Pages nie służy do gromadzenia danych od uczestników.
