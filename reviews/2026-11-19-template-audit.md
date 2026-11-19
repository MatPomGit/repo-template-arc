# Niezależny audyt `repo-template-arc` — 2026-11-19

**Baza:** `main` @ `a85cd647fa5fb92ad65855668acee250417ef917`.  
**Zakres:** szablon nadrzędnego programu badawczego `arc-*`, rejestry `msc-*`, źródła zależności `app-*`/`lib-*`, audyt aktualności SHA, katalog publiczny oraz governance.  
**Metoda:** statyczna inspekcja plików i konfiguracji GitHub; bez uruchamiania testów, audytu zdalnych repozytoriów ani wdrożenia Pages. Ustalenia są oceną pokrycia kontroli, nie dowodem wycieku lub błędnych wyników.

## Werdykt

**Ocena orientacyjna 7/10 (osąd ekspercki, nie wynik testów).** Szablon ma spójną i użyteczną architekturę programu badawczego. W porównaniu z pojedynczymi szablonami `msc-*`/`app-*` oferuje konkretne mechanizmy kontroli powiązań oraz odróżnia historyczny snapshot od aktualnego HEAD. Jednak brak CI, mechanicznej kontroli metadanych YAML i walidacji rzeczywistych dowodów oraz niewystarczający proces przeglądu katalogu publicznego uniemożliwiają uznanie go za w pełni egzekwowalny standard.

| Kryterium | Ocena orientacyjna |
| --- | ---: |
| Architektura portfela i granice własności | 9/10 |
| Walidacja rejestrów i powiązań | 7/10 |
| Reprodukowalność oraz audit-live | 8/10 |
| Prywatność i kontrola publikacji (projekt) | 7/10 |
| Zarządzanie publikacjami naukowymi | 7/10 |
| Automatyczne CI i bramki PR | 2/10 |
| Inicjalizacja i obsługa wieloprojektowa | 7/10 |
| Integracja z Research Autopilot | 8/10 |

### Mocne strony potwierdzone w repozytorium

1. Rozdział ról: `arc-*` indeksuje badania i źródła dowodów, `msc-*` posiada protokoły/manuskrypty, `app-*`/`lib-*` pozostają niezależne; zredukowano ryzyko duplikacji kodu i wyników.
2. `scripts/validate_repository.py` sprawdza m.in. identyfikatory, relacje artykuł–projekt, URL repozytoriów, statusy, dopuszczalne linie badawcze i ścieżki submodułów. Gdy checkout Git jest dostępny, sprawdza zgodność `gitlink` z `snapshot_sha`.
3. `scripts/check_freshness.py` rozróżnia `CURRENT`, `STALE`, `UNPINNED` i `UNAVAILABLE`. `scripts/bootstrap.py` oddziela `reproduce` (przypięte commity) od `audit-live` (zdalne HEAD); nie modyfikuje snapshotów w trakcie audytu.
4. `scripts/build_public_catalog.py` filtruje rekordy wymagając `visibility=public`, `public_listing=true` i poprawnego składniowo URL HTTPS; testy obejmują prywatny projekt i przykłady niezaufanych URL.
5. Domyślnie nie istnieją dane uczestników, projekty ani publikacje, a publiczny portal nie jest automatycznie publikowany. Szablon ma `is_template=true`.

## Ustalenia i plan naprawczy

| ID | Priorytet | Dowód i ryzyko | Rekomendacja |
| --- | --- | --- | --- |
| ARC-01 | P0 | Brak `.github/workflows/`; brak wykonanych GitHub Actions. Ruleset `main` ogranicza usuwanie/non-fast-forward, lecz nie wymaga CI ani review. | Minimalny offline CI na `pull_request`/`push`, testy rejestrów, generatora i walidatora, potem wymagane status checks i przegląd. |
| ARC-02 | P0 | `build_public_catalog.py` uznaje sam `public_listing=true` i syntaktyczny HTTPS za wystarczający warunek umieszczenia wpisu. Nie ma maszynowego dowodu zatwierdzenia publikacji; walidator nie potwierdza istnienia ani publicznej dostępności URL. | Rozdzielić życzenie publikacji od udokumentowanego zatwierdzenia; walidować bezpieczną domenę i pochodzenie metadanych; wymagać przeglądu przed publikacją całego `docs/`, nie tylko wygenerowanej listy. |
| ARC-03 | P0 | `scripts/validate_repository.py` sprawdza wybrane pola `program.json`, ale nie czyta treści `PROJECT_STATE.yaml`; liczniki projektów/artykułów mogą być niezgodne z rejestrami. | Parsować YAML, walidować schematy i spójność `programme`, właściciela, `template_version`, statusów oraz liczników względem JSON. |
| ARC-04 | P1 | Weryfikacja `papers.json` sprawdza właściciela, repo i status, ale nie wymaga źródła dowodowego dla wpisu accepted/published ani poprawnego DOI; unikalność właściciela między różnymi repo ARC nie jest sprawdzana globalnie. | Dodać kontrolę pochodzenia statusów i identyfikatorów, a globalne konflikty właściciela wykrywać centralnie w Research Autopilot. |
| ARC-05 | P1 | `check_freshness.py` przy pustym katalogu i bez `--require-current` zwraca kod 0, mimo `NO_PROJECTS`; `STALE` bez tego przełącznika również nie jest kodem błędu. | Utrzymać rozróżnienie kodu procesu i stanu naukowego; zapewnić jawny tryb strict dla bramek audytowych i testy jego semantyki, bez wymuszania aktualnego HEAD w historycznej reprodukcji. |
| ARC-06 | P1 | Rejestry `portfolio/*.json` są puste, a przykłady nie tworzą pełnej, testowanej ścieżki: rejestracja projektu → artykuł → dependency → `snapshot_sha` → kontrola katalogu. | Dodać mały syntetyczny fixture end-to-end oraz testy negatywne: prywatny rekord, konflikt ID, brak SHA, niepoprawny URL i niezgodny gitlink. |
| ARC-07 | P1 | `CITATION.cff` nadal ma `REPLACE_AUTHOR` zamiast wymaganej tożsamości autora. | Mateusz Pomianek jest zawsze co najmniej jednym z autorów repozytorium programu; dopuszczać współautorów z udokumentowanym wkładem i uzgodnioną kolejnością. |
| ARC-08 | P1 | Szablon nie ma skryptu idempotentnej konfiguracji `program.json`, `PROJECT_STATE.yaml`, `CITATION.cff`, `VERSION`, `README.md`; można pozostawić rozbieżne placeholdery. | Dodać lekki inicjalizator i testy generowania nowego ARC, bez kopiowania logiki schedulera. |
| ARC-09 | P1 | `.gitmodules` jest sprawdzany pod kątem ścieżek, ale brak pełnej weryfikacji zgodności URL submodułu z kanonicznym `repository` w rejestrze. | Porównywać URL `.gitmodules` i repo z portfela oraz `gitlink` z `snapshot_sha`; bezpiecznie raportować `UNAVAILABLE`. |
| ARC-10 | P2 | `template_version=1.0.0` jest zaszyte w walidatorze, podczas gdy `VERSION=0.1.0` opisuje stan repo; nie ma procesu migracji potomnych projektów. | Rozdzielić wersję szablonu i wydania programu, wprowadzić SemVer, changelog i kompatybilne migracje. |
| ARC-11 | P2 | W `load_json` poprawny JSON o nieoczekiwanym typie korzenia (np. lista zamiast obiektu) może wywołać błąd wykonania przy `.get`. | Walidować typy korzeni plików rejestrów, zwracać czytelne `FAIL`; rozszerzyć testy o celowo uszkodzone dane. |
| ARC-12 | P2 | `LICENSE` jest świadomie pustą deklaracją praw; projekt publiczny nie ma jeszcze jawnej licencji na ponowne wykorzystanie. | Przed redystrybucją odróżnić licencje kodu, dokumentacji i materiałów naukowych; weryfikować zgodność z manifestem. |

Przykładowo `safe_public_page_url` sprawdza podstawową składnię i część hostów lokalnych, ale **nie** poświadcza, że host jest oficjalną, sprawdzoną witryną projektu. Powyższe wskazuje zakres przyszłych kontroli; nie stwierdzono opublikowania prywatnego wpisu.

## Zasady obowiązujące przy powielaniu template'u

**Autorstwo.** Mateusz Pomianek pozostaje co najmniej jednym z autorów repozytorium programu w `CITATION.cff` i metadanych dokumentacji. Dodatkowi współautorzy są możliwi po potwierdzeniu rzeczywistego wkładu oraz uzgodnieniu kolejności i afiliacji. Autorstwo oprogramowania/programu nie zastępuje właściwego ustalania autorów poszczególnych artykułów w kanonicznych `msc-*`; prawa autorskie i tożsamość autora commita to odrębne kwestie.

**Runnery.** Repozytoria **publiczne mogą używać GitHub-hosted runners** do krótkich, izolowanych testów offline (np. `ubuntu-latest`). Stałe lokalne runnery HomeServer/Andromeda nie są konieczne do zwykłej walidacji. Żadne sekrety, identyfikatory prywatnych źródeł ani dane uczestników nie mogą trafić do niezaufanego CI; `audit-live` wymagający prywatnych poświadczeń jest oddzielnym, kontrolowanym zadaniem. Stosować `permissions: contents: read`, unikać wykonywania kodu z niezaufanych PR przez uprzywilejowane `pull_request_target`, przestrzegać limitów usług i zasady zero dodatkowych wydatków bez zgody.

**Granice.** ARC nie uruchamia własnego kontrolera/schedulera poza Research Autopilot, nie dubluje manuskryptów, aplikacji ani katalogu aparatury. Publikacja GitHub Pages oraz przenoszenie projektów wymagają odrębnej decyzji.

## Zadania i kryteria zakończenia

### P0: automatycznie egzekwowalne minimum
- [ ] Dodać bezpieczny, tani offline CI i po potwierdzonym PASS egzekwować status checks/PR review.
- [ ] Połączyć publikację katalogu z zatwierdzonym źródłem/recenzją i wykonać negatywne testy wycieku metadanych.
- [ ] Parsować `PROJECT_STATE.yaml` i walidować spójność z rejestrami oraz `program.json`.

### P1: stabilne utrzymanie portfela
- [ ] Weryfikacja statusów publikacyjnych i źródeł dowodowych; globalna unikalność właścicieli przez Research Autopilot.
- [ ] Testowany fixture obejmujący projekt, artykuł, zależność, SHA, submoduł i katalog.
- [ ] Idempotentny inicjalizator czterech wariantów ARC, z wymaganym autorem Mateuszem Pomiankiem i opcjonalnymi współautorami.
- [ ] Doprecyzować semantykę strict w `audit-live`, nie nadpisując zamrożonych SHA.

### P2: utrzymanie długoterminowe
- [ ] Migracje wersji szablonu, obsługa niepoprawnych korzeni JSON i jasna licencja.

### Scenariusz akceptacyjny

Utworzyć repo z szablonu jako jeden z czterech dozwolonych programów, poprawnie skonfigurować metadane (obowiązkowy Mateusz Pomianek, opcjonalny współautor), dodać syntetyczne `msc-example` i `P01`, zweryfikować zgodność SHA i raport `audit-live`, sprawdzić odtwarzanie submodułu, potwierdzić brak prywatnych rekordów w wygenerowanym katalogu, umyślnie uszkodzić owner/DOI/JSON i wykazać FAIL. Następnie otworzyć PR i potwierdzić wymagany status CI na publicznym GitHub-hosted runner. Faktyczne urządzenia i prywatne repo nie są niezbędne do akceptacji szkieletu.

**Zakres niniejszego PR:** udokumentowany audyt, priorytety napraw i korekta polityk autorstwa/runnerów. **Poza zakresem:** implementacja workflow, zmiana rulesetów, migracja istniejących projektów, publikacja Pages, uruchomienie pełnej ścieżki akceptacji. Checkboxy pozostają otwarte.
