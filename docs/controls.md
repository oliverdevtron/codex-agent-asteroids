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

Wenn ein neuer Highscore erreicht wird, erscheint ein Namenseingabe-Bildschirm:

| Aktion | Tasten |
|--------|--------|
| Buchstabe eingeben | `A`-`Z` |
| Buchstabe löschen | `BACKSPACE` |
| Name bestätigen | `RETURN` |
| Abbrechen | `ESCAPE` |

Der Name besteht aus maximal 3 Buchstaben (Arcade-Stil).

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
