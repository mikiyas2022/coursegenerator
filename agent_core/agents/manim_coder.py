"""
agents/manim_coder.py — Manim Developer Agent

Translates enriched scene dicts into valid ManimCE Python classes using
manim-voiceover + the local MMS TTS service.

Key update (Obj 2): Every generated class MUST import and use theme.py
constants/utilities — no hardcoded colours or font strings.
"""

import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import get_llm
from langchain_core.messages import HumanMessage, SystemMessage

# ─────────────────────────────────────────────────────────────────────────────
# Script header (injected by critic.py before running manim)
# NOTE: theme.py path is substituted dynamically in critic._build_script()
# ─────────────────────────────────────────────────────────────────────────────
# This module only defines the TEMPLATE string used to build the real header.
SCRIPT_HEADER_TEMPLATE = '''import os, sys
os.environ["PATH"] = (
    "/tmp/stem_venv/bin:/Library/TeX/texbin:"
    "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
)
os.environ["HF_HOME"] = "/tmp/huggingface_cache"

# ── Theme & Manim ─────────────────────────────────────────────────────────────
sys.path.insert(0, "{agent_core_path}")
from theme import *          # AmharicEduScene, BG_COLOR, ACCENT_COLOR, ...
from manim import *

'''

# Keep MMS_SERVICE_HEADER as a fallback alias (used by older imports)
MMS_SERVICE_HEADER = SCRIPT_HEADER_TEMPLATE


# ─────────────────────────────────────────────────────────────────────────────
# System prompt — Obj 2: enforce theme.py usage in ALL generated code
# ─────────────────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are a senior ManimCE developer generating production-ready animation code.
The theme module is ALREADY imported. You MUST use its utilities to save time.

ABSOLUTE RULES — breaking any rule causes a runtime crash:
1. Import ONLY from `manim`. Do NOT re-import manim or theme.
2. DO NOT write setup boilerplate. You must inherit exactly from AmharicEduScene.
   Example: `class Scene1(AmharicEduScene):`
3. Amharic Ge'ez text: Use the built-in helper `self.show_text("ሰላም", position=UP)`.
   NEVER use Tex(), MathTex(), or Text() directly for Ge'ez script.
4. Latin/Math: MathTex(r"F = ma", color=FORMULA_COLOR, font_size=FONT_SIZE_MATH)
5. ALWAYS use `self.tracker.duration` for ALL run_time values inside voiceover blocks:
     with self.voiceover(text="...Amharic...") as tracker:
         self.play(Create(obj), run_time=tracker.duration * 0.8)
         self.wait(tracker.duration * 0.2)
6. Spatial safety: use clamp_to_screen(mob) on any Mobject placed near edges
7. Use branded_axes() instead of raw Axes()
8. Use branded_vector() instead of raw Arrow() for vectors
9. Use ValueTracker + always_redraw for continuous/parametric animations
10. Generate ONE class per scene. Name it EXACTLY as given.
11. Output ONLY raw Python class code. NO markdown fences. NO explanations.

AVAILABLE THEME API (all in scope via `from theme import *`):
  Colors: BG_COLOR, PRIMARY_COLOR, ACCENT_COLOR, FORMULA_COLOR, TEXT_COLOR,
          MUTED_COLOR, WARNING_COLOR, VECTOR_COLOR, HIGHLIGHT_COLOR, GRID_COLOR
  Sizes:  FONT_SIZE_TITLE, FONT_SIZE_HEADER, FONT_SIZE_BODY, FONT_SIZE_LABEL, FONT_SIZE_MATH
  Fonts:  FONT_AMHARIC="Nyala", FONT_LATIN="Inter"
  fns:    setup_scene(self), amharic_text("ሰላም"), latin_text("Physics"),
          title_card(amharic, latin), formula_box(r"F=ma"), branded_axes(),
          branded_vector(), branded_circle(), section_divider(), clamp_to_screen(mob)

CORRECT TEMPLATE:
class Scene1_Example(VoiceoverScene):
    def construct(self):
        setup_scene(self)
        self.set_speech_service(LocalMMSService(persona_id=1))

        heading = title_card("ሰላም ልጆች", "Introduction")
        self.add(heading)

        with self.voiceover(text="ሰላም ልጆች፣ ዛሬ ፒታጎረስን እናያለን።") as tracker:
            formula = formula_box(r"a^2 + b^2 = c^2")
            clamp_to_screen(formula)
            self.play(Write(formula[1]), Create(formula[0]), run_time=tracker.duration * 0.85)
            self.wait(tracker.duration * 0.15)
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
    Generate ManimCE scene classes.

    Args:
        scenes:          Enriched scene dicts from scriptwriter.
        persona_id:      Voice persona (1–5) for LocalMMSService.
        error_context:   Manim traceback string (syntax self-heal).
        visual_feedback: VL model critique string (visual self-heal).
        previous_code:   Previous generated classes (needed for healing).

    Returns:
        List of Python class code strings (one per scene).
    """
    llm = get_llm(temperature=0.05)

    if (error_context or visual_feedback) and previous_code:
        combined_error = "\n".join(filter(None, [error_context, visual_feedback]))
        return _heal_code(llm, previous_code, combined_error)

    class_strings = []
    for scene in scenes:
        class_code = _generate_scene_class(llm, scene, persona_id)
        class_strings.append(class_code)

    print(f"  [manim_coder] Generated {len(class_strings)} theme-aware scene classes.", flush=True)
    return class_strings


# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────────────────────

def _generate_scene_class(llm, scene: dict, persona_id: int) -> str:
    formulas_str = ", ".join(scene.get("latex_formulas", [])) or "None"

    user_prompt = f"""Generate a ManimCE VoiceoverScene class for this educational scene.

Class name:       {scene["scene_name"]}
Concept:          {scene["concept"]}
Visual Plan:      {scene["visual"]}
Amharic Script:   {scene["amharic_script"]}
LaTeX Formulas:   {formulas_str}
Persona ID:       {persona_id}

REMINDER: use theme API (amharic_text, formula_box, branded_axes, etc), setup_scene(self) first.
Output ONLY the Python class definition."""

    try:
        response = llm.invoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ])
        code = response.content.strip()
        code = re.sub(r"^```(?:python)?", "", code, flags=re.MULTILINE).strip()
        code = re.sub(r"```$",            "", code, flags=re.MULTILINE).strip()
        return code

    except Exception as exc:
        print(f"  [manim_coder] LLM error for {scene['scene_name']}: {exc}", flush=True)
        name = scene["scene_name"]
        text = scene.get("amharic_script", "ምንም ዓይነት ንግግር አልተሰጠም።")[:100]
        concept = scene.get("concept", "Scene").replace('"', "'")
        return f"""
class {name}(VoiceoverScene):
    def construct(self):
        setup_scene(self)
        self.set_speech_service(LocalMMSService(persona_id={persona_id}))
        heading = title_card("{concept}")
        self.add(heading)
        with self.voiceover(text="{text}") as tracker:
            self.play(Write(heading), run_time=tracker.duration)
"""


def _heal_code(llm, previous_classes: list[str], error: str) -> list[str]:
    """Self-heal: ask the LLM to fix both runtime and visual errors."""
    print(f"  [manim_coder] Healing — error: {error[:200]}", flush=True)

    # If the error output says which scene failed, extract it. Usually critic passes single scene tracebacks.
    full_code_context = "\n\n".join(previous_classes)
    
    user_prompt = f"""The following ManimCE code produced an error. 
Identify which class is causing the error, and rewrite ONLY that specific class to fix it.

ERROR:
{error[:1800]}

FULL SCRIPT CONTEXT:
{full_code_context}

Output ONLY the completely corrected Python `class ...` block for the single class that failed.
Do not output the other classes. No markdown fences. No explanations."""

    try:
        response = llm.invoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ])
        fixed = response.content.strip()
        fixed = re.sub(r"^```(?:python)?", "", fixed, flags=re.MULTILINE).strip()
        fixed = re.sub(r"```$",            "", fixed, flags=re.MULTILINE).strip()

        # Find which class the LLM returned
        match = re.search(r"^class\s+(\w+)\s*\(", fixed, re.MULTILINE)
        if not match:
            print("  [manim_coder] Healer did not return a valid class. Using original.", flush=True)
            return previous_classes
            
        healed_class_name = match.group(1)
        
        # Substitute the healed class back into the array
        new_classes = []
        for code_block in previous_classes:
            block_match = re.search(r"^class\s+(\w+)\s*\(", code_block, re.MULTILINE)
            if block_match and block_match.group(1) == healed_class_name:
                new_classes.append(fixed)
            else:
                new_classes.append(code_block)

        print(f"  [manim_coder] Successfully healed class: {healed_class_name}.", flush=True)
        return new_classes

    except Exception as exc:
        print(f"  [manim_coder] Heal LLM error: {exc}. Returning original.", flush=True)
        return previous_classes
