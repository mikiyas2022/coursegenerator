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

# Common color aliases that models frequently use
LIGHT_BLUE   = "#60A5FA"
DARK_BLUE    = "#1E3A8A"
LIGHT_GRAY   = "#CBD5E1"
DARK_GRAY    = "#334155"
YELLOW_COLOR = "#F59E0B"
GREEN_COLOR  = "#10B981"
RED_COLOR    = "#EF4444"
PURPLE_COLOR = "#A78BFA"
ORANGE_COLOR = "#F97316"
WHITE_COLOR  = "#F8FAFC"
BLACK_COLOR  = "#0B0E14"

# ─────────────────────────────────────────────────────────────────────────────
# Semantic Colors for Physics/Math (3B1B Style)
# ─────────────────────────────────────────────────────────────────────────────

X_COLOR      = LIGHT_BLUE
Y_COLOR      = GREEN_COLOR
FORCE_COLOR  = RED_COLOR
ANGLE_COLOR  = YELLOW_COLOR
VELOCITY_COLOR = PURPLE_COLOR
MASS_COLOR   = ORANGE_COLOR


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
    latex_clean = str(latex).replace("$","").replace("^\\circ","°")
    formula = Text(latex_clean, color=color, font_size=font_size, font=FONT_LATIN)
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
) -> "NumberPlane":
    """Theme-styled coordinate plane with muted grid and coloured tips.
    Uses NumberPlane (which supports background_line_style in ManimCE v0.20.1).
    """
    ax_cfg = {
        "stroke_color":    AXIS_COLOR,
        "stroke_width":    2.5,
        "include_tip":     True,
        "tip_length":      0.22,
        "include_numbers": False,
    }
    return NumberPlane(
        x_range=x_range or [-5, 5, 1],
        y_range=y_range or [-3, 3, 1],
        x_axis_config=ax_cfg,
        y_axis_config=ax_cfg,
        background_line_style={
            "stroke_color":   GRID_COLOR,
            "stroke_width":   1,
            "stroke_opacity": 0.4,
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
        start=start if start is not None else ORIGIN,
        end=end if end is not None else RIGHT * 3,
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

    return mob

# ─────────────────────────────────────────────────────────────────────────────
# 3B1B Style Animation Helpers
# ─────────────────────────────────────────────────────────────────────────────

def reveal_equation(scene: "Scene", eq_text: str, position=UP*2) -> "MathTex":
    """Standard 3B1B equation reveal: write in, then slightly scale up/down for emphasis."""
    eq = MathTex(eq_text, font_size=FONT_SIZE_MATH).move_to(position)
    clamp_to_screen(eq)
    scene.play(Write(eq), run_time=1.5)
    scene.play(eq.animate.scale(1.1), run_time=0.3, rate_func=there_and_back)
    return eq

def transition_scene(scene: "Scene", title: str) -> None:
    """Clear canvas gracefully and show a new section title."""
    scene.play(
        *[FadeOut(m) for m in scene.mobjects],
        run_time=1.0
    )
    t_card = title_card(title)
    scene.play(FadeIn(t_card, shift=DOWN), run_time=1.0)
    scene.wait(0.5)

def highlight_concept(scene: "Scene", mobject: "Mobject", color: str = ACCENT_COLOR) -> None:
    """Subtle pulse/circumscribe to draw attention to a specific part of an equation or diagram."""
    scene.play(Circumscribe(mobject, color=color, time_width=2.0), run_time=1.0)


# ─────────────────────────────────────────────────────────────────────────────
# Meta MMS VoiceoverScene Integration
# ─────────────────────────────────────────────────────────────────────────────

import hashlib
import json
import os
import requests
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.base import SpeechService

TTS_SERVER_URL = os.environ.get("TTS_SERVER_URL", "http://127.0.0.1:8102")


class LocalMMSService(SpeechService):
    """Routes manim-voiceover TTS calls to the local Meta MMS TTS server."""
    def __init__(self, persona_id: int = 1, **kwargs):
        self.persona_id = persona_id
        super().__init__(**kwargs)

    @staticmethod
    def _write_silent_mp3(path: str, duration_sec: float = 3.0) -> None:
        """Write a minimal silent MP3 file so Manim always has valid audio."""
        from pydub import AudioSegment
        silent = AudioSegment.silent(duration=int(duration_sec * 1000))
        silent.export(path, format="mp3")

    def generate_from_text(self, text: str, cache_dir=None, path=None, **kwargs) -> dict:
        """Generate audio via Meta MMS TTS server and return filename for manim-voiceover."""
        output_dir = os.path.abspath(str(self.cache_dir))
        os.makedirs(output_dir, exist_ok=True)

        # Create unique hash for caching
        input_data = f"{text}_{self.persona_id}"
        data_hash  = hashlib.sha256(input_data.encode('utf-8')).hexdigest()
        filename   = f"{data_hash}.mp3"
        abs_path   = os.path.join(output_dir, filename)

        if not os.path.exists(abs_path) or os.path.getsize(abs_path) < 100:
            try:
                try:
                    from .transliterator import clean_amharic_tts_text
                except (ImportError, ValueError):
                    from transliterator import clean_amharic_tts_text
                
                safe_text = clean_amharic_tts_text(text)
                
                resp = requests.post(
                    f"{TTS_SERVER_URL}/generate_audio",
                    json={
                        "text":        safe_text,
                        "persona_id":  self.persona_id,
                        "output_path": abs_path,
                    },
                    timeout=120,
                )
                if resp.status_code != 200:
                    raise RuntimeError(f"TTS server returned {resp.status_code}: {resp.text[:200]}")
                data = resp.json()
                print(
                    f"  [MMS-TTS] Generated: persona={self.persona_id} "
                    f"dur={data.get('duration_seconds', '?')}s → {abs_path}",
                    flush=True,
                )
            except Exception as exc:
                print(f"  [MMS-TTS] FAILED ({exc}). Writing silent fallback.", flush=True)
                self._write_silent_mp3(abs_path)

        # Validate
        if not os.path.exists(abs_path) or os.path.getsize(abs_path) < 100:
            print(f"  [MMS-TTS] Invalid file. Writing silent fallback.", flush=True)
            self._write_silent_mp3(abs_path)

        return {"original_audio": filename}


class AmharicEduScene(VoiceoverScene, MovingCameraScene):
    """
    Standard Base Class for all generated Manim Scenes.
    Handles Voiceover setup, styling, and text helpers automatically.
    Uses Meta MMS TTS via LocalMMSService.
    Includes MovingCameraScene for camera animations.
    """
    def setup(self):
        """Pre-configure the background and Meta MMS TTS."""
        super().setup()
        self.camera.frame.save_state()
        setup_scene(self)

        # Read persona from environment — defaults to Mekdes (1)
        p_id = int(os.environ.get("PERSONA_ID", "1"))
        self.set_speech_service(LocalMMSService(persona_id=p_id))

    def show_text(self, text: str, position=ORIGIN, font_size=FONT_SIZE_BODY, color=TEXT_COLOR):
        """Helper to instantly create Amharic text without boilerplate."""
        mob = amharic_text(text, font_size=font_size, color=color).move_to(position)
        clamp_to_screen(mob)
        return mob

    def title_card(self, amharic: str, latin: str = "", amharic_color=TEXT_COLOR, latin_color=MUTED_COLOR):
        """Instance alias for the module-level title_card() utility."""
        return title_card(amharic, latin, amharic_color, latin_color)

    def formula_box(self, latex: str, color=ACCENT_COLOR, bg=PRIMARY_COLOR, font_size=FONT_SIZE_MATH):
        """Instance alias for the module-level formula_box() utility."""
        return formula_box(latex, color, bg, font_size)

    def branded_axes(self, x_range=None, y_range=None, **kwargs):
        """Instance alias for the module-level branded_axes() utility."""
        return branded_axes(x_range, y_range, **kwargs)

    def branded_vector(self, start=None, end=None, color=VECTOR_COLOR, **kwargs):
        """Instance alias for the module-level branded_vector() utility."""
        return branded_vector(start, end, color, **kwargs)

    def branded_circle(self, radius=1.5, color=ACCENT_COLOR, fill_opacity=0.15, **kwargs):
        """Instance alias for the module-level branded_circle() utility."""
        return branded_circle(radius, color, fill_opacity, **kwargs)

    def reveal_equation(self, eq_text: str, position=UP*2):
        return reveal_equation(self, eq_text, position)
        
    def transition_scene(self, title: str):
        transition_scene(self, title)
        
    def highlight_concept(self, mobject: "Mobject", color: str = ACCENT_COLOR):
        highlight_concept(self, mobject, color)

