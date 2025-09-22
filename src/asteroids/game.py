"""High level game loop management."""
from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Optional

import pygame

from .config import Config, load_config
from .input import FrameActions, InputHandler
from .render import Renderer
from .world import GameWorld


class GameMode(str, Enum):
    TITLE = "title"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"


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

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(self.config.game.fps) / 1000.0
            events = pygame.event.get()
            actions = self.input_handler.process_events(events)
            self._dispatch(actions, dt)
            fps = self.clock.get_fps()
            self.renderer.draw(self.world, self.mode.value, fps=fps)
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


def run(config_path: Optional[Path] = None) -> None:
    config = load_config(config_path) if config_path is not None else load_config()
    game = AsteroidsGame(config)
    game.run()


__all__ = ["AsteroidsGame", "GameMode", "run"]
