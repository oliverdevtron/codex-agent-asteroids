"""Game entities used by the Asteroids clone."""
from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Optional

from .utils import Vector2, angle_to_vector, clamp, wrap_position


@dataclass(slots=True)
class Bullet:
    position: Vector2
    velocity: Vector2
    radius: float
    lifetime: float
    age: float = 0.0
    active: bool = True
    friendly: bool = True  # False means fired by enemies

    def update(self, dt: float, width: float, height: float) -> None:
        if not self.active:
            return
        self.position += self.velocity * dt
        self.position = wrap_position(self.position, width, height)
        self.age += dt
        if self.age >= self.lifetime:
            self.active = False


class Ship:
    """Player controlled ship."""

    def __init__(self, config, bullet_config, position: Vector2) -> None:
        self.config = config
        self.bullet_config = bullet_config
        self.position = Vector2(position)
        self.velocity = Vector2()
        self.angle = -90.0  # Facing up by default
        self.fire_cooldown = 0.0
        self.hyperspace_cooldown = 0.0
        self.invulnerable_timer = 0.0
        self.alive = True
        self.respawn_timer = 0.0

    @property
    def radius(self) -> float:
        return self.config.radius

    def reset(self, position: Vector2) -> None:
        self.position = Vector2(position)
        self.velocity = Vector2()
        self.angle = -90.0
        self.fire_cooldown = 0.0
        self.hyperspace_cooldown = 0.0
        self.invulnerable_timer = self.config.respawn_invuln_s
        self.alive = True
        self.respawn_timer = 0.0

    def update(self, dt: float, width: float, height: float) -> None:
        if not self.alive:
            if self.respawn_timer > 0.0:
                self.respawn_timer -= dt
            return

        self.position += self.velocity * dt
        self.position = wrap_position(
            self.position, width, height, margin=self.config.wrap_margin_px
        )
        self.velocity *= 0.999  # subtle damping to avoid runaway rounding errors

        if self.fire_cooldown > 0.0:
            self.fire_cooldown -= dt
        if self.hyperspace_cooldown > 0.0:
            self.hyperspace_cooldown -= dt
        if self.invulnerable_timer > 0.0:
            self.invulnerable_timer -= dt

    def apply_rotation(self, direction: float, dt: float) -> None:
        if not self.alive:
            return
        rotation = self.config.turn_rate_deg_per_s * dt * direction
        self.angle = (self.angle + rotation) % 360.0

    def apply_thrust(self, dt: float) -> None:
        if not self.alive:
            return
        direction = angle_to_vector(self.angle)
        self.velocity += direction * self.config.thrust_px_per_s2 * dt
        if self.velocity.length() > self.config.max_speed_px_per_s:
            self.velocity.scale_to_length(self.config.max_speed_px_per_s)

    def can_fire(self) -> bool:
        return self.alive and self.fire_cooldown <= 0.0

    def fire(self) -> Optional[Bullet]:
        if not self.can_fire():
            return None
        direction = angle_to_vector(self.angle)
        bullet_velocity = direction * self.bullet_config.speed_px_per_s + self.velocity
        bullet_position = self.position + direction * (self.radius + 6)
        bullet = Bullet(
            position=bullet_position,
            velocity=bullet_velocity,
            radius=self.bullet_config.radius,
            lifetime=self.bullet_config.lifetime_s,
            friendly=True,
        )
        self.fire_cooldown = 1.0 / self.bullet_config.fire_rate_per_s
        return bullet

    def can_hyperspace(self) -> bool:
        return self.alive and self.hyperspace_cooldown <= 0.0

    def trigger_hyperspace(self, rng: random.Random, width: float, height: float) -> bool:
        """Attempt to hyperspace jump.

        Returns ``True`` if the ship survives the attempt, ``False`` if it fails
        catastrophically.
        """

        if not self.can_hyperspace():
            return True

        self.hyperspace_cooldown = self.config.hyperspace_cooldown_s
        if rng.random() < self.config.hyperspace_fail_chance:
            self.destroy()
            return False

        self.position = Vector2(rng.uniform(0, width), rng.uniform(0, height))
        self.velocity = Vector2()
        self.invulnerable_timer = self.config.respawn_invuln_s
        return True

    def destroy(self) -> None:
        if not self.alive:
            return
        self.alive = False
        self.respawn_timer = self.config.respawn_invuln_s

    def ready_to_respawn(self) -> bool:
        return not self.alive and self.respawn_timer <= 0.0


class Asteroid:
    def __init__(self, size_config, position: Vector2, velocity: Vector2) -> None:
        self.config = size_config
        self.position = Vector2(position)
        self.velocity = Vector2(velocity)
        self.alive = True
        self.angle = random.uniform(0, 360)
        self.spin = random.uniform(-40, 40)

    @property
    def radius(self) -> float:
        return self.config.radius

    def update(self, dt: float, width: float, height: float) -> None:
        if not self.alive:
            return
        self.position += self.velocity * dt
        self.position = wrap_position(self.position, width, height)
        self.angle = (self.angle + self.spin * dt) % 360


class Saucer:
    def __init__(self, config, kind: str, position: Vector2, direction: int, rng: random.Random) -> None:
        self.config = config
        self.kind = kind  # 'large' or 'small'
        self.type_config = config.large if kind == "large" else config.small
        self.position = Vector2(position)
        self.direction = direction
        self.velocity = Vector2(self.type_config.speed_px_per_s * direction, 0)
        self.radius = self.type_config.radius
        self.alive = True
        self.fire_timer = 0.0
        self.lifetime = 0.0
        self.max_lifetime = self.type_config.lifetime_s.random(rng)
        self.reset_fire_timer(rng)

    def reset_fire_timer(self, rng: random.Random) -> None:
        self.fire_timer = self.type_config.fire_cooldown_s.random(rng)

    def update(self, dt: float, width: float, height: float) -> None:
        if not self.alive:
            return
        self.position += self.velocity * dt
        self.lifetime += dt
        if self.direction < 0 and self.position.x < -self.radius * 2:
            self.alive = False
        elif self.direction > 0 and self.position.x > width + self.radius * 2:
            self.alive = False
        if self.fire_timer > 0.0:
            self.fire_timer -= dt

    def try_fire(self, rng: random.Random, ship: Ship, wave: int) -> Optional[Bullet]:
        if not self.alive or self.fire_timer > 0.0:
            return None

        bullet_speed = self.type_config.bullet_speed_px_per_s
        if self.kind == "large":
            base_angle = rng.uniform(0, 360)
            sigma = self.type_config.aim_error_deg_sigma.random(rng)
            angle = base_angle + rng.gauss(0, sigma)
        else:
            to_ship = ship.position - self.position
            if to_ship.length_squared() == 0:
                angle = rng.uniform(0, 360)
            else:
                base_angle = math.degrees(math.atan2(to_ship.y, to_ship.x))
                error_range = self.type_config.aim_error_deg_sigma
                denom = max(1, len(self.config.small_chance_by_wave) - 1)
                progress = clamp((wave - 1) / denom, 0.0, 1.0)
                sigma = max(
                    self.type_config.min_error_floor_deg or 0.0,
                    error_range.max - (error_range.max - error_range.min) * progress,
                )
                angle = base_angle + rng.gauss(0, sigma)
        direction = angle_to_vector(angle)
        bullet = Bullet(
            position=self.position + direction * (self.radius + 4),
            velocity=direction * bullet_speed,
            radius=3,
            lifetime=1.4,
            friendly=False,
        )
        self.reset_fire_timer(rng)
        return bullet

    def expired(self) -> bool:
        if not self.alive:
            return True
        return self.lifetime >= self.max_lifetime


def build_ship(config, width: float, height: float) -> Ship:
    ship = Ship(config.ship, config.bullet, Vector2(width / 2, height / 2))
    ship.reset(Vector2(width / 2, height / 2))
    return ship


__all__ = ["Ship", "Asteroid", "Saucer", "Bullet", "build_ship"]
