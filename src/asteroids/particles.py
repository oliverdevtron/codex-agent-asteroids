"""Particle system for explosions and thrust effects."""
from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import List, Tuple

from .utils import Vector2, angle_to_vector

# Default colors for different entity explosions
COLOR_ASTEROID_EXPLOSION = (160, 160, 160)
COLOR_SHIP_EXPLOSION = (255, 165, 60)
COLOR_SAUCER_EXPLOSION = (220, 60, 60)
COLOR_THRUST_BASE = (255, 165, 0)
COLOR_THRUST_TIP = (255, 255, 100)

MAX_PARTICLES = 500


@dataclass(slots=True)
class Particle:
    """A single visual particle."""

    position: Vector2
    velocity: Vector2
    color: Tuple[int, int, int]
    lifetime: float
    age: float
    size: float

    @property
    def alive(self) -> bool:
        return self.age < self.lifetime

    @property
    def alpha(self) -> float:
        """Normalized remaining life (1.0 = just born, 0.0 = dead)."""
        return max(0.0, 1.0 - self.age / self.lifetime)


class ParticleSystem:
    """Manages a pool of particles with emit helpers."""

    def __init__(self, max_particles: int = MAX_PARTICLES) -> None:
        self.max_particles = max_particles
        self.particles: List[Particle] = []

    def update(self, dt: float) -> None:
        for p in self.particles:
            p.position += p.velocity * dt
            p.age += dt
        self.particles = [p for p in self.particles if p.alive]

    def emit_explosion(
        self,
        position: Vector2,
        color: Tuple[int, int, int],
        count: int = 15,
        speed_range: Tuple[float, float] = (50.0, 200.0),
        lifetime_range: Tuple[float, float] = (0.3, 1.0),
        rng: random.Random | None = None,
    ) -> None:
        rng = rng or random.Random()
        available = self.max_particles - len(self.particles)
        count = min(count, available)
        for _ in range(count):
            angle = rng.uniform(0, 360)
            speed = rng.uniform(speed_range[0], speed_range[1])
            direction = angle_to_vector(angle)
            lifetime = rng.uniform(lifetime_range[0], lifetime_range[1])
            # Slight color variation
            r = min(255, max(0, color[0] + rng.randint(-20, 20)))
            g = min(255, max(0, color[1] + rng.randint(-20, 20)))
            b = min(255, max(0, color[2] + rng.randint(-20, 20)))
            self.particles.append(
                Particle(
                    position=Vector2(position),
                    velocity=direction * speed,
                    color=(r, g, b),
                    lifetime=lifetime,
                    age=0.0,
                    size=rng.uniform(1.5, 3.5),
                )
            )

    def emit_thrust(
        self,
        position: Vector2,
        ship_angle: float,
        rng: random.Random | None = None,
        thrust_speed: Tuple[float, float] = (30.0, 80.0),
        thrust_lifetime: Tuple[float, float] = (0.2, 0.5),
    ) -> None:
        rng = rng or random.Random()
        if len(self.particles) >= self.max_particles:
            return
        # Thrust particles go opposite to ship heading with some spread
        back_angle = (ship_angle + 180.0) % 360.0
        spread = rng.uniform(-25, 25)
        direction = angle_to_vector(back_angle + spread)
        speed = rng.uniform(thrust_speed[0], thrust_speed[1])
        lifetime = rng.uniform(thrust_lifetime[0], thrust_lifetime[1])
        color = COLOR_THRUST_BASE if rng.random() > 0.4 else COLOR_THRUST_TIP
        self.particles.append(
            Particle(
                position=Vector2(position),
                velocity=direction * speed,
                color=color,
                lifetime=lifetime,
                age=0.0,
                size=rng.uniform(1.0, 2.5),
            )
        )

    def clear(self) -> None:
        self.particles.clear()


__all__ = [
    "Particle",
    "ParticleSystem",
    "COLOR_ASTEROID_EXPLOSION",
    "COLOR_SHIP_EXPLOSION",
    "COLOR_SAUCER_EXPLOSION",
]
