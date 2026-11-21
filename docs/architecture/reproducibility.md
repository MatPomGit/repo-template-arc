# Architektura odtwarzalności ARC

`snapshot_sha` jest migawką projektu używaną w historycznej analizie, a `remote_head_sha` opisuje aktualny stan zdalny. `STALE` oznacza rozbieżność wersji, **nie** nieważność wyników. `UNAVAILABLE` oznacza brak potwierdzonych danych o stanie.

Odtwarzanie wymaga dokładnego SHA rzeczywistego właściciela manuskryptu (ARC dla `local`, repozytorium projektu dla `external`) i źródeł oprogramowania, wersji zależności, kontraktów aparatury, manifestu zbioru danych oraz dowodów w repozytorium kanonicznym. Dla źródeł zewnętrznych ARC przechowuje odnośniki i stan odczytu; lokalny manuskrypt jest odtwarzany z dokładnego SHA ARC. Nie replikuje się danych ani manuskryptów zewnętrznych. Składniowa kontrola 40-znakowego SHA nie poświadcza istnienia Git object. Lokalny `commit_sha` sprawdzany jest względem zawartego w nim `main.tex`; podany `blob_sha` musi odpowiadać obiektowi w tej migawce. Brak historii Git oznacza `UNAVAILABLE`, a brak metadanych SHA oznacza `NOT_RUN`. Weryfikacja źródła zewnętrznego wymaga odrębnego autoryzowanego audytu.

Jeżeli projekt wykorzystuje submoduły, kontroluj zgodność gitlinku z rejestrem, ale nie wykonuj `submodule update --remote` w katalogu historycznego eksperymentu. Każde przemianowanie lub odtworzenie musi zachować mapę dawnych identyfikatorów i historię.

Nadrzędny opis: [REPRODUCIBILITY.md](../../REPRODUCIBILITY.md); procedura: [runbook](../operations/runbook.md).
