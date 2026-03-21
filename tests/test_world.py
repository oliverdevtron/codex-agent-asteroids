"""Tests for the game world behaviour."""

from asteroids.entities import Bullet
from asteroids.utils import Vector2
from asteroids.world import ControlState, GameWorld


def test_extra_life_awarded(game_config):
    world = GameWorld(game_config)
    initial_lives = world.lives
    world._add_score(world.extra_life_threshold)
    assert world.lives == initial_lives + 1
    assert world.extra_life_threshold == game_config.game.extra_life_every * 2


def test_asteroid_split_and_scoring(game_config):
    world = GameWorld(game_config)
    world.asteroids.clear()
    world.bullets.clear()
    world._spawn_asteroid("large", position=Vector2(100, 100), velocity=Vector2(0, 0))
    bullet = Bullet(position=Vector2(100, 100), velocity=Vector2(), radius=game_config.bullet.radius, lifetime=1.0)
    world.bullets.append(bullet)
    world._handle_collisions()
    assert world.score == game_config.scoring["large_asteroid"]
    assert all(asteroid.config.name != "large" for asteroid in world.asteroids)


def test_saucer_spawn_prefer_small(game_config):
    world = GameWorld(game_config)
    world.score = game_config.saucer.prefer_small_if_score_ge + 1000
    world.wave = 5
    world.saucer = None
    world.saucer_spawn_timer = 0.0
    world.rng.random = lambda: 0.0  # force small saucer
    world.update(0.1, ControlState())
    assert world.saucer is not None
    assert world.saucer.kind == "small"


def test_hyperspace_failure_consumes_life(game_config):
    world = GameWorld(game_config)
    world.config.ship.hyperspace_fail_chance = 1.0
    world.ship.hyperspace_cooldown = 0.0
    initial_lives = world.lives
    world.update(0.1, ControlState(hyperspace=True))
    assert not world.ship.alive
    assert world.game_over is False
    total_time = 0.0
    while not world.ship.alive and total_time < 5.0:
        world.update(0.5, ControlState())
        total_time += 0.5
    assert world.ship.alive
    assert world.lives == initial_lives - 1


def test_saucer_bullet_destroys_asteroid(game_config):
    """Saucer bullets should destroy asteroids on collision (original game behavior)."""
    world = GameWorld(game_config)
    world.asteroids.clear()
    world.bullets.clear()
    world.saucer_bullets.clear()

    # Spawn a single asteroid
    world._spawn_asteroid("large", position=Vector2(200, 200), velocity=Vector2(0, 0))
    assert len(world.asteroids) == 1

    # Place a saucer bullet right on top of the asteroid
    saucer_bullet = Bullet(
        position=Vector2(200, 200),
        velocity=Vector2(0, 0),
        radius=game_config.bullet.radius,
        lifetime=2.0,
        friendly=False,
    )
    world.saucer_bullets.append(saucer_bullet)

    world._handle_collisions()

    # The large asteroid should be destroyed and split into medium ones
    assert not any(a.config.name == "large" for a in world.asteroids)
    # Saucer bullet should be consumed
    assert len(world.saucer_bullets) == 0


def test_score_popup_created_on_asteroid_destroy(game_config):
    """Destroying an asteroid with a player bullet should create a score popup."""
    world = GameWorld(game_config)
    world.asteroids.clear()
    world.bullets.clear()
    world.score_popups.clear()

    world._spawn_asteroid("small", position=Vector2(300, 300), velocity=Vector2(0, 0))
    bullet = Bullet(
        position=Vector2(300, 300),
        velocity=Vector2(),
        radius=game_config.bullet.radius,
        lifetime=1.0,
        friendly=True,
    )
    world.bullets.append(bullet)
    world._handle_collisions()

    assert len(world.score_popups) == 1
    assert world.score_popups[0].text == f"+{game_config.scoring['small_asteroid']}"


def test_wave_clear_flag(game_config):
    """Wave completion should use a boolean flag, not floating-point comparison."""
    world = GameWorld(game_config)
    world.asteroids.clear()  # clear all asteroids
    world.wave_clear_pending = True

    # First call should start the timer
    world._check_wave_completion(0.0)
    assert world.wave_clear_timer == 2.0
    assert not world.wave_clear_pending

    # Subsequent calls should count down
    world._check_wave_completion(1.0)
    assert world.wave_clear_timer == 1.0
