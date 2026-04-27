"""
manim_config/theme.py — 3B1B-Quality Global Manim Theming Engine (v4)
=======================================================================
Grant Sanderson–inspired visual system for every generated scene.

Imported in every scene header:
    from manim_config.theme import *

Features:
  • True 3B1B color palette (deep navy, teal, gold, rose, violet)
  • Typography (Nyala for Amharic, Inter for Latin)
  • Rich animation helpers: morph, bounce, camera pan, playful reveal
  • Safe-zone enforcement for 16:9 canvas
"""

from manim import *

# ─────────────────────────────────────────────────────────────────────────────
# 3B1B Color Palette (dark-navy base, teal accents, golden highlights)
# ─────────────────────────────────────────────────────────────────────────────

# Background layers
BG_COLOR         = "#1C1C2E"   # Deep navy — true 3B1B background
PANEL_COLOR      = "#16213E"   # Slightly lighter panel
SURFACE_COLOR    = "#0F3460"   # Card / box surfaces

# Primary accents (signature 3B1B teal & blue)
TEAL_ACCENT      = "#3DCCC7"   # Signature 3B1B teal  ← NEW
ACCENT_COLOR     = TEAL_ACCENT  # alias
PRIMARY_COLOR    = "#1E3A8A"   # Deep educational blue (banners)
SKY_BLUE         = "#87CEEB"   # Sky blue for lighter elements

# Highlight colors
STAR_YELLOW      = "#FFD700"   # Bright gold — 3B1B "aha!" moments  ← NEW
YELLOW_COLOR     = STAR_YELLOW  # alias
WARNING_COLOR    = "#F59E0B"   # Amber — caution / important

# Text
TEXT_COLOR       = "#FFFEF0"   # Warm near-white (not cold blue-white)
FORMULA_COLOR    = "#E8F4FD"   # Formula text
MUTED_COLOR      = "#8892B0"   # Muted labels / secondary

# Semantic colors
ERROR_COLOR      = "#FF6B6B"   # Warm red — corrections
SUCCESS_COLOR    = "#4ECDC4"   # Teal-green — correct / positive
HIGHLIGHT_COLOR  = "#C792EA"   # Purple — paths, secondary highlights
ROSE_COLOR       = "#FF8FAB"   # Soft rose — curiosity beats

# Geometry semantics (physics / math)
VECTOR_COLOR     = "#61AFEF"   # Blue-300 — vectors, arrows
FORCE_COLOR      = "#E06C75"   # Soft red — force arrows
VELOCITY_COLOR   = "#C792EA"   # Purple — velocity vectors
ANGLE_COLOR      = STAR_YELLOW  # Gold — angles, arcs
X_COLOR          = "#61AFEF"   # x-axis
Y_COLOR          = "#98C379"   # y-axis
Z_COLOR          = "#E5C07B"   # z-axis
MASS_COLOR       = "#F97316"   # Orange — mass

# Grid / axis infrastructure
GRID_COLOR       = "#2D2D4E"   # Very subtle grid
AXIS_COLOR       = "#4A4A7A"   # Coordinate axes

# Convenience aliases
LIGHT_BLUE   = "#61AFEF"
DARK_BLUE    = "#1E3A8A"
LIGHT_GRAY   = "#ABB2BF"
DARK_GRAY    = "#3E4451"
GREEN_COLOR  = "#98C379"
RED_COLOR    = "#E06C75"
PURPLE_COLOR = "#C792EA"
ORANGE_COLOR = "#F97316"
WHITE_COLOR  = "#FFFEF0"
BLACK_COLOR  = "#1C1C2E"

# ─────────────────────────────────────────────────────────────────────────────
# Typography
# ─────────────────────────────────────────────────────────────────────────────

FONT_AMHARIC = "Nyala"    # Ge'ez script — required for Amharic
FONT_LATIN   = "Inter"    # English / Latin labels (fallback: sans-serif)
FONT_WEIGHT  = BOLD

FONT_SIZE_TITLE  = 68
FONT_SIZE_HEADER = 54
FONT_SIZE_BODY   = 44
FONT_SIZE_LABEL  = 34
FONT_SIZE_SMALL  = 26
FONT_SIZE_MATH   = 52
FONT_SIZE_CAPTION = 22

# ─────────────────────────────────────────────────────────────────────────────
# Layout Constants — 16:9 safe zone
# ─────────────────────────────────────────────────────────────────────────────

SAFE_TOP    =  3.4
SAFE_BOTTOM = -3.4
SAFE_LEFT   = -6.8
SAFE_RIGHT  =  6.8
CENTER      = ORIGIN

# Canvas limits for generated code
CANVAS_X_MAX = 5.5
CANVAS_Y_MAX = 3.0


# ─────────────────────────────────────────────────────────────────────────────
# Scene Setup
# ─────────────────────────────────────────────────────────────────────────────

def setup_scene(scene: "Scene") -> None:
    """
    Apply 3B1B theme to any Scene / VoiceoverScene.
    Call once at the very start of construct().
    """
    scene.camera.background_color = BG_COLOR
    Text.set_default(font=FONT_LATIN, weight=BOLD)


# ─────────────────────────────────────────────────────────────────────────────
# Text Factories
# ─────────────────────────────────────────────────────────────────────────────

def amharic_text(
    text: str,
    font_size: int = FONT_SIZE_BODY,
    color: str = TEXT_COLOR,
    **kwargs,
) -> "Text":
    """Render Amharic Ge'ez script with the Nyala font."""
    return Text(text, font=FONT_AMHARIC, font_size=font_size, color=color, **kwargs)


def latin_text(
    text: str,
    font_size: int = FONT_SIZE_BODY,
    color: str = TEXT_COLOR,
    **kwargs,
) -> "Text":
    """Render Latin / English text with the Inter font."""
    return Text(text, font=FONT_LATIN, font_size=font_size, color=color, weight=BOLD, **kwargs)


def title_card(
    amharic: str,
    latin: str = "",
    amharic_color: str = TEXT_COLOR,
    latin_color: str = MUTED_COLOR,
) -> "VGroup":
    """
    Two-line title: large Amharic heading + small Latin subtitle.
    Positioned at top of safe zone.
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
    color: str = TEAL_ACCENT,
    bg: str = SURFACE_COLOR,
    font_size: int = FONT_SIZE_MATH,
) -> "VGroup":
    """
    Boxed formula text with a teal-bordered background rectangle.
    Returns VGroup(rect, formula).
    """
    latex_clean = str(latex).replace("$", "").replace("^\\circ", "°")
    formula = Text(latex_clean, color=color, font_size=font_size, font=FONT_LATIN)
    rect = SurroundingRectangle(
        formula,
        color=color,
        fill_color=bg,
        fill_opacity=0.30,
        buff=0.3,
        corner_radius=0.1,
    )
    return VGroup(rect, formula)


def section_divider(color: str = TEAL_ACCENT) -> "Line":
    """Horizontal divider line, teal-colored."""
    return Line(
        start=LEFT * 6,
        end=RIGHT * 6,
        stroke_color=color,
        stroke_width=2,
        stroke_opacity=0.5,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Geometry Factories (all 3B1B-styled)
# ─────────────────────────────────────────────────────────────────────────────

def branded_axes(
    x_range: list | None = None,
    y_range: list | None = None,
    **kwargs,
) -> "NumberPlane":
    """
    Theme-styled coordinate plane: dark grid, teal axis tips.
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
            "stroke_opacity": 0.35,
        },
        **kwargs,
    )


def branded_vector(
    start: list | None = None,
    end: list | None = None,
    color: str = VECTOR_COLOR,
    **kwargs,
) -> "Arrow":
    """Thick, tip-capped arrow in the theme VECTOR_COLOR."""
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
    color: str = TEAL_ACCENT,
    fill_opacity: float = 0.15,
    **kwargs,
) -> "Circle":
    """Theme-styled circle with teal glow."""
    return Circle(
        radius=radius,
        color=color,
        fill_color=color,
        fill_opacity=fill_opacity,
        stroke_width=3,
        **kwargs,
    )


def glow_dot(
    point=None,
    color: str = STAR_YELLOW,
    radius: float = 0.12,
    **kwargs,           # absorb any LLM-hallucinated args (glow_factor, etc.)
) -> "Dot":
    """Bright glowing dot — used as 'aha!' marker."""
    import numpy as np
    if point is None:
        _pt = ORIGIN
    else:
        try:
            _pt = np.array(point, dtype=float)
        except Exception:
            _pt = ORIGIN
    d = Dot(
        point=_pt,
        radius=radius,
        color=color,
        fill_opacity=1.0,
    )
    d.set_stroke(color=color, width=4, opacity=0.5)
    return d

# Alias — LLM hallucinates GlowDot instead of glow_dot
GlowDot = glow_dot


# ─────────────────────────────────────────────────────────────────────────────
# 3B1B Animation Helpers
# ─────────────────────────────────────────────────────────────────────────────

def reveal_equation(scene: "Scene", eq_text: str, position=UP * 2) -> "Text":
    """Standard 3B1B equation reveal: Write → subtle scale pulse."""
    eq = Text(eq_text, color=FORMULA_COLOR, font_size=FONT_SIZE_MATH, font=FONT_LATIN)
    eq.move_to(position)
    clamp_to_screen(eq)
    scene.play(Write(eq), run_time=1.5)
    scene.play(eq.animate.scale(1.08), run_time=0.25, rate_func=there_and_back)
    return eq


def transition_scene(scene: "Scene", title: str) -> None:
    """Graceful clear + new section title card."""
    if scene.mobjects:
        scene.play(*[FadeOut(m) for m in scene.mobjects], run_time=0.8)
    t_card = title_card(title)
    scene.play(FadeIn(t_card, shift=DOWN * 0.3), run_time=0.7)
    scene.wait(0.4)


def highlight_concept(scene: "Scene", mobject: "Mobject", color: str = TEAL_ACCENT) -> None:
    """Teal circumscribe to draw attention to key element."""
    scene.play(Circumscribe(mobject, color=color, time_width=2.0), run_time=1.0)


def playful_bounce(scene: "Scene", mobject: "Mobject", n: int = 2) -> None:
    """
    Quick UP-DOWN bounce animation — adds humor and life.
    Great for 'aha' moments or humorous reveals.
    """
    for _ in range(n):
        scene.play(mobject.animate.shift(UP * 0.25), run_time=0.15, rate_func=rush_into)
        scene.play(mobject.animate.shift(DOWN * 0.25), run_time=0.15, rate_func=rush_from)


def morph_shape(
    scene: "Scene",
    source: "Mobject",
    target: "Mobject",
    run_time: float = 1.2,
) -> None:
    """
    Signature 3B1B shape morph: ReplacementTransform with spring rate_func.
    Use this for concept transitions: circle → square, vector → formula, etc.
    """
    scene.play(
        ReplacementTransform(source, target),
        run_time=run_time,
        rate_func=smooth,
    )


def camera_zoom_to(
    scene: "MovingCameraScene",
    target: "Mobject",
    zoom: float = 1.5,
    run_time: float = 1.0,
) -> None:
    """
    Signature 3B1B camera zoom-in on a specific element.
    ONLY call this inside MovingCameraScene subclasses.
    """
    scene.play(
        scene.camera.frame.animate.set(width=target.width * zoom),
        scene.camera.frame.animate.move_to(target.get_center()),
        run_time=run_time,
        rate_func=smooth,
    )


def camera_restore(scene: "MovingCameraScene", run_time: float = 0.8) -> None:
    """Restore camera to default frame — call after camera_zoom_to."""
    scene.play(scene.camera.frame.animate.to_default_state(), run_time=run_time)


def number_ticker(
    scene: "Scene",
    start: float,
    end: float,
    run_time: float = 1.5,
    position=ORIGIN,
    color: str = STAR_YELLOW,
    fmt: str = "{:.1f}",
) -> "DecimalNumber":
    """
    Animated number counter — runs from `start` to `end`.
    Returns the final DecimalNumber mobject (still on screen).
    """
    tracker = ValueTracker(start)
    num = always_redraw(lambda: DecimalNumber(
        tracker.get_value(),
        num_decimal_places=1,
        color=color,
        font_size=FONT_SIZE_HEADER,
    ).move_to(position))
    scene.add(num)
    scene.play(tracker.animate.set_value(end), run_time=run_time, rate_func=smooth)
    return num


def clamp_to_screen(mob: "Mobject", margin: float = 0.3) -> "Mobject":
    """
    Move a Mobject back onto the 16:9 safe zone if it has drifted off-screen.
    Returns the (possibly repositioned) Mobject for chaining.
    """
    x, y, _ = mob.get_center()
    w, h = mob.width, mob.height
    new_x = max(SAFE_LEFT + w / 2 + margin, min(SAFE_RIGHT - w / 2 - margin, x))
    new_y = max(SAFE_BOTTOM + h / 2 + margin, min(SAFE_TOP - h / 2 - margin, y))
    if (new_x, new_y) != (x, y):
        mob.move_to([new_x, new_y, 0])
    return mob


# ─────────────────────────────────────────────────────────────────────────────
# TTS / Voiceover Integration — EdgeTTS English (crystal-clear neural voice)
# ─────────────────────────────────────────────────────────────────────────────

import asyncio
import hashlib
import os
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.base import SpeechService

# Default Amharic voice for 3B1B mode
EDGE_TTS_VOICE = os.environ.get("EDGE_TTS_VOICE", "am-ET-MekdesNeural")


class EdgeTTSAmharicService(SpeechService):
    """
    High-quality English TTS via Microsoft Edge neural voices.
    Free, open-source (edge-tts), zero API key required.
    Voices: en-US-GuyNeural (warm male), en-US-AriaNeural (female)
    """

    def __init__(self, voice: str = EDGE_TTS_VOICE, **kwargs):
        self.voice = voice
        super().__init__(**kwargs)

    @staticmethod
    def _write_silent_mp3(path: str, duration_sec: float = 3.0) -> None:
        """Write a minimal silent MP3 so Manim always has valid audio."""
        try:
            from pydub import AudioSegment
            silent = AudioSegment.silent(duration=int(duration_sec * 1000))
            silent.export(path, format="mp3")
        except Exception:
            with open(path, "wb") as f:
                f.write(b"\xff\xfb\x90\x00" * 4000)

    def generate_from_text(self, text: str, cache_dir=None, path=None, **kwargs) -> dict:
        """Generate audio via edge-tts and return filename for manim-voiceover."""
        output_dir = os.path.abspath(str(self.cache_dir))
        os.makedirs(output_dir, exist_ok=True)

        input_data = f"{text}_{self.voice}"
        data_hash = hashlib.sha256(input_data.encode("utf-8")).hexdigest()
        filename = f"{data_hash}.mp3"
        abs_path = os.path.join(output_dir, filename)

        if not os.path.exists(abs_path) or os.path.getsize(abs_path) < 100:
            try:
                import edge_tts

                async def _synthesize():
                    communicate = edge_tts.Communicate(text, self.voice)
                    await communicate.save(abs_path)

                # Run async edge-tts in sync context
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        import concurrent.futures
                        with concurrent.futures.ThreadPoolExecutor() as pool:
                            pool.submit(lambda: asyncio.run(_synthesize())).result(timeout=60)
                    else:
                        loop.run_until_complete(_synthesize())
                except RuntimeError:
                    asyncio.run(_synthesize())

                if os.path.exists(abs_path) and os.path.getsize(abs_path) > 100:
                    print(
                        f"  [EdgeTTS] Generated: voice={self.voice} → {abs_path}",
                        flush=True,
                    )
                else:
                    raise RuntimeError("EdgeTTS produced empty file")

            except Exception as exc:
                print(f"  [EdgeTTS] FAILED ({exc}). Writing silent fallback.", flush=True)
                self._write_silent_mp3(abs_path)

        if not os.path.exists(abs_path) or os.path.getsize(abs_path) < 100:
            print("  [EdgeTTS] Invalid file — silent fallback.", flush=True)
            self._write_silent_mp3(abs_path)

        return {"original_audio": filename}


# Keep backward compat alias
LocalMMSService = EdgeTTSAmharicService


# ─────────────────────────────────────────────────────────────────────────────
# Base Scene Class
# ─────────────────────────────────────────────────────────────────────────────

class AmharicEduScene(VoiceoverScene, MovingCameraScene):
    """
    Standard base class for all generated Manim scenes.
    Uses EdgeTTS English neural voice for crystal-clear narration.
    """

    def setup(self):
        super().setup()
        self.camera.frame.save_state()
        setup_scene(self)
        voice = os.environ.get("EDGE_TTS_VOICE", EDGE_TTS_VOICE)
        self.set_speech_service(EdgeTTSAmharicService(voice=voice))

    # ── Text helpers ──────────────────────────────────────────────────────────
    def show_text(self, text: str, position=ORIGIN, font_size=FONT_SIZE_BODY, color=TEXT_COLOR):
        mob = amharic_text(text, font_size=font_size, color=color).move_to(position)
        clamp_to_screen(mob)
        return mob

    # ── Instance aliases for all module-level helpers ─────────────────────────
    def title_card(self, am: str, la: str = "", am_color=TEXT_COLOR, la_color=MUTED_COLOR):
        return title_card(am, la, am_color, la_color)

    def formula_box(self, latex: str, color=TEAL_ACCENT, bg=SURFACE_COLOR, font_size=FONT_SIZE_MATH):
        return formula_box(latex, color, bg, font_size)

    def branded_axes(self, x_range=None, y_range=None, **kw):
        return branded_axes(x_range, y_range, **kw)

    def branded_vector(self, start=None, end=None, color=VECTOR_COLOR, **kw):
        return branded_vector(start, end, color, **kw)

    def branded_circle(self, radius=1.5, color=TEAL_ACCENT, fill_opacity=0.15, **kw):
        return branded_circle(radius, color, fill_opacity, **kw)

    def reveal_equation(self, eq_text: str, position=UP * 2):
        return reveal_equation(self, eq_text, position)

    def transition_scene(self, title: str):
        transition_scene(self, title)

    def highlight_concept(self, mobject: "Mobject", color: str = TEAL_ACCENT):
        highlight_concept(self, mobject, color)

    def playful_bounce(self, mobject: "Mobject", n: int = 2):
        playful_bounce(self, mobject, n)

    def morph_shape(self, source: "Mobject", target: "Mobject", run_time: float = 1.2):
        morph_shape(self, source, target, run_time)

    def number_ticker(self, start: float, end: float, run_time: float = 1.5,
                      position=ORIGIN, color: str = STAR_YELLOW):
        return number_ticker(self, start, end, run_time, position, color)

    def glow_dot(self, point=None, color=STAR_YELLOW, radius=0.12):
        return glow_dot(point, color, radius)
# ─────────────────────────────────────────────────────────────────────────────
# Blackboard Theming Engine
# Realistic blackboard simulation for step-by-step EUEE exam solutions.
# ─────────────────────────────────────────────────────────────────────────────

# Blackboard Colors
BB_BG_COLOR = "#1A2518"        # Dark green/black texture
BB_CHALK_WHITE = "#F4F4F0"     # Chalk white
BB_CHALK_YELLOW = "#FFF59D"    # Yellow chalk
BB_CHALK_BLUE = "#81D4FA"      # Blue chalk
BB_CHALK_RED = "#EF9A9A"       # Red chalk

def setup_blackboard(scene: Scene) -> None:
    """Setup realistic blackboard background."""
    scene.camera.background_color = BB_BG_COLOR
    Text.set_default(font="Inter", color=BB_CHALK_WHITE)

class BlackboardScene(Scene):
    """Base class for blackboard videos without TTS, realistic writing."""
    def setup(self):
        super().setup()
        setup_blackboard(self)

    def write_step(self, mobject: Mobject, run_time=2.0):
        """Simulates realistic stroke-by-stroke chalk writing."""
        self.play(Write(mobject, run_time=run_time, rate_func=linear))
