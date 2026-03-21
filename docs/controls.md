# Steuerung & Input Mapping

Standard-Keymap (siehe auch Spezifikation):

| Aktion | Tasten |
|--------|--------|
| Rotate Left | `LEFT`, `A` |
| Rotate Right | `RIGHT`, `D` |
| Thrust | `UP`, `W` |
| Fire | `SPACE`, `LCONTROL` |
| Hyperspace | `LSHIFT` |
| Pause | `P` |
| Start | `RETURN` |
| Quit / Back to Title | `ESCAPE` |

## Highscore Name Entry

Bei Erreichen eines Top-10-Scores wird der Namenseingabe-Bildschirm angezeigt:

| Aktion | Taste |
|--------|-------|
| Buchstabe hoch | `UP` |
| Buchstabe runter | `DOWN` |
| Cursor links | `LEFT` |
| Cursor rechts | `RIGHT` |
| Name bestätigen | `RETURN` |
| Abbrechen | `ESCAPE` |

## Remapping

- Die Tastenlisten in `config.yaml` können beliebig erweitert werden.
- Unterstützte Namen orientieren sich an `pygame.key.key_code`. Für Modifier existieren zusätzliche Aliasse (`LCONTROL`, `RCONTROL`, `LSHIFT`, `RSHIFT`, `LALT`, `RALT`).
- Doppelte Belegungen sind erlaubt – beim ersten Match in `InputHandler` gewinnt die zuletzt eingetragene Taste.

## Gamepad (zukünftig)

Das Projekt ist auf Keyboard ausgelegt. Die Architektur erlaubt aber problemlos einen zusätzlichen `GamepadInputHandler`, der `FrameActions` erzeugt. Vorschläge:

- Linker Stick X → Rotation
- RT → Thrust
- A / Cross → Fire
- B / Circle → Hyperspace
- Start → Pause

Dieser Teil ist als Roadmap-Punkt markiert und wird in späteren Iterationen ergänzt.
