"""High level game loop management."""
from __future__ import annotations

from datetime import date
from enum import Enum
from pathlib import Path
from typing import List, Optional

import pygame

from .config import Config, load_config
from .highscore import HighscoreEntry, HighscoreManager
from .input import FrameActions, InputHandler
from .render import Renderer
from .world import GameWorld


class GameMode(str, Enum):
    TITLE = "title"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    HIGHSCORE_ENTRY = "highscore_entry"


class AsteroidsGame:
    def __init__(self, config: Optional[Config] = None) -> None:
        self.config = config or load_config()
        pygame.init()
        window_cfg = self.config.game.window
        self.screen = pygame.display.set_mode((window_cfg.width, window_cfg.height))
        pygame.display.set_caption("Asteroids")
        self.clock = pygame.time.Clock()
        self.world = GameWorld(self.config)
        self.renderer = Renderer(self.screen, self.config)
        self.input_handler = InputHandler(self.config.controls)
        self.mode = GameMode.TITLE
        self.running = True

        # Highscore system
        hs_cfg = self.config.highscore
        hs_path = Path(hs_cfg.file_path) if hs_cfg.file_path else None
        self.highscore_manager = HighscoreManager(
            max_entries=hs_cfg.max_entries,
            name_length=hs_cfg.name_length,
            file_path=hs_path,
        )

        # Name entry state
        self._name_chars: List[str] = ["A", "A", "A"]
        self._name_cursor: int = 0

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(self.config.game.fps) / 1000.0
            events = pygame.event.get()
            actions = self.input_handler.process_events(events)
            self._dispatch(actions, dt, events)
            fps = self.clock.get_fps()
            self._render(fps)
        pygame.quit()

    def _render(self, fps: float) -> None:
        if self.mode == GameMode.TITLE:
            self.renderer.draw(self.world, self.mode.value, fps=fps)
            self.renderer.draw_highscore_table(self.highscore_manager.entries)
            pygame.display.flip()
        elif self.mode == GameMode.HIGHSCORE_ENTRY:
            self.renderer.draw(self.world, self.mode.value, fps=fps)
            self.renderer.draw_highscore_entry(self.world, self._name_chars, self._name_cursor)
            pygame.display.flip()
        else:
            self.renderer.draw(self.world, self.mode.value, fps=fps)

    def _dispatch(self, actions: FrameActions, dt: float, events) -> None:
        if actions.quit:
            if self.mode in (GameMode.PLAYING, GameMode.PAUSED, GameMode.GAME_OVER, GameMode.HIGHSCORE_ENTRY):
                self.mode = GameMode.TITLE
                self.world.reset()
            else:
                self.running = False
            return

        if self.mode == GameMode.TITLE:
            self._handle_title(actions)
        elif self.mode == GameMode.PLAYING:
            self._handle_playing(actions, dt)
        elif self.mode == GameMode.PAUSED:
            self._handle_paused(actions)
        elif self.mode == GameMode.GAME_OVER:
            self._handle_game_over(actions)
        elif self.mode == GameMode.HIGHSCORE_ENTRY:
            self._handle_highscore_entry(events)

    def _handle_title(self, actions: FrameActions) -> None:
        if actions.start:
            self.world.reset()
            self.mode = GameMode.PLAYING

    def _handle_playing(self, actions: FrameActions, dt: float) -> None:
        if actions.pause:
            self.mode = GameMode.PAUSED
            return
        # Pass thrust state to renderer for flame drawing
        self.renderer._draw_ship_thrusting = actions.controls.thrust
        self.world.update(dt, actions.controls)
        if self.world.game_over:
            if self.highscore_manager.qualifies(self.world.score):
                self._name_chars = ["A", "A", "A"]
                self._name_cursor = 0
                self.mode = GameMode.HIGHSCORE_ENTRY
            else:
                self.mode = GameMode.GAME_OVER

    def _handle_paused(self, actions: FrameActions) -> None:
        if actions.pause or actions.start:
            self.mode = GameMode.PLAYING

    def _handle_game_over(self, actions: FrameActions) -> None:
        if actions.start:
            self.world.reset()
            self.mode = GameMode.PLAYING
        elif actions.pause:
            self.mode = GameMode.TITLE

    def _handle_highscore_entry(self, events) -> None:
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue
            if event.key == pygame.K_UP:
                # Cycle character up
                ch = self._name_chars[self._name_cursor]
                if ch == "Z":
                    self._name_chars[self._name_cursor] = "A"
                else:
                    self._name_chars[self._name_cursor] = chr(ord(ch) + 1)
            elif event.key == pygame.K_DOWN:
                ch = self._name_chars[self._name_cursor]
                if ch == "A":
                    self._name_chars[self._name_cursor] = "Z"
                else:
                    self._name_chars[self._name_cursor] = chr(ord(ch) - 1)
            elif event.key == pygame.K_LEFT:
                self._name_cursor = max(0, self._name_cursor - 1)
            elif event.key == pygame.K_RIGHT:
                self._name_cursor = min(len(self._name_chars) - 1, self._name_cursor + 1)
            elif event.key == pygame.K_RETURN:
                name = "".join(self._name_chars)
                entry = HighscoreEntry(
                    name=name,
                    score=self.world.score,
                    wave=self.world.wave,
                    date=date.today().isoformat(),
                )
                self.highscore_manager.add(entry)
                self.mode = GameMode.GAME_OVER


def run(config_path: Optional[Path] = None) -> None:
    config = load_config(config_path) if config_path is not None else load_config()
    game = AsteroidsGame(config)
    game.run()


__all__ = ["AsteroidsGame", "GameMode", "run"]
