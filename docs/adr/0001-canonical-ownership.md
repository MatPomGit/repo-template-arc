# ADR-0001: jeden kanoniczny właściciel artykułu

**Status:** proposed  
**Data:** 2026-11-20

## Kontekst

Programy badawcze ARC mogą wykorzystywać wspólne metody, aparaturę i oprogramowanie. Nie usprawiedliwia to tworzenia dwóch kopii tego samego manuskryptu lub rejestru wyników w różnych programach.

## Propozycja

Jeden manuskrypt ma jedno globalne ID MSC i jedno repozytorium kanoniczne, którym może być lokalny ARC albo zewnętrzny MSC. Programy powiązane używają `related`. Szczegóły: [ADR-0003](0003-hybrid-arc-ownership.md). ARC nie utrzymuje źródłowych danych, kodu aplikacji i protokołu badania jako kopii. Publiczny katalog wybiera świadomie zaakceptowane odnośniki.

## Alternatywy i konsekwencje

Duplikacja uprościłaby początkową nawigację, lecz prowadziłaby do niespójnych DOI, dat i SHA. Utrzymanie jednego źródła wymaga kontroli identyfikatorów i decyzji przy migracji. Przed zmianą statusu na `accepted` zweryfikuj rzeczywiste projekty i repozytoria.
