# GitHub Pages programu badawczego ARC

**Zakres:** publiczny portal *programu badawczego*, a nie strona pojedynczej aplikacji, manuskryptu ani wewnętrzny panel zarządzania. Szablon ma status `scaffold`; obecność `pages/` nie oznacza publikacji. Szczegółowe protokoły i wyniki należą do kanonicznych źródeł: lokalnych ARC albo zewnętrznych `msc-*`, a kod aplikacji i bibliotek do `app-*` i `lib-*`.

## 1. Architektura i granice publikacji

Źródłem witryny jest **wyłącznie `pages/`**; `docs/` zawiera dokumentację techniczną, ADR, polityki bezpieczeństwa i procedury agentów. Konfiguracja `mkdocs.yml` wymaga `docs_dir: pages` oraz `site_dir: site`. Każda publiczna strona i zasób źródłowy musi być jawnie wskazany w `config/pages-policy.json`. Kontrola obejmuje także 24 zatwierdzone zasoby motywu z SHA-256, skrypty w końcowym HTML oraz sumy i wybrane metadane obrazów. Motyw nie ładuje zewnętrznego `highlight.js`. Katalog wynikowy `site/` podlega niezależnemu audytowi `python scripts/validate_site.py --strict` po `mkdocs build --strict`.

Nie przenoś na portal `portfolio/`, `areas/`, `program.json`, `research/`, `equipment/`, `AGENTS.md`, `.github/`, `docs/`, plików danych, logów, nazw prywatnych projektów ani raportów `audit-live`. Katalog publiczny `pages/projects.md` powstaje przez `scripts/build_public_catalog.py` wyłącznie z projektów o `visibility=public`, `public_listing=true` i zweryfikowanym publicznym URL. Generator nie powinien otwierać prywatnych repozytoriów ani kopiować ich plików. **Nawet nazwy projektów prywatnych nie mogą trafić do publicznej historii Git.**

GitHub Pages w repozytorium prywatnym może być publiczne. Przed publikacją sprawdź rzeczywistą widoczność, domenę, ustawienia uprawnień i plany kosztowe. **Zakaz `Deploy from a branch` z `main`, katalogu głównego lub `/docs`.** Publikuj dopiero osobno zatwierdzony `site/`, za pomocą izolowanego artefaktu workflow lub kontrolowanej gałęzi zawierającej wyłącznie wynik. Sam szablon nie włącza automatycznego deploymentu.

## 2. Informacja naukowa dla odbiorcy zewnętrznego

Publiczna strona powinna jasno wyjaśniać cel programu, pytania badawcze, zakres metod, rolę projektów oraz znaczenie wyników bez przypisywania badaniom statusu, którego nie potwierdzają dowody. Zachowaj neutralny, naukowy i przystępny język. Preferowana architektura informacji:

| Sekcja | Zawartość |
| --- | --- |
| O programie | Cele, zakres, główne pytania i kryteria przypisywania projektów do ARC |
| Kierunki badań | Zweryfikowane, ogólne opisy linii badawczych bez wewnętrznych planów |
| Projekty | Wyłącznie projekty odrębnie dopuszczone do publicznego katalogu, z linkiem do kanonicznego źródła |
| Publikacje | Wyłącznie potwierdzone pozycje, identyfikatory MSC, autorzy, data, rzeczywisty DOI/preprint i udokumentowany status |
| Metody i odtwarzalność | Publiczny opis podejścia, zakresu metod, wersji i ograniczeń; nieujawniający prywatnych danych |
| Materiały i cytowanie | Odnośniki do zweryfikowanych, legalnie rozpowszechnianych zasobów; wersja migawki ARC |

Nie twórz pustych zakładek ani dublowanych ręcznie list `portfolio/*.json`. Jeśli lista publikacji nie ma niezależnie zatwierdzonych rekordów, w ogóle nie dodawaj zakładki. Nazwy zakładek powinny odpowiadać tytułom stron. Wiele wersji językowych musi przejść identyczną kontrolę merytoryczną i ujawniania danych.

## 3. Powiązanie ARC, MSC, APP, LIB i urządzeń

ARC jest **indeksem programu i zależności**, a nie właścicielem wszystkich wyników: jedna pozycja `MSC-*` ma jednego kanonicznego właściciela. Pozostałe przypisania są wyłącznie `related`. Dla opublikowanej pozycji podawaj identyfikator, tytuł i link do źródłowego manuskryptu tylko wtedy, gdy jest publicznie dostępny i jego status `submitted` / `accepted` / `published` potwierdza odpowiedni dowód. Sama obecność DOI/URL w rejestrze nie uprawnia do ujawnienia treści.

Aplikacje `app-*` i biblioteki `lib-*` opisuj jedynie jako odrębne, wersjonowane narzędzia, z zatwierdzonym odnośnikiem. Nie kopiuj kodu, dokumentacji implementacyjnej, prywatnych kontraktów ani niezweryfikowanych deklaracji o działaniu aparatury. Publiczna karta sprzętu nie może zawierać prywatnych identyfikatorów, ścieżek, adresów sieciowych czy danych uczestników; wewnętrzne karty urządzeń należą do odrębnego prywatnego repozytorium `devices`.

## 4. Wizualizacje, prywatność i dostępność

Dopuszczalne są zatwierdzone schematy, ilustracje objaśniające metody, syntetyczne przykłady i wykresy, dla których można zweryfikować źródło, jednostki, skale, metodę obliczeń oraz status wyników. Dane rzeczywiste publikuj dopiero po ocenie zgody, reidentyfikacji, praw i polityki udostępniania. Nie publikuj surowych EEG, okulometrii, wideo, psychometrii, plików uczestników, materiałów wrażliwych ani identyfikowalnych logów.

Dla każdego obrazu sprawdź EXIF/XMP/IPTC, miniatury, informacje GPS i osadzone identyfikatory; usuń zbędne metadane. Przy wykresach podawaj etykiety osi, jednostki, liczebność, zakres niepewności i pochodzenie danych, jeśli jest to potrzebne do interpretacji. Zadbaj o responsywność, kontrast, nawigację klawiaturą i cel WCAG 2.2 AA. Nie wprowadzaj niezaufanych zewnętrznych skryptów, trackerów, fontów z CDN i formularzy zbierających dane bez osobnej analizy bezpieczeństwa i prywatności.

Na publicznej stronie **nie wolno umieszczać** instrukcji dla agentów AI, promptów, wewnętrznych procedur, notatek redakcyjnych, komunikatów do właściciela, oznaczeń `TODO`/`REPLACE`, ani porad dotyczących pracy nad repozytorium i `CONTRIBUTING`. Tekst ma być samodzielną informacją dla czytelnika. Regex wykrywa tylko część takich treści, dlatego obowiązkowy pozostaje przegląd redakcyjny.

## 5. Bramka publikacyjna i kontrola po wdrożeniu

1. Ustal aktualne SHA, poziom uprawnień, status publiczny każdego rekordu i dowody uprawniające do jego ujawnienia. Potwierdź, że w publicznym ARC nie ma nawet ścieżek prywatnych projektów.
2. Uruchom `python scripts/validate_repository.py --phase scaffold`, `python scripts/build_public_catalog.py` i ponownie `python scripts/validate_pages.py`. Generator może zmienić wyłącznie `pages/projects.md`; porównaj wynik z zatwierdzonym katalogiem i źródłami.
3. W izolowanym CI wykonaj `mkdocs build --strict` i `python scripts/validate_site.py`. Sprawdź cały `site/`, wygenerowany HTML, indeks wyszukiwania, skrypty, obrazy, metadane, linki i zgodność nawigacji. Nie traktuj poprawnego builda jako zatwierdzenia publikacji.
4. Sprawdź finalny SHA, przegląd techniczny witryny i osobną, jawną zgodę właściciela na publikację konkretnego portalu i zakresu treści. Niezależne review jest opcjonalne. Dopiero wtedy wolno skonfigurować kontrolowane GitHub Pages; brak automatycznego deployu przy merge.
5. Sprawdź rzeczywistą witrynę po wdrożeniu, HTTPS, widoczność, strony 404, dostępność, linki i możliwość wycofania. Zachowaj identyfikator wdrożenia, SHA i protokół decyzji.

W przypadku wycieku zatrzymaj publikację, zabezpiecz dowody i wycofaj witrynę, następnie wykonaj procedurę [reagowania na incydent](security/incident-response.md). Usunięcie pliku z aktualnego builda nie usuwa kopii w pamięci przeglądarek i archiwach. **Wydanie migawki programu ARC jest odrębne od publikacji witryny:** zasady zawiera [procedura wydań](releases.md).



## 6. Identyfikacja wizualna programu i projektów

Nagłówek każdej strony programu używa logo całego ARC, jeżeli jest dostępne w lokalnej, zatwierdzonej postaci `pages/assets/brand/logo.png` (również WebP lub JPEG). Obsługuje to opcja `theme.logo` w MkDocs. Bez logo widoczny pozostaje tytuł programu. Nie stosuje się zastępczego ani fikcyjnego znaku.

Wpis publicznego projektu w katalogu może użyć jego własnego znaku `pages/assets/projects/<project_id>.png` (WebP/JPEG również obsługiwane). Znak jest przypisany do identyfikatora projektu, a nie do samego programu. Logo może pojawić się wyłącznie przy projekcie z `visibility=public` i `public_listing=true`, z poprawnym publicznym adresem. Samo występowanie grafiki w innym repozytorium nie uprawnia do kopiowania jej na Pages.

Każdy obraz musi znajdować się w jawnej liście `config/pages-policy.json:public_files`, z sumą SHA-256 w `approved_image_sha256` odpowiadającą dokładnie opublikowanym bajtom. Kontrolę metadanych i kompletności przeprowadzają walidatory Pages. Dla logo programu `python scripts/site_branding.py --apply` ustawia lokalną ścieżkę w `mkdocs.yml`. Bez tej operacji CI zatrzyma niespójny nagłówek. W CI używany jest tryb tylko do odczytu, `python scripts/site_branding.py`. Publikacja pozostaje osobną czynnością.

Główne README opisuje program i jest przeznaczone dla czytelników zewnętrznych. Komendy konfiguracji, instrukcje redakcyjne, procedury dla agentów i kryteria wewnętrznego przeglądu należą do `TEMPLATE_SETUP.md`, `docs/` oraz `AGENTS.md`, nie do publicznego opisu programu.
