"""
agents/manim_coder.py — Manim Developer Agent (v5 — 3B1B Quality)

Architecture:
  - ONE voiceover block per sentence (perfect audio-visual sync)
  - GUARANTEED safe fallback (scenes NEVER get skipped)
  - Complex, layered animations (not just text dumps)
  - Strict canvas bounds enforced in both prompt and fallback
"""

import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import get_llm, MANIM_CODER_MODEL
from langchain_core.messages import HumanMessage, SystemMessage

# ─────────────────────────────────────────────────────────────────────────────
# Script header (injected before running manim)
# ─────────────────────────────────────────────────────────────────────────────
SCRIPT_HEADER_TEMPLATE = '''import os, sys
import numpy as np
os.environ["PATH"] = (
    "/tmp/stem_venv/bin:/Library/TeX/texbin:"
    "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
)
os.environ["HF_HOME"] = "/tmp/huggingface_cache"
os.environ['LIBGS'] = '/opt/homebrew/lib/libgs.dylib'
tex_dist = '/opt/homebrew/Cellar/texlive/20260301/share/texmf-dist'
os.environ['TEXMFCNF'] = tex_dist + '/web2c'
os.environ['TEXMFDIST'] = tex_dist
os.environ['TEXMFMAIN'] = tex_dist

# ── Theme & Manim ─────────────────────────────────────────────────────────────
sys.path.insert(0, "{agent_core_path}")
from theme import *          # AmharicEduScene, BG_COLOR, ACCENT_COLOR, ...
from manim import *

# === CONDITIONAL LATEX ===
import manim

# Only mock if latex isn't found (though it should be via PATH)
import subprocess
try:
    subprocess.run(["latex", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    HAS_LATEX = True
except FileNotFoundError:
    HAS_LATEX = False

if not HAS_LATEX:
    def _mock_tex(*args, **kwargs):
        text = " ".join(str(a) for a in args).replace("$","").replace("^\\\\circ","°")
        kwargs.pop("tex_environment", None)
        return manim.Text(text, font="Inter", font_size=kwargs.get("font_size", 48), color=kwargs.get("color", "#E2E8F0"))
    
    manim.MathTex = _mock_tex
    manim.Tex = _mock_tex
    MathTex = _mock_tex
    Tex = _mock_tex

# Prevent hallucinated CurvedBezier class
def CurvedBezier(*args, **kwargs):
    return CurvedArrow(*args, **kwargs)
'''

MMS_SERVICE_HEADER = SCRIPT_HEADER_TEMPLATE

# ─────────────────────────────────────────────────────────────────────────────
# System Prompt — 3B1B-Quality strict rules
# ─────────────────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are a senior ManimCE v0.20.1 developer building 3Blue1Brown-quality educational STEM videos.

==== IRONCLAD RULES — Violating ANY of these causes a crash or ugly video ====

INHERITANCE & SETUP:
1. ALWAYS inherit from AmharicEduScene: `class SceneName(AmharicEduScene):`
2. ALWAYS call `setup_scene(self)` as the VERY FIRST LINE of construct().
3. DO NOT call `self.camera.frame.save_state()` or try to zoom/scale the camera. LEAVE CAMERA COMPLETELY ALONE.

ONE SENTENCE = ONE VOICEOVER BLOCK (CRITICAL FOR SYNC):
4. You will be given a list of narration sentences. Each sentence MUST be its own `with self.voiceover(text="...") as tracker:` block.
5. ALWAYS use `run_time=tracker.duration * 0.9` for the MAIN animation inside each block so it perfectly matches the audio.

CANVAS MANAGEMENT (prevents cropping):
6. NEVER place objects beyond: RIGHT*5.5, LEFT*5.5, UP*3.0, DOWN*3.0.
7. ALWAYS call `self.clear()` at the start of every 2nd or 3rd voiceover block to prevent screen clutter.
8. NEVER use `.scale()` or `.zoom()` anywhere. Use `font_size=` to size text instead.

ANIMATION QUALITY (3B1B style):
9. Use `always_redraw` and `ValueTracker` for dynamic animations. NEVER just show static text. Every block MUST have at least ONE real animation.
   - Use `TransformMatchingTex` or `ReplacementTransform` for formulas.
   - Draw arrows/vectors with `GrowArrow()`
   - Reveal axes with `Create(branded_axes(...))`
   - Highlight with `Circumscribe()` or `Indicate()`
   - Transform shapes with `ReplacementTransform()` or `Transform()`
   - Show motion with `MoveAlongPath()` or `.animate.move_to()`
10. For intro blocks: Use `title_card()`, a `branded_circle()` or `Square`, and `DrawBorderThenFill()`.
11. For concept blocks: Use `branded_axes()` with labeled vectors showing the physics.
12. For formula blocks: Use `reveal_equation(self, "formula")` or `formula_box()`, then `Circumscribe()` it.
13. For summary blocks: `VGroup` multiple key elements already on screen and `Indicate()` them together.

LAYOUT:
14. Stack text with `VGroup(...).arrange(DOWN, buff=0.4)` — NEVER pile things at ORIGIN.
15. For side-by-side: `VGroup(left, right).arrange(RIGHT, buff=1.0)`

FORBIDDEN (these crash Manim):
- `thickness=` anywhere (use `stroke_width=`)
- `Arc(ORIGIN, ...)` positional args (use `Arc(radius=1, start_angle=0, angle=PI/4)`)
- `FadeOut(*self.mobjects)` on an empty scene (use `self.clear()` instead)
- `self.play(SomeMobject)` without an Animation wrapper
- `self.wait(run_time=...)` — `self.wait()` only takes a duration float, e.g. `self.wait(1.0)` or `self.wait(tracker.duration * 0.1)`

EXAMPLE 3B1B-STYLE SCENE STRUCTURE:
```python
class PhysicsExample(AmharicEduScene):
    def construct(self):
        setup_scene(self)
        
        # Grid Background
        grid = branded_axes([-1, 8, 1], [-1, 5, 1]).set_opacity(0.4).shift(UP * 0.5)
        
        origin = grid.c2p(0, 0)
        theta_tracker = ValueTracker(35 * DEGREES)
        force_magnitude = 5.0
        
        vector = always_redraw(lambda: Arrow(
            start=origin,
            end=grid.c2p(
                force_magnitude * np.cos(theta_tracker.get_value()),
                force_magnitude * np.sin(theta_tracker.get_value())
            ),
            buff=0, color=FORCE_COLOR, stroke_width=6, max_tip_length_to_length_ratio=0.1
        ))

        with self.voiceover(text="Here is the force vector.") as tracker:
            self.play(Create(grid), run_time=tracker.duration * 0.5)
            self.play(GrowArrow(vector), run_time=tracker.duration * 0.4)
            
        with self.voiceover(text="Watch the angle sweep.") as tracker:
            self.play(
                theta_tracker.animate.set_value(65 * DEGREES),
                rate_func=there_and_back,
                run_time=tracker.duration * 0.9
            )
```

OUTPUT: Raw Python ONLY. No markdown. No comments outside # comments. Perfect 4-space indentation.
NOTE: `title_card()`, `formula_box()`, `branded_axes()`, `branded_vector()`, `branded_circle()`, `reveal_equation()`, `transition_scene()`, `highlight_concept()` can be called EITHER as module-level functions OR as `self.title_card()` etc. — both work.
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
    """
    Generate ManimCE scene classes. Never returns empty — always provides a safe fallback.
    """
    llm = get_llm(model_name=MANIM_CODER_MODEL, temperature=0.1, max_tokens=12000)

    if (error_context or visual_feedback) and previous_code:
        combined_error = "\n".join(filter(None, [error_context, visual_feedback]))
        return _heal_code(llm, previous_code, combined_error)

    class_strings = []
    for scene in scenes:
        class_code = _generate_scene_class(llm, scene, persona_id)
        # Apply the sanitizer to catch hallucinations early
        class_code = _sanitize(class_code)
        class_strings.append(class_code)

    print(f"  [manim_coder] Generated {len(class_strings)} scene classes.", flush=True)
    return class_strings


# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────────────────────

def _generate_scene_class(llm, scene: dict, persona_id: int) -> str:
    scene_name = scene.get("scene_name", "FallbackScene")
    concept = scene.get("concept", "")
    formulas_str = ", ".join(scene.get("latex_formulas", [])) or "None"
    manim_visual_instructions = scene.get("manim_visual_instructions", scene.get("visual", ""))

    # Get sentences — ONE per voiceover block
    sentences = scene.get("sentences", [])
    if not sentences:
        script = scene.get("amharic_script", "")
        sentences = [s.strip() + "።" for s in script.replace("?", "።").replace("!", "።").split("።") if s.strip()]
    if not sentences:
        sentences = ["ይህ መሠረታዊ ጽንሰ ሐሳብ ነው።"]

    # Build one-sentence-per-block prompt section
    sentence_blocks = ""
    for i, s in enumerate(sentences):
        sentence_blocks += f"  Block {i+1}: \"{s}\"\n"

    user_prompt = f"""Generate a complete, richly animated ManimCE class for this educational scene.

CLASS NAME: {scene_name}
CONCEPT: {concept}
KEY FORMULAS: {formulas_str}

ANIMATION DIRECTOR'S INSTRUCTIONS:
{manim_visual_instructions}

NARRATION — ONE BLOCK PER SENTENCE (strict, do not merge or skip any):
{sentence_blocks}

REQUIREMENTS:
- Each "Block N" above MUST become its own `with self.voiceover(text="...") as tracker:` block.
- Total voiceover blocks in your output = {len(sentences)} exactly.
- CLEAR SCREEN every 3 blocks with `self.clear()` to prevent visual clutter.
- Include rich geometric animations (axes, vectors, circles, formulas) that EXPLAIN the concept visually.
- Keep all objects inside: x ∈ [-5.5, 5.5], y ∈ [-3.0, 3.0]. No camera scaling.

Output the complete Python class only. No markdown fences. Start immediately with `class {scene_name}(`."""

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
                print(f"  [manim_coder] No class found in output — using safe fallback for {scene_name}", flush=True)
                return _guaranteed_fallback(scene)

        # Sanitize known bad patterns
        code = _sanitize(code)
        return code

    except Exception as exc:
        print(f"  [manim_coder] LLM error for {scene_name}: {exc} — using safe fallback", flush=True)
        return _guaranteed_fallback(scene)


def _sanitize(code: str) -> str:
    """Fix common LLM hallucinations that crash Manim."""
    # Replace thickness= with stroke_width=
    code = re.sub(r'\bthickness\s*=', 'stroke_width=', code)
    # Fix Arc(ORIGIN, radius=...) → Arc(radius=...)
    code = re.sub(r'Arc\s*\(\s*ORIGIN\s*,\s*', 'Arc(', code)
    # Fix self.wait(run_time=X) → self.wait(X)
    code = re.sub(r'self\.wait\(run_time\s*=\s*([^)]+)\)', r'self.wait(\1)', code)
    # Fix self.wait(duration=X) → self.wait(X)
    code = re.sub(r'self\.wait\(duration\s*=\s*([^)]+)\)', r'self.wait(\1)', code)
    # Remove axis_config kwarg passed to branded_axes (not supported — it uses x_axis_config/y_axis_config)
    # Strip any axis_config={...} kwarg from branded_axes calls
    code = re.sub(r',?\s*axis_config\s*=\s*\{[^}]*\}', '', code)
    # Strip include_tip= and include_numbers= from branded_axes calls (not valid as top-level kwargs)
    code = re.sub(r',?\s*include_tip\s*=\s*\w+', '', code)
    code = re.sub(r',?\s*include_numbers\s*=\s*\w+', '', code)
    # Strip bare width=/height= kwargs from shape constructors (breaks VMobject.__init__)
    code = re.sub(r',?\s*\bwidth\s*=\s*[\d.]+(?=\s*[,)])', '', code)
    code = re.sub(r',?\s*\bheight\s*=\s*[\d.]+(?=\s*[,)])', '', code)
    # Fix Rectangle(, ...) or Rectangle(color=...) missing dimensions
    code = re.sub(r'Rectangle\s*\(\s*,', 'Rectangle(width=2.0, height=1.0,', code)
    code = re.sub(r'Rectangle\s*\(\s*color=', 'Rectangle(width=2.0, height=1.0, color=', code)
    code = re.sub(r'Square\s*\(\s*color=', 'Square(side_length=1.0, color=', code)
    # Fix legacy Manim names
    code = code.replace('ShowCreation', 'Create')
    code = code.replace('ShowCreationThenDestruction', 'Create')
    code = code.replace('WriteThenDestruction', 'Write')
    code = code.replace('FadeOutAndShift', 'FadeOut')
    # Fix formula_box = formula_box(...) masking
    code = re.sub(r'\bformula_box\s*=\s*formula_box\(', 'f_box = formula_box(', code)
    code = re.sub(r'self\.play\(Write\(formula_box\)', 'self.play(Write(f_box)', code)
    code = re.sub(r'self\.play\(Create\(formula_box\)', 'self.play(Create(f_box)', code)
    return code


def _guaranteed_fallback(scene: dict) -> str:
    """
    A mathematically SAFE fallback scene that ALWAYS renders without errors.
    This ensures no scene is ever skipped, even if the LLM completely fails.
    """
    name = scene.get("scene_name", "FallbackScene")
    concept = scene.get("concept", "ሳይንስ").replace('"', "'")
    formulas = scene.get("latex_formulas", [])
    formula_str = formulas[0].replace('"', "'") if formulas else "F = ma"

    sentences = scene.get("sentences", [])
    if not sentences:
        script = scene.get("amharic_script", "ይህ ወሳኝ የሳይንስ ጽንሰ ሐሳብ ነው።")
        sentences = [s.strip() + "།" for s in script.replace("?", "།").replace("!", "།").split("།") if s.strip()]
    if not sentences:
        sentences = ["ይህ ወሳኝ ጽንሰ ሐሳብ ነው።", "በጥንቃቄ እንተነትነው።", "ከዚህ ቀን ጀምሮ ጥሩ አድርጋችሁ ትረዱታላችሁ።"]

    # Build guaranteed-safe voiceover blocks
    blocks = []

    # Block 1: Title intro
    s0 = sentences[0].replace('"', "'")
    blocks.append(f'''        with self.voiceover(text="{s0}") as tracker:
            self.clear()
            title = amharic_text("{concept}", font_size=FONT_SIZE_HEADER, color=TEXT_COLOR)
            title.move_to(UP * 2.0)
            underline = Line(LEFT * 3, RIGHT * 3, color=ACCENT_COLOR, stroke_width=3)
            underline.next_to(title, DOWN, buff=0.2)
            self.play(Write(title), run_time=tracker.duration * 0.6)
            self.play(Create(underline), run_time=tracker.duration * 0.3)''')

    # Block 2: Axes + vector visualization
    if len(sentences) > 1:
        s1 = sentences[1].replace('"', "'")
        blocks.append(f'''        with self.voiceover(text="{s1}") as tracker:
            self.clear()
            axes = branded_axes([-4, 4, 1], [-3, 3, 1])
            axes.scale(0.75).move_to(ORIGIN)
            vec = branded_vector(ORIGIN, np.array([2.5, 1.5, 0]), color=VECTOR_COLOR)
            label = latin_text("→ v", font_size=FONT_SIZE_LABEL, color=VECTOR_COLOR)
            label.next_to(vec.get_end(), UP, buff=0.2)
            self.play(Create(axes), run_time=tracker.duration * 0.4)
            self.play(GrowArrow(vec), run_time=tracker.duration * 0.4)
            self.play(Write(label), run_time=tracker.duration * 0.2)''')

    # Block 3: Formula
    if len(sentences) > 2:
        s2 = sentences[2].replace('"', "'")
        blocks.append(f'''        with self.voiceover(text="{s2}") as tracker:
            self.clear()
            f_box = formula_box("{formula_str}")
            f_box.move_to(ORIGIN)
            self.play(Create(f_box[0]), Write(f_box[1]), run_time=tracker.duration * 0.6)
            self.play(Circumscribe(f_box, color=ACCENT_COLOR), run_time=tracker.duration * 0.3)''')

    # Remaining sentences: alternate between text label and indicator
    for i, s in enumerate(sentences[3:], start=3):
        s_safe = s.replace('"', "'")
        if i % 2 == 0:
            blocks.append(f'''        with self.voiceover(text="{s_safe}") as tracker:
            self.clear()
            label = amharic_text("{concept}", font_size=FONT_SIZE_BODY, color=ACCENT_COLOR)
            label.move_to(ORIGIN)
            circle = branded_circle(1.2, color=HIGHLIGHT_COLOR)
            circle.move_to(LEFT * 2.5)
            self.play(DrawBorderThenFill(circle), run_time=tracker.duration * 0.5)
            self.play(Write(label), run_time=tracker.duration * 0.4)''')
        else:
            blocks.append(f'''        with self.voiceover(text="{s_safe}") as tracker:
            explanation = amharic_text("{s_safe[:30]}", font_size=FONT_SIZE_LABEL, color=MUTED_COLOR)
            explanation.move_to(DOWN * 2.0)
            self.play(FadeIn(explanation), run_time=tracker.duration * 0.8)''')

    blocks_str = "\n\n".join(blocks)

    return f'''class {name}(AmharicEduScene):
    def construct(self):
        setup_scene(self)

{blocks_str}

        self.wait(0.5)
'''


def _heal_code(llm, previous_classes: list[str], error: str) -> list[str]:
    """Self-heal: ask the LLM to fix the broken class. Falls back to guaranteed_fallback if healing fails."""
    print(f"  [manim_coder] Healing — error: {error[:200]}", flush=True)

    full_code_context = "\n\n".join(previous_classes)

    user_prompt = f"""The following ManimCE code has a runtime error.
Fix ONLY the broken class. Keep all voiceover blocks and animations intact.
Output ONLY the corrected `class ...` block. No markdown. No explanation.

ERROR:
{error[:1500]}

BROKEN CODE:
{full_code_context[:3000]}"""

    try:
        response = llm.invoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ])
        fixed = response.content.strip()

        match_fence = re.search(r"```(?:python)?\n?(.*?)\n?```", fixed, re.DOTALL)
        if match_fence:
            fixed = match_fence.group(1).strip()
        else:
            fixed = re.sub(r"^```(?:python)?", "", fixed, flags=re.MULTILINE).strip()
            fixed = re.sub(r"```$", "", fixed, flags=re.MULTILINE).strip()

        match = re.search(r"^class\s+(\w+)\s*\(", fixed, re.MULTILINE)
        if not match:
            print("  [manim_coder] Healer returned no valid class — keeping originals.", flush=True)
            return previous_classes

        healed_class_name = match.group(1)
        fixed = _sanitize(fixed)

        new_classes = []
        for code_block in previous_classes:
            block_match = re.search(r"^class\s+(\w+)\s*\(", code_block, re.MULTILINE)
            if block_match and block_match.group(1) == healed_class_name:
                new_classes.append(fixed)
            else:
                new_classes.append(code_block)

        print(f"  [manim_coder] Healed class: {healed_class_name}.", flush=True)
        return new_classes

    except Exception as exc:
        print(f"  [manim_coder] Heal error: {exc}. Returning originals.", flush=True)
        return previous_classes
