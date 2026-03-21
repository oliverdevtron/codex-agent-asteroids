"""Tests for the highscore system."""
import json
import tempfile
from pathlib import Path

from asteroids.highscore import HighscoreEntry, HighscoreManager


def test_empty_highscore():
    """New highscore manager with no file should start empty."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = Path(f.name)
    path.unlink(missing_ok=True)  # ensure file doesn't exist
    mgr = HighscoreManager(file_path=path)
    assert len(mgr.entries) == 0
    assert mgr.qualifies(100)
    path.unlink(missing_ok=True)


def test_add_and_save():
    """Adding entries should persist to file."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = Path(f.name)
    path.unlink(missing_ok=True)

    mgr = HighscoreManager(max_entries=3, file_path=path)
    mgr.add(HighscoreEntry(name="AAA", score=500, wave=3, date="2026-01-01"))
    mgr.add(HighscoreEntry(name="BBB", score=300, wave=2, date="2026-01-02"))
    mgr.add(HighscoreEntry(name="CCC", score=700, wave=5, date="2026-01-03"))

    assert len(mgr.entries) == 3
    assert mgr.entries[0].score == 700  # sorted descending
    assert mgr.entries[0].name == "CCC"

    # Reload from file
    mgr2 = HighscoreManager(max_entries=3, file_path=path)
    assert len(mgr2.entries) == 3
    assert mgr2.entries[0].score == 700

    path.unlink(missing_ok=True)


def test_max_entries_limit():
    """Should keep only top N entries."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = Path(f.name)
    path.unlink(missing_ok=True)

    mgr = HighscoreManager(max_entries=2, file_path=path)
    mgr.add(HighscoreEntry(name="AAA", score=100, wave=1, date="2026-01-01"))
    mgr.add(HighscoreEntry(name="BBB", score=200, wave=2, date="2026-01-02"))
    mgr.add(HighscoreEntry(name="CCC", score=300, wave=3, date="2026-01-03"))

    assert len(mgr.entries) == 2
    assert mgr.entries[0].score == 300
    assert mgr.entries[1].score == 200
    # 100 should have been pruned

    path.unlink(missing_ok=True)


def test_qualifies():
    """qualifies() should check if score beats the lowest entry."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = Path(f.name)
    path.unlink(missing_ok=True)

    mgr = HighscoreManager(max_entries=2, file_path=path)
    mgr.add(HighscoreEntry(name="AAA", score=100, wave=1, date="2026-01-01"))
    mgr.add(HighscoreEntry(name="BBB", score=200, wave=2, date="2026-01-02"))

    assert mgr.qualifies(300)  # beats lowest
    assert mgr.qualifies(150)  # beats lowest
    assert not mgr.qualifies(50)  # doesn't beat lowest
    assert not mgr.qualifies(100)  # tied, doesn't beat

    path.unlink(missing_ok=True)


def test_corrupt_file():
    """Should handle corrupt JSON gracefully."""
    with tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False) as f:
        f.write("not valid json{{{")
        path = Path(f.name)

    mgr = HighscoreManager(file_path=path)
    assert len(mgr.entries) == 0  # graceful fallback

    path.unlink(missing_ok=True)
