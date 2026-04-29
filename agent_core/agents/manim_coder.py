"""
agents/manim_coder.py — Manim Developer Agent (v6 — Full 3B1B Quality)
Integrates Visual Designer storyboard_plan, uses manim_config.theme import.
"""
from __future__ import annotations

import re
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import get_llm, MANIM_CODER_MODEL
from logger import get_logger
from langchain_core.messages import HumanMessage, SystemMessage

log = get_logger("manim_coder")

# ─────────────────────────────────────────────────────────────────────────────
# Script header — uses dynamic agent_core path, relative not hardcoded
# ─────────────────────────────────────────────────────────────────────────────
SCRIPT_HEADER_TEMPLATE = '''import os, sys
import numpy as np

# ── Dynamic PATH setup (no hardcoded /opt/homebrew) ──────────────────────────
import shutil, glob

_tex_bin = ""
for _c in ["/Library/TeX/texbin", "/opt/homebrew/bin", "/usr/local/bin"]:
    if os.path.exists(os.path.join(_c, "kpsewhich")):
        _tex_bin = _c
        break

_path_parts = ["/tmp/stem_venv/bin"]
if _tex_bin:
    _path_parts.append(_tex_bin)
_path_parts += ["/opt/homebrew/bin", "/usr/local/bin", "/usr/bin", "/bin"]
os.environ["PATH"] = ":".join(_path_parts)
os.environ["HF_HOME"] = "/tmp/huggingface_cache"

_gs_candidates = ["/opt/homebrew/lib/libgs.dylib", "/usr/local/lib/libgs.dylib"]
for _gs in _gs_candidates:
    if os.path.exists(_gs):
        os.environ["LIBGS"] = _gs
        break

_texmf_candidates = glob.glob("/opt/homebrew/Cellar/texlive/*/share/texmf-dist") + \
                    glob.glob("/usr/local/Cellar/texlive/*/share/texmf-dist")
if _texmf_candidates:
    _td = sorted(_texmf_candidates)[-1]
    os.environ["TEXMFCNF"]  = _td + "/web2c"
    os.environ["TEXMFDIST"] = _td
    os.environ["TEXMFMAIN"] = _td

# ── Theme & Manim ─────────────────────────────────────────────────────────────
sys.path.insert(0, "{project_root}")
from manim_config.theme import *          # AmharicEduScene, BG_COLOR, TEAL_ACCENT, STAR_YELLOW, ...
from manim import *

# === CONDITIONAL LATEX ===
import manim, subprocess
try:
    subprocess.run(["latex", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    HAS_LATEX = True
except (FileNotFoundError, subprocess.CalledProcessError):
    HAS_LATEX = False

if not HAS_LATEX:
    def _mock_tex(*args, **kwargs):
        text = " ".join(str(a) for a in args).replace("$","").replace("^\\\\circ","°")
        kwargs.pop("tex_environment", None)
        return manim.Text(text, font="Inter", font_size=kwargs.get("font_size", 48), color=kwargs.get("color", "#FFFEF0"))
    manim.MathTex = _mock_tex
    manim.Tex = _mock_tex
    MathTex = _mock_tex
    Tex = _mock_tex

# Prevent hallucinated CurvedBezier
def CurvedBezier(*args, **kwargs):
    return CurvedArrow(*args, **kwargs)
'''

# BLACKBOARD_HEADER_TEMPLATE removed — 3B1B mode only.
MMS_SERVICE_HEADER = SCRIPT_HEADER_TEMPLATE
BLACKBOARD_HEADER_TEMPLATE = SCRIPT_HEADER_TEMPLATE  # backward compat alias

# ─────────────────────────────────────────────────────────────────────────────
# 3B1B System Prompt — massive quality upgrade
# ─────────────────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are a SENIOR ManimCE v0.20.1 developer building 3Blue1Brown-quality educational STEM videos.
Your code must be visually stunning, perfectly synced to audio, and emotionally engaging.
EVERY voiceover block MUST have rich visual animation — NEVER just self.wait() with nothing on screen.

==== IRONCLAD RULES (any violation = crash or ugly video) ====

INHERITANCE & SETUP:
1. ALWAYS inherit: `class SceneName(AmharicEduScene):`
2. ALWAYS start construct() with: `setup_scene(self)`
3. DO NOT touch the camera at all (no save_state, no zoom, no scale).

VOICEOVER SYNC (CRITICAL):
4. One sentence = one `with self.voiceover(text="...") as tracker:` block. NEVER merge or skip.
5. ALWAYS use `run_time=tracker.duration * X` (where X is 0.3-0.9) for animations in each block.
6. NEVER have a voiceover block that only calls self.wait() — ALWAYS show something visual.

CANVAS BOUNDS (prevents cropping):
7. NEVER place objects beyond: x in [-5.5, 5.5], y in [-3.0, 3.0]
8. Call `self.clear()` at the START of each voiceover block to prevent clutter.

VISUAL DIVERSITY (CRITICAL — DO NOT repeat the same pattern):
Each voiceover block should use a DIFFERENT visual approach. Mix and match from:
- Title: title_card() + Line underline + Indicate()
- Axes: branded_axes() + Arrow with always_redraw() + ValueTracker sweep
- Formula: formula_box() + Circumscribe() + glow_dot()
- Trajectory: branded_axes() + TracedPath + animated Dot
- Number line: NumberLine() + Triangle marker + ValueTracker slide
- Graph: axes.plot(lambda x: ...) + Create(graph)
- Bullet text: latin_text() + FadeIn(shift=RIGHT) (use clamp_to_screen())
- Circle morph: branded_circle() + ReplacementTransform into formula_box()

AVAILABLE THEME HELPERS (imported from theme):
- title_card(title, subtitle) -> VGroup
- branded_axes(x_range, y_range) -> Axes
- branded_vector(start, end, color) -> Arrow
- branded_circle(radius, color, fill_opacity) -> Circle
- formula_box(latex_str, color) -> VGroup (index [0]=box, [1]=formula)
- glow_dot(point, color) -> Dot
- latin_text(text, font_size, color) -> Text (use for ALL text — English only)
- amharic_text(text, font_size, color) -> Text (DEPRECATED, use latin_text instead)
- playful_bounce(self, mobject) -> None (call directly, NOT inside self.play())
- clamp_to_screen(mobject) -> mobject (keeps within frame bounds)
- setup_scene(self) -> None

COLOR SYSTEM (use the theme colors, not raw hex):
- BG_COLOR, TEAL_ACCENT, STAR_YELLOW, VECTOR_COLOR, FORCE_COLOR
- TEXT_COLOR, FORMULA_COLOR, MUTED_COLOR, SUCCESS_COLOR, AXIS_COLOR

FORBIDDEN (these crash Manim):
- `thickness=` anywhere -> use `stroke_width=`
- `Arc(ORIGIN, ...)` positional -> use `Arc(radius=1, ...)`
- `self.wait(run_time=X)` -> use `self.wait(X)`
- `self.play(SomeMobject)` without Animation wrapper
- `self.play(playful_bounce(...))` -> call `playful_bounce(...)` directly, it returns None
- `self.play(None)` -> crashes. Never pass None to self.play()
- `FadeOut(*self.mobjects)` -> use `self.clear()`
- `.scale()`, `.zoom()` on camera
- `GlowDot` -> use `glow_dot()`

FEW-SHOT EXAMPLE (study this pattern — notice EVERY block has unique visuals):
```python
class MotionDemo(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        with self.voiceover(text="Sentence 1 here") as tracker:
            self.clear()
            tc = title_card("Motion", "")
            underline = Line(LEFT * 3, RIGHT * 3, color=TEAL_ACCENT, stroke_width=4)
            underline.next_to(tc, DOWN, buff=0.2)
            self.play(FadeIn(tc, shift=UP * 0.3), run_time=tracker.duration * 0.4)
            self.play(Create(underline), run_time=tracker.duration * 0.3)
            self.play(Indicate(tc, color=STAR_YELLOW), run_time=tracker.duration * 0.2)

        with self.voiceover(text="Sentence 2 here") as tracker:
            self.clear()
            angle_t = ValueTracker(0)
            plane = branded_axes([-4, 4, 1], [-3, 3, 1]).scale(0.7)
            vec = always_redraw(lambda: Arrow(
                start=plane.c2p(0, 0),
                end=plane.c2p(2.5 * np.cos(angle_t.get_value()), 2.5 * np.sin(angle_t.get_value())),
                buff=0, color=VECTOR_COLOR, stroke_width=6, max_tip_length_to_length_ratio=0.15
            ))
            self.play(Create(plane), run_time=tracker.duration * 0.3)
            self.add(vec)
            self.play(angle_t.animate.set_value(PI / 3), run_time=tracker.duration * 0.5, rate_func=smooth)

        with self.voiceover(text="Sentence 3 here") as tracker:
            self.clear()
            plane = branded_axes([-1, 6, 1], [-1, 4, 1]).scale(0.65).shift(DOWN * 0.5)
            self.play(Create(plane), run_time=tracker.duration * 0.2)
            t_param = ValueTracker(0)
            trace_dot = always_redraw(lambda: Dot(
                point=plane.c2p(5 * t_param.get_value(), 4 * t_param.get_value() - 4 * t_param.get_value()**2),
                radius=0.12, color=STAR_YELLOW
            ))
            trail = TracedPath(trace_dot.get_center, stroke_color=TEAL_ACCENT, stroke_width=3)
            self.add(trail, trace_dot)
            self.play(t_param.animate.set_value(1), run_time=tracker.duration * 0.7, rate_func=linear)

        with self.voiceover(text="Sentence 4 here") as tracker:
            self.clear()
            fb = formula_box("F = ma", color=TEAL_ACCENT)
            fb.move_to(ORIGIN)
            self.play(Create(fb[0]), Write(fb[1]), run_time=tracker.duration * 0.5)
            self.play(Circumscribe(fb, color=STAR_YELLOW, time_width=2), run_time=tracker.duration * 0.3)
            dot = glow_dot(fb.get_corner(UR) + UP * 0.2, color=STAR_YELLOW)
            self.play(FadeIn(dot, scale=3), run_time=tracker.duration * 0.2)
```

OUTPUT: Raw Python ONLY. No markdown. No comments outside # comments. Perfect 4-space indentation.
Start immediately with `class ClassName(AmharicEduScene):`.
"""


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def run_manim_coder(
    scenes: list[dict],
    persona_id: int = 1,
    error_context: str = "",
    visual_feedback: str = "",
    previous_code: list[str] | None = None,
) -> list[str]:
    """Generate ManimCE scene classes. Never returns empty."""
    llm = get_llm(model_name=MANIM_CODER_MODEL, temperature=0.1, max_tokens=12000)

    if (error_context or visual_feedback) and previous_code:
        combined_error = "\n".join(filter(None, [error_context, visual_feedback]))
        return _heal_code(llm, previous_code, combined_error)

    class_strings = []
    for scene in scenes:
        code = _generate_scene_class(llm, scene, persona_id)
        code = _sanitize(code)
        class_strings.append(code)

    log.info(f"Generated {len(class_strings)} scene classes.")
    return class_strings


# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────────────────────

def _generate_scene_class(llm, scene: dict, persona_id: int) -> str:
    scene_name = scene.get("scene_name", "FallbackScene")
    concept = scene.get("concept", "")
    formulas_str = ", ".join(scene.get("latex_formulas", [])) or "None"
    manim_visual = scene.get("manim_visual_instructions", scene.get("visual", ""))
    storyboard = scene.get("storyboard_plan", {})
    math_warnings = scene.get("math_verification", {}).get("warnings", [])

    sentences = scene.get("sentences", [])
    if not sentences:
        script = scene.get("amharic_script", "")
        sentences = [s.strip() + "።" for s in script.replace("?", "።").replace("!", "།").split("།") if s.strip()]
    if not sentences:
        sentences = ["ይህ መሠረታዊ ጽንሰ ሐሳብ ነው።"]

    sentence_blocks = ""
    for i, s in enumerate(sentences):
        sentence_blocks += f"  Block {i+1}: \"{s}\"\n"

    # Format storyboard plan for the prompt
    storyboard_section = ""
    if storyboard:
        storyboard_section = f"""
VISUAL STORYBOARD PLAN (FOLLOW THIS):
- Metaphor: {storyboard.get('metaphor_chain', '')}
- Opening visual: {storyboard.get('opening_visual', '')}
- Color arc: {storyboard.get('color_arc', '')}
- Aha moment: {storyboard.get('aha_moment', '')}
- Morph sequence: {json.dumps(storyboard.get('morph_sequence', []), ensure_ascii=False)}
- Camera moves: {json.dumps(storyboard.get('camera_moves', []), ensure_ascii=False)}
- Humor beats: {json.dumps(storyboard.get('humor_beats', []), ensure_ascii=False)}
- Key animations: {json.dumps(storyboard.get('key_animations', []), ensure_ascii=False)}
"""

    math_warning_section = ""
    if math_warnings:
        math_warning_section = f"\nMATH WARNINGS (fix these formulas if used):\n" + "\n".join(f"  - {w}" for w in math_warnings)

    user_prompt = f"""Generate a complete, richly animated ManimCE class for this educational scene.

CLASS NAME: {scene_name}
CONCEPT: {concept}
KEY FORMULAS: {formulas_str}

ANIMATION DIRECTOR'S INSTRUCTIONS:
{manim_visual}
{storyboard_section}{math_warning_section}

NARRATION — ONE VOICEOVER BLOCK PER SENTENCE (STRICT):
{sentence_blocks}

REQUIREMENTS:
- Exactly {len(sentences)} `with self.voiceover(...)` blocks — no more, no less.
- CLEAR SCREEN every 3 blocks with `self.clear()`.
- Include playful_bounce() for at least ONE humor beat.
- Use STAR_YELLOW for the 'aha!' moment (glow_dot or Circumscribe).
- Use always_redraw + ValueTracker for dynamic quantities.
- Keep all objects inside: x ∈ [-5.5, 5.5], y ∈ [-3.0, 3.0].

Output the complete Python class only. No markdown fences. Start with `class {scene_name}(`."""

    try:
        response = llm.invoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ])
        code = response.content.strip()

        # Strip markdown fences
        match = re.search(r"```(?:python)?\n?(.*?)\n?```", code, re.DOTALL)
        if match:
            code = match.group(1).strip()
        else:
            code = re.sub(r"^```(?:python)?", "", code, flags=re.MULTILINE).strip()
            code = re.sub(r"```$", "", code, flags=re.MULTILINE).strip()

        # Extract class block
        class_match = re.search(r"(class\s+\w+\s*\(AmharicEduScene\):.*)", code, re.DOTALL)
        if class_match:
            code = class_match.group(1)
        else:
            class_match = re.search(r"(class\s+\w+.*)", code, re.DOTALL)
            if class_match:
                code = class_match.group(1)
            else:
                log.warning(f"No class found for {scene_name} — using fallback")
                return _guaranteed_fallback(scene)

        return _sanitize(code)

    except Exception as exc:
        log.error(f"LLM error for {scene_name}: {exc} — using fallback")
        return _guaranteed_fallback(scene)


def _sanitize(code: str) -> str:
    """Fix common LLM hallucinations that crash Manim."""
    code = re.sub(r'\bthickness\s*=', 'stroke_width=', code)
    code = re.sub(r'Arc\s*\(\s*ORIGIN\s*,\s*', 'Arc(', code)
    # Fix Rectangle(, leading-comma patterns (left by width=/height= removal)
    code = re.sub(r'Rectangle\(\s*,', 'Rectangle(width=4.0, height=2.0,', code)
    code = re.sub(r'Square\(\s*,', 'Square(side_length=2.0,', code)
    code = re.sub(r'Circle\(\s*,', 'Circle(radius=1.0,', code)
    code = re.sub(r'self\.wait\(run_time\s*=\s*([^)]+)\)', r'self.wait(\1)', code)
    code = re.sub(r'self\.wait\(duration\s*=\s*([^)]+)\)', r'self.wait(\1)', code)
    code = re.sub(r',?\s*axis_config\s*=\s*\{[^}]*\}', '', code)
    code = re.sub(r',?\s*include_tip\s*=\s*\w+', '', code)
    code = re.sub(r',?\s*include_numbers\s*=\s*\w+', '', code)
    code = re.sub(r',?\s*\bwidth\s*=\s*[\d.]+(?=\s*[,)])', '', code)
    code = re.sub(r',?\s*\bheight\s*=\s*[\d.]+(?=\s*[,)])', '', code)
    code = re.sub(r'Rectangle\s*\(\s*,', 'Rectangle(width=2.0, height=1.0,', code)
    code = re.sub(r'Rectangle\s*\(\s*color=', 'Rectangle(width=2.0, height=1.0, color=', code)
    code = re.sub(r'Square\s*\(\s*color=', 'Square(side_length=1.0, color=', code)
    code = code.replace('ShowCreation', 'Create')
    code = code.replace('ShowCreationThenDestruction', 'Create')
    code = code.replace('FadeOutAndShift', 'FadeOut')
    code = re.sub(r'\bformula_box\s*=\s*formula_box\(', 'f_box = formula_box(', code)
    code = re.sub(r'self\.play\(Write\(formula_box\)', 'self.play(Write(f_box)', code)
    code = re.sub(r'self\.play\(Create\(formula_box\)', 'self.play(Create(f_box)', code)
    code = re.sub(
        r'(Axes\s*\([^)]*?)\s*,?\s*background_line_style\s*=\s*\{[^}]*\}',
        r'\1', code, flags=re.DOTALL
    )
    # ── Hallucination fixes ───────────────────────────────────────────────────
    code = code.replace('GlowDot(', 'glow_dot(')
    code = code.replace('CurvedBezier(', 'CurvedArrow(')
    code = re.sub(r'\.animate\.zoom\([^)]*\)', '', code)
    code = re.sub(r',?\s*glow_factor\s*=\s*[\d.]+', '', code)
    code = re.sub(r',?\s*glow_radius\s*=\s*[\d.]+', '', code)
    code = re.sub(r',?\s*glow_color\s*=\s*[^,)]+', '', code)
    code = re.sub(
        r'self\.play\(\s*\*\\[FadeOut\(m\) for m in self\.mobjects\\]\s*(?:,\s*run_time=[^)]+)?\)',
        'self.clear()', code
    )
    code = re.sub(r'\.set_color_by_gradient\(([^)]+)\)', r'.set_color(\1)', code)
    code = re.sub(r'Dot\(np\.array\(\[[^\]]*\]\)\s+or\s+ORIGIN', 'Dot(ORIGIN', code)
    code = re.sub(
        r'point\s*=\s*(\w+)\s+or\s+ORIGIN',
        r'point=(\1 if \1 is not None else ORIGIN)',
        code
    )
    code = re.sub(r',?\s*tex_template\s*=\s*\w+', '', code)
    code = re.sub(r'self\.camera\.frame\.animate\.scale\([^)]+\)', '', code)
    code = re.sub(r'Rectangle\(\s*,', 'Rectangle(width=4.0, height=2.0,', code)
    code = re.sub(r'Square\(\s*,', 'Square(side_length=2.0,', code)
    code = re.sub(r'Circle\(\s*,', 'Circle(radius=1.0,', code)
    code = re.sub(r'self\.play\(None,\s*', 'self.play(', code)
    code = re.sub(r'self\.play\(None\)', 'pass  # removed None play', code)
    code = re.sub(r',\s*None\s*(?=[,)])', '', code)
    for _h in ['playful_bounce', 'camera_zoom_to', 'camera_restore',
               'highlight_concept', 'transition_scene', 'morph_shape']:
        code = re.sub(
            rf'self\.play\({re.escape(_h)}\(([^)]+)\)\)',
            rf'{_h}(\1)',
            code
        )
    code = re.sub(r',\s*\)', ')', code)
    return code


def _guaranteed_fallback(scene: dict) -> str:
    """Visually RICH fallback — 8 distinct animation patterns. ALWAYS renders."""
    name = scene.get("scene_name", "FallbackScene")
    concept = scene.get("concept", "Physics").replace('"', "'")
    formulas = scene.get("latex_formulas", [])
    formula_str = formulas[0].replace('"', "'") if formulas else "F = ma"

    sentences = scene.get("sentences", scene.get("sentences_english", []))
    if not sentences:
        sentences = [
            f"Let's explore {concept} together.",
            "This is one of the most elegant ideas in science.",
            f"The key equation is {formula_str}. Watch what each part does.",
            "Imagine plugging in real numbers. The pattern becomes clear.",
            "See how the graph changes? That's the beautiful insight.",
            "Let's trace this out step by step.",
            "Notice how everything connects. This is why math works.",
            f"And that's {concept}. Pretty satisfying, right?",
        ]

    blocks = []
    n = len(sentences)

    for i, s in enumerate(sentences):
        s_safe = s.replace('"', "'").replace("\\", "\\\\")
        pattern = i % 8

        if i == 0:
            # Pattern 0: Title card + animated underline
            blocks.append(f'''        with self.voiceover(text="{s_safe}") as tracker:
            self.clear()
            tc = title_card("{concept}", "")
            underline = Line(LEFT * 3, RIGHT * 3, color=TEAL_ACCENT, stroke_width=4)
            underline.next_to(tc, DOWN, buff=0.2)
            self.play(FadeIn(tc, shift=UP * 0.3), run_time=tracker.duration * 0.4)
            self.play(Create(underline), run_time=tracker.duration * 0.3)
            self.play(Indicate(tc, color=STAR_YELLOW), run_time=tracker.duration * 0.2)
            self.wait(tracker.duration * 0.1)''')

        elif pattern == 1:
            # Pattern 1: Axes + animated vector sweep
            blocks.append(f'''        with self.voiceover(text="{s_safe}") as tracker:
            self.clear()
            angle_t = ValueTracker(0)
            plane = branded_axes([-4, 4, 1], [-3, 3, 1]).scale(0.7)
            vec = always_redraw(lambda: Arrow(
                start=plane.c2p(0, 0),
                end=plane.c2p(2.5 * np.cos(angle_t.get_value()), 2.5 * np.sin(angle_t.get_value())),
                buff=0, color=VECTOR_COLOR, stroke_width=6, max_tip_length_to_length_ratio=0.15
            ))
            self.play(Create(plane), run_time=tracker.duration * 0.3)
            self.add(vec)
            self.play(angle_t.animate.set_value(PI / 3), run_time=tracker.duration * 0.5, rate_func=smooth)
            self.play(Indicate(vec, color=STAR_YELLOW), run_time=tracker.duration * 0.2)''')

        elif pattern == 2:
            # Pattern 2: Formula box + circumscribe + glow
            blocks.append(f'''        with self.voiceover(text="{s_safe}") as tracker:
            self.clear()
            fb = formula_box("{formula_str}", color=TEAL_ACCENT)
            fb.move_to(ORIGIN)
            self.play(Create(fb[0]), Write(fb[1]), run_time=tracker.duration * 0.5)
            self.play(Circumscribe(fb, color=STAR_YELLOW, time_width=2), run_time=tracker.duration * 0.3)
            dot = glow_dot(fb.get_corner(UR) + UP * 0.2, color=STAR_YELLOW)
            self.play(FadeIn(dot, scale=3), run_time=tracker.duration * 0.2)''')

        elif pattern == 3:
            # Pattern 3: Parabolic trajectory trace
            blocks.append(f'''        with self.voiceover(text="{s_safe}") as tracker:
            self.clear()
            plane = branded_axes([-1, 6, 1], [-1, 4, 1]).scale(0.65).shift(DOWN * 0.5)
            self.play(Create(plane), run_time=tracker.duration * 0.2)
            t_param = ValueTracker(0)
            trace_dot = always_redraw(lambda: Dot(
                point=plane.c2p(5 * t_param.get_value(), 4 * t_param.get_value() - 4 * t_param.get_value()**2),
                radius=0.12, color=STAR_YELLOW
            ))
            trail = TracedPath(trace_dot.get_center, stroke_color=TEAL_ACCENT, stroke_width=3)
            self.add(trail, trace_dot)
            self.play(t_param.animate.set_value(1), run_time=tracker.duration * 0.7, rate_func=linear)
            self.wait(tracker.duration * 0.1)''')

        elif pattern == 4:
            # Pattern 4: Number line + sliding marker
            blocks.append(f'''        with self.voiceover(text="{s_safe}") as tracker:
            self.clear()
            nl = NumberLine(x_range=[0, 10, 1], length=10, color=AXIS_COLOR,
                           include_numbers=True, font_size=24)
            nl.scale(0.8)
            marker = Triangle(fill_color=TEAL_ACCENT, fill_opacity=1, stroke_width=0).scale(0.2)
            marker.next_to(nl.n2p(0), UP, buff=0.1)
            t_val = ValueTracker(0)
            marker.add_updater(lambda m: m.next_to(nl.n2p(t_val.get_value()), UP, buff=0.1))
            self.play(Create(nl), run_time=tracker.duration * 0.3)
            self.add(marker)
            self.play(t_val.animate.set_value(7), run_time=tracker.duration * 0.5, rate_func=smooth)
            lbl = latin_text("7", font_size=FONT_SIZE_HEADER, color=STAR_YELLOW)
            lbl.next_to(marker, UP, buff=0.2)
            self.play(FadeIn(lbl, scale=2), run_time=tracker.duration * 0.2)''')

        elif pattern == 5:
            # Pattern 5: Sine graph with peak glow
            blocks.append(f'''        with self.voiceover(text="{s_safe}") as tracker:
            self.clear()
            plane = branded_axes([-1, 7, 1], [-2, 2, 1]).scale(0.7)
            self.play(Create(plane), run_time=tracker.duration * 0.2)
            graph = plane.plot(lambda x: 1.5 * np.sin(x), x_range=[0, 6.28], color=TEAL_ACCENT, stroke_width=4)
            self.play(Create(graph), run_time=tracker.duration * 0.5)
            peak_dot = glow_dot(plane.c2p(PI / 2, 1.5), color=STAR_YELLOW)
            self.play(FadeIn(peak_dot, scale=3), run_time=tracker.duration * 0.15)
            self.play(Indicate(peak_dot, color=STAR_YELLOW), run_time=tracker.duration * 0.15)''')

        elif pattern == 6:
            # Pattern 6: Bullet-point text reveal
            words = s_safe.split()
            mid = max(1, len(words) // 2)
            line1 = " ".join(words[:mid])
            line2 = " ".join(words[mid:]) if mid < len(words) else ""
            blocks.append(f'''        with self.voiceover(text="{s_safe}") as tracker:
            self.clear()
            b1 = latin_text("{line1}", font_size=FONT_SIZE_LABEL, color=TEXT_COLOR)
            b1.move_to(UP * 0.8)
            clamp_to_screen(b1)
            self.play(FadeIn(b1, shift=RIGHT * 0.5), run_time=tracker.duration * 0.3)
            b2 = latin_text("{line2}", font_size=FONT_SIZE_LABEL, color=MUTED_COLOR)
            b2.next_to(b1, DOWN, buff=0.4, aligned_edge=LEFT)
            clamp_to_screen(b2)
            self.play(FadeIn(b2, shift=RIGHT * 0.5), run_time=tracker.duration * 0.3)
            accent = Line(LEFT * 4, LEFT * 3.9, color=TEAL_ACCENT, stroke_width=8)
            accent.next_to(b1, LEFT, buff=0.2)
            self.play(Create(accent), run_time=tracker.duration * 0.15)
            self.wait(tracker.duration * 0.2)''')

        elif pattern == 7:
            # Pattern 7: Circle morph into formula
            blocks.append(f'''        with self.voiceover(text="{s_safe}") as tracker:
            self.clear()
            circ = branded_circle(1.5, color=TEAL_ACCENT, fill_opacity=0.15)
            ctxt = latin_text("{concept[:20]}", font_size=FONT_SIZE_BODY, color=TEXT_COLOR)
            ctxt.move_to(circ.get_center())
            self.play(DrawBorderThenFill(circ), run_time=tracker.duration * 0.3)
            self.play(Write(ctxt), run_time=tracker.duration * 0.3)
            fb = formula_box("{formula_str}", color=STAR_YELLOW)
            fb.move_to(circ.get_center())
            self.play(ReplacementTransform(VGroup(circ, ctxt), fb), run_time=tracker.duration * 0.3)
            self.wait(tracker.duration * 0.1)''')

        # Override last sentence with summary checkmark
        if i == n - 1 and n > 1:
            blocks[-1] = f'''        with self.voiceover(text="{s_safe}") as tracker:
            self.clear()
            chk = latin_text("Done!", font_size=FONT_SIZE_TITLE, color=SUCCESS_COLOR)
            chk.move_to(LEFT * 2 + UP * 0.5)
            summary = latin_text("{concept[:25]}", font_size=FONT_SIZE_HEADER, color=TEAL_ACCENT)
            summary.move_to(RIGHT * 1)
            self.play(FadeIn(chk, scale=3), run_time=tracker.duration * 0.3)
            self.play(Write(summary), run_time=tracker.duration * 0.3)
            playful_bounce(self, chk)
            self.play(Indicate(summary, color=STAR_YELLOW), run_time=tracker.duration * 0.2)
            self.wait(tracker.duration * 0.1)'''

    blocks_str = "\n\n".join(blocks)
    return f'''class {name}(AmharicEduScene):
    def construct(self):
        setup_scene(self)

{blocks_str}

        self.wait(0.5)
'''


def _heal_code(llm, previous_classes: list[str], error: str) -> list[str]:
    """Self-heal broken code."""
    log.info(f"Healing code — error: {error[:200]}")
    full_code = "\n\n".join(previous_classes)
    user_prompt = f"""Fix this ManimCE code. Output ONLY the corrected `class ...` block.

ERROR:
{error[:1500]}

BROKEN CODE:
{full_code[:3000]}"""

    try:
        response = llm.invoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ])
        fixed = response.content.strip()
        match_fence = re.search(r"```(?:python)?\n?(.*?)\n?```", fixed, re.DOTALL)
        if match_fence:
            fixed = match_fence.group(1).strip()
        fixed = _sanitize(fixed)
        match = re.search(r"^class\s+(\w+)\s*\(", fixed, re.MULTILINE)
        if not match:
            return previous_classes
        healed_name = match.group(1)
        new_classes = []
        for block in previous_classes:
            bm = re.search(r"^class\s+(\w+)\s*\(", block, re.MULTILINE)
            if bm and bm.group(1) == healed_name:
                new_classes.append(fixed)
            else:
                new_classes.append(block)
        log.info(f"Healed class: {healed_name}")
        return new_classes
    except Exception as exc:
        log.error(f"Heal error: {exc}")
        return previous_classes
