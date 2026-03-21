"""Rendering helpers for the Asteroids clone."""
from __future__ import annotations

import math
import random
from typing import List, Optional, Tuple

import pygame

from .config import Config
from .entities import Asteroid, Bullet, Saucer, Ship
from .particles import Particle
from .utils import Vector2
from .world import GameWorld

COLOR_BG = (5, 5, 12)
COLOR_SHIP = (220, 220, 220)
COLOR_SHIP_SAFE = (120, 200, 255)
COLOR_ASTEROID = (160, 160, 160)
COLOR_SAUCER = (200, 80, 80)
COLOR_SAUCER_DOME = (220, 100, 100)
COLOR_SAUCER_LIGHT = (255, 255, 100)
COLOR_BULLET = (255, 255, 180)
COLOR_BULLET_GLOW = (255, 255, 180)
COLOR_TEXT = (230, 230, 230)
COLOR_THRUST_FLAME = (255, 165, 0)


def _generate_star_layer(
    rng: random.Random, width: int, height: int, count: int, brightness: int, size: int
) -> List[Tuple[float, float, int, int]]:
    """Generate a layer of stars: (x, y, brightness, size)."""
    return [
        (rng.uniform(0, width), rng.uniform(0, height), brightness + rng.randint(-20, 20), size)
        for _ in range(count)
    ]


class Renderer:
    def __init__(self, screen: pygame.Surface, config: Config) -> None:
        self.screen = screen
        self.config = config
        pygame.font.init()
        self.font = pygame.font.SysFont("Consolas", 24)
        self.large_font = pygame.font.SysFont("Consolas", 48)
        self.small_font = pygame.font.SysFont("Consolas", 18)
        # Generate starfield layers (seeded for consistency)
        self._starfield = self._generate_starfield(screen.get_width(), screen.get_height())

    def _generate_starfield(
        self, width: int, height: int
    ) -> List[List[Tuple[float, float, int, int]]]:
        """Generate 3 parallax star layers: [(x, y, brightness, size), ...]."""
        rng = random.Random(42)
        layers: List[List[Tuple[float, float, int, int]]] = []
        layer_specs = [
            (80, 80, 1),   # many dim small stars
            (40, 150, 2),  # medium stars
            (15, 230, 3),  # few bright large stars
        ]
        for count, brightness, size in layer_specs:
            stars = []
            for _ in range(count):
                x = rng.uniform(0, width)
                y = rng.uniform(0, height)
                b = rng.randint(max(40, brightness - 40), brightness)
                stars.append((x, y, b, size))
            layers.append(stars)
        return layers

    def draw(self, world: GameWorld, mode: str, fps: Optional[float] = None) -> None:
        self.screen.fill(COLOR_BG)
        # Draw starfield behind everything
        self._draw_starfield(world)
        if mode == "title":
            self._draw_title(world)
        elif mode == "paused":
            self._draw_playfield(world, show_hud=True, fps=fps)
            self._draw_pause()
        elif mode == "game_over":
            self._draw_playfield(world, show_hud=True, fps=fps)
            self._draw_game_over(world)
        elif mode == "highscore_entry":
            self._draw_playfield(world, show_hud=True, fps=fps)
            self._draw_game_over(world)
        else:
            self._draw_playfield(world, show_hud=True, fps=fps)
        pygame.display.flip()

    def _draw_starfield(self, world: GameWorld) -> None:
        w = self.screen.get_width()
        h = self.screen.get_height()
        # Parallax speeds per layer
        speeds = [0.02, 0.05, 0.1]
        sx = world.ship.velocity.x if world.ship.alive else 0.0
        sy = world.ship.velocity.y if world.ship.alive else 0.0
        for layer_idx, stars in enumerate(self._starfield):
            speed = speeds[min(layer_idx, len(speeds) - 1)]
            for base_x, base_y, brightness, size in stars:
                x = (base_x - sx * speed) % w
                y = (base_y - sy * speed) % h
                color = (brightness, brightness, brightness)
                if size <= 1:
                    self.screen.set_at((int(x), int(y)), color)
                else:
                    pygame.draw.circle(self.screen, color, (int(x), int(y)), size)

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
        # Get screen shake offset
        ox, oy = world.shake_offset

        if world.ship.alive:
            self._draw_ship(world.ship, ox, oy, thrusting=world.thrusting)
        for asteroid in world.asteroids:
            self._draw_asteroid(asteroid, ox, oy)
        if world.saucer is not None and world.saucer.alive:
            self._draw_saucer(world.saucer, ox, oy)
        for bullet in world.bullets:
            self._draw_bullet(bullet, ox, oy)
        for bullet in world.saucer_bullets:
            self._draw_bullet(bullet, ox, oy)
        # Draw particles
        self._draw_particles(world.particles.particles, ox, oy)
        # Draw score popups
        self._draw_score_popups(world, ox, oy)
        # Draw wave announcement
        self._draw_wave_announcement(world)
        if show_hud:
            self._draw_hud(world, fps)

    def _draw_ship(self, ship: Ship, ox: float = 0, oy: float = 0, thrusting: bool = False) -> None:
        angle = math.radians(ship.angle)
        direction = Vector2(math.cos(angle), math.sin(angle))
        left = Vector2(math.cos(angle + 2.5), math.sin(angle + 2.5))
        right = Vector2(math.cos(angle - 2.5), math.sin(angle - 2.5))
        ox, oy = self.shake_offset.x, self.shake_offset.y
        nose = ship.position + direction * ship.radius
        tail_left = ship.position + left * ship.radius * 0.8
        tail_right = ship.position + right * ship.radius * 0.8
        color = COLOR_SHIP_SAFE if ship.invulnerable_timer > 0 else COLOR_SHIP
        points = [
            (nose.x + ox, nose.y + oy),
            (tail_left.x + ox, tail_left.y + oy),
            (tail_right.x + ox, tail_right.y + oy),
        ]
        pygame.draw.polygon(self.screen, color, points, width=2)
        # Thrust flame
        if thrusting:
            self._draw_thrust_flame(ship, tail_left, tail_right, direction, ox, oy)

    def _draw_thrust_flame(
        self, ship: Ship, tail_left: Vector2, tail_right: Vector2,
        direction: Vector2, ox: float, oy: float
    ) -> None:
        mid_tail = (tail_left + tail_right) * 0.5
        # Flicker: vary flame length
        flicker = 0.7 + 0.6 * abs(math.sin(pygame.time.get_ticks() * 0.02))
        flame_tip = mid_tail - direction * ship.radius * 0.6 * flicker
        flame_points = [
            (tail_left.x + ox, tail_left.y + oy),
            (flame_tip.x + ox, flame_tip.y + oy),
            (tail_right.x + ox, tail_right.y + oy),
        ]
        pygame.draw.polygon(self.screen, COLOR_THRUST_FLAME, flame_points, width=2)

    def _draw_asteroid(self, asteroid: Asteroid, ox: float = 0, oy: float = 0) -> None:
        # Draw as polygon using stored vertex offsets
        num_points = len(asteroid.vertices)
        if num_points < 3:
            # fallback to circle
            pygame.draw.circle(
                self.screen, COLOR_ASTEROID,
                (int(asteroid.position.x + ox), int(asteroid.position.y + oy)),
                int(asteroid.radius), width=2,
            )
            return
        angle_rad = math.radians(asteroid.angle)
        points = []
        for i, scale in enumerate(asteroid.vertices):
            theta = angle_rad + (2 * math.pi * i / num_points)
            r = asteroid.radius * scale
            px = asteroid.position.x + math.cos(theta) * r + ox
            py = asteroid.position.y + math.sin(theta) * r + oy
            points.append((px, py))
        pygame.draw.polygon(self.screen, COLOR_ASTEROID, points, width=2)

    def _draw_saucer(self, saucer: Saucer, ox: float = 0, oy: float = 0) -> None:
        cx = saucer.position.x + ox
        cy = saucer.position.y + oy
        r = saucer.radius
        # Main body ellipse
        body_rect = pygame.Rect(0, 0, int(r * 2), int(r))
        body_rect.center = (int(cx), int(cy))
        pygame.draw.ellipse(self.screen, COLOR_SAUCER, body_rect, width=2)
        # Dome on top
        dome_rect = pygame.Rect(0, 0, int(r), int(r * 0.6))
        dome_rect.midbottom = (int(cx), int(cy - r * 0.15))
        pygame.draw.ellipse(self.screen, COLOR_SAUCER_DOME, dome_rect, width=2)
        # Flashing lights along body
        light_phase = (pygame.time.get_ticks() // 200) % 3
        light_positions = [
            (cx - r * 0.5, cy),
            (cx, cy + r * 0.2),
            (cx + r * 0.5, cy),
        ]
        for i, (lx, ly) in enumerate(light_positions):
            if i == light_phase:
                pygame.draw.circle(self.screen, COLOR_SAUCER_LIGHT, (int(lx), int(ly)), 2)

    def _draw_bullet(self, bullet: Bullet, ox: float = 0, oy: float = 0) -> None:
        bx = int(bullet.position.x + ox)
        by = int(bullet.position.y + oy)
        # Glow effect: larger semi-transparent circle
        glow_radius = max(3, int(bullet.radius * 3))
        glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(
            glow_surface, (*COLOR_BULLET_GLOW, 50),
            (glow_radius, glow_radius), glow_radius,
        )
        self.screen.blit(glow_surface, (bx - glow_radius, by - glow_radius))
        # Core bullet
        pygame.draw.circle(
            self.screen, COLOR_BULLET, (bx, by), max(1, int(bullet.radius)),
        )

    def _draw_particles(self, particles: list, ox: float = 0, oy: float = 0) -> None:
        for p in particles:
            alpha = max(0, min(255, int(p.alpha * 255)))
            if alpha <= 0:
                continue
            px = int(p.position.x + ox)
            py = int(p.position.y + oy)
            size = max(1, int(p.size * p.alpha))
            if size <= 1:
                color = (*p.color, alpha)
                surf = pygame.Surface((2, 2), pygame.SRCALPHA)
                surf.fill(color)
                self.screen.blit(surf, (px - 1, py - 1))
            else:
                color = (*p.color, alpha)
                surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(surf, color, (size, size), size)
                self.screen.blit(surf, (px - size, py - size))

    def _draw_score_popups(self, world: GameWorld, ox: float, oy: float) -> None:
        for popup in world.score_popups:
            progress = popup.age / popup.duration
            alpha = max(0, int(255 * (1.0 - progress)))
            color = (255, 255, 100, alpha)
            surf = self.small_font.render(popup.text, True, (255, 255, 100))
            surf.set_alpha(alpha)
            x = int(popup.position.x + ox)
            y = int(popup.position.y + oy)
            rect = surf.get_rect(center=(x, y))
            self.screen.blit(surf, rect)

    def _draw_wave_announcement(self, world: GameWorld) -> None:
        if world.wave_announce_timer <= 0:
            return
        duration = self.config.effects.wave_announce_duration
        progress = world.wave_announce_timer / duration
        # Fade in first 30%, hold, fade out last 30%
        if progress > 0.7:
            alpha = int(255 * ((1.0 - progress) / 0.3))
        elif progress < 0.3:
            alpha = int(255 * (progress / 0.3))
        else:
            alpha = 255
        alpha = max(0, min(255, alpha))
        text = self.large_font.render(world.wave_announce_text, True, COLOR_TEXT)
        text.set_alpha(alpha)
        rect = text.get_rect(center=(self.screen.get_width() / 2, self.screen.get_height() / 3))
        self.screen.blit(text, rect)

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

    def draw_highscore_table(self, entries: list) -> None:
        """Draw highscore table on screen (used in title screen)."""
        cx = self.screen.get_width() / 2
        start_y = self.screen.get_height() / 2 + 80
        header = self.font.render("HIGH SCORES", True, COLOR_TEXT)
        rect = header.get_rect(center=(cx, start_y))
        self.screen.blit(header, rect)
        for i, entry in enumerate(entries[:10]):
            line = f"{i + 1:2d}. {entry.name:3s}  {entry.score:>8d}  W{entry.wave}"
            surf = self.small_font.render(line, True, COLOR_TEXT)
            rect = surf.get_rect(center=(cx, start_y + 30 + i * 22))
            self.screen.blit(surf, rect)

    def draw_name_entry(self, current_name: str) -> None:
        """Draw the highscore name entry overlay."""
        cx = self.screen.get_width() / 2
        cy = self.screen.get_height() / 2
        text = self.large_font.render("NEW HIGH SCORE!", True, (255, 255, 100))
        rect = text.get_rect(center=(cx, cy - 40))
        self.screen.blit(text, rect)
        # Show current name with cursor
        display = current_name + "_" * (3 - len(current_name))
        name_surf = self.large_font.render(display, True, COLOR_TEXT)
        rect = name_surf.get_rect(center=(cx, cy + 20))
        self.screen.blit(name_surf, rect)
        hint = self.small_font.render("Type 3 letters, then press ENTER", True, COLOR_TEXT)
        rect = hint.get_rect(center=(cx, cy + 70))
        self.screen.blit(hint, rect)


__all__ = ["Renderer"]
