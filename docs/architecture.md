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
- **GameWorld**: Enthält die komplette Spielsimulation (Bewegung, Kollisionslogik, Scoring, Wellenverwaltung, Saucer-Spawn, Partikel, Screen-Shake, Score-Popups, Wave-Announcements).
- **Entities**: Definieren das Verhalten einzelner Spielobjekte. Asteroiden besitzen zufällig generierte Polygon-Vertices für authentisches Rendering.
- **ParticleSystem**: Verwaltet einen Pool von Partikeln für Explosions- und Schubeffekte. Verschiedene Farben je Entity-Typ (Asteroid: grau, Schiff: orange, Saucer: rot).
- **Renderer**: Zeichnet die aktuelle Welt über pygame und kümmert sich um HUD, Titel, Game Over & Pause Overlays, Parallax-Sternenhintergrund, Polygon-Asteroiden, Schubflamme, Bullet-Glow, verbessertes Saucer-Design, Screen-Shake, Wave-Announcements und Score-Popups.
- **InputHandler**: Übersetzt Tastaturevents auf abstrakte Aktionen (`ControlState`), inklusive Debounce für Hyperspace und Toggle-Events (Pause, Start, Quit).
- **HighscoreManager**: Verwaltet eine Top-10 lokale Highscore-Tabelle mit JSON-Persistenz. Arcade-Style 3-Buchstaben Namenseingabe.
- **Config**: Lädt `config.yaml` in klar typisierte Dataclasses. Ranges sind als Hilfsklasse gekapselt und bieten Komfortmethoden (z. B. `random`). Neue Sektionen: `particles`, `effects`, `highscore`.

## Update Loop

1. `pygame.event.get()` → `InputHandler.process_events()` erstellt ein `FrameActions` Objekt.
2. Abhängig vom Game-State wendet `AsteroidsGame` die Aktionen an (z. B. `GameWorld.update`).
3. `GameWorld.update` führt mehrere Schritte aus:
   - Ship-Steuerung (Rotation, Thrust, Fire, Hyperspace)
   - Bewegungsintegration aller Entities (inkl. Wrap-Around)
   - Spawn-Management für Asteroiden-Wellen und Saucers
   - Kollisions-Detection mit sofortigem Clean-up (inkl. Saucer-Bullet vs. Asteroid)
   - Score/Award-Logik (Extra-Leben, Score-Popups)
   - Partikel-Emissionen bei Explosionen und Schub
   - Screen-Shake bei Zerstörungen
   - Wave-Announcement-Timer
4. `Renderer.draw` zeichnet die aktuelle Szene und das HUD.

## Testbarkeit

- `GameWorld` benötigt kein Display und kann isoliert instanziiert werden.
- Pytest setzt `SDL_VIDEODRIVER=dummy`, damit pygame in CI/headless läuft.
- `InputHandler` trennt Polling (pygame) und Zustandsrepräsentation, sodass Logik ohne echte Events getestet werden kann.
- `ParticleSystem` und `HighscoreManager` sind vollständig unabhängig von pygame testbar.

## Erweiterbarkeit

- Neue Gegner (z. B. Kometschwärme) können als Entities implementiert und in `GameWorld` integriert werden.
- Konfigurationswerte lassen sich ohne Code-Anpassung verändern oder per `--config` überschreiben.
- Rendering kann problemlos durch z. B. OpenGL oder eine andere Bibliothek ersetzt werden, da die Spielwelt keine pygame-spezifischen Abhängigkeiten hält.
