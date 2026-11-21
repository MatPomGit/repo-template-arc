# ADR-0003: hybrydowa własność manuskryptów ARC

**Status:** accepted  
**Data:** 2026-11-21

## Kontekst

Programy ARC rozwijają lokalne źródła TeX, choć dotychczasowy szablon traktował ARC wyłącznie jako indeks zewnętrznych MSC. Wymóg osobnego repozytorium dla każdej koncepcji rozdrabnia portfel; kopiowanie kanonicznego manuskryptu prowadzi do rozbieżności i błędów w reprodukcji.

## Decyzja

Artykuł ma jedno globalne ID MSC i jedno kanoniczne repozytorium. Tryb `local`: kanoniczny TeX, plan badawczy i dowody pochodzą z ARC. Tryb `external`: źródłem jest odrębne MSC lub repo historyczne, a ARC utrzymuje tylko referencję, SHA i opcjonalny niekanoniczny plan. Inne programy wskazują `related`, nie utrzymują drugiej kopii.

Rejestrem artykułów programu jest `portfolio/papers.json`; widoki Pages i globalny indeks Research Autopilot są wyprowadzane z zatwierdzonych danych. Wrażliwe dane i kod APP/LIB/DEVICES zachowują odrębnych właścicieli. Migracja własności wymaga mapy ścieżek, SHA, kontroli praw, historii i planu cofnięcia. Nie podwyższa automatycznie stanu naukowego.

## Alternatywy

Wyłącznie odrębne MSC mnożą repozytoria; kopiowanie manuskryptów narusza jedno źródło prawdy. Hybryda wymaga migracji schematu i testów, ale obejmuje oba istniejące sposoby pracy.

## Konsekwencje

Przejście z v1 na v2 jest zmianą kontraktu, realizowaną osobnym PR. Do wdrożenia rejestru v2 lokalne pozycje nie mogą być zapisywane w rejestrze v1 przez tworzenie fikcyjnych projektów. ADR nie przenosi samodzielnie istniejących źródeł i nie stanowi zgody na publiczne ujawnienie treści. W publicznym ARC commit manuskryptu, planu lub protokołu ujawnia ich zawartość i historię niezależnie od `pages/`; wymagane jest osobne potwierdzenie praw do udostępnienia. Przed akceptacją konieczne są testy i weryfikacja rzeczywistych projektów.
