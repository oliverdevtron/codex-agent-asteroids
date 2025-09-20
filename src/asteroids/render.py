"""Rendering helpers for the Asteroids clone."""
from __future__ import annotations

import math
from typing import Optional

import pygame

from .config import Config
from .entities import Asteroid, Bullet, Saucer, Ship
from .utils import Vector2
from .world import GameWorld

COLOR_BG = (5, 5, 12)
COLOR_SHIP = (220, 220, 220)
COLOR_SHIP_SAFE = (120, 200, 255)
COLOR_ASTEROID = (160, 160, 160)
COLOR_SAUCER = (200, 80, 80)
COLOR_BULLET = (255, 255, 180)
COLOR_TEXT = (230, 230, 230)


class Renderer:
    def __init__(self, screen: pygame.Surface, config: Config) -> None:
        self.screen = screen
        self.config = config
        pygame.font.init()
        self.font = pygame.font.SysFont("Consolas", 24)
        self.large_font = pygame.font.SysFont("Consolas", 48)

    def draw(self, world: GameWorld, mode: str, fps: Optional[float] = None) -> None:
        self.screen.fill(COLOR_BG)
        if mode == "title":
            self._draw_title(world)
        elif mode == "paused":
            self._draw_playfield(world, show_hud=True, fps=fps)
            self._draw_pause()
        elif mode == "game_over":
            self._draw_playfield(world, show_hud=True, fps=fps)
            self._draw_game_over(world)
        else:
            self._draw_playfield(world, show_hud=True, fps=fps)
        pygame.display.flip()

    def _draw_title(self, world: GameWorld) -> None:
        self._draw_playfield(world, show_hud=False)
        title = self.large_font.render("ASTEROIDS", True, COLOR_TEXT)
        subtitle = self.font.render("Press ENTER to start", True, COLOR_TEXT)
        rect = title.get_rect(center=(self.screen.get_width() / 2, self.screen.get_height() / 2 - 40))
        self.screen.blit(title, rect)
        rect = subtitle.get_rect(center=(self.screen.get_width() / 2, self.screen.get_height() / 2 + 20))
        self.screen.blit(subtitle, rect)

    def _draw_game_over(self, world: GameWorld) -> None:
        text = self.large_font.render("GAME OVER", True, COLOR_TEXT)
        prompt = self.font.render("Press ENTER to play again", True, COLOR_TEXT)
        rect = text.get_rect(center=(self.screen.get_width() / 2, self.screen.get_height() / 2))
        self.screen.blit(text, rect)
        rect = prompt.get_rect(center=(self.screen.get_width() / 2, self.screen.get_height() / 2 + 40))
        self.screen.blit(prompt, rect)

    def _draw_pause(self) -> None:
        text = self.large_font.render("PAUSED", True, COLOR_TEXT)
        rect = text.get_rect(center=(self.screen.get_width() / 2, self.screen.get_height() / 2))
        self.screen.blit(text, rect)

    def _draw_playfield(self, world: GameWorld, show_hud: bool, fps: Optional[float] = None) -> None:
        if world.ship.alive:
            self._draw_ship(world.ship)
        for asteroid in world.asteroids:
            self._draw_asteroid(asteroid)
        if world.saucer is not None and world.saucer.alive:
            self._draw_saucer(world.saucer)
        for bullet in world.bullets:
            self._draw_bullet(bullet)
        for bullet in world.saucer_bullets:
            self._draw_bullet(bullet)
        if show_hud:
            self._draw_hud(world, fps)

    def _draw_ship(self, ship: Ship) -> None:
        angle = math.radians(ship.angle)
        direction = Vector2(math.cos(angle), math.sin(angle))
        left = Vector2(math.cos(angle + 2.5), math.sin(angle + 2.5))
        right = Vector2(math.cos(angle - 2.5), math.sin(angle - 2.5))
        nose = ship.position + direction * ship.radius
        tail_left = ship.position + left * ship.radius * 0.8
        tail_right = ship.position + right * ship.radius * 0.8
        color = COLOR_SHIP_SAFE if ship.invulnerable_timer > 0 else COLOR_SHIP
        points = [nose.as_tuple(), tail_left.as_tuple(), tail_right.as_tuple()]
        pygame.draw.polygon(self.screen, color, points, width=2)

    def _draw_asteroid(self, asteroid: Asteroid) -> None:
        pygame.draw.circle(
            self.screen,
            COLOR_ASTEROID,
            (int(asteroid.position.x), int(asteroid.position.y)),
            int(asteroid.radius),
            width=2,
        )

    def _draw_saucer(self, saucer: Saucer) -> None:
        rect = pygame.Rect(0, 0, saucer.radius * 2, saucer.radius)
        rect.center = (saucer.position.x, saucer.position.y)
        pygame.draw.ellipse(self.screen, COLOR_SAUCER, rect, width=2)
        pygame.draw.line(
            self.screen,
            COLOR_SAUCER,
            (saucer.position.x - saucer.radius / 2, saucer.position.y - saucer.radius / 2),
            (saucer.position.x + saucer.radius / 2, saucer.position.y - saucer.radius / 2),
            width=2,
        )

    def _draw_bullet(self, bullet: Bullet) -> None:
        pygame.draw.circle(
            self.screen,
            COLOR_BULLET,
            (int(bullet.position.x), int(bullet.position.y)),
            max(1, int(bullet.radius)),
        )

    def _draw_hud(self, world: GameWorld, fps: Optional[float]) -> None:
        margin = self.config.ui.hud_margin_px
        score_surface = self.font.render(f"Score: {world.score}", True, COLOR_TEXT)
        self.screen.blit(score_surface, (margin, margin))
        lives = world.lives_display
        for i in range(lives):
            self._draw_life_icon(margin + i * 24, margin + 40)
        wave_surface = self.font.render(f"Wave: {world.wave}", True, COLOR_TEXT)
        self.screen.blit(wave_surface, (margin, margin + 72))
        if self.config.ui.show_fps and fps is not None:
            fps_surface = self.font.render(f"{fps:5.1f} FPS", True, COLOR_TEXT)
            rect = fps_surface.get_rect(topright=(self.screen.get_width() - margin, margin))
            self.screen.blit(fps_surface, rect)

    def _draw_life_icon(self, x: float, y: float) -> None:
        size = 12
        points = [
            (x, y - size / 2),
            (x - size / 2, y + size / 2),
            (x + size / 2, y + size / 2),
        ]
        pygame.draw.polygon(self.screen, COLOR_SHIP, points, width=2)


__all__ = ["Renderer"]
