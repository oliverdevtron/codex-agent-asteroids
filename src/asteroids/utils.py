"""Utility helpers for the Asteroids game."""
from __future__ import annotations

import math
from typing import Iterator, Sequence


class Vector2:
    """Light-weight 2D vector implementation without pygame dependency."""

    __slots__ = ("x", "y")

    def __init__(self, x: float = 0.0, y: float | None = None) -> None:
        if y is None:
            if isinstance(x, Vector2):
                self.x = float(x.x)
                self.y = float(x.y)
            elif isinstance(x, Sequence):
                self.x = float(x[0])
                self.y = float(x[1])
            else:
                self.x = float(x)
                self.y = 0.0
        else:
            self.x = float(x)
            self.y = float(y)

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"Vector2({self.x:.3f}, {self.y:.3f})"

    # basic container behaviour ------------------------------------------------
    def __iter__(self) -> Iterator[float]:
        yield self.x
        yield self.y

    def copy(self) -> "Vector2":
        return Vector2(self.x, self.y)

    def as_tuple(self) -> tuple[float, float]:
        return (self.x, self.y)

    # arithmetic ----------------------------------------------------------------
    def __add__(self, other: "Vector2") -> "Vector2":
        return Vector2(self.x + other.x, self.y + other.y)

    def __iadd__(self, other: "Vector2") -> "Vector2":
        self.x += other.x
        self.y += other.y
        return self

    def __sub__(self, other: "Vector2") -> "Vector2":
        return Vector2(self.x - other.x, self.y - other.y)

    def __isub__(self, other: "Vector2") -> "Vector2":
        self.x -= other.x
        self.y -= other.y
        return self

    def __mul__(self, value: float) -> "Vector2":
        return Vector2(self.x * value, self.y * value)

    def __rmul__(self, value: float) -> "Vector2":
        return self.__mul__(value)

    def __imul__(self, value: float) -> "Vector2":
        self.x *= value
        self.y *= value
        return self

    def __truediv__(self, value: float) -> "Vector2":
        return Vector2(self.x / value, self.y / value)

    def __itruediv__(self, value: float) -> "Vector2":
        self.x /= value
        self.y /= value
        return self

    # vector operations ---------------------------------------------------------
    def length(self) -> float:
        return math.hypot(self.x, self.y)

    def length_squared(self) -> float:
        return self.x * self.x + self.y * self.y

    def scale_to_length(self, new_length: float) -> None:
        current = self.length()
        if current == 0:
            return
        factor = new_length / current
        self.x *= factor
        self.y *= factor


def angle_to_vector(angle_degrees: float) -> Vector2:
    radians = math.radians(angle_degrees)
    return Vector2(math.cos(radians), math.sin(radians))


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def wrap_position(position: Vector2, width: float, height: float, margin: float = 0.0) -> Vector2:
    x = position.x
    y = position.y
    if x < -margin:
        x = width + margin
    elif x > width + margin:
        x = -margin
    if y < -margin:
        y = height + margin
    elif y > height + margin:
        y = -margin
    return Vector2(x, y)


def distance(a: Vector2, b: Vector2) -> float:
    return (a - b).length()


def random_point_with_margin(rng, width: float, height: float, margin: float) -> Vector2:
    return Vector2(rng.uniform(margin, width - margin), rng.uniform(margin, height - margin))


def pick_spawn_position(rng, width: float, height: float, safe_radius: float, ship_pos: Vector2, max_attempts: int = 50) -> Vector2:
    for _ in range(max_attempts):
        pos = Vector2(rng.uniform(0, width), rng.uniform(0, height))
        if (pos - ship_pos).length() >= safe_radius:
            return pos
    return Vector2(rng.uniform(0, width), rng.uniform(0, height))


__all__ = [
    "Vector2",
    "angle_to_vector",
    "clamp",
    "wrap_position",
    "distance",
    "random_point_with_margin",
    "pick_spawn_position",
]
