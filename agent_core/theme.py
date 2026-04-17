"""
theme.py — Global Manim Theming & Branding Engine
==================================================
Imported by every generated Manim scene for a consistent visual language.

Usage in generated code:
    from theme import (
        setup_scene, amharic_text, accent_formula, branded_axes,
        BG_COLOR, PRIMARY_COLOR, ACCENT_COLOR, FORMULA_COLOR, ...
    )
"""

from manim import *

# ─────────────────────────────────────────────────────────────────────────────
# Color Palette
# ─────────────────────────────────────────────────────────────────────────────

BG_COLOR         = "#0B0E14"   # Deep-space background (main)
PANEL_COLOR      = "#0F172A"   # Secondary panels / sidebars
PRIMARY_COLOR    = "#1E3A8A"   # Deep educational blue (banners, rectangles)
ACCENT_COLOR     = "#10B981"   # Emerald — highlights, correct answers
FORMULA_COLOR    = "#E2E8F0"   # Light slate — LaTeX formulas
TEXT_COLOR       = "#F8FAFC"   # Near-white — primary narration text
MUTED_COLOR      = "#64748B"   # Slate — labels, secondary annotations
WARNING_COLOR    = "#F59E0B"   # Amber — important concepts, cautions
ERROR_COLOR      = "#EF4444"   # Red — corrections, negatives
GRID_COLOR       = "#1E293B"   # Subtle grid lines
AXIS_COLOR       = "#334155"   # Coordinate axis strokes
VECTOR_COLOR     = "#60A5FA"   # Blue-300 — vectors, arrows
HIGHLIGHT_COLOR  = "#A78BFA"   # Violet-400 — secondary highlights / paths

# ─────────────────────────────────────────────────────────────────────────────
# Typography
# ─────────────────────────────────────────────────────────────────────────────

FONT_AMHARIC   = "Nyala"        # Ge'ez script — required for Amharic
FONT_LATIN     = "Inter"        # English / Latin labels
FONT_WEIGHT    = BOLD

FONT_SIZE_TITLE  = 64
FONT_SIZE_HEADER = 52
FONT_SIZE_BODY   = 42
FONT_SIZE_LABEL  = 32
FONT_SIZE_SMALL  = 24
FONT_SIZE_MATH   = 52

# ─────────────────────────────────────────────────────────────────────────────
# Layout Constants (16:9 safe zone — keep objects inside these bounds)
# ─────────────────────────────────────────────────────────────────────────────

SAFE_TOP    =  3.4    # Max UP for text to stay on-screen
SAFE_BOTTOM = -3.4    # Max DOWN
SAFE_LEFT   = -6.8    # Max LEFT
SAFE_RIGHT  =  6.8    # Max RIGHT
CENTER      = ORIGIN

# ─────────────────────────────────────────────────────────────────────────────
# Utility: Scene Setup
# ─────────────────────────────────────────────────────────────────────────────

def setup_scene(scene: "Scene") -> None:
    """
    Apply the standard STEM Studio theme to any Scene / VoiceoverScene.
    Call once at the start of construct().
    """
    scene.camera.background_color = BG_COLOR
    Text.set_default(font=FONT_LATIN, weight=BOLD)
    MathTex.set_default(font_size=FONT_SIZE_MATH, color=FORMULA_COLOR)


# ─────────────────────────────────────────────────────────────────────────────
# Utility: Text Factories
# ─────────────────────────────────────────────────────────────────────────────

def amharic_text(
    text: str,
    font_size: int = FONT_SIZE_BODY,
    color: str = TEXT_COLOR,
    **kwargs,
) -> "Text":
    """Render Amharic Ge'ez script with the theme Nyala font."""
    return Text(text, font=FONT_AMHARIC, font_size=font_size, color=color, **kwargs)


def latin_text(
    text: str,
    font_size: int = FONT_SIZE_BODY,
    color: str = TEXT_COLOR,
    **kwargs,
) -> "Text":
    """Render Latin / English text with the theme Inter font."""
    return Text(text, font=FONT_LATIN, font_size=font_size, color=color, weight=BOLD, **kwargs)


def title_card(
    amharic: str,
    latin: str = "",
    amharic_color: str = TEXT_COLOR,
    latin_color: str = MUTED_COLOR,
) -> "VGroup":
    """
    Create a two-line title: large Amharic heading + small Latin subtitle.
    Returns a VGroup positioned at the top of the safe zone.
    """
    am = amharic_text(amharic, font_size=FONT_SIZE_HEADER, color=amharic_color)
    group = VGroup(am)
    if latin:
        la = latin_text(latin, font_size=FONT_SIZE_LABEL, color=latin_color)
        la.next_to(am, DOWN, buff=0.3)
        group.add(la)
    group.move_to(UP * 2.8)
    return group


def formula_box(
    latex: str,
    color: str = ACCENT_COLOR,
    bg: str = PRIMARY_COLOR,
    font_size: int = FONT_SIZE_MATH,
) -> "VGroup":
    """
    Boxed LaTeX formula with a coloured background rectangle.
    Returns a VGroup(rect, formula).
    """
    formula = MathTex(latex, color=color, font_size=font_size)
    rect = SurroundingRectangle(
        formula,
        color=color,
        fill_color=bg,
        fill_opacity=0.25,
        buff=0.3,
    )
    return VGroup(rect, formula)


def section_divider(color: str = PRIMARY_COLOR) -> "Line":
    """Horizontal divider line for separating sections of a scene."""
    return Line(
        start=LEFT * 6,
        end=RIGHT * 6,
        stroke_color=color,
        stroke_width=2,
        stroke_opacity=0.4,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Utility: Geometry Factories
# ─────────────────────────────────────────────────────────────────────────────

def branded_axes(
    x_range: list | None = None,
    y_range: list | None = None,
    **kwargs,
) -> "Axes":
    """Theme-styled Axes with muted grid and coloured tips."""
    return Axes(
        x_range=x_range or [-5, 5, 1],
        y_range=y_range or [-3, 3, 1],
        axis_config={
            "stroke_color":  AXIS_COLOR,
            "stroke_width":  2.5,
            "include_tip":   True,
            "tip_length":    0.22,
            "include_numbers": False,
        },
        background_line_style={
            "stroke_color":   GRID_COLOR,
            "stroke_width":   1,
            "stroke_opacity": 0.5,
        },
        **kwargs,
    )


def branded_vector(
    start: list | None = None,
    end: list | None = None,
    color: str = VECTOR_COLOR,
    **kwargs,
) -> "Arrow":
    """A thick, tip-capped arrow in the theme VECTOR_COLOR."""
    return Arrow(
        start=start or ORIGIN,
        end=end or RIGHT * 3,
        buff=0,
        color=color,
        stroke_width=7,
        max_tip_length_to_length_ratio=0.12,
        **kwargs,
    )


def branded_circle(
    radius: float = 1.5,
    color: str = ACCENT_COLOR,
    fill_opacity: float = 0.15,
    **kwargs,
) -> "Circle":
    """A theme-styled circle."""
    return Circle(
        radius=radius,
        color=color,
        fill_color=color,
        fill_opacity=fill_opacity,
        stroke_width=3,
        **kwargs,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Utility: Safe Positioning
# ─────────────────────────────────────────────────────────────────────────────

def clamp_to_screen(mob: "Mobject", margin: float = 0.3) -> "Mobject":
    """
    Move a Mobject back onto the 16:9 safe zone if it has drifted off-screen.
    Returns the (possibly repositioned) Mobject for chaining.
    """
    x, y, _ = mob.get_center()
    w, h     = mob.width, mob.height

    new_x = max(SAFE_LEFT  + w / 2 + margin, min(SAFE_RIGHT  - w / 2 - margin, x))
    new_y = max(SAFE_BOTTOM + h / 2 + margin, min(SAFE_TOP   - h / 2 - margin, y))

    if abs(new_x - x) > 0.01 or abs(new_y - y) > 0.01:
        mob.move_to([new_x, new_y, 0])

    return mob


# ─────────────────────────────────────────────────────────────────────────────
# Objective 2: Base Class Inheritance
# ─────────────────────────────────────────────────────────────────────────────

import hashlib
import requests
import os
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.base import SpeechService

class LocalMMSService(SpeechService):
    """Routes manim-voiceover TTS calls to the local Meta MMS server."""
    def __init__(self, persona_id: int = 1, **kwargs):
        self.persona_id = persona_id
        super().__init__(**kwargs)

    def generate_from_text(self, text: str, cache_dir=None, path=None, **kwargs) -> dict:
        if cache_dir is None:
            cache_dir = self.cache_dir or "/tmp/stem_tts_output"
        os.makedirs(cache_dir, exist_ok=True)
        data_hash = hashlib.sha256((text + str(self.persona_id)).encode()).hexdigest()
        if path is None:
            path = os.path.join(cache_dir, f"{data_hash}.wav")
        if not os.path.exists(path):
            resp = requests.post(
                "http://127.0.0.1:8100/generate_audio",
                json={"text": text, "persona_id": self.persona_id, "output_path": path},
                timeout=180,
            )
            resp.raise_for_status()
            path = resp.json().get("output_path", path)
        return {"original_audio": path}


class AmharicEduScene(VoiceoverScene):
    """
    Standard Base Class for all generated Manim Scenes.
    Handles Voiceover setup, styling, and text helpers automatically.
    """
    def setup(self):
        """Pre-configure the 3Blue1Brown background and local Amharic TTS."""
        super().setup()
        setup_scene(self)
        
        # Read from environment to keep LLM code perfectly clean
        p_id = int(os.environ.get("PERSONA_ID", "1"))
        self.set_speech_service(LocalMMSService(persona_id=p_id))

    def show_text(self, text: str, position=ORIGIN, font_size=FONT_SIZE_BODY, color=TEXT_COLOR):
        """Helper to instantly draw Amharic text without boilerplate."""
        mob = amharic_text(text, font_size=font_size, color=color).move_to(position)
        clamp_to_screen(mob)
        return mob
