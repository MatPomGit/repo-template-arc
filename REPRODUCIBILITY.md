# Odtwarzalność i aktualność

| Tryb | Definicja | Działanie |
| --- | --- | --- |
| `reproduce` | Migawka historycznego eksperymentu | inicjalizacja submodułów przy ich **przypiętych** SHA |
| `audit-live` | Bieżący stan programu badawczego | `git ls-remote` dla zarejestrowanych gałęzi źródłowych; bez zmian w checkoutach |

Przypisanie wersji zależy od właściciela manuskryptu:

- `local`: `ARC commit SHA -> manuscripts/MSC-*/ (lub zadeklarowany manuscript_root) -> protokół i plan badania -> app/lib version@SHA -> equipment_id/contract_version -> dataset manifest/checksum -> wynik/DOI`.
- `external`: `ARC commit SHA -> zarejestrowany project snapshot SHA -> kanoniczny manuskrypt w repozytorium zewnętrznym -> app/lib version@SHA -> equipment_id/contract_version -> dataset manifest/checksum -> wynik/DOI`.

Nie twórz fikcyjnego projektu ani `snapshot_sha` projektu dla źródeł lokalnych. Każdy dowód odtwarzalności należy powiązać z dokładnym SHA rzeczywistego właściciela; `audit-live` nie zmienia zamrożonych odniesień.

`STALE` oznacza tylko nowszy zdalny commit; to nie dowodzi błędu ani nieważności historycznego eksperymentu. `UNAVAILABLE` oznacza brak podstaw do pełnego aktualnego audytu. Automatyzacja może zgłosić PR aktualizacyjny po testach, ale nie przepina samodzielnie danych z trwającego eksperymentu.

Dla programów otwartych publikuj wyłącznie przefiltrowany katalog z odrębnego `pages/` i publiczne informacje. GitHub Pages nie służy do gromadzenia danych od uczestników.
