"""
logger.py — Centralized logging for all pipeline agents.

Usage:
    from logger import get_logger
    log = get_logger(__name__)
    log.info("Starting render...")
"""

import logging
import os
from pathlib import Path


def get_logger(name: str) -> logging.Logger:
    """Return a logger that writes to both console and logs/pipeline.log."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger  # Already configured

    logger.setLevel(logging.DEBUG)

    # ── File handler ─────────────────────────────────────────────────────────
    project_root = Path(__file__).parent.parent
    logs_dir = project_root / "logs"
    logs_dir.mkdir(exist_ok=True)

    fh = logging.FileHandler(logs_dir / "pipeline.log", encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))

    # ── Console handler ───────────────────────────────────────────────────────
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter("  [%(name)s] %(message)s"))

    logger.addHandler(fh)
    logger.addHandler(ch)
    logger.propagate = False

    return logger
