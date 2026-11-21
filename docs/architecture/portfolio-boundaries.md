# Granice portfolio i odpowiedzialności

`arc-*` utrzymuje linie badawcze i rejestry: `areas/index.json`, `portfolio/projects.json`, `portfolio/papers.json`, `portfolio/dependencies.json`. Własność pojedynczego manuskryptu, protokołu i analizy może pozostawać w lokalnym ARC (`local`) albo w kanonicznym zewnętrznym `msc-*`/historycznym repozytorium (`external`). Lokalny plan artykułu zewnętrznego nie jest drugim kanonicznym manuskryptem. `app-*` i `lib-*` zachowują własne wersjonowane źródła i kontrakty.

Jedna publikacja ma jednego kanonicznego właściciela (lokalne ARC lub zewnętrzny projekt), a przypisania innych programów służą wyłącznie jako `related`. ARC może odsyłać do submodułów, lecz nie może zastąpić zamrożonych gitlinków bieżącym SHA podczas reprodukcji. Zmiany nazw i repozytoriów wymagają mapy kompatybilności i decyzji właściciela.

Nie twórz równoległej bazy tych samych projektów w dokumentacji. Dane o stanie odczytuj z rejestrów, dokumenty mają wyjaśniać ich kontrakty. Publiczne strony korzystają wyłącznie z zatwierdzonych metadanych i nie mogą zdradzać nazw prywatnych projektów.

## Referencje dowodowe statusów artykułów

Etapy `submitted`, `accepted` i `published` wymagają `stage_evidence` zawierającego `kind`, sumę SHA-256 dowodu (`sha256`) i datę weryfikacji (`checked_on`). Odpowiednie rodzaje dowodów to `submission_receipt`, `editorial_decision` i `publication_record`. Sam skrót nie zastępuje kontroli źródłowego dokumentu przez uprawnionego recenzenta. W ARC zapisuje się wyłącznie identyfikator odcisku, bez prywatnych listów od redakcji. Status `published` wymaga ponadto DOI lub publicznego URL do wydanej publikacji. Rejestry używają zamkniętych zestawów pól, a nowe rodzaje metadanych wymagają rewizji kontraktu i testów.

Pola publicznych adresów są sprawdzane składniowo, w tym odrzucane są prywatne adresy IP. Nie jest to dowód dostępności witryny ani prawa do publikacji. Jawna decyzja właściciela oraz audyt rzeczywistej domeny pozostają osobnymi warunkami.
