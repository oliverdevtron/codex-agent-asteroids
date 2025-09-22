"""Configuration loading tests."""
import random

from asteroids.config import Range


def test_default_config_values(game_config):
    cfg = game_config
    assert cfg.game.fps == 60
    assert cfg.game.window.width == 1280
    assert cfg.controls.rotate_left[0] == "LEFT"
    assert cfg.ship.radius == 14
    assert cfg.bullet.pool_size == 8
    assert cfg.asteroids.spawn.base_count == 4
    assert cfg.saucer.large.score == 200
    assert cfg.scoring["saucer_small"] == 1000
    assert cfg.ui.hud_margin_px == 12


def test_range_random(game_config):
    rng = Range(1, 2)
    value = rng.random(random.Random(42))
    assert 1 <= value <= 2
