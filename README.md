# Asteroids (Python) – Enhanced Clone

Diese Codebasis implementiert einen spielbaren **Asteroids**-Klon in Python 3.10+ auf Basis von [pygame](https://www.pygame.org/). Ziel ist eine moderne, gut konfigurierbare Referenzimplementierung, die den klassischen Arcade-Flow (Wellen, Saucers, Punktevergabe, Extra-Leben) respektiert und sich für weitere Iterationen eignet.

## Projektüberblick

- **Sprache:** Python ≥ 3.10
- **Framework:** pygame 2.5+
- **Konfiguration:** YAML (`config.yaml`)
- **Build & Tests:** `pytest`
- **Lizenz:** MIT

Die Runtime trennt klar zwischen Spielwelt-Logik (`GameWorld`), Eingaben (`InputHandler`), Rendering (`Renderer`), Partikeleffekten (`ParticleSystem`) und dem High-Level Game-Loop (`AsteroidsGame`). Dadurch lassen sich Komponenten isoliert testen und erweitern.

## Features

- **Polygon-Asteroiden**: Zufällig generierte, gezackte Polygonformen statt einfacher Kreise, mit Rotation
- **Partikel-/Explosionssystem**: Farbige Explosionen (grau für Asteroiden, orange für Schiff, rot für Saucer) und Schubflammen-Partikel
- **Parallax-Sternenhintergrund**: Drei Ebenen von Sternen mit unterschiedlicher Geschwindigkeit
- **Screen-Shake**: Bildschirmerschütterung bei Explosionen
- **Bullet-Glow**: Leuchteffekte um Geschosse
- **Verbessertes Saucer-Design**: Kuppel und blinkende Lichter
- **Score-Popups**: Aufsteigende Punktanzeigen bei Zerstörungen
- **Wave-Ankündigungen**: Ein-/Ausblendende Wellenanzeige
- **Lokales Highscore-System**: Top-10 Bestenliste mit 3-Buchstaben Namenseingabe (Arcade-Stil), JSON-Persistenz
- **Saucer-Bullet vs. Asteroid Kollision**: Wie im Originalspiel können Saucer-Geschosse Asteroiden zerstören

## Features

- Klassisches Asteroids-Gameplay mit Wellen, Saucers und Extra-Leben
- **Partikel-/Explosionssystem** mit unterschiedlichen Farben pro Entity-Typ
- **Parallax-Starfield** Hintergrund (3 Ebenen)
- **Polygon-Asteroiden** mit individuellen, zufälligen Formen und Rotation
- **Schubflammen-Animation** am Schiff beim Beschleunigen
- **Bullet-Glow-Effekte** für bessere Sichtbarkeit
- **Verbessertes Saucer-Design** mit Kuppel und blinkenden Lichtern
- **Bildschirmshake** bei Explosionen (konfigurierbar)
- **Wellenankündigungen** ("WAVE X" mit Ein-/Ausblendung)
- **Score-Popups** an der Zerstörungsstelle
- **Lokales Highscore-System** mit 3-Buchstaben-Namenentry (Arcade-Stil, JSON-Persistenz)
- **Saucer-Bullets zerstören Asteroiden** (wie im Original-Arcade-Spiel)
- Vollständig konfigurierbar über `config.yaml`

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

Die Tests laufen headless; die SDL Video-Treiber werden automatisch auf `dummy` gesetzt. Abgedeckt werden u. a. Score-Logik, Saucer-Spawn, Hyperspace-Verhalten, Partikelsystem, Highscores und Saucer-Bullet-Kollisionen.

## Projektstruktur

```
├── config.yaml              # Standardkonfiguration
├── src/asteroids            # Python-Paket mit Spielcode
│   ├── config.py            # YAML-Lader & Dataklassen
│   ├── entities.py          # Ship, Asteroids, Saucer, Bullets
│   ├── game.py              # High-Level Game Loop & States
│   ├── highscore.py         # Lokale Highscore-Persistenz
│   ├── input.py             # Keyboard-Mapping
│   ├── main.py              # CLI-Einstiegspunkt
│   ├── particles.py         # Partikel-/Explosionssystem
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
- [docs/REVIEW.md](docs/REVIEW.md) enthält die Code-Review-Ergebnisse.

## Roadmap / Ideen für Iteration 0.4+

- Gamepad-Unterstützung (SDL Controller Mapping)
- Soundeffekte & Musik
- Online Highscore-Tabelle
- Hot-Reload für Konfigurationsdateien
