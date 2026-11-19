# Portal GitHub Pages

Używaj wspólnego szablonu MkDocs, ale tylko jawnie zatwierdzonych treści. `python scripts/build_public_catalog.py` generuje `docs/projects.md` z publicznych rekordów; rekord prywatny zawsze zostaje pominięty, nawet jeśli przez pomyłkę włączono `public_listing=true`. Zweryfikuj ręcznie wszelkie inne pliki w `docs/` i ich źródła przed publicznym deploymentem. Automatyczne workflowy Pages nie są częścią szkieletu; uruchomienie wymaga zatwierdzonej konfiguracji GitHub i kontroli kosztów.
