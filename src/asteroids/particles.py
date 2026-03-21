"""Particle system for explosions and thrust effects."""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import List, Tuple

from .utils import Vector2


@dataclass(slots=True)
class Particle:
    position: Vector2
    velocity: Vector2
    color: Tuple[int, int, int]
    lifetime: float
    age: float = 0.0
    size: float = 2.0

    @property
    def alive(self) -> bool:
        return self.age < self.lifetime

    @property
    def alpha(self) -> float:
        """Return 1.0 → 0.0 as particle ages."""
        if self.lifetime <= 0:
            return 0.0
        return max(0.0, 1.0 - self.age / self.lifetime)


class ParticleSystem:
    """Manages a pool of particles with a configurable cap."""

    def __init__(self, max_particles: int = 500) -> None:
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
        _rng = rng or random.Random()
        for _ in range(count):
            if len(self.particles) >= self.max_particles:
                break
            angle = _rng.uniform(0, 2 * math.pi)
            speed = _rng.uniform(speed_range[0], speed_range[1])
            vel = Vector2(math.cos(angle) * speed, math.sin(angle) * speed)
            lt = _rng.uniform(lifetime_range[0], lifetime_range[1])
            size = _rng.uniform(1.0, 3.0)
            self.particles.append(
                Particle(
                    position=Vector2(position),
                    velocity=vel,
                    color=color,
                    lifetime=lt,
                    size=size,
                )
            )

    def emit_thrust(
        self,
        position: Vector2,
        direction_angle: float,
        color: Tuple[int, int, int] = (255, 165, 0),
        count: int = 2,
        speed_range: Tuple[float, float] = (30.0, 80.0),
        lifetime_range: Tuple[float, float] = (0.2, 0.5),
        rng: random.Random | None = None,
    ) -> None:
        _rng = rng or random.Random()
        # Thrust particles emit opposite to ship direction (behind the ship)
        back_angle = math.radians(direction_angle) + math.pi
        spread = 0.4  # radians of spread
        for _ in range(count):
            if len(self.particles) >= self.max_particles:
                break
            angle = back_angle + _rng.uniform(-spread, spread)
            speed = _rng.uniform(speed_range[0], speed_range[1])
            vel = Vector2(math.cos(angle) * speed, math.sin(angle) * speed)
            lt = _rng.uniform(lifetime_range[0], lifetime_range[1])
            self.particles.append(
                Particle(
                    position=Vector2(position),
                    velocity=vel,
                    color=color,
                    lifetime=lt,
                    size=_rng.uniform(1.0, 2.0),
                )
            )

    def clear(self) -> None:
        self.particles.clear()


# Explosion color constants for different entity types
COLOR_EXPLOSION_ASTEROID = (180, 180, 180)
COLOR_EXPLOSION_SHIP = (255, 165, 0)
COLOR_EXPLOSION_SAUCER = (220, 60, 60)
COLOR_THRUST = (255, 165, 0)


__all__ = [
    "Particle",
    "ParticleSystem",
    "COLOR_EXPLOSION_ASTEROID",
    "COLOR_EXPLOSION_SHIP",
    "COLOR_EXPLOSION_SAUCER",
    "COLOR_THRUST",
]
