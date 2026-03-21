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
COLOR_BULLET = (255, 255, 180)
COLOR_TEXT = (230, 230, 230)


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

        # Generate parallax starfield layers (seeded for consistency)
        star_rng = random.Random(42)
        w, h = screen.get_width(), screen.get_height()
        self.star_layers = [
            (_generate_star_layer(star_rng, w, h, 60, 60, 1), 0.1),   # dim, small, slow
            (_generate_star_layer(star_rng, w, h, 30, 120, 1), 0.3),  # medium
            (_generate_star_layer(star_rng, w, h, 15, 200, 2), 0.6),  # bright, large, fast
        ]

        # Shake offset
        self.shake_offset = Vector2()

    def draw(self, world: GameWorld, mode: str, fps: Optional[float] = None) -> None:
        self.screen.fill(COLOR_BG)

        # Update screen shake offset
        self._update_shake(world)

        # Draw starfield (always behind everything)
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
        else:
            self._draw_playfield(world, show_hud=True, fps=fps)
        pygame.display.flip()

    def _update_shake(self, world: GameWorld) -> None:
        if world.shake_timer > 0:
            intensity = world.shake_intensity * (world.shake_timer / self.config.effects.screen_shake_duration)
            self.shake_offset = Vector2(
                random.uniform(-intensity, intensity),
                random.uniform(-intensity, intensity),
            )
        else:
            self.shake_offset = Vector2()

    def _offset(self, x: float, y: float) -> Tuple[float, float]:
        """Apply screen shake offset to coordinates."""
        return (x + self.shake_offset.x, y + self.shake_offset.y)

    def _draw_starfield(self, world: GameWorld) -> None:
        w, h = self.screen.get_width(), self.screen.get_height()
        for stars, parallax in self.star_layers:
            # Parallax based on ship velocity
            vx = world.ship.velocity.x * parallax * 0.01 if world.ship.alive else 0
            vy = world.ship.velocity.y * parallax * 0.01 if world.ship.alive else 0
            for sx, sy, brightness, size in stars:
                # Wrap star positions
                draw_x = (sx - vx) % w
                draw_y = (sy - vy) % h
                b = max(0, min(255, brightness))
                color = (b, b, b)
                self.screen.set_at((int(draw_x), int(draw_y)), color)
                if size > 1:
                    self.screen.set_at((int(draw_x) + 1, int(draw_y)), color)

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
            self._draw_ship(world.ship, thrusting=False)
        for asteroid in world.asteroids:
            self._draw_asteroid(asteroid)
        if world.saucer is not None and world.saucer.alive:
            self._draw_saucer(world.saucer)
        for bullet in world.bullets:
            self._draw_bullet(bullet)
        for bullet in world.saucer_bullets:
            self._draw_bullet(bullet)

        # Draw particles
        self._draw_particles(world.particles.particles)

        # Draw score popups
        self._draw_score_popups(world)

        # Draw wave announcement
        self._draw_wave_announce(world)

        if show_hud:
            self._draw_hud(world, fps)

    def _draw_ship(self, ship: Ship, thrusting: bool = False) -> None:
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

        # Draw thrust flame when thrusting
        if thrusting:
            self._draw_thrust_flame(ship, tail_left, tail_right, direction, ox, oy)

    def _draw_thrust_flame(
        self, ship: Ship, tail_left: Vector2, tail_right: Vector2,
        direction: Vector2, ox: float, oy: float
    ) -> None:
        # Animated flickering flame behind the ship
        mid_tail = (tail_left + tail_right) * 0.5
        flame_length = ship.radius * (0.6 + random.random() * 0.5)
        flame_tip = mid_tail - direction * flame_length
        flame_color = (255, 165 + random.randint(-30, 30), 0)
        flame_points = [
            (tail_left.x + ox, tail_left.y + oy),
            (flame_tip.x + ox, flame_tip.y + oy),
            (tail_right.x + ox, tail_right.y + oy),
        ]
        pygame.draw.polygon(self.screen, flame_color, flame_points, width=2)

    def _draw_asteroid(self, asteroid: Asteroid) -> None:
        ox, oy = self.shake_offset.x, self.shake_offset.y
        cx, cy = asteroid.position.x + ox, asteroid.position.y + oy
        num_verts = len(asteroid.vertices)
        if num_verts < 3:
            # Fallback to circle
            pygame.draw.circle(
                self.screen, COLOR_ASTEROID,
                (int(cx), int(cy)), int(asteroid.radius), width=2,
            )
            return

        angle_rad = math.radians(asteroid.angle)
        points = []
        for i, radius_mult in enumerate(asteroid.vertices):
            theta = angle_rad + (2 * math.pi * i / num_verts)
            px = cx + math.cos(theta) * radius_mult
            py = cy + math.sin(theta) * radius_mult
            points.append((px, py))
        pygame.draw.polygon(self.screen, COLOR_ASTEROID, points, width=2)

    def _draw_saucer(self, saucer: Saucer) -> None:
        ox, oy = self.shake_offset.x, self.shake_offset.y
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
        pygame.draw.ellipse(self.screen, COLOR_SAUCER, dome_rect, width=2)

        # Horizontal line across body
        pygame.draw.line(
            self.screen, COLOR_SAUCER,
            (cx - r, cy), (cx + r, cy), width=1,
        )

        # Lights (small dots along the body)
        for dx in (-r * 0.5, 0, r * 0.5):
            light_color = (255, 200, 100)
            pygame.draw.circle(
                self.screen, light_color,
                (int(cx + dx), int(cy + r * 0.15)), 2,
            )

    def _draw_bullet(self, bullet: Bullet) -> None:
        ox, oy = self.shake_offset.x, self.shake_offset.y
        bx = int(bullet.position.x + ox)
        by = int(bullet.position.y + oy)
        r = max(1, int(bullet.radius))

        # Glow effect: larger semi-transparent circle
        glow_radius = r + 3
        glow_surface = pygame.Surface((glow_radius * 2 + 2, glow_radius * 2 + 2), pygame.SRCALPHA)
        glow_color = (255, 255, 180, 60)
        pygame.draw.circle(glow_surface, glow_color, (glow_radius + 1, glow_radius + 1), glow_radius)
        self.screen.blit(glow_surface, (bx - glow_radius - 1, by - glow_radius - 1))

        # Core bullet
        pygame.draw.circle(self.screen, COLOR_BULLET, (bx, by), r)

    def _draw_particles(self, particles: List[Particle]) -> None:
        ox, oy = self.shake_offset.x, self.shake_offset.y
        for p in particles:
            alpha = p.alpha
            if alpha <= 0:
                continue
            r, g, b = p.color
            # Fade out
            r = int(r * alpha)
            g = int(g * alpha)
            b = int(b * alpha)
            size = max(1, int(p.size * alpha))
            px = int(p.position.x + ox)
            py = int(p.position.y + oy)
            if size <= 1:
                self.screen.set_at((px, py), (r, g, b))
            else:
                pygame.draw.circle(self.screen, (r, g, b), (px, py), size)

    def _draw_score_popups(self, world: GameWorld) -> None:
        for popup in world.score_popups:
            alpha = popup.alpha
            if alpha <= 0:
                continue
            gray = int(230 * alpha)
            color = (gray, gray, gray)
            text_surface = self.small_font.render(popup.text, True, color)
            rect = text_surface.get_rect(center=(int(popup.position.x), int(popup.position.y)))
            self.screen.blit(text_surface, rect)

    def _draw_wave_announce(self, world: GameWorld) -> None:
        if world.wave_announce_timer <= 0:
            return
        duration = self.config.effects.wave_announce_duration
        progress = world.wave_announce_timer / duration
        # Fade in for first 30%, hold, then fade out for last 30%
        if progress > 0.7:
            alpha = (1.0 - progress) / 0.3
        elif progress < 0.3:
            alpha = progress / 0.3
        else:
            alpha = 1.0
        gray = int(230 * alpha)
        color = (gray, gray, gray)
        text = self.large_font.render(f"WAVE {world.wave_announce_wave}", True, color)
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

    def draw_highscore_entry(self, world: GameWorld, name_chars: List[str], cursor_pos: int) -> None:
        """Draw the highscore name entry overlay."""
        cx = self.screen.get_width() / 2
        cy = self.screen.get_height() / 2

        title = self.large_font.render("HIGH SCORE!", True, COLOR_TEXT)
        rect = title.get_rect(center=(cx, cy - 80))
        self.screen.blit(title, rect)

        score_text = self.font.render(f"Score: {world.score}", True, COLOR_TEXT)
        rect = score_text.get_rect(center=(cx, cy - 30))
        self.screen.blit(score_text, rect)

        prompt = self.font.render("Enter your name:", True, COLOR_TEXT)
        rect = prompt.get_rect(center=(cx, cy + 10))
        self.screen.blit(prompt, rect)

        # Draw name characters with cursor
        name_display = ""
        for i, ch in enumerate(name_chars):
            if i == cursor_pos:
                name_display += f"[{ch}]"
            else:
                name_display += f" {ch} "
        name_surface = self.large_font.render(name_display, True, (255, 255, 100))
        rect = name_surface.get_rect(center=(cx, cy + 60))
        self.screen.blit(name_surface, rect)

        hint = self.small_font.render("UP/DOWN to change, LEFT/RIGHT to move, ENTER to confirm", True, COLOR_TEXT)
        rect = hint.get_rect(center=(cx, cy + 110))
        self.screen.blit(hint, rect)

    def draw_highscore_table(self, entries) -> None:
        """Draw highscore table on the title screen."""
        if not entries:
            return
        cx = self.screen.get_width() / 2
        start_y = self.screen.get_height() / 2 + 70
        header = self.small_font.render("HIGH SCORES", True, (180, 180, 180))
        rect = header.get_rect(center=(cx, start_y))
        self.screen.blit(header, rect)
        for i, entry in enumerate(entries[:5]):  # Show top 5 on title
            text = f"{i + 1}. {entry.name:3s}  {entry.score:>7d}  W{entry.wave}"
            line = self.small_font.render(text, True, (160, 160, 160))
            rect = line.get_rect(center=(cx, start_y + 25 + i * 22))
            self.screen.blit(line, rect)


__all__ = ["Renderer"]
