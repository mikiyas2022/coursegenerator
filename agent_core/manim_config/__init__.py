"""
manim_config/__init__.py
Re-exports everything from theme.py so `from manim_config.theme import *` works.
"""
from .theme import *   # noqa: F401, F403
