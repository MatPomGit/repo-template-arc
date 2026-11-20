# ADR-0001: jeden kanoniczny właściciel artykułu

**Status:** proposed  
**Data:** 2026-11-20

## Kontekst

Programy badawcze ARC mogą wykorzystywać wspólne metody, aparaturę i oprogramowanie. Nie usprawiedliwia to tworzenia dwóch kopii tego samego manuskryptu lub rejestru wyników w różnych programach.

## Propozycja

Jeden manuskrypt ma jedno `owner_project_id` i repozytorium kanoniczne, a programy powiązane używają odnośników `related`. ARC nie utrzymuje źródłowych danych, kodu aplikacji i protokołu badania jako kopii. Publiczny katalog wybiera świadomie zaakceptowane odnośniki.

## Alternatywy i konsekwencje

Duplikacja uprościłaby początkową nawigację, lecz prowadziłaby do niespójnych DOI, dat i SHA. Utrzymanie jednego źródła wymaga kontroli identyfikatorów i decyzji przy migracji. Przed zmianą statusu na `accepted` zweryfikuj rzeczywiste projekty i repozytoria.
