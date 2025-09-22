"""Configuration loader for the Asteroids clone."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

import copy
import warnings

try:  # pragma: no cover - optional dependency
    import yaml  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - fallback path
    yaml = None


DEFAULT_CONFIG_DATA: Dict[str, Any] = {
    "game": {
        "fps": 60,
        "window": {"width": 1280, "height": 720},
        "extra_life_every": 10000,
        "starting_lives": 3,
        "rng_seed": None,
    },
    "controls": {
        "rotate_left": ["LEFT", "A"],
        "rotate_right": ["RIGHT", "D"],
        "thrust": ["UP", "W"],
        "fire": ["SPACE", "LCONTROL"],
        "hyperspace": ["LSHIFT"],
        "pause": ["P"],
        "start": ["RETURN"],
        "quit": ["ESCAPE"],
    },
    "ship": {
        "radius": 14,
        "turn_rate_deg_per_s": 220,
        "thrust_px_per_s2": 260,
        "max_speed_px_per_s": 380,
        "respawn_invuln_s": 2.0,
        "hyperspace_cooldown_s": 3.0,
        "hyperspace_fail_chance": 0.08,
        "wrap_margin_px": 16,
    },
    "bullet": {
        "speed_px_per_s": 520,
        "lifetime_s": 1.35,
        "fire_rate_per_s": 6.5,
        "pool_size": 8,
        "radius": 2,
    },
    "asteroids": {
        "sizes": [
            {
                "name": "large",
                "radius": 48,
                "speed_px_per_s": [40, 70],
                "fragments": 2,
                "score": 20,
            },
            {
                "name": "medium",
                "radius": 28,
                "speed_px_per_s": [60, 100],
                "fragments": 2,
                "score": 50,
            },
            {
                "name": "small",
                "radius": 16,
                "speed_px_per_s": [90, 140],
                "fragments": 0,
                "score": 100,
            },
        ],
        "spawn": {
            "base_count": 4,
            "count_growth": 1,
            "speed_scale_per_wave": 0.06,
            "safe_spawn_radius_px": 140,
        },
    },
    "saucer": {
        "max_active": 1,
        "spawn_delay_s": [5.0, 8.0],
        "spawn_interval_s": [7.0, 12.0],
        "small_chance_by_wave": [0.0, 0.2, 0.6, 0.7, 0.8],
        "prefer_small_if_score_ge": 40000,
        "large": {
            "radius": 18,
            "speed_px_per_s": 120,
            "fire_cooldown_s": [1.1, 1.6],
            "bullet_speed_px_per_s": 360,
            "aim_error_deg_sigma": [25, 40],
            "lifetime_s": [8.0, 12.0],
            "score": 200,
        },
        "small": {
            "radius": 14,
            "speed_px_per_s": 160,
            "fire_cooldown_s": [0.8, 1.2],
            "bullet_speed_px_per_s": 420,
            "aim_error_deg_sigma": [4, 10],
            "min_error_floor_deg": 4,
            "lifetime_s": [10.0, 14.0],
            "score": 1000,
        },
    },
    "scoring": {
        "large_asteroid": 20,
        "medium_asteroid": 50,
        "small_asteroid": 100,
        "saucer_large": 200,
        "saucer_small": 1000,
    },
    "ui": {"show_fps": False, "hud_margin_px": 12},
}


@dataclass(slots=True)
class Range:
    """Simple helper to represent an inclusive numeric range."""

    min: float
    max: float

    def random(self, rng) -> float:
        """Return a uniformly sampled value using ``rng``.

        Args:
            rng: A :class:`random.Random` compatible object with ``uniform``.
        """

        return rng.uniform(self.min, self.max)

    @classmethod
    def from_raw(cls, raw: Iterable[float]) -> "Range":
        values = list(raw)
        if len(values) != 2:
            raise ValueError(f"Range expects exactly two entries, got {values!r}")
        return cls(float(values[0]), float(values[1]))


@dataclass(slots=True)
class WindowConfig:
    width: int
    height: int


@dataclass(slots=True)
class GameConfig:
    fps: int
    window: WindowConfig
    extra_life_every: int
    starting_lives: int
    rng_seed: Optional[int] = None


@dataclass(slots=True)
class ControlsConfig:
    rotate_left: List[str]
    rotate_right: List[str]
    thrust: List[str]
    fire: List[str]
    hyperspace: List[str]
    pause: List[str]
    start: List[str]
    quit: List[str]

    @property
    def all_bindings(self) -> Dict[str, List[str]]:
        return {
            "rotate_left": self.rotate_left,
            "rotate_right": self.rotate_right,
            "thrust": self.thrust,
            "fire": self.fire,
            "hyperspace": self.hyperspace,
            "pause": self.pause,
            "start": self.start,
            "quit": self.quit,
        }


@dataclass(slots=True)
class ShipConfig:
    radius: float
    turn_rate_deg_per_s: float
    thrust_px_per_s2: float
    max_speed_px_per_s: float
    respawn_invuln_s: float
    hyperspace_cooldown_s: float
    hyperspace_fail_chance: float
    wrap_margin_px: float


@dataclass(slots=True)
class BulletConfig:
    speed_px_per_s: float
    lifetime_s: float
    fire_rate_per_s: float
    pool_size: int
    radius: float


@dataclass(slots=True)
class AsteroidSizeConfig:
    name: str
    radius: float
    speed_px_per_s: Range
    fragments: int
    score: int


@dataclass(slots=True)
class AsteroidSpawnConfig:
    base_count: int
    count_growth: int
    speed_scale_per_wave: float
    safe_spawn_radius_px: float


@dataclass(slots=True)
class AsteroidConfig:
    sizes: List[AsteroidSizeConfig]
    spawn: AsteroidSpawnConfig

    def size_by_name(self, name: str) -> AsteroidSizeConfig:
        for size in self.sizes:
            if size.name == name:
                return size
        raise KeyError(name)


@dataclass(slots=True)
class SaucerTypeConfig:
    radius: float
    speed_px_per_s: float
    fire_cooldown_s: Range
    bullet_speed_px_per_s: float
    aim_error_deg_sigma: Range
    lifetime_s: Range
    score: int
    min_error_floor_deg: Optional[float] = None


@dataclass(slots=True)
class SaucerConfig:
    max_active: int
    spawn_delay_s: Range
    spawn_interval_s: Range
    small_chance_by_wave: List[float]
    prefer_small_if_score_ge: int
    large: SaucerTypeConfig
    small: SaucerTypeConfig


@dataclass(slots=True)
class UIConfig:
    show_fps: bool
    hud_margin_px: float


@dataclass(slots=True)
class Config:
    game: GameConfig
    controls: ControlsConfig
    ship: ShipConfig
    bullet: BulletConfig
    asteroids: AsteroidConfig
    saucer: SaucerConfig
    scoring: Mapping[str, int]
    ui: UIConfig


def _load_yaml(path: Path) -> Mapping[str, Any]:
    if yaml is None:
        warnings.warn(
            "PyYAML is not installed; falling back to built-in default configuration.",
            RuntimeWarning,
            stacklevel=2,
        )
        return copy.deepcopy(DEFAULT_CONFIG_DATA)
    try:
        with path.open("r", encoding="utf8") as fh:
            return yaml.safe_load(fh)
    except FileNotFoundError:
        warnings.warn(
            f"Configuration file {path} not found; using built-in defaults.",
            RuntimeWarning,
            stacklevel=2,
        )
        return copy.deepcopy(DEFAULT_CONFIG_DATA)


def _parse_controls(data: Mapping[str, Any]) -> ControlsConfig:
    return ControlsConfig(
        rotate_left=list(data["rotate_left"]),
        rotate_right=list(data["rotate_right"]),
        thrust=list(data["thrust"]),
        fire=list(data["fire"]),
        hyperspace=list(data["hyperspace"]),
        pause=list(data["pause"]),
        start=list(data["start"]),
        quit=list(data["quit"]),
    )


def _parse_ship(data: Mapping[str, Any]) -> ShipConfig:
    return ShipConfig(
        radius=float(data["radius"]),
        turn_rate_deg_per_s=float(data["turn_rate_deg_per_s"]),
        thrust_px_per_s2=float(data["thrust_px_per_s2"]),
        max_speed_px_per_s=float(data["max_speed_px_per_s"]),
        respawn_invuln_s=float(data["respawn_invuln_s"]),
        hyperspace_cooldown_s=float(data["hyperspace_cooldown_s"]),
        hyperspace_fail_chance=float(data["hyperspace_fail_chance"]),
        wrap_margin_px=float(data["wrap_margin_px"]),
    )


def _parse_bullet(data: Mapping[str, Any]) -> BulletConfig:
    return BulletConfig(
        speed_px_per_s=float(data["speed_px_per_s"]),
        lifetime_s=float(data["lifetime_s"]),
        fire_rate_per_s=float(data["fire_rate_per_s"]),
        pool_size=int(data["pool_size"]),
        radius=float(data["radius"]),
    )


def _parse_asteroids(data: Mapping[str, Any]) -> AsteroidConfig:
    sizes = [
        AsteroidSizeConfig(
            name=item["name"],
            radius=float(item["radius"]),
            speed_px_per_s=Range.from_raw(item["speed_px_per_s"]),
            fragments=int(item["fragments"]),
            score=int(item["score"]),
        )
        for item in data["sizes"]
    ]
    spawn_raw = data["spawn"]
    spawn = AsteroidSpawnConfig(
        base_count=int(spawn_raw["base_count"]),
        count_growth=int(spawn_raw["count_growth"]),
        speed_scale_per_wave=float(spawn_raw["speed_scale_per_wave"]),
        safe_spawn_radius_px=float(spawn_raw["safe_spawn_radius_px"]),
    )
    return AsteroidConfig(sizes=sizes, spawn=spawn)


def _parse_saucer_type(data: Mapping[str, Any]) -> SaucerTypeConfig:
    return SaucerTypeConfig(
        radius=float(data["radius"]),
        speed_px_per_s=float(data["speed_px_per_s"]),
        fire_cooldown_s=Range.from_raw(data["fire_cooldown_s"]),
        bullet_speed_px_per_s=float(data["bullet_speed_px_per_s"]),
        aim_error_deg_sigma=Range.from_raw(data["aim_error_deg_sigma"]),
        lifetime_s=Range.from_raw(data["lifetime_s"]),
        score=int(data["score"]),
        min_error_floor_deg=float(data.get("min_error_floor_deg", 0.0))
        if "min_error_floor_deg" in data
        else None,
    )


def _parse_saucer(data: Mapping[str, Any]) -> SaucerConfig:
    return SaucerConfig(
        max_active=int(data["max_active"]),
        spawn_delay_s=Range.from_raw(data["spawn_delay_s"]),
        spawn_interval_s=Range.from_raw(data["spawn_interval_s"]),
        small_chance_by_wave=[float(v) for v in data["small_chance_by_wave"]],
        prefer_small_if_score_ge=int(data["prefer_small_if_score_ge"]),
        large=_parse_saucer_type(data["large"]),
        small=_parse_saucer_type(data["small"]),
    )


def _parse_ui(data: Mapping[str, Any]) -> UIConfig:
    return UIConfig(
        show_fps=bool(data["show_fps"]),
        hud_margin_px=float(data["hud_margin_px"]),
    )


def _parse_game(data: Mapping[str, Any]) -> GameConfig:
    window = data["window"]
    return GameConfig(
        fps=int(data["fps"]),
        window=WindowConfig(width=int(window["width"]), height=int(window["height"])),
        extra_life_every=int(data["extra_life_every"]),
        starting_lives=int(data["starting_lives"]),
        rng_seed=data.get("rng_seed"),
    )


def load_config(path: Optional[Path | str] = None) -> Config:
    """Load the configuration from ``path`` or the project default."""

    if path is None:
        path = Path(__file__).resolve().parents[2] / "config.yaml"
    else:
        path = Path(path)

    data = _load_yaml(path)

    return Config(
        game=_parse_game(data["game"]),
        controls=_parse_controls(data["controls"]),
        ship=_parse_ship(data["ship"]),
        bullet=_parse_bullet(data["bullet"]),
        asteroids=_parse_asteroids(data["asteroids"]),
        saucer=_parse_saucer(data["saucer"]),
        scoring={k: int(v) for k, v in data["scoring"].items()},
        ui=_parse_ui(data["ui"]),
    )


__all__ = [
    "Config",
    "GameConfig",
    "ControlsConfig",
    "ShipConfig",
    "BulletConfig",
    "AsteroidConfig",
    "AsteroidSizeConfig",
    "AsteroidSpawnConfig",
    "SaucerConfig",
    "SaucerTypeConfig",
    "UIConfig",
    "Range",
    "load_config",
]
