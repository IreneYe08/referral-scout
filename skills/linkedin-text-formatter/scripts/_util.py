#!/usr/bin/env python3
"""Shared helpers for LinkedIn formatter scripts."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path


def skill_scripts_dir() -> Path:
    return Path(__file__).resolve().parent


def repo_root() -> Path:
    """Repository root (parent of scripts/)."""
    return skill_scripts_dir().parent


def resolve_formatter_home() -> Path | None:
    """Find repo root via env var or install marker file."""
    import os

    env = os.environ.get("LINKEDIN_FORMATTER_HOME")
    if env:
        p = Path(env).expanduser()
        if (p / "scripts" / "linkedin_post.py").is_file():
            return p
    marker = Path.home() / ".linkedin-formatter-home"
    if marker.is_file():
        p = Path(marker.read_text(encoding="utf-8").strip()).expanduser()
        if (p / "scripts" / "linkedin_post.py").is_file():
            return p
    for candidate in (
        Path.home() / "linkedin-smart-formatter",
        Path.home() / "Projects" / "linkedin-smart-formatter",
    ):
        if (candidate / "scripts" / "linkedin_post.py").is_file():
            return candidate
    return repo_root() if (repo_root() / "scripts" / "linkedin_post.py").is_file() else None


def formatter_cli() -> Path:
    home = resolve_formatter_home()
    if home:
        return home / "scripts" / "linkedin_post.py"
    return skill_scripts_dir() / "linkedin_post.py"


def ensure_utf8_stdout() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except (AttributeError, OSError, ValueError):
            pass


def write_temp_draft(text: str, name: str = "linkedin-draft.txt") -> Path:
    """Write draft to OS temp dir — avoids Windows shell escaping issues."""
    p = Path(tempfile.gettempdir()) / name
    p.write_text(text, encoding="utf-8")
    return p
