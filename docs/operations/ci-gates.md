# Kontrola CI i bramki PR programu ARC

Program ARC uruchamia izolowany workflow GitHub-hosted dla publicznych repozytoriów na zdarzeniach pull_request i push do main. Checkout działa na dokładnym HEAD SHA, bez utrwalania poświadczeń, bez submodułów i LFS, z uprawnieniami contents: read. Prywatne repozytoria nie uruchamiają tego joba automatycznie i wymagają oddzielnej polityki dostępu i kosztów.

Wymagany wynik techniczny przed merge:
- arc-program-contract: PASS, zerowe findings, kontrola widoczności repozytorium;
- walidacja katalogu pages, dokumentacji, SHA oraz deterministyczności;
- testy E2E generatorów, walidacja study.yaml i schematów, kontrola testów negatywnych;
- MkDocs build --strict i audyt całego HTML.

Przed merge sprawdź pozytywny wynik CI, diff i bezpieczeństwo finalnego exact SHA. Niezależne review jest opcjonalne, bez obowiązkowego `APPROVED`. Zalecane jest egzekwowanie checku `offline-arc-validation` w ruleset `main`, bez wymagania drugiego recenzenta. Gdy ruleset nie egzekwuje CI, raportuj `CI_NOT_ENFORCED` i sprawdź wynik przed merge; nie utożsamiaj braku formalnej ochrony z poprawnością testów.

Samo scalenie PR nie upoważnia do publikacji GitHub Pages, artykułów, wyników eksperymentalnych, archiwum danych ani Release. Publikacja pozostaje osobnym zadaniem z kontrolą uprawnień i zakresu ujawnienia. Nie uruchamia się niezaufanego kodu na stałym runnerze HomeServer.

E4.0 B1: walidator `study.yaml` odrzuca dowiązania w każdym komponencie ścieżki, a ponowne użycie generatora wymaga zgodności rejestru i planu. Zapis wieloplikowy jest odwracalny przy zwykłych błędach procesu z jawnym `ROLLBACK_INCOMPLETE` przy nieudanym przywróceniu; **nie** stanowi transakcji atomowej względem awarii zasilania ani równoległych zmian innych procesów.
