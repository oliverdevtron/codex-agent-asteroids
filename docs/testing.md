# Teststrategie & Qualitätssicherung

## Automatisierte Tests

- `pytest`: Führt Unit- und Integrationstests aus (`tests/`).
- Fixtures setzen `SDL_VIDEODRIVER=dummy`, damit pygame ohne Display läuft.
- Abgedeckte Aspekte:
  - Laden & Struktur der Konfiguration
  - Score- und Extra-Leben-Logik (`GameWorld._add_score`)
  - Asteroiden-Splitting und Saucer-Spawn-Verhalten
  - Hyperspace-Risiko (Fail-Case reduziert Leben)

## Manuelles Playtesting

1. Spiel starten (`python -m asteroids.main`).
2. Steuerung prüfen (Rotation, Thrust, Fire, Hyperspace, Pause, Quit).
3. Wellenfortschritt validieren (Asteroiden-Splits, Score-Anzeige, Extra-Leben bei 10.000 Punkten).
4. Saucer-Spawn beobachten (Frequenz, Zielgenauigkeit nimmt mit Wave zu).

## Coding Guidelines

- Keine Seiteneffekte im Rendering: `GameWorld` bleibt rein logisch.
- Konfiguration wird einmalig beim Start geladen; Änderungen erfordern Neustart (Hot-Reload ist Roadmap).
- Tests sollen deterministisch sein – bei Zufall immer Seeds setzen oder RNG mocken.

## CI-Empfehlung

- Pipeline-Schritte: `pip install -e .` → `pytest` → optional `flake8`/`black`.
- Für visuelle Regressionen kann später ein automatisierter Screenshot mit Vergleich hinzugefügt werden.
