"""Game world state and update loop for the Asteroids clone."""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from .config import Config
from .entities import Asteroid, Bullet, Saucer, build_ship
from .particles import (
    COLOR_EXPLOSION_ASTEROID,
    COLOR_EXPLOSION_SAUCER,
    COLOR_EXPLOSION_SHIP,
    COLOR_THRUST,
    ParticleSystem,
)
from .utils import Vector2, angle_to_vector, distance, pick_spawn_position


@dataclass(slots=True)
class ScorePopup:
    """Floating score text that drifts upward and fades out."""
    position: Vector2
    text: str
    age: float = 0.0
    duration: float = 1.0


@dataclass(slots=True)
class ControlState:
    rotate_left: bool = False
    rotate_right: bool = False
    thrust: bool = False
    fire: bool = False
    hyperspace: bool = False

    @property
    def rotation_direction(self) -> float:
        direction = 0.0
        if self.rotate_left:
            direction -= 1.0
        if self.rotate_right:
            direction += 1.0
        return direction


@dataclass(slots=True)
class ScorePopup:
    """Floating score text that rises and fades out."""

    position: Vector2
    text: str
    age: float = 0.0
    duration: float = 1.0
    speed: float = 60.0

    @property
    def alive(self) -> bool:
        return self.age < self.duration

    @property
    def alpha(self) -> float:
        return max(0.0, 1.0 - self.age / self.duration)


class GameWorld:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.width = float(config.game.window.width)
        self.height = float(config.game.window.height)
        self.rng = random.Random(config.game.rng_seed)
        self.ship = build_ship(config, self.width, self.height)
        self.asteroids: List[Asteroid] = []
        self.bullets: List[Bullet] = []
        self.saucer_bullets: List[Bullet] = []
        self.saucer: Optional[Saucer] = None
        self.score = 0
        self.lives = max(0, config.game.starting_lives - 1)
        self.extra_life_threshold = config.game.extra_life_every
        self.wave = 1
        self.wave_clear_timer = 0.0
        self.wave_clear_pending = True  # boolean flag to avoid float == 0.0 comparison
        self.saucer_spawn_timer = 0.0
        self.game_over = False
        self.asteroid_order = [size.name for size in config.asteroids.sizes]
        self.asteroid_next = {
            name: self.asteroid_order[idx + 1]
            for idx, name in enumerate(self.asteroid_order[:-1])
        }
        # Particle system
        self.particles = ParticleSystem(config.particles.max_particles)
        # Screen shake
        self.shake_timer = 0.0
        self.shake_intensity = 0.0
        # Score popups
        self.score_popups: List[ScorePopup] = []
        # Wave announcement
        self.wave_announce_timer = 0.0
        self.wave_announce_text = ""
        # Thrust state for renderer
        self.thrusting = False
        self.reset()

    def reset(self) -> None:
        seed = self.config.game.rng_seed
        self.rng = random.Random(seed) if seed is not None else random.Random()
        self.ship.reset(Vector2(self.width / 2, self.height / 2))
        self.asteroids.clear()
        self.bullets.clear()
        self.saucer_bullets.clear()
        self.saucer = None
        self.score = 0
        self.lives = max(0, self.config.game.starting_lives - 1)
        self.extra_life_threshold = self.config.game.extra_life_every
        self.wave = 1
        self.wave_clear_timer = 0.0
        self.wave_clear_pending = True
        self.game_over = False
        self.saucer_spawn_timer = self.config.saucer.spawn_delay_s.random(self.rng)
        self.particles.clear()
        self.shake_timer = 0.0
        self.shake_intensity = 0.0
        self.score_popups.clear()
        self.wave_announce_timer = 0.0
        self.wave_announce_text = ""
        self.thrusting = False
        self.spawn_wave(initial=True)

    # region spawning helpers -------------------------------------------------
    def spawn_wave(self, initial: bool = False) -> None:
        spawn_cfg = self.config.asteroids.spawn
        count = spawn_cfg.base_count + (self.wave - 1) * spawn_cfg.count_growth
        for _ in range(count):
            self._spawn_asteroid("large", safe_spawn=initial)
        self.saucer_spawn_timer = self.config.saucer.spawn_delay_s.random(self.rng)

    def _spawn_asteroid(
        self,
        size_name: str,
        position: Optional[Vector2] = None,
        velocity: Optional[Vector2] = None,
        safe_spawn: bool = False,
    ) -> None:
        size_cfg = self.config.asteroids.size_by_name(size_name)
        if position is None:
            if safe_spawn:
                position = pick_spawn_position(
                    self.rng,
                    self.width,
                    self.height,
                    self.config.asteroids.spawn.safe_spawn_radius_px,
                    self.ship.position,
                )
            else:
                position = Vector2(self.rng.uniform(0, self.width), self.rng.uniform(0, self.height))
        if velocity is None:
            direction = angle_to_vector(self.rng.uniform(0, 360))
            speed = size_cfg.speed_px_per_s.random(self.rng)
            speed *= 1 + (self.wave - 1) * self.config.asteroids.spawn.speed_scale_per_wave
            velocity = direction * speed
        asteroid = Asteroid(size_cfg, position, velocity, rng=self.rng)
        self.asteroids.append(asteroid)

    def _spawn_saucer(self) -> None:
        if self.saucer is not None and self.saucer.alive:
            return
        if self.config.saucer.max_active <= 0:
            return

        chance_list = self.config.saucer.small_chance_by_wave
        idx = min(self.wave - 1, len(chance_list) - 1)
        small_chance = chance_list[idx]
        if self.score >= self.config.saucer.prefer_small_if_score_ge:
            small_chance = max(small_chance, 0.7)
        kind = "small" if self.rng.random() < small_chance else "large"
        type_cfg = self.config.saucer.small if kind == "small" else self.config.saucer.large
        direction = 1 if self.rng.random() < 0.5 else -1
        if direction > 0:
            start_x = -type_cfg.radius * 2
        else:
            start_x = self.width + type_cfg.radius * 2
        start_y = self.rng.uniform(type_cfg.radius, self.height - type_cfg.radius)
        self.saucer = Saucer(
            self.config.saucer,
            self.config.bullet,
            kind,
            Vector2(start_x, start_y),
            direction,
            self.rng,
        )
        self.saucer_spawn_timer = self.config.saucer.spawn_interval_s.random(self.rng)

    # endregion ----------------------------------------------------------------

    def _trigger_shake(self, intensity: Optional[float] = None, duration: Optional[float] = None) -> None:
        self.shake_intensity = intensity or self.config.effects.screen_shake_intensity
        self.shake_timer = duration or self.config.effects.screen_shake_duration

    def _add_score_popup(self, position: Vector2, points: int) -> None:
        self.score_popups.append(
            ScorePopup(
                position=Vector2(position),
                text=f"+{points}",
                duration=self.config.effects.score_popup_duration,
                speed=self.config.effects.score_popup_speed,
            )
        )

    def _emit_explosion(self, position: Vector2, color: Tuple[int, int, int], count: Optional[int] = None) -> None:
        cfg = self.config.particles
        self.particles.emit_explosion(
            position=position,
            color=color,
            count=count or cfg.explosion_count,
            speed_range=(cfg.explosion_speed.min, cfg.explosion_speed.max),
            lifetime_range=(cfg.explosion_lifetime.min, cfg.explosion_lifetime.max),
            rng=self.rng,
        )

    def update(self, dt: float, controls: ControlState) -> None:
        # Always update effects
        self.particles.update(dt)
        self._update_shake(dt)
        self._update_score_popups(dt)
        if self.wave_announce_timer > 0:
            self.wave_announce_timer -= dt

        if self.game_over:
            self._update_entities(dt)
            self.thrusting = False
            return

        # Player controls
        rotation = controls.rotation_direction
        if rotation:
            self.ship.apply_rotation(rotation, dt)
        self.thrusting = controls.thrust and self.ship.alive
        if controls.thrust:
            self.ship.apply_thrust(dt)
            if self.ship.alive:
                self.particles.emit_thrust(
                    self.ship.position,
                    self.ship.angle,
                    COLOR_THRUST,
                    count=max(1, int(self.config.particles.thrust_rate * dt)),
                    speed_range=(self.config.particles.thrust_speed.min, self.config.particles.thrust_speed.max),
                    lifetime_range=(self.config.particles.thrust_lifetime.min, self.config.particles.thrust_lifetime.max),
                    rng=self.rng,
                )
        if controls.fire and self.ship.can_fire():
            if self._active_player_bullets() < self.config.bullet.pool_size:
                bullet = self.ship.fire()
                if bullet is not None:
                    self.bullets.append(bullet)
        if controls.hyperspace:
            if not self.ship.trigger_hyperspace(self.rng, self.width, self.height):
                self._on_ship_destroyed()
                self._register_ship_loss()

        self.ship.update(dt, self.width, self.height)

        self._update_entities(dt)
        self._handle_collisions()
        self._check_wave_completion(dt)
        self._update_effects(dt)

        if not self.ship.alive and self.ship.ready_to_respawn():
            if not self.game_over and self.lives > 0:
                self.lives -= 1
                self.ship.reset(Vector2(self.width / 2, self.height / 2))
            else:
                self.game_over = True

    def _update_effects(self, dt: float) -> None:
        # Update particles
        self.particles.update(dt)

        # Update screen shake
        if self.shake_timer > 0:
            self.shake_timer -= dt
            if self.shake_timer <= 0:
                self.shake_timer = 0.0
                self.shake_intensity = 0.0

        # Update score popups
        for popup in self.score_popups:
            popup.age += dt
            popup.position.y -= popup.speed * dt
        self.score_popups = [p for p in self.score_popups if p.alive]

        # Update wave announcement
        if self.wave_announce_timer > 0:
            self.wave_announce_timer -= dt

    def _update_entities(self, dt: float) -> None:
        # Update asteroids
        for asteroid in self.asteroids:
            if asteroid.alive:
                asteroid.update(dt, self.width, self.height)

        # Update saucer
        if self.saucer is not None and self.saucer.alive:
            self.saucer.update(dt, self.width, self.height)
            if self.saucer.expired():
                self.saucer.alive = False
        if self.saucer is not None and not self.saucer.alive:
            self.saucer = None

        if self.saucer is None and self.config.saucer.max_active > 0:
            self.saucer_spawn_timer -= dt
            if self.saucer_spawn_timer <= 0.0:
                self._spawn_saucer()

        # Update bullets
        for bullet in self.bullets:
            if bullet.active:
                bullet.update(dt, self.width, self.height)

        for bullet in self.saucer_bullets:
            if bullet.active:
                bullet.update(dt, self.width, self.height)

        # Saucer firing
        if self.saucer is not None and self.ship.alive:
            bullet = self.saucer.try_fire(self.rng, self.ship, self.wave)
            if bullet is not None:
                self.saucer_bullets.append(bullet)

    def _handle_collisions(self) -> None:
        if self.ship.alive and self.ship.invulnerable_timer <= 0.0:
            for asteroid in self.asteroids:
                if asteroid.alive and distance(self.ship.position, asteroid.position) <= asteroid.radius + self.ship.radius:
                    self._on_asteroid_destroyed(asteroid)
                    asteroid.alive = False
                    self._on_ship_destroyed()
                    self._register_ship_loss()
                    self._split_asteroid(asteroid)
                    break
            if self.saucer is not None and self.saucer.alive:
                if distance(self.ship.position, self.saucer.position) <= self.saucer.radius + self.ship.radius:
                    self._on_saucer_destroyed(self.saucer)
                    self.saucer.alive = False
                    self._on_ship_destroyed()
                    self._register_ship_loss()

        # Player bullets -> asteroids / saucer
        for bullet in self.bullets:
            if not bullet.active:
                continue
            for asteroid in self.asteroids:
                if not asteroid.alive:
                    continue
                if distance(bullet.position, asteroid.position) <= asteroid.radius + bullet.radius:
                    bullet.active = False
                    self._on_asteroid_destroyed(asteroid)
                    asteroid.alive = False
                    self._split_asteroid(asteroid)
                    self._add_score(asteroid.config.score, position=asteroid.position)
                    break
            if not bullet.active:
                continue
            if self.saucer is not None and self.saucer.alive:
                if distance(bullet.position, self.saucer.position) <= self.saucer.radius + bullet.radius:
                    bullet.active = False
                    self._emit_explosion(self.saucer.position, COLOR_SAUCER_EXPLOSION, count=20)
                    self._trigger_shake()
                    score_key = "saucer_small" if self.saucer.kind == "small" else "saucer_large"
                    self._add_score_popup(self.saucer.position, self.config.scoring[score_key])
                    self._destroy_saucer(by_player=True)

        # Saucer bullets -> ship
        if self.ship.alive:
            for bullet in self.saucer_bullets:
                if not bullet.active:
                    continue
                if distance(bullet.position, self.ship.position) <= bullet.radius + self.ship.radius:
                    bullet.active = False
                    self._on_ship_destroyed()
                    self._register_ship_loss()
                    break

        # Saucer bullets -> asteroids (like original arcade game)
        for bullet in self.saucer_bullets:
            if not bullet.active:
                continue
            for asteroid in self.asteroids:
                if not asteroid.alive:
                    continue
                if distance(bullet.position, asteroid.position) <= asteroid.radius + bullet.radius:
                    bullet.active = False
                    self._on_asteroid_destroyed(asteroid)
                    asteroid.alive = False
                    self._split_asteroid(asteroid)
                    break

        # Cleanup inactive entities that may have been destroyed this frame
        self.asteroids = [asteroid for asteroid in self.asteroids if asteroid.alive]
        self.bullets = [bullet for bullet in self.bullets if bullet.active]
        self.saucer_bullets = [bullet for bullet in self.saucer_bullets if bullet.active]

    def _split_asteroid(self, asteroid: Asteroid) -> None:
        next_size = self.asteroid_next.get(asteroid.config.name)
        if next_size is None or asteroid.config.fragments <= 0:
            return
        for _ in range(asteroid.config.fragments):
            direction = angle_to_vector(self.rng.uniform(0, 360))
            speed = self.config.asteroids.size_by_name(next_size).speed_px_per_s.random(self.rng)
            velocity = direction * speed + asteroid.velocity * 0.25
            self._spawn_asteroid(next_size, position=asteroid.position, velocity=velocity, safe_spawn=False)

    def _destroy_saucer(self, by_player: bool) -> None:
        if self.saucer is None:
            return
        self._on_saucer_destroyed(self.saucer)
        if by_player:
            score_key = "saucer_small" if self.saucer.kind == "small" else "saucer_large"
            self._add_score(self.config.scoring[score_key], position=self.saucer.position)
        self.saucer.alive = False
        self.saucer = None
        self.saucer_spawn_timer = self.config.saucer.spawn_interval_s.random(self.rng)

    def _register_ship_loss(self) -> None:
        if self.ship.alive:
            self.ship.destroy()
        if self.lives <= 0:
            self.game_over = True

    def _active_player_bullets(self) -> int:
        return sum(1 for bullet in self.bullets if bullet.active and bullet.friendly)

    def _add_score(self, points: int, position: Optional[Vector2] = None) -> None:
        self.score += points
        while self.score >= self.extra_life_threshold:
            self.lives += 1
            self.extra_life_threshold += self.config.game.extra_life_every
        if position is not None and points > 0:
            self.score_popups.append(
                ScorePopup(
                    position=Vector2(position),
                    text=f"+{points}",
                    duration=self.config.effects.score_popup_duration,
                )
            )

    def _check_wave_completion(self, dt: float) -> None:
        if self.asteroids:
            self.wave_clear_timer = 0.0
            self.wave_clear_pending = True
            return
        if self.wave_clear_pending:
            self.wave_clear_timer = 2.0
            self.wave_clear_pending = False
        else:
            self.wave_clear_timer -= dt
            if self.wave_clear_timer <= 0.0:
                self.wave += 1
                self.wave_clear_pending = True
                self.wave_announce_timer = self.config.effects.wave_announce_duration
                self.wave_announce_text = f"WAVE {self.wave}"
                self.spawn_wave()

    # Effects helpers ----------------------------------------------------------
    def _on_asteroid_destroyed(self, asteroid: Asteroid) -> None:
        cfg = self.config.particles
        self.particles.emit_explosion(
            asteroid.position,
            COLOR_EXPLOSION_ASTEROID,
            count=cfg.explosion_count,
            speed_range=(cfg.explosion_speed.min, cfg.explosion_speed.max),
            lifetime_range=(cfg.explosion_lifetime.min, cfg.explosion_lifetime.max),
            rng=self.rng,
        )
        self._trigger_shake(0.5)

    def _on_ship_destroyed(self) -> None:
        cfg = self.config.particles
        self.particles.emit_explosion(
            self.ship.position,
            COLOR_EXPLOSION_SHIP,
            count=cfg.explosion_count * 2,
            speed_range=(cfg.explosion_speed.min, cfg.explosion_speed.max * 1.5),
            lifetime_range=(cfg.explosion_lifetime.min, cfg.explosion_lifetime.max * 1.5),
            rng=self.rng,
        )
        self._trigger_shake(1.0)

    def _on_saucer_destroyed(self, saucer: Saucer) -> None:
        cfg = self.config.particles
        self.particles.emit_explosion(
            saucer.position,
            COLOR_EXPLOSION_SAUCER,
            count=cfg.explosion_count,
            speed_range=(cfg.explosion_speed.min, cfg.explosion_speed.max),
            lifetime_range=(cfg.explosion_lifetime.min, cfg.explosion_lifetime.max),
            rng=self.rng,
        )
        self._trigger_shake(0.7)

    def _trigger_shake(self, intensity_scale: float = 1.0) -> None:
        self.shake_intensity = self.config.effects.screen_shake_intensity * intensity_scale
        self.shake_timer = self.config.effects.screen_shake_duration

    def _update_shake(self, dt: float) -> None:
        if self.shake_timer > 0:
            self.shake_timer -= dt
            if self.shake_timer <= 0:
                self.shake_timer = 0.0
                self.shake_intensity = 0.0

    def _update_score_popups(self, dt: float) -> None:
        for popup in self.score_popups:
            popup.age += dt
            popup.position.y -= self.config.effects.score_popup_speed * dt
        self.score_popups = [p for p in self.score_popups if p.age < p.duration]

    @property
    def shake_offset(self) -> Tuple[float, float]:
        if self.shake_timer <= 0:
            return (0.0, 0.0)
        import math
        progress = self.shake_timer / self.config.effects.screen_shake_duration
        magnitude = self.shake_intensity * progress
        angle = self.rng.uniform(0, 2 * math.pi)
        return (math.cos(angle) * magnitude, math.sin(angle) * magnitude)

    # Convenience getters -----------------------------------------------------
    @property
    def lives_display(self) -> int:
        return self.lives + (1 if self.ship.alive and not self.game_over else 0)


__all__ = ["GameWorld", "ControlState", "ScorePopup"]
