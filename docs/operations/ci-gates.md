# Kontrola CI i bramki PR programu ARC

Program ARC uruchamia izolowany workflow GitHub-hosted dla publicznych repozytoriów na zdarzeniach pull_request i push do main. Checkout działa na dokładnym HEAD SHA, bez utrwalania poświadczeń, bez submodułów i LFS, z uprawnieniami contents: read. Prywatne repozytoria nie uruchamiają tego joba automatycznie i wymagają oddzielnej polityki dostępu i kosztów.

Wymagany wynik techniczny przed merge:
- arc-program-contract: PASS, zerowe findings, kontrola widoczności repozytorium;
- walidacja katalogu pages, dokumentacji, SHA oraz deterministyczności;
- testy E2E generatorów, walidacja study.yaml i schematów, kontrola testów negatywnych;
- MkDocs build --strict i audyt całego HTML.

Samo SUCCESS CI nie jest niezależnym APPROVED. Formalna recenzja E3/E4 musi odnosić się do finalnego exact SHA, a odrębny uprawniony recenzent musi zatwierdzić PR zgodnie z polityką R2/R3. Do rulesetu main należy dodać obowiązkowy status check offline-arc-validation i wymaganie pull request review. W aktualnym rulesecie są tylko blokady deletion i non_fast_forward, więc egzekucja tego warunku na serwerze GitHub wymaga uprawnień administracyjnych. Jeżeli administracja nie pozwala potwierdzić reguł, status bramki to GATE_UNENFORCED / HOLD.

Samo scalenie PR nie upoważnia do publikacji GitHub Pages, artykułów, wyników eksperymentalnych, archiwum danych ani Release. Publikacja pozostaje osobnym zadaniem z kontrolą uprawnień i zakresu ujawnienia. Nie uruchamia się niezaufanego kodu na stałym runnerze HomeServer.
