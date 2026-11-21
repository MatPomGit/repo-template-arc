# Migracja rejestrów ARC v1 → v2

Nie zmieniaj starych repozytoriów przez bezpośrednie kopiowanie szablonu. Najpierw zinwentaryzuj rzeczywiste projekty, ID, statusy, źródła `main.tex`, historię, prawa, SHA i `PROJECT_STATE.yaml`. Dla każdego artykułu ustal *jednego* właściciela:

- **local**: kanoniczny TeX pozostaje w bieżącym ARC. Zarejestruj `owner.mode=local`, `owner.project_id=null`, ścieżkę i obszar. Nowy układ to dokładnie `manuscripts/<MSC-ID>/main.tex`; zgodność ze starszym ARC to `papers/<area>/<MSC-ID>/main.tex`, gdzie `area` odpowiada polu z rejestru. Nie generuj fikcyjnego projektu MSC.
- **external**: projekt źródłowy pozostaje kanoniczny; rejestr zawiera `owner.mode=external`, `project_id` i odnośnik do repozytorium. Nie przenoś oryginału na podstawie samej rejestracji.
- **related**: odnotuj relację bez zmiany właściciela.

W zależnościach podaj dokładnie jeden niepusty identyfikator `paper_id` albo `project_id` (drugi klucz musi być nieobecny, nie `null`). `commit_sha` lokalnego manuskryptu odtwarzaj ze wskazanej migawki Git, a `blob_sha` porównuj z plikiem w tym commicie. Kontrola bez wskazanego SHA to `NOT_RUN`; brak obiektu historycznego w płytkim checkout to `UNAVAILABLE`, nigdy `PASS`. Zdalne źródła `external` wymagają osobnego audytu referencji.

W v2 rozdziel `research_state` i `publication_stage`; przekształcenie starych stanów wymaga jawnej mapy, bez automatycznego podwyższania dojrzałości. Rejestry `projects`, `papers` i `dependencies` otrzymują `schema_version=2`; `program.json` ma `schema_version=2` i `template_version=2.0.0`, a `PROJECT_STATE.yaml` zgodną wersję.

Przed zapisem utwórz raport zmian, mapę dawnych ścieżek i źródłowe SHA. Po migracji porównaj liczbę rekordów, tożsamości manuskryptów, ich treści, linki, pochodzenie i testy. Uruchom `python scripts/validate_repository.py --phase scaffold` i testy. Cofnięcie polega na przywróceniu zweryfikowanego SHA poprzedniej gałęzi, bez wymuszania historii `main`.

Właściwy zautomatyzowany migrator i kontrola repozytoriów potomnych należą do fazy C. Ten dokument nie oznacza, że migracje już wykonano.
