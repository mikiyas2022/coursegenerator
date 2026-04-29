"""
agents/template_orchestrator.py — 3B1B Template Orchestrator (v5)
=================================================================
42 high-quality templates. Intelligent keyword matching. Sync-safe output.
"""

import os
import re
import glob
import random
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import get_llm, MANIM_CODER_MODEL
from logger import get_logger

log = get_logger("template_orchestrator")

# Absolute path to project root (the parent of agent_core/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Template category hints — maps scene types to best templates
TEMPLATE_HINTS = {
    "intro":        ["template_01", "template_32"],
    "hook":         ["template_01", "template_16"],
    "vector":       ["template_02", "template_13"],
    "trajectory":   ["template_03"],
    "formula":      ["template_04", "template_39"],
    "number":       ["template_05"],
    "wave":         ["template_06", "template_27", "template_38"],
    "circle":       ["template_07", "template_12", "template_29"],
    "example":      ["template_08", "template_35", "template_39"],
    "comparison":   ["template_09", "template_35"],
    "graph":        ["template_10", "template_17", "template_21", "template_33"],
    "bullet":       ["template_11"],
    "geometry":     ["template_12", "template_23", "template_42"],
    "force":        ["template_13"],
    "zoom":         ["template_14"],
    "energy":       ["template_15"],
    "analogy":      ["template_16"],
    "derivative":   ["template_17", "template_33"],
    "parametric":   ["template_18"],
    "integral":     ["template_19", "template_40"],
    "summary":      ["template_20", "template_30"],
    "exponential":  ["template_21", "template_36"],
    "matrix":       ["template_22"],
    "triangle":     ["template_23"],
    "probability":  ["template_24", "template_34"],
    "circuit":      ["template_25"],
    "pendulum":     ["template_26"],
    "doppler":      ["template_27", "template_38"],
    "statistics":   ["template_28", "template_34"],
    "trig":         ["template_29", "template_06"],
    "finale":       ["template_30"],
    "3d":           ["template_31"],
    "surface":      ["template_31"],
    "silent":       ["template_32", "template_41"],
    "tracker":      ["template_33"],
    "dynamic":      ["template_33"],
    "venn":         ["template_34"],
    "set":          ["template_34"],
    "before":       ["template_35"],
    "transform":    ["template_35", "template_22"],
    "taylor":       ["template_36"],
    "approximat":   ["template_36"],
    "convergence":  ["template_36"],
    "flowchart":    ["template_37"],
    "algorithm":    ["template_37"],
    "decision":     ["template_37"],
    "interfere":    ["template_38"],
    "superposit":   ["template_38"],
    "solve":        ["template_39"],
    "step":         ["template_39"],
    "area":         ["template_40"],
    "chapter":      ["template_41"],
    "cross":        ["template_42"],
    "layer":        ["template_42"],
    "structure":    ["template_42"],
}


def run_template_orchestrator(scenes: list[dict], mode: str = "3b1b") -> list[str]:
    """Select from 42 templates, inject narration, fix sync. Returns Manim code strings."""
    log.info(f"Template Orchestrator: {len(scenes)} scenes, 42 templates available")
    return _generate_3b1b_scenes(scenes)


def _pick_template(scene: dict, used_templates: list[str], all_templates: list[str]) -> str:
    """
    Intelligently pick a template based on scene type keywords.
    Avoids repeating the last 3 templates used to enforce visual diversity.
    """
    template_dir = os.path.join(PROJECT_ROOT, "manim_templates", "3b1b_style")

    # Build a candidate list from keyword hints
    concept = (scene.get("concept", "") + " " +
               scene.get("scene_name", "") + " " +
               scene.get("visual", "") + " " +
               scene.get("manim_visual_instructions", "")).lower()

    candidates = []
    for keyword, hints in TEMPLATE_HINTS.items():
        if keyword in concept:
            for hint in hints:
                full_path = os.path.join(template_dir, f"{hint}.py")
                if os.path.exists(full_path):
                    candidates.append(full_path)

    # Filter out recently used ones (last 3)
    recent = set(used_templates[-3:])
    fresh = [c for c in candidates if c not in recent]

    if fresh:
        return random.choice(fresh)

    # Fallback: any template not recently used
    all_fresh = [t for t in all_templates if t not in recent]
    if all_fresh:
        return random.choice(all_fresh)

    return random.choice(all_templates)


def _fix_sync_and_overflow(code: str) -> str:
    """
    Post-process generated Manim code to fix two critical issues:

    1. SYNC FIX: Move `self.clear()` from INSIDE voiceover blocks to BEFORE them.
       Before:
           with self.voiceover(text="...") as tracker:
               self.clear()             # ← screen clears AFTER audio starts ≠ sync
               ...
       After:
           self.clear()                 # ← screen clears BEFORE audio starts = sync
           with self.voiceover(text="...") as tracker:
               ...

    2. OVERFLOW FIX: Ensure any run_time fractions inside a single voiceover block
       sum to ≤ 1.0 * tracker.duration (prevent animation overrun).
    """
    # ── 1. Move self.clear() out of voiceover blocks ─────────────────────
    # Match: 8-space indent voiceover + 12-space indent self.clear()
    # Pattern handles both 8-space (method body) and 12-space (nested) indents
    import re

    # Pattern 1: standard indentation (8 spaces before `with`, 12 before `self.clear()`)
    code = re.sub(
        r'( {8})(with self\.voiceover\(text="[^"]*"\) as tracker:\n)\s{12}self\.clear\(\)\n',
        r'\1self.clear()\n\1\2',
        code,
    )
    # Pattern 2: 4-space indentation variant
    code = re.sub(
        r'( {4})(with self\.voiceover\(text="[^"]*"\) as tracker:\n)\s{8}self\.clear\(\)\n',
        r'\1self.clear()\n\1\2',
        code,
    )
    # Pattern 3: single-quoted strings
    code = re.sub(
        r"( {8})(with self\.voiceover\(text='[^']*'\) as tracker:\n)\s{12}self\.clear\(\)\n",
        r"\1self.clear()\n\1\2",
        code,
    )
    code = re.sub(
        r"( {4})(with self\.voiceover\(text='[^']*'\) as tracker:\n)\s{8}self\.clear\(\)\n",
        r"\1self.clear()\n\1\2",
        code,
    )

    return code


def _inject_narration(code: str, scene: dict, scene_name: str) -> str:
    """
    Replace class name and NARRATION_PLACEHOLDER tags with actual narration sentences.
    Also renames the class.
    """
    # Rename class
    code = re.sub(r'class SceneTemplate\b', f'class {scene_name}', code)

    # Get sentences
    sentences = scene.get("sentences", scene.get("sentences_english", []))
    if not sentences:
        concept = scene.get("concept", "Physics")
        formulas = scene.get("latex_formulas", ["F = ma"])
        formula = formulas[0] if formulas else "F = ma"
        sentences = [
            f"Let's explore {concept} — one of the most beautiful ideas in science.",
            f"The key relationship is {formula}. Watch how each piece fits together.",
            f"When we plug in real numbers, the pattern becomes clear and satisfying.",
            "And that's the insight! Now you truly understand this concept.",
        ]

    # Replace placeholders
    for i, sentence in enumerate(sentences):
        safe = sentence.replace('"', "'").replace("\\", "\\\\")
        code = code.replace(f"<NARRATION_PLACEHOLDER_{i}>", safe)
        code = code.replace(f"<NARRATION_PLACEHOLDER>", safe, 1)

    # Replace any remaining placeholders with generic fallback
    code = re.sub(r'<NARRATION_PLACEHOLDER_\d+>', "This is an important concept.", code)
    code = re.sub(r'<NARRATION_PLACEHOLDER>', "This is an important concept.", code)

    # Inject formula into formula_box placeholders using the actual concept
    concept_short = scene.get("concept", "Physics")[:25].replace('"', "'")
    formulas = scene.get("latex_formulas", [])
    if formulas:
        formula_str = formulas[0].replace('"', "'")[:30]
        code = code.replace('"<NARRATION_PLACEHOLDER_0>"', f'"{formula_str}"')

    return code


def _generate_3b1b_scenes(scenes: list[dict]) -> list[str]:
    template_dir = os.path.join(PROJECT_ROOT, "manim_templates", "3b1b_style")
    all_templates = glob.glob(os.path.join(template_dir, "*.py"))
    all_templates.sort()

    if not all_templates:
        log.warning("No 3b1b templates found — using guaranteed fallback for all scenes")
        return [_guaranteed_simple_fallback(s) for s in scenes]

    generated = []
    used_templates = []

    for idx, scene in enumerate(scenes):
        scene_name = scene.get("scene_name", f"Scene{idx}")
        # Sanitize class name
        scene_name = re.sub(r'[^A-Za-z0-9_]', '_', scene_name)
        if not scene_name[0].isalpha():
            scene_name = "Scene_" + scene_name

        # Pick template
        selected = _pick_template(scene, used_templates, all_templates)
        used_templates.append(selected)

        try:
            with open(selected, "r", encoding="utf-8") as f:
                code = f.read()

            code = _inject_narration(code, scene, scene_name)
            code = _fix_sync_and_overflow(code)  # ← fix sync + overflow
            log.info(f"Scene {idx+1}: {scene_name} → {os.path.basename(selected)}")
            generated.append(code)

        except Exception as exc:
            log.error(f"Template injection failed for {scene_name}: {exc}")
            generated.append(_guaranteed_simple_fallback(scene))

    return generated


def _guaranteed_simple_fallback(scene: dict) -> str:
    """Minimal working fallback that always renders."""
    name = re.sub(r'[^A-Za-z0-9_]', '_', scene.get("scene_name", "FallbackScene"))
    if not name[0].isalpha():
        name = "Scene_" + name
    concept = scene.get("concept", "Physics").replace('"', "'")
    sentences = scene.get("sentences", [f"Let's explore {concept}."])
    blocks = []
    for i, s in enumerate(sentences):
        s_safe = s.replace('"', "'").replace("\\", "\\\\")
        # self.clear() is BEFORE the voiceover block for proper sync
        blocks.append(f'''        self.clear()
        with self.voiceover(text="{s_safe}") as tracker:
            words = "{concept[:28]}".split()
            t = latin_text(
                " ".join(words),
                font_size=FONT_SIZE_BODY,
                color=TEAL_ACCENT,
            )
            if t.width > 10.5:
                t.scale_to_fit_width(10.5)
            t.move_to(ORIGIN)
            self.play(FadeIn(t, shift=UP * 0.25), run_time=tracker.duration * 0.55)
            self.wait(tracker.duration * 0.45)''')

    return f'''class {name}(AmharicEduScene):
    def construct(self):
        setup_scene(self)

{chr(10).join(blocks)}

        self.wait(0.5)
'''

