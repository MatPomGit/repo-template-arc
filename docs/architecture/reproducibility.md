# Architektura odtwarzalności ARC

`snapshot_sha` jest migawką projektu używaną w historycznej analizie, a `remote_head_sha` opisuje aktualny stan zdalny. `STALE` oznacza rozbieżność wersji, **nie** nieważność wyników. `UNAVAILABLE` oznacza brak potwierdzonych danych o stanie.

Odtwarzanie wymaga przypiętych SHA repozytoriów `msc-*` i źródeł oprogramowania, wersji zależności, kontraktów aparatury, manifestu zbioru danych i dowodów w projekcie kanonicznym. ARC przechowuje odnośniki i stan odczytu, nie replikuje danych ani manuskryptów.

Jeżeli projekt wykorzystuje submoduły, kontroluj zgodność gitlinku z rejestrem, ale nie wykonuj `submodule update --remote` w katalogu historycznego eksperymentu. Każde przemianowanie lub odtworzenie musi zachować mapę dawnych identyfikatorów i historię.

Nadrzędny opis: [REPRODUCIBILITY.md](../../REPRODUCIBILITY.md); procedura: [runbook](../operations/runbook.md).
