# Bezpieczeństwo i uprawnienia

Rejestry mogą zawierać odnośniki do prywatnych repozytoriów. Nie ujawniaj ich w GitHub Pages bez jawnego `public_listing=true` i osobnego przeglądu. Nie zapisuj tokenów, kluczy i surowych danych uczestników w Git, logach, plikach `.gitmodules` ani GitHub Pages. Dostęp do prywatnych submodułów zapewnia zatwierdzona integracja z kontrolą uprawnień; brak dostępu blokuje pełny audit-live. Nie uruchamiaj kodu obcego PR na stałych runnerach.
