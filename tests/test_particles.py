"""Tests for the particle system."""

import random

from asteroids.particles import Particle, ParticleSystem
from asteroids.utils import Vector2


def test_particle_ages_and_dies():
    p = Particle(
        position=Vector2(0, 0),
        velocity=Vector2(10, 0),
        color=(255, 255, 255),
        lifetime=1.0,
    )
    assert p.alive
    assert p.alpha == 1.0
    p.age = 0.5
    assert p.alive
    assert 0.4 < p.alpha < 0.6
    p.age = 1.0
    assert not p.alive
    assert p.alpha == 0.0


def test_particle_system_update_removes_dead():
    ps = ParticleSystem(max_particles=100)
    ps.emit_explosion(Vector2(50, 50), (255, 0, 0), count=10, rng=random.Random(1))
    assert len(ps.particles) == 10
    # Age all particles past their lifetime
    for p in ps.particles:
        p.age = p.lifetime + 1.0
    ps.update(0.0)
    assert len(ps.particles) == 0


def test_particle_system_max_cap():
    ps = ParticleSystem(max_particles=5)
    ps.emit_explosion(Vector2(0, 0), (255, 0, 0), count=20, rng=random.Random(1))
    assert len(ps.particles) <= 5


def test_emit_thrust():
    ps = ParticleSystem(max_particles=100)
    ps.emit_thrust(
        Vector2(100, 100), 0.0, count=5,
        speed_range=(30.0, 80.0), lifetime_range=(0.2, 0.5),
        rng=random.Random(1),
    )
    assert len(ps.particles) == 5
    # All thrust particles should be alive
    for p in ps.particles:
        assert p.alive


def test_particle_system_clear():
    ps = ParticleSystem(max_particles=100)
    ps.emit_explosion(Vector2(0, 0), (255, 0, 0), count=10, rng=random.Random(1))
    assert len(ps.particles) > 0
    ps.clear()
    assert len(ps.particles) == 0


def test_particle_position_updates():
    ps = ParticleSystem(max_particles=100)
    ps.particles.append(
        Particle(
            position=Vector2(0, 0),
            velocity=Vector2(100, 0),
            color=(255, 255, 255),
            lifetime=2.0,
        )
    )
    ps.update(1.0)
    assert ps.particles[0].position.x > 90.0
    assert ps.particles[0].age == 1.0
