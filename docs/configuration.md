# Konfiguration (`config.yaml`)

Alle spielrelevanten Parameter befinden sich in `config.yaml`. Beim Start kann eine alternative Datei via `python -m asteroids.main --config pfad/zur/config.yaml` geladen werden.

## game

| Schlüssel | Beschreibung |
|-----------|--------------|
| `fps` | Ziel-Bildwiederholrate. Wird von `pygame.time.Clock.tick()` verwendet. |
| `window.width/height` | Fensterauflösung. |
| `extra_life_every` | Punkteschwelle für zusätzliche Leben. |
| `starting_lives` | Anzahl der Leben beim Start (inkl. aktuellem Schiff). |
| `rng_seed` | Optionaler Seed für deterministisches Verhalten (Asteroiden-Spawn, Saucer, Hyperspace etc.). |

## controls

Listen von Key-Namen (siehe `pygame.key.key_code`). Für Modifier existieren Aliasse: `LCONTROL`, `LSHIFT`, `LALT`, `RCONTROL`, `RSHIFT`, `RALT`.

## ship

- `radius`: Größe des Hitbox-Kreises (Pixel).
- `turn_rate_deg_per_s`: Drehgeschwindigkeit in Grad/Sek.
- `thrust_px_per_s2`: Beschleunigung beim Thrust.
- `max_speed_px_per_s`: obere Geschwindigkeitsgrenze.
- `respawn_invuln_s`: Dauer der Unverwundbarkeit nach Spawn.
- `hyperspace_cooldown_s`: Minimalabstand zwischen zwei Sprüngen.
- `hyperspace_fail_chance`: Ausfallwahrscheinlichkeit (0.08 = 8 %).
- `wrap_margin_px`: Sicherheitsmarge fürs Screen-Wrapping.

## bullet

- `speed_px_per_s`: Mündungsgeschwindigkeit.
- `lifetime_s`: Lebensdauer vor Autodespawn.
- `fire_rate_per_s`: Schüsse pro Sekunde.
- `pool_size`: Maximal gleichzeitig aktive Spieler-Schüsse.
- `radius`: Kollisionsradius.

## asteroids

### sizes

Jeder Eintrag beschreibt eine Asteroiden-Größe. `speed_px_per_s` ist ein `[min, max]`-Array und wird pro Spawn zufällig gewählt; `fragments` bestimmt die Anzahl der Splitter beim Zerstören.

### spawn

- `base_count`: Anzahl großer Asteroiden in Welle 1.
- `count_growth`: Zuwachs pro Welle.
- `speed_scale_per_wave`: Multiplikator pro Welle (z. B. 0.06 = +6 % Geschwindigkeit).
- `safe_spawn_radius_px`: Mindestabstand zwischen Spawnpunkt und Schiff (nur beim Initial-Spawn).

## saucer

Globale Einstellungen plus Substrukturen für `large` und `small`.

- `max_active`: Anzahl gleichzeitig aktiver UFOs.
- `spawn_delay_s`: `[min, max]` Sekunden bis zur ersten Spawnprüfung in einer Welle.
- `spawn_interval_s`: `[min, max]` Sekunden zwischen Spawns.
- `small_chance_by_wave`: Wahrscheinlichkeit für das kleine UFO je Welle (Index = Wave - 1, letzte Zahl = Obergrenze).
- `prefer_small_if_score_ge`: Ab diesem Score wird mind. 70 % Wahrscheinlichkeit für das kleine UFO erzwungen.

### Saucer-Typen

| Schlüssel | Bedeutung |
|-----------|-----------|
| `radius` | Hitbox-Radius |
| `speed_px_per_s` | horizontale Reisegeschwindigkeit |
| `fire_cooldown_s` | `[min, max]` Sekunden zwischen Schüssen |
| `bullet_speed_px_per_s` | Geschwindigkeit der UFO-Schüsse |
| `aim_error_deg_sigma` | Gaußsche Streuung (Sigma in Grad) |
| `min_error_floor_deg` | Untergrenze der Streuung (nur beim kleinen UFO) |
| `lifetime_s` | `[min, max]` Bildschirmverweildauer |
| `score` | Punktewert |

## scoring

Zuordnung zwischen Ereignis und Punkten. Die Werte spiegeln 1:1 die Tabellen aus der Spezifikation wider.

## ui

- `show_fps`: Blendet FPS oben rechts ein.
- `hud_margin_px`: Abstand von Score/Leben/Wave zum Rand.
