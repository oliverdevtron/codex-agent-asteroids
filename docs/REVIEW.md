# Code Review – Asteroids Clone v0.2.0

**Reviewer:** Astra (AI Code Review)  
**Datum:** 2026-03-21  
**Branch:** `feature/review-and-enhancements`

---

## Gesamtbewertung

Die Codebasis ist **solide strukturiert** und zeigt eine gute Trennung der Verantwortlichkeiten (MVC-artiges Pattern). Die Architektur ist sauber, gut dokumentiert und erweiterbar. Version 0.2.0 bietet eine spielbare Grundlage, die einige Verbesserungen in Codequalität, Performance und visueller Darstellung vertragen kann.

**Gesamtnote: 7/10** — Solide Basis mit klarem Verbesserungspotenzial.

---

## Positives

### Architektur
- **Saubere Schichtentrennung**: `GameWorld` ist komplett unabhängig von pygame-Rendering, was Unit-Tests erheblich vereinfacht.
- **Konfigurierbar über YAML**: Alle Gameplay-Parameter sind externalisiert. Balancing-Änderungen erfordern keinen Code-Eingriff.
- **Typisierte Dataclasses**: `Config`, `Range` etc. sind sauber typisiert mit `slots=True` für Speichereffizienz.
- **Graceful Fallback**: Fehlt PyYAML oder `config.yaml`, greift das System auf eingebettete Defaults zurück.

### Code-Qualität
- Konsistente Docstrings in allen Modulen.
- `__all__`-Exports in jedem Modul definiert.
- Headless-Test-Setup über `SDL_VIDEODRIVER=dummy`.
- RNG-Seed-Option für reproduzierbare Testläufe.

---

## Befunde (nach Schweregrad)

### Kritisch

| # | Datei | Zeile | Befund |
|---|-------|-------|--------|
| C1 | `entities.py` | 71 | **Frame-Rate-abhängiges Damping**: `self.velocity *= 0.999` wird pro Frame angewendet, nicht delta-time-normalisiert. Bei 60 FPS ergibt sich ein anderes Damping als bei 120 FPS. Fix: `self.velocity *= (0.999 ** (dt * 60))` oder `pow(damping_factor, dt)`. |
| C2 | `world.py` | 292 | **Floating-Point-Vergleich**: `if self.wave_clear_timer == 0.0` ist fragil. Bei Gleitkomma-Arithmetik kann der Timer nie exakt 0.0 sein. Fix: Sentinel-Wert oder Flag verwenden. |

### Wichtig

| # | Datei | Zeile | Befund |
|---|-------|-------|--------|
| W1 | `world.py` | 205-251 | **O(n²) Kollisionserkennung**: Jedes Bullet wird gegen jeden Asteroid geprüft. Bei vielen Entities (hohe Waves) wird dies zum Performance-Bottleneck. Spatial Hashing oder Quadtree wäre angebracht. |
| W2 | `world.py` | 249-251 | **List Rebuilds pro Frame**: `self.asteroids = [a for a if a.alive]` erstellt jedes Frame eine neue Liste. Besser: In-place-Filterung oder dirty-Flag. |
| W3 | `entities.py` | 152-153 | **Globaler `random`-Aufruf in Asteroid.__init__**: Verwendet `random.uniform` statt dem kontrollierten `rng`-Objekt aus `GameWorld`. Bricht die Reproduzierbarkeit bei gesetztem Seed. |
| W4 | `render.py` | 93-100 | **Asteroiden als einfache Kreise**: Visuell monoton und nicht repräsentativ für das Original-Spiel. Zufällig generierte Polygone wären authentischer. |
| W5 | `render.py` | 28-29 | **System-Font-Abhängigkeit**: `SysFont("Consolas")` ist plattformabhängig. Auf Linux/macOS existiert Consolas typischerweise nicht. Besserer Ansatz: mitgelieferter Font oder Fallback-Kette. |
| W6 | `input.py` | 61-66 | **Key-Collision ohne Warnung**: Wenn zwei Actions denselben Key binden, überschreibt der letzte. Keine Warnung an den User. |

### Verbesserungen

| # | Datei | Befund |
|---|-------|--------|
| V1 | `render.py` | Kein Partikel-/Explosionssystem. Entities verschwinden abrupt. |
| V2 | `render.py` | Kein Sternenhintergrund — nur schwarzer Screen. |
| V3 | `render.py` | Keine Schubflamme beim Beschleunigen des Schiffs. |
| V4 | Allgemein | Kein Highscore-System oder Persistenz. |
| V5 | `render.py` | Keine visuellen Effekte (Glow, Screen-Shake, Nachleuchten). |
| V6 | `game.py` | Keine Wave-Ankündigung oder Übergangsanimation. |
| V7 | Tests | Nur 4 Tests — grundlegende Szenarien abgedeckt, aber keine Edge-Cases, kein Collision-Boundary-Test, kein Config-Validation-Test. |
| V8 | `world.py` | Saucer-Bullets haben keine Kollision mit Asteroiden (anders als im Original-Asteroids). |

### Stil/Nit-Picks

| # | Datei | Befund |
|---|-------|--------|
| S1 | `config.py` | Doppelte Scoring-Daten: `asteroids.sizes[].score` und `scoring.*` definieren dieselben Werte. Potenzielle Inkonsistenz. |
| S2 | `README.md` vs `readme.md` | Zwei README-Dateien mit unterschiedlichen Namen. `readme.md` sollte entfernt werden. |
| S3 | `entities.py` L102 | Magic Number `6` beim Bullet-Spawn-Offset. Sollte konfigurierbar oder benannt sein. |
| S4 | `entities.py` L224-226 | Saucer-Bullets haben hardcodierte Werte (radius=3, lifetime=1.4) statt Config-Werte. |

---

## Empfohlene Maßnahmen

1. **Damping frame-rate-unabhängig machen** (C1)
2. **Floating-Point-Vergleich fixen** (C2)
3. **Asteroiden-RNG auf World.rng umstellen** (W3)
4. **Visuelles Upgrade**: Partikel, Sterne, Polygon-Asteroiden, Schubflamme (V1-V3)
5. **Highscore-System** implementieren (V4)
6. **Testabdeckung** erheblich erweitern (V7)
7. **Saucer-Bullet vs. Asteroid Collision** hinzufügen (V8)

---

*Review abgeschlossen am 2026-03-21.*
