"""Input handling for keyboard controls."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable

import pygame

from .config import ControlsConfig
from .world import ControlState


@dataclass(slots=True)
class FrameActions:
    controls: ControlState
    pause: bool = False
    start: bool = False
    quit: bool = False


_SPECIAL_KEYS: Dict[str, int] = {
    "lcontrol": pygame.K_LCTRL,
    "rcontrol": pygame.K_RCTRL,
    "lctrl": pygame.K_LCTRL,
    "rctrl": pygame.K_RCTRL,
    "lshift": pygame.K_LSHIFT,
    "rshift": pygame.K_RSHIFT,
    "lalt": pygame.K_LALT,
    "ralt": pygame.K_RALT,
}


def _resolve_key(name: str) -> int:
    normalized = name.strip().lower()
    if normalized in _SPECIAL_KEYS:
        return _SPECIAL_KEYS[normalized]
    try:
        return pygame.key.key_code(normalized)
    except ValueError:
        attr = f"K_{normalized.upper()}"
        if hasattr(pygame, attr):
            return getattr(pygame, attr)
        raise KeyError(f"Unknown key name: {name}")


class InputHandler:
    def __init__(self, controls: ControlsConfig) -> None:
        self.controls = controls
        self.held_state: Dict[str, bool] = {
            "rotate_left": False,
            "rotate_right": False,
            "thrust": False,
            "fire": False,
        }
        self.hyperspace_pending = False
        self.pause_pending = False
        self.start_pending = False
        self.quit_pending = False
        self.key_bindings = self._build_keymap(controls)

    def _build_keymap(self, controls: ControlsConfig) -> Dict[int, str]:
        mapping: Dict[int, str] = {}
        for action, keys in controls.all_bindings.items():
            for key in keys:
                mapping[_resolve_key(key)] = action
        return mapping

    def process_events(self, events: Iterable[pygame.event.Event]) -> FrameActions:
        for event in events:
            if event.type == pygame.QUIT:
                self.quit_pending = True
                continue
            if event.type not in (pygame.KEYDOWN, pygame.KEYUP):
                continue
            key = event.key
            if key not in self.key_bindings:
                continue
            action = self.key_bindings[key]
            is_down = event.type == pygame.KEYDOWN
            if action in self.held_state:
                self.held_state[action] = is_down
            elif action == "hyperspace" and is_down:
                self.hyperspace_pending = True
            elif action == "pause" and is_down:
                self.pause_pending = True
            elif action == "start" and is_down:
                self.start_pending = True
            elif action == "quit" and is_down:
                self.quit_pending = True

        controls = ControlState(
            rotate_left=self.held_state["rotate_left"],
            rotate_right=self.held_state["rotate_right"],
            thrust=self.held_state["thrust"],
            fire=self.held_state["fire"],
            hyperspace=self.hyperspace_pending,
        )
        frame = FrameActions(
            controls=controls,
            pause=self.pause_pending,
            start=self.start_pending,
            quit=self.quit_pending,
        )
        self.hyperspace_pending = False
        self.pause_pending = False
        self.start_pending = False
        self.quit_pending = False
        return frame


__all__ = ["InputHandler", "FrameActions"]
