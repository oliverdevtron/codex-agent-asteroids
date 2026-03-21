# Architekturüberblick

Dieses Dokument fasst die wichtigsten technischen Bausteine des Projekts zusammen.

## High-Level Komponenten

```
AsteroidsGame (game.py)
 ├── GameWorld (world.py)
 │    ├── Ship, Asteroid, Saucer, Bullet (entities.py)
 │    ├── ParticleSystem (particles.py)
 │    ├── Hilfsfunktionen (utils.py)
 │    └── Config-Datenklassen (config.py)
 ├── InputHandler (input.py)
 ├── Renderer (render.py)
 └── HighscoreManager (highscore.py)
```

- **AsteroidsGame**: Verwaltet Zustandsautomaten (Titel, Playing, Pause, Game Over, Highscore Entry), orchestriert Input → Simulation → Rendering.
- **GameWorld**: Enthält die komplette Spielsimulation (Bewegung, Kollisionslogik, Scoring, Wellenverwaltung, Saucer-Spawn, Partikeleffekte, Bildschirmshake, Score-Popups).
- **Entities**: Definieren das Verhalten einzelner Spielobjekte. Sie sind zustandslos gegenüber dem Rendering, was Tests erleichtert. Asteroiden speichern Polygonvertices für individuelle Formen.
- **Renderer**: Zeichnet die aktuelle Welt über pygame und kümmert sich um HUD, Titel, Game Over & Pause Overlays. Unterstützt Parallax-Starfield, Polygon-Asteroiden, Schubflammen, Bullet-Glow, Partikel und Score-Popups.
- **InputHandler**: Übersetzt Tastaturevents auf abstrakte Aktionen (`ControlState`), inklusive Debounce für Hyperspace und Toggle-Events (Pause, Start, Quit).
- **Config**: Lädt `config.yaml` in klar typisierte Dataclasses. Ranges sind als Hilfsklasse gekapselt und bieten Komfortmethoden (z. B. `random`). Neue Sektionen: `particles`, `effects`, `highscore`.
- **ParticleSystem** (`particles.py`): Verwaltete Pool von Partikeln für Explosionen und Schubeffekte. Unterstützt verschiedene Farben für Asteroiden (grau), Schiff (orange), Untertassen (rot) und Schub (orange/gelb).
- **HighscoreManager** (`highscore.py`): Lokale Highscore-Persistenz in JSON. Top-10-Einträge mit 3-Buchstaben-Namenentry (Arcade-Stil).

## Update Loop

1. `pygame.event.get()` → `InputHandler.process_events()` erstellt ein `FrameActions` Objekt.
2. Abhängig vom Game-State wendet `AsteroidsGame` die Aktionen an (z. B. `GameWorld.update`).
3. `GameWorld.update` führt mehrere Schritte aus:
   - Partikel- und Effekt-Updates (Shake, Popups, Wave-Announcements)
   - Ship-Steuerung (Rotation, Thrust mit Partikelemission, Fire, Hyperspace)
   - Bewegungsintegration aller Entities (inkl. Wrap-Around)
   - Spawn-Management für Asteroiden-Wellen und Saucers
   - Kollisions-Detection (inkl. Saucer-Bullets → Asteroiden) mit sofortigem Clean-up
   - Score/Award-Logik (Extra-Leben, Score-Popups)
4. `Renderer.draw` zeichnet die aktuelle Szene und das HUD, inklusive Starfield, Partikel und Shake-Offset.

## Testbarkeit

- `GameWorld` benötigt kein Display und kann isoliert instanziiert werden.
- Pytest setzt `SDL_VIDEODRIVER=dummy`, damit pygame in CI/headless läuft.
- `InputHandler` trennt Polling (pygame) und Zustandsrepräsentation, sodass Logik ohne echte Events getestet werden kann.
- `ParticleSystem` und `HighscoreManager` sind unabhängig testbar.

## Erweiterbarkeit

- Neue Gegner (z. B. Kometschwärme) können als Entities implementiert und in `GameWorld` integriert werden.
- Konfigurationswerte lassen sich ohne Code-Anpassung verändern oder per `--config` überschreiben.
- Rendering kann problemlos durch z. B. OpenGL oder eine andere Bibliothek ersetzt werden, da die Spielwelt keine pygame-spezifischen Abhängigkeiten hält.
