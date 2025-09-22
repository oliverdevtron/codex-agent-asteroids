"""Console entry point for the Asteroids clone."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ is None or __package__ == "":  # pragma: no cover - script execution path
    # Allow running ``python src/asteroids/main.py`` by injecting the package root.
    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from asteroids.config import load_config
    from asteroids.game import AsteroidsGame
else:  # pragma: no cover - normal package import path
    from .config import load_config
    from .game import AsteroidsGame


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Asteroids clone")
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Optional path to a configuration YAML file.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.config) if args.config is not None else load_config()
    game = AsteroidsGame(config)
    game.run()


if __name__ == "__main__":  # pragma: no cover - CLI entry
    main()
