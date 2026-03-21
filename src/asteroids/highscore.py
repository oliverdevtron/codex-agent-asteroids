"""Local highscore persistence (JSON, top-10, arcade-style name entry)."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import List, Optional


DEFAULT_SCORE_FILE = Path.home() / ".asteroids_scores.json"


@dataclass
class Highscore:
    name: str
    score: int
    wave: int
    date: str  # ISO format string


class HighscoreManager:
    """Manage a top-N leaderboard persisted to a JSON file."""

    def __init__(self, max_entries: int = 10, file_path: Optional[Path] = None) -> None:
        self.max_entries = max_entries
        self.file_path = file_path or DEFAULT_SCORE_FILE
        self.entries: List[Highscore] = []
        self.load()

    def load(self) -> None:
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.entries = [
                Highscore(
                    name=str(e.get("name", "???")),
                    score=int(e.get("score", 0)),
                    wave=int(e.get("wave", 1)),
                    date=str(e.get("date", "")),
                )
                for e in data
            ]
            self.entries.sort(key=lambda h: h.score, reverse=True)
            self.entries = self.entries[: self.max_entries]
        except (FileNotFoundError, json.JSONDecodeError, TypeError, KeyError):
            self.entries = []

    def save(self) -> None:
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump([asdict(e) for e in self.entries], f, indent=2)
        except OSError:
            pass  # silently fail if we can't write

    def qualifies(self, score: int) -> bool:
        """Check if a score qualifies for the leaderboard."""
        if score <= 0:
            return False
        if len(self.entries) < self.max_entries:
            return True
        return score > self.entries[-1].score

    def add(self, name: str, score: int, wave: int) -> None:
        entry = Highscore(
            name=name[:3].upper(),
            score=score,
            wave=wave,
            date=date.today().isoformat(),
        )
        self.entries.append(entry)
        self.entries.sort(key=lambda h: h.score, reverse=True)
        self.entries = self.entries[: self.max_entries]
        self.save()


__all__ = ["Highscore", "HighscoreManager"]
