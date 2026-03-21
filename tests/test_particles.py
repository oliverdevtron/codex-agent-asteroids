"""Tests for the particle system."""
import random

from asteroids.particles import Particle, ParticleSystem
from asteroids.utils import Vector2


def test_particle_lifecycle():
    """Particles should age and become dead after their lifetime."""
    p = Particle(
        position=Vector2(100, 100),
        velocity=Vector2(10, 0),
        color=(255, 255, 255),
        lifetime=1.0,
        age=0.0,
        size=2.0,
    )
    assert p.alive
    assert p.alpha == 1.0

    # Halfway through
    p.age = 0.5
    assert p.alive
    assert abs(p.alpha - 0.5) < 0.01

    # Expired
    p.age = 1.0
    assert not p.alive
    assert p.alpha == 0.0


def test_particle_system_update():
    """ParticleSystem should remove dead particles on update."""
    ps = ParticleSystem(max_particles=100)
    rng = random.Random(42)
    ps.emit_explosion(Vector2(50, 50), (255, 255, 255), count=10, rng=rng)
    assert len(ps.particles) == 10

    # Age them past their lifetime
    for p in ps.particles:
        p.age = p.lifetime + 0.1

    ps.update(0.016)
    assert len(ps.particles) == 0


def test_particle_system_max_cap():
    """emit_explosion should not exceed max_particles."""
    ps = ParticleSystem(max_particles=5)
    rng = random.Random(42)
    ps.emit_explosion(Vector2(0, 0), (255, 0, 0), count=20, rng=rng)
    assert len(ps.particles) <= 5


def test_emit_thrust():
    """emit_thrust should add a single particle."""
    ps = ParticleSystem(max_particles=100)
    rng = random.Random(42)
    ps.emit_thrust(Vector2(100, 100), ship_angle=90.0, rng=rng)
    assert len(ps.particles) == 1


def test_particle_movement():
    """Particles should move based on velocity."""
    ps = ParticleSystem()
    ps.particles.append(
        Particle(
            position=Vector2(0, 0),
            velocity=Vector2(100, 0),
            color=(255, 255, 255),
            lifetime=2.0,
            age=0.0,
            size=1.0,
        )
    )
    ps.update(1.0)
    assert abs(ps.particles[0].position.x - 100.0) < 0.01


def test_clear():
    """clear() should remove all particles."""
    ps = ParticleSystem()
    rng = random.Random(42)
    ps.emit_explosion(Vector2(0, 0), (255, 0, 0), count=10, rng=rng)
    assert len(ps.particles) > 0
    ps.clear()
    assert len(ps.particles) == 0
