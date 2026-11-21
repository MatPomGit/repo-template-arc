# Przepływy danych i granice zaufania ARC

**Stan:** schemat, bez skonfigurowanych projektów źródłowych.

| Przepływ | Kanoniczne źródło | Reguła |
| --- | --- | --- |
| Rejestr projektów i ich własności | `portfolio/projects.json` | Jeden właściciel, jawna widoczność i SHA |
| Artykuły i identyfikatory | `portfolio/papers.json` | Jedna własność `local`/`external`, bez fałszywych DOI i statusów |
| Lokalne manuskrypty | `manuscript_root/.../MSC-*/main.tex` | Kanoniczny commit ARC, nie kopia zewnętrznego źródła |
| Zależności sprzętowe i oprogramowanie | `portfolio/dependencies.json` | Wyłącznie referencje, bez kopiowania prywatnych źródeł |
| Odtwarzanie | `snapshot_sha` i gitlink | Historyczny stan zachowany |
| Odczyt na żywo | `remote_head_sha` / `audit-live` | Nie modyfikuje checkoutu; brak dostępu = `UNAVAILABLE` |
| Publikacja | `pages/projects.md` | Tylko rekordy publiczne, po zatwierdzeniu |

**Granica poufności:** w publicznym repozytorium nie wolno commitować metadanych identyfikujących prywatny projekt, nawet przy `public_listing: false`. Generator katalogu nie może czytać prywatnych repozytoriów ani zapisywać surowych danych do Pages. Przy każdym nowym przepływie zewnętrznym udokumentuj źródło, uprawnienia, cel, walidację, retencję, rezultat i status dowodu.

Powiązania: [SECURITY](../../SECURITY.md), [model zagrożeń](../security/threat-model.md), [ADR granic publikacji](../adr/0002-publication-boundaries.md).
