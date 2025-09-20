"""Pytest fixtures for the Asteroids project."""
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

try:  # pragma: no cover - optional dependency
    import pygame  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    pygame = None

import pytest

from asteroids.config import Config, load_config


@pytest.fixture(scope="session")
def pygame_setup():
    if pygame is None:
        yield
        return
    pygame.init()
    yield
    pygame.quit()


@pytest.fixture(scope="session")
def game_config(pygame_setup) -> Config:
    return load_config()
