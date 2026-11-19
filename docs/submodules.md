# Submoduły, historia i aktualność

Domyślnie program ARC wskazuje projekty przez rejestr/link. Gdy potrzebne wspólne pobranie, można dodać submoduł poleceniem:

```bash
git submodule add https://github.com/OWNER/msc-project.git projects/msc-project
git commit -m "Add project submodule"
python scripts/bootstrap.py --mode reproduce
```

W pliku `portfolio/projects.json` ustaw `submodule_path` i **dokładny** `snapshot_sha` zgodny z `gitlink`. Skrypt `bootstrap.py` odtwarza przypięte SHA z historią repo nadrzędnego. Nie używaj `submodule update --remote` w produkcyjnym katalogu eksperymentu.

Do bieżących ocen użyj `python scripts/bootstrap.py --mode audit-live`: skrypt porównuje `git ls-remote` z `snapshot_sha`, niczego nie checkoutuje i raportuje `STALE`/`CURRENT`/`UNAVAILABLE`. Wymaga własnego uprzednio skonfigurowanego bezpiecznego uwierzytelnienia; nie wpisuj tokenów do adresów URL.

Git subtree przechowuje kopię historii/kodu i nie synchronizuje się sam. Nie stosować do ciągle aktualizowanych podprojektów. Dostęp do prywatnych repo zapewnia osobno zaakceptowana tożsamość GitHub App/credential helper. Brak uprawnień nie oznacza, że repozytorium jest aktualne.
