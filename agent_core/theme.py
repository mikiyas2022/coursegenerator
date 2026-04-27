"""
agent_core/theme.py — Backward-compatibility shim.
All canonical definitions live in manim_config/theme.py.
This file simply re-exports everything so old imports keep working.
"""
import sys
import os

# Ensure the agent_core directory is on the path so manim_config can be found
sys.path.insert(0, os.path.dirname(__file__))

from manim_config.theme import *   # noqa: F401, F403
from manim_config.theme import (   # noqa: F401
    AmharicEduScene,
    LocalMMSService,
    setup_scene,
    amharic_text,
    latin_text,
    title_card,
    formula_box,
    section_divider,
    branded_axes,
    branded_vector,
    branded_circle,
    glow_dot,
    GlowDot,
    clamp_to_screen,
    reveal_equation,
    transition_scene,
    highlight_concept,
    playful_bounce,
    morph_shape,
    camera_zoom_to,
    camera_restore,
    number_ticker,
    # Colors
    BG_COLOR, PANEL_COLOR, SURFACE_COLOR,
    TEAL_ACCENT, ACCENT_COLOR, PRIMARY_COLOR, SKY_BLUE,
    STAR_YELLOW, YELLOW_COLOR, WARNING_COLOR,
    TEXT_COLOR, FORMULA_COLOR, MUTED_COLOR,
    ERROR_COLOR, SUCCESS_COLOR, HIGHLIGHT_COLOR, ROSE_COLOR,
    VECTOR_COLOR, FORCE_COLOR, VELOCITY_COLOR, ANGLE_COLOR,
    X_COLOR, Y_COLOR, Z_COLOR, MASS_COLOR,
    GRID_COLOR, AXIS_COLOR,
    LIGHT_BLUE, DARK_BLUE, LIGHT_GRAY, DARK_GRAY,
    GREEN_COLOR, RED_COLOR, PURPLE_COLOR, ORANGE_COLOR, WHITE_COLOR, BLACK_COLOR,
    # Typography
    FONT_AMHARIC, FONT_LATIN, FONT_WEIGHT,
    FONT_SIZE_TITLE, FONT_SIZE_HEADER, FONT_SIZE_BODY,
    FONT_SIZE_LABEL, FONT_SIZE_SMALL, FONT_SIZE_MATH, FONT_SIZE_CAPTION,
    # Layout
    SAFE_TOP, SAFE_BOTTOM, SAFE_LEFT, SAFE_RIGHT, CENTER,
    CANVAS_X_MAX, CANVAS_Y_MAX,
)
