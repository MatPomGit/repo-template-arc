# ADR-0002: granice publicznego katalogu i GitHub Pages

**Status:** proposed  
**Data:** 2026-11-20  
**Kategoria:** security, privacy, architecture

## Kontekst

ARC może indeksować informacje z prywatnych projektów. Publikowanie bezpośrednio `docs/` lub repozytorium może ujawnić nazwy niepublicznych projektów, historię, SHA, instrukcje agentowe i inne nieprzeznaczone do upublicznienia informacje.

## Propozycja

Dokumentacja repozytorium pozostaje w `docs/`, a **wyłącznie** zatwierdzona projekcja publiczna w `pages/`. Każdy zasób publiczny jest na liście `config/pages-policy.json`. Generator katalogu czyta tylko dozwolone, jawne rekordy, nie wykonuje `audit-live` i nie pobiera prywatnych zasobów. Publikacja jest osobną czynnością, poprzedzoną przeglądem renderowanych materiałów i kontroli widoczności witryny.

## Alternatywy

Publikacja `docs/` w trybie `Deploy from a branch` jest łatwiejsza, lecz narusza granice bezpieczeństwa i nie zapewnia jawnego dopuszczenia plików. Pełny eksport portfolio ujawnia rejestry. Publiczny i prywatny rejestr powinny być rozdzielone w źródłach już na etapie zapisu.

## Konsekwencje

Potrzebny jest audyt źródła Pages, allowlisty, wygenerowanego HTML i wszystkich zasobów, a dla repo prywatnego dodatkowo kontrola rzeczywistej widoczności strony. Dokument nie stanowi zatwierdzonego wdrożenia. Szczegóły: [polityka Pages](../pages.md) i [model zagrożeń](../security/threat-model.md).
