"""High level game loop management."""
from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Optional

import pygame

from .config import Config, load_config
from .highscore import HighscoreManager
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
        hs_path = None
        if self.config.highscore.file_path:
            hs_path = Path(self.config.highscore.file_path)
        self.highscore_manager = HighscoreManager(
            max_entries=self.config.highscore.max_entries,
            file_path=hs_path,
        )
        self.entry_name = ""

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(self.config.game.fps) / 1000.0
            events = pygame.event.get()
            if self.mode == GameMode.HIGHSCORE_ENTRY:
                self._handle_highscore_events(events)
            else:
                actions = self.input_handler.process_events(events)
                self._dispatch(actions, dt)
            fps = self.clock.get_fps()
            self.renderer.draw(self.world, self.mode.value, fps=fps)
            # Overlay for highscore entry
            if self.mode == GameMode.HIGHSCORE_ENTRY:
                self.renderer.draw_name_entry(self.entry_name)
                pygame.display.flip()
        pygame.quit()

    def _dispatch(self, actions: FrameActions, dt: float) -> None:
        if actions.quit:
            if self.mode in (GameMode.PLAYING, GameMode.PAUSED, GameMode.GAME_OVER):
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

    def _handle_title(self, actions: FrameActions) -> None:
        if actions.start:
            self.world.reset()
            self.mode = GameMode.PLAYING

    def _handle_playing(self, actions: FrameActions, dt: float) -> None:
        if actions.pause:
            self.mode = GameMode.PAUSED
            return
        self.world.update(dt, actions.controls)
        if self.world.game_over:
            if self.highscore_manager.qualifies(self.world.score):
                self.entry_name = ""
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

    def _handle_highscore_events(self, events: list) -> None:
        max_len = self.config.highscore.name_length
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.mode = GameMode.GAME_OVER
                    return
                if event.key == pygame.K_RETURN:
                    if len(self.entry_name) > 0:
                        self.highscore_manager.add(
                            self.entry_name, self.world.score, self.world.wave
                        )
                        self.mode = GameMode.GAME_OVER
                        return
                elif event.key == pygame.K_BACKSPACE:
                    self.entry_name = self.entry_name[:-1]
                elif len(self.entry_name) < max_len and event.unicode.isalpha():
                    self.entry_name += event.unicode.upper()


def run(config_path: Optional[Path] = None) -> None:
    config = load_config(config_path) if config_path is not None else load_config()
    game = AsteroidsGame(config)
    game.run()


__all__ = ["AsteroidsGame", "GameMode", "run"]
