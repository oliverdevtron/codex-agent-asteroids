"""Local highscore persistence (top-10, JSON file)."""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional


DEFAULT_HIGHSCORE_PATH = Path.home() / ".asteroids_scores.json"
MAX_ENTRIES = 10
NAME_LENGTH = 3


@dataclass(slots=True)
class HighscoreEntry:
    name: str
    score: int
    wave: int
    date: str  # ISO-format date string


class HighscoreManager:
    """Manages a top-N local highscore table."""

    def __init__(
        self,
        max_entries: int = MAX_ENTRIES,
        name_length: int = NAME_LENGTH,
        file_path: Optional[Path] = None,
    ) -> None:
        self.max_entries = max_entries
        self.name_length = name_length
        self.file_path = file_path or DEFAULT_HIGHSCORE_PATH
        self.entries: List[HighscoreEntry] = []
        self.load()

    def load(self) -> None:
        try:
            with self.file_path.open("r", encoding="utf-8") as fh:
                raw = json.load(fh)
            self.entries = [
                HighscoreEntry(
                    name=str(e.get("name", "???"))[:self.name_length],
                    score=int(e.get("score", 0)),
                    wave=int(e.get("wave", 1)),
                    date=str(e.get("date", "")),
                )
                for e in raw
            ]
            self.entries.sort(key=lambda e: e.score, reverse=True)
            self.entries = self.entries[: self.max_entries]
        except (FileNotFoundError, json.JSONDecodeError, TypeError, ValueError):
            self.entries = []

    def save(self) -> None:
        try:
            with self.file_path.open("w", encoding="utf-8") as fh:
                json.dump([asdict(e) for e in self.entries], fh, indent=2)
        except OSError:
            pass  # silently fail on write errors

    def qualifies(self, score: int) -> bool:
        if len(self.entries) < self.max_entries:
            return score > 0
        return score > self.entries[-1].score

    def add(self, entry: HighscoreEntry) -> int:
        """Add an entry and return its rank (0-based). Saves automatically."""
        self.entries.append(entry)
        self.entries.sort(key=lambda e: e.score, reverse=True)
        self.entries = self.entries[: self.max_entries]
        self.save()
        for i, e in enumerate(self.entries):
            if e is entry:
                return i
        return -1


__all__ = ["HighscoreEntry", "HighscoreManager"]
