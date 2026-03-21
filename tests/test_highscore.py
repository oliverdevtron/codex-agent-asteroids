"""Tests for the highscore system."""

import json
import tempfile
from pathlib import Path

from asteroids.highscore import HighscoreManager


def test_add_and_persist():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
        f.write("[]")
        path = Path(f.name)
    try:
        mgr = HighscoreManager(max_entries=5, file_path=path)
        mgr.add("ACE", 5000, 3)
        mgr.add("BOB", 3000, 2)
        assert len(mgr.entries) == 2
        assert mgr.entries[0].score == 5000
        # Reload from disk
        mgr2 = HighscoreManager(max_entries=5, file_path=path)
        assert len(mgr2.entries) == 2
        assert mgr2.entries[0].name == "ACE"
    finally:
        path.unlink(missing_ok=True)


def test_qualifies():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
        f.write("[]")
        path = Path(f.name)
    try:
        mgr = HighscoreManager(max_entries=2, file_path=path)
        assert mgr.qualifies(100)
        mgr.add("AAA", 500, 1)
        mgr.add("BBB", 300, 1)
        assert not mgr.qualifies(200)
        assert mgr.qualifies(600)
        assert not mgr.qualifies(0)
    finally:
        path.unlink(missing_ok=True)


def test_max_entries_enforced():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
        f.write("[]")
        path = Path(f.name)
    try:
        mgr = HighscoreManager(max_entries=3, file_path=path)
        for i in range(10):
            mgr.add("TST", (i + 1) * 100, 1)
        assert len(mgr.entries) == 3
        assert mgr.entries[0].score == 1000
        assert mgr.entries[-1].score == 800
    finally:
        path.unlink(missing_ok=True)


def test_load_missing_file():
    path = Path("/tmp/nonexistent_test_scores.json")
    path.unlink(missing_ok=True)
    mgr = HighscoreManager(max_entries=10, file_path=path)
    assert len(mgr.entries) == 0


def test_load_corrupt_file():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
        f.write("not valid json")
        path = Path(f.name)
    try:
        mgr = HighscoreManager(max_entries=10, file_path=path)
        assert len(mgr.entries) == 0
    finally:
        path.unlink(missing_ok=True)


def test_name_truncated_to_three():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
        f.write("[]")
        path = Path(f.name)
    try:
        mgr = HighscoreManager(max_entries=10, file_path=path)
        mgr.add("LONGNAME", 100, 1)
        assert mgr.entries[0].name == "LON"
    finally:
        path.unlink(missing_ok=True)
