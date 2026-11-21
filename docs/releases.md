# Wydania i wersjonowanie programu badawczego ARC

**Przedmiot wydania:** zweryfikowana, odtwarzalna **migawka programu i jego publicznych metadanych**, a nie publikacja artykułu naukowego, danych uczestników, aplikacji ani bibliotek. Kanoniczne wyniki badań pozostają w repozytorium ich właściciela (lokalne ARC albo zewnętrzne MSC), a oprogramowanie w `app-*` i `lib-*`. GitHub Release, publikacja Pages, DOI, prerejestracja i zgłoszenie do czasopisma są odrębnymi czynnościami, z odrębnymi zgodami i dowodami. Szablon ma status `scaffold`; aktualnie nie jest dopuszczony do wydania.

## 1. Tożsamość, wersje i zakres

`VERSION` określa wersję migawki **programu ARC**, a `program.json:template_version` i `PROJECT_STATE.yaml:template_version` określają niezależną wersję szablonu. Nie synchronizuj ich automatycznie. Dla wydań stosuj **SemVer 2.0.0**:
- `MAJOR`: niezgodna zmiana schematu rejestrów, semantyki pól lub relacji własności;
- `MINOR`: zgodne rozszerzenie zakresu, nowe zatwierdzone linie i projekty albo dodatkowa funkcja indeksu;
- `PATCH`: zgodna korekta metadanych, odnośnika czy dokumentacji, bez zmiany znaczenia dowodów.

Dopuszczalne są wersje przedwydaniowe, np. `0.3.0-rc.1`; tag wydania `v0.3.0` ma wskazywać **jeden konkretny commit**. Po publicznym wydaniu nie przesuwaj tagu ani nie nadpisuj artefaktu. Zamrożona migawka historyczna pozostaje identyczna nawet wtedy, gdy `audit-live` wykryje nowsze zdalne commity. Aktualizacja publikowana jest jako **nowa wersja**.

## 2. Dwa typy pakietów

| Typ | Zawartość dozwolona | Wymagania |
| --- | --- | --- |
| `arc-catalogue` | Zatwierdzone publiczne metadane programu, objaśnienie zakresu, `CITATION.cff`, changelog, odnośniki do publicznych źródeł | Każdy wpis jawnie dopuszczony; brak ścieżek prywatnych projektów, ich nazw, danych, tokenów i wewnętrznych logów |
| `arc-reproducibility` | Manifest zamrożonych wersji, SHA commitów i sum danych **tylko w uprawnionym zakresie**, konfiguracja oraz instrukcja odtworzenia | Spójne gitlinki, jawne kontrakty, wersje środowiska i skryptów, status dostępu do danych oraz odpowiednio ograniczony kanał dystrybucji |

Pakiety `arc-catalogue` i `arc-reproducibility` nie powinny zawierać pełnych manuskryptów, nawet jeśli ARC jest ich kanonicznym właścicielem. Lokalny TeX może należeć do repozytorium ARC, ale jego publikacja i odrębne wydanie manuskryptu podlegają osobnej decyzji. Pakiety nie obejmują także surowych danych, kodu `app-*`/`lib-*`, firmware, pakietów urządzeń ani prywatnych raportów `audit-live`. Dostęp do artefaktu prywatnego nie może być zastępowany „publicznym zipem”; zakres danych zawsze wynika z zgód, etyki i praw. Dla repozytorium prywatnego przyjmij **private-only** jako domyślny kanał wydania. Widoczność poszczególnych elementów sprawdzaj niezależnie od widoczności repo.

## 3. Manifest dowodowy

Dla planowanej wersji przygotuj **nieśledzony** manifest `outputs/arc-release-manifest.json` zawierający co najmniej: `schema_version`, `kind`, `version`, `programme`, `commit_sha`, `audience` (`public`/`restricted`), sumy SHA-256 kanonicznych rejestrów i co najmniej jednego konkretnego artefaktu oraz rzeczywiste wyniki kontroli. Manifest powinien wiązać:
 
`ARC commit -> program.json -> areas/index.json -> portfolio/projects.json + papers.json + dependencies.json -> canonical owner SHA (ARC/local albo project snapshot SHA/external) -> manuscript source / app-lib release -> dataset manifest / checksum -> scientific result / verified DOI`.

Elementy niepubliczne opisuj wyłącznie w chronionym obiegu. Nie wystawiaj URL lub nawet nazwy prywatnego `msc-*` w publicznym manifeście. Stan `STALE` w audycie live oznacza pojawienie się nowego commita, a nie brak odtwarzalności historycznej migawki; `UNAVAILABLE` nie znaczy `PASS`.

Kontrola strukturalna manifestu może potwierdzić spójność SHA plików i statusów. **Nie dowodzi sama z siebie** poprawności merytorycznej, prawa do publikacji, autentyczności raportu testowego ani tożsamości zatwierdzającego. Przed rzeczywistym wydaniem zweryfikuj pochodzenie artefaktu z zaufanego joba, digest i claims niezależnej atestacji (np. GitHub artifact attestations), repozytorium, SHA, workflow oraz upoważnienie osoby dopuszczającej. Nie uznawaj samodeklaracji typu `approved: true` za dowód.

## 4. Bramka wydania R0–R3

1. **R0 – zakres i tożsamość:** nazwa jednego z programów ARC, właściciel, rzeczywista widoczność, kompletne kanoniczne rejestry, brak placeholderów, wybrana licencja i potwierdzone prawa do treści.
2. **R1 – zgodność rejestrów:** pozytywny wynik `python scripts/validate_repository.py --phase scaffold`, kontrola `PROJECT_STATE.yaml`, jednoznacznej własności `local`/`external` dla każdego MSC, spójności SHA submodułów, identyfikatorów projektów i zależności, brak wpisów prywatnych w publicznym ARC.
3. **R2 – odtwarzalność i dowody:** manifest na **exact SHA**, konkretne artefakty i sumy, wyniki testów w czystym środowisku, deterministyczny generator katalogu, weryfikacja publicznych źródeł i renderu. Dla reprodukcji korzystaj z trybu `reproduce`, a nie `audit-live`; brak dostępnej próbki lub sprzętu oznacz `UNAVAILABLE`/`NOT_RUN`.
4. **R3 – decyzja i dystrybucja:** kontrola finalnego SHA i wyniku CI oraz osobna zgoda właściciela na **wersję, artefakt, kanał i publiczność**. Niezależne review jest opcjonalne. Brak egzekwowania status checks w ruleset oznacz `CI_NOT_ENFORCED`; nie traktuj zielonego CI jako zgody na Release.

Procedura `python scripts/validate_repository.py --phase publish` dotyczy kontroli metadanych i gotowości **katalogu publicznego**. Nie jest bramką GitHub Release, atestacją artykułu ani zgodą etyczną. Wydanie migawki programu nie wymaga automatycznej publikacji Pages; wdrożenie portalu pozostaje osobną decyzją według [polityki Pages](pages.md).

## 5. Publikacje naukowe i DOI

Statusy artykułu `submitted`, `accepted` i `published` wolno deklarować wyłącznie z odpowiednim `stage_evidence` w kanonicznym repozytorium (lokalnym ARC lub zewnętrznym MSC). Wpis do katalogu ARC nie oznacza zgody czasopisma, recenzji naukowej ani możliwości upublicznienia tekstu. Prawdziwy DOI, data i URL wymagają niezależnej weryfikacji; nie przypisuj DOI repozytorium ani artefaktowi „na zapas”.

Rozróżniaj wersję programu, wersję datasetu, wersję kodu, wersję protokołu i etap publikacji. Wydania `arc-reproducibility` mogą zawierać metadane zbioru, ale udostępnienie samych danych odbywa się według odrębnej polityki danego zasobu. Zmiana wyników analizy po wydaniu wymaga nowej wersji artefaktu i odnotowania wpływu na powiązane manuskrypty, nie korekty wstecznej bez śladu.

## 6. Procedura operacyjna i wycofanie

Przed tagowaniem wykonaj przegląd diff i historii, skontroluj listę plików w paczce, licencję, zależności, odnośniki, widoczność danych, status dowodów i sumy SHA. Właściciel lub uprawniony operator potwierdza finalny commit. Dopiero po zatwierdzeniu zbuduj niezmienny artefakt, podpisz/zatestuj go zgodnie z możliwościami środowiska, opublikuj tag i Release oraz dołącz datę, changelog i instrukcję odtworzenia; sprawdź pobrane pliki. Nie uruchamiaj niezaufanych projektów na stałym runnerze ani nie wydawaj pieniędzy bez zgody.

Przy wykryciu błędu oznacz wydanie jako wycofane lub zastąpione, zablokuj dalszą dystrybucję poufnych plików, powiadom odbiorców i wydaj nową wersję z odniesieniem do poprzedniej. Nie przepinaj tagu. W razie ujawnienia prywatnych danych postępuj zgodnie z [procedurą incydentu](security/incident-response.md); usunięcie bieżącego Release nie wycofuje skopiowanych plików. Rejestr utrzymuje dokładne SHA i źródło decyzji.

**Stan szablonu:** brak zgody na GitHub Release, brak danych naukowych i brak atestowanego artefaktu. Status takich czynności to **NOT_RUN**, a nie PASS.

