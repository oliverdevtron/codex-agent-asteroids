# Asteroids (Python) – Minimal Playable Clone

Diese Codebasis implementiert einen spielbaren **Asteroids**-Klon in Python 3.10+ auf Basis von [pygame](https://www.pygame.org/). Ziel ist eine moderne, gut konfigurierbare Referenzimplementierung, die den klassischen Arcade-Flow (Wellen, Saucers, Punktevergabe, Extra-Leben) respektiert und sich für weitere Iterationen eignet.

## Projektüberblick

- **Sprache:** Python ≥ 3.10
- **Framework:** pygame 2.5+
- **Konfiguration:** YAML (`config.yaml`)
- **Build & Tests:** `pytest`
- **Lizenz:** MIT

Die Runtime trennt klar zwischen Spielwelt-Logik (`GameWorld`), Eingaben (`InputHandler`), Rendering (`Renderer`) und dem High-Level Game-Loop (`AsteroidsGame`). Dadurch lassen sich Komponenten isoliert testen und erweitern.

## Installation & Setup

1. Abhängigkeiten installieren (empfohlen in einem virtuellen Environment):
   ```bash
   pip install -e .
   ```
   *Hinweis:* Ist `PyYAML` nicht verfügbar, verwendet die Engine automatisch die eingebauten Defaults. Für eigene `config.yaml`-Anpassungen sollte das Paket nachinstalliert werden.
2. Optional: eigenes Config-File erstellen und beim Start übergeben (`--config`).

## Spiel starten

```bash
python -m asteroids.main
```

- **ENTER** startet das Spiel aus dem Titelbildschirm.
- **ESC** bricht eine Runde ab oder beendet die Anwendung aus dem Titelbildschirm.
- **P** pausiert / setzt fort.

Weitere Standard-Belegungen siehe [docs/controls.md](docs/controls.md). Alle Tasten lassen sich in `config.yaml` anpassen.

## Tests ausführen

```bash
pytest
```

Die Tests laufen headless; die SDL Video-Treiber werden automatisch auf `dummy` gesetzt. Abgedeckt werden u. a. Score-Logik, Saucer-Spawn und Hyperspace-Verhalten.

## Projektstruktur

```
├── config.yaml              # Standardkonfiguration
├── src/asteroids            # Python-Paket mit Spielcode
│   ├── config.py            # YAML-Lader & Dataklassen
│   ├── entities.py          # Ship, Asteroids, Saucer, Bullets
│   ├── game.py              # High-Level Game Loop & States
│   ├── input.py             # Keyboard-Mapping
│   ├── main.py              # CLI-Einstiegspunkt
│   ├── render.py            # Zeichnen via pygame
│   ├── utils.py             # Mathematische Helferlein
│   └── world.py             # Kernlogik & Kollisionshandling
├── tests                    # Pytest-Suite
└── docs                     # zusätzliche Dokumentation
```

## Dokumentation

- [docs/architecture.md](docs/architecture.md) beschreibt das technische Design.
- [docs/configuration.md](docs/configuration.md) erklärt alle Konfigurationswerte.
- [docs/controls.md](docs/controls.md) listet Steuerungen & Remapping.
- [docs/testing.md](docs/testing.md) fasst QA-Strategie & Checks zusammen.

## Roadmap / Ideen für Iteration 0.3+

- Gamepad-Unterstützung (SDL Controller Mapping)
- Soundeffekte & Musik
- Partikel-/Explosionssystem
- Online Highscore / lokale Scoreboards
- Hot-Reload für Konfigurationsdateien

Viel Spaß beim Zocken und Modden! 🎮
