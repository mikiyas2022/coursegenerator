"""
agents/template_orchestrator.py — Context-Aware 3B1B Template Orchestrator (v6)
=================================================================================
42 base templates + dynamic generation = 1000+ effective variations.
Uses TF-IDF cosine similarity to match templates to scenes.
Generates specialized variants via Template Generator Agent when needed.
Ensures sync-safe output and visual diversity.
"""

import os
import re
import glob
import random
import sys
import json
import math

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import get_llm, MANIM_CODER_MODEL
from logger import get_logger

log = get_logger("template_orchestrator")

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ─────────────────────────────────────────────────────────────────────────────
# Template metadata for TF-IDF matching
# ─────────────────────────────────────────────────────────────────────────────

TEMPLATE_DESCRIPTIONS = {
    "template_01": "hook intro cinematic title reveal curiosity question opener surprise",
    "template_02": "vector sweep rotating arrow decomposition angle trig force component",
    "template_03": "parabolic trace trajectory projectile motion arc dot path",
    "template_04": "formula reveal equation box explosion highlight circumscribe law",
    "template_05": "number ticker counter numberline sliding marker counting",
    "template_06": "sine cosine wave phase amplitude oscillation frequency",
    "template_07": "circle morph shape transformation formula abstraction geometry",
    "template_08": "worked example panel step-by-step calculation solution problem",
    "template_09": "side-by-side comparison contrast two concepts difference",
    "template_10": "graph transformation parameter slider function family curve",
    "template_11": "bullet reveal key takeaways list summary points text",
    "template_12": "geometric growth area scaling radius expansion live label",
    "template_13": "force diagram free body arrows newton physics weight normal",
    "template_14": "camera zoom scale reveal detail magnify close-up",
    "template_15": "energy bar conservation kinetic potential thermodynamics",
    "template_16": "bouncing analogy humorous metaphor playful object everyday",
    "template_17": "derivative tangent line slope calculus rate change instantaneous",
    "template_18": "lissajous spiral parametric trace polar coordinates curve",
    "template_19": "riemann sum integral rectangle area approximation calculus",
    "template_20": "summary closer checklist recap finale golden stars",
    "template_21": "exponential growth curve compound interest halflife decay",
    "template_22": "matrix grid linear transformation determinant eigenvector",
    "template_23": "pythagorean proof visual geometry triangle squares hypotenuse",
    "template_24": "probability tree branching outcomes statistics chance event",
    "template_25": "circuit battery wire resistor bulb current ohm electricity",
    "template_26": "pendulum oscillation simple harmonic motion period gravity",
    "template_27": "doppler wavefront frequency shift moving source sound",
    "template_28": "histogram bar chart statistics mean distribution data",
    "template_29": "unit circle angle sweep sin cos projection trig identity",
    "template_30": "grand finale orbit collapse starburst celebration closing",
    "template_31": "3d surface concentric ring contour multivariable field",
    "template_32": "silent intro title card no narration cinematic opening brand",
    "template_33": "always redraw tracker live coordinates dynamic label position",
    "template_34": "venn diagram intersection overlap set theory logic classification",
    "template_35": "before after split comparison simplification transformation",
    "template_36": "taylor series approximation polynomial convergence expansion",
    "template_37": "flowchart decision tree algorithm branching logic if else",
    "template_38": "wave interference superposition constructive destructive",
    "template_39": "step-by-step solve multi-line equation algebra derivation",
    "template_40": "area under curve integral fill accumulation density",
    "template_41": "chapter card episode divider section title silent transition",
    "template_42": "cross-section reveal layers structure anatomy internal",
}


def _tokenize(text: str) -> list[str]:
    """Simple word-level tokenizer."""
    return re.findall(r'[a-z0-9]+', text.lower())


def _build_tfidf_index():
    """Build a simple TF-IDF index over template descriptions."""
    docs = {}
    df = {}  # document frequency
    N = len(TEMPLATE_DESCRIPTIONS)

    for name, desc in TEMPLATE_DESCRIPTIONS.items():
        tokens = _tokenize(desc)
        docs[name] = tokens
        for token in set(tokens):
            df[token] = df.get(token, 0) + 1

    # Compute TF-IDF vectors
    vectors = {}
    for name, tokens in docs.items():
        tf = {}
        for t in tokens:
            tf[t] = tf.get(t, 0) + 1
        vec = {}
        for t, count in tf.items():
            idf = math.log(N / (1 + df.get(t, 0)))
            vec[t] = (count / len(tokens)) * idf
        vectors[name] = vec

    return vectors


def _cosine_sim(v1: dict, v2: dict) -> float:
    """Cosine similarity between two sparse vectors."""
    common = set(v1.keys()) & set(v2.keys())
    if not common:
        return 0.0
    dot = sum(v1[k] * v2[k] for k in common)
    mag1 = math.sqrt(sum(x * x for x in v1.values()))
    mag2 = math.sqrt(sum(x * x for x in v2.values()))
    if mag1 == 0 or mag2 == 0:
        return 0.0
    return dot / (mag1 * mag2)


# Pre-build the index at import time
_TFIDF_INDEX = _build_tfidf_index()


def _semantic_match(scene: dict, used_templates: list[str], top_k: int = 5) -> list[str]:
    """
    Use TF-IDF cosine similarity to find the best matching templates for a scene.
    Returns top-k template names, excluding recently used ones.
    """
    # Build query from all scene text
    query_text = " ".join([
        scene.get("concept", ""),
        scene.get("scene_name", ""),
        scene.get("visual", ""),
        scene.get("manim_visual_instructions", ""),
        scene.get("explanation", ""),
        " ".join(scene.get("sentences", [])[:3]),
        scene.get("worked_example", ""),
        json.dumps(scene.get("storyboard_plan", {})),
    ]).lower()

    query_tokens = _tokenize(query_text)
    if not query_tokens:
        return []

    # Build query TF vector
    tf = {}
    for t in query_tokens:
        tf[t] = tf.get(t, 0) + 1
    N = len(TEMPLATE_DESCRIPTIONS)
    query_vec = {}
    for t, count in tf.items():
        idf = math.log(N / 2)  # approximate
        query_vec[t] = (count / len(query_tokens)) * idf

    # Score all templates
    scores = []
    recent = set(used_templates[-4:])  # avoid last 4 templates
    for name, vec in _TFIDF_INDEX.items():
        if name in recent:
            continue
        sim = _cosine_sim(query_vec, vec)
        scores.append((sim, name))

    scores.sort(reverse=True)
    return [name for _, name in scores[:top_k]]


def _pick_template_smart(scene: dict, used_templates: list[str], all_paths: list[str]) -> str:
    """
    Context-aware template selection:
    1. Try TF-IDF semantic match
    2. Check storyboard_plan for recommended_template
    3. Fall back to random unused template
    """
    template_dir = os.path.join(PROJECT_ROOT, "manim_templates", "3b1b_style")

    # Check if visual designer recommended a template
    plan = scene.get("storyboard_plan", {})
    recommended = plan.get("recommended_template", "")
    if recommended:
        full = os.path.join(template_dir, f"{recommended}.py")
        if os.path.exists(full) and full not in used_templates[-3:]:
            return full

    # Semantic match
    matches = _semantic_match(scene, [os.path.basename(t).replace(".py", "") for t in used_templates])
    for match_name in matches:
        full = os.path.join(template_dir, f"{match_name}.py")
        if os.path.exists(full):
            return full

    # Fallback: random unused
    recent = set(used_templates[-4:])
    fresh = [t for t in all_paths if t not in recent]
    return random.choice(fresh) if fresh else random.choice(all_paths)


def _fix_sync_and_overflow(code: str) -> str:
    """
    Post-process: move self.clear() from inside voiceover blocks to before them.
    """
    import re as _re

    for indent_with, indent_clear in [(" {8}", " {12}"), (" {4}", " {8}")]:
        for quote in ['"', "'"]:
            pattern = (
                rf'({indent_with})(with self\.voiceover\(text={quote}[^{quote}]*{quote}\) as tracker:\n)'
                rf'\s{indent_clear}self\.clear\(\)\n'
            )
            code = _re.sub(pattern, r'\1self.clear()\n\1\2', code)

    return code


def _inject_narration(code: str, scene: dict, scene_name: str) -> str:
    """Replace class name and NARRATION_PLACEHOLDER tags with actual narration."""
    code = re.sub(r'class SceneTemplate\b', f'class {scene_name}', code)

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

    for i, sentence in enumerate(sentences):
        safe = sentence.replace('"', "'").replace("\\", "\\\\")
        code = code.replace(f"<NARRATION_PLACEHOLDER_{i}>", safe)
        code = code.replace("<NARRATION_PLACEHOLDER>", safe, 1)

    code = re.sub(r'<NARRATION_PLACEHOLDER_\d+>', "This is an important concept.", code)
    code = re.sub(r'<NARRATION_PLACEHOLDER>', "This is an important concept.", code)

    concept_short = scene.get("concept", "Physics")[:25].replace('"', "'")
    formulas = scene.get("latex_formulas", [])
    if formulas:
        formula_str = formulas[0].replace('"', "'")[:30]
        code = code.replace('"<NARRATION_PLACEHOLDER_0>"', f'"{formula_str}"')

    return code


def run_template_orchestrator(scenes: list[dict], mode: str = "3b1b") -> list[str]:
    """
    Context-aware template orchestrator.
    42 base templates + dynamic generation = 1000+ effective variations.
    """
    template_dir = os.path.join(PROJECT_ROOT, "manim_templates", "3b1b_style")
    all_templates = sorted(glob.glob(os.path.join(template_dir, "template_*.py")))

    if not all_templates:
        log.warning("No templates found — using fallback")
        return [_guaranteed_simple_fallback(s) for s in scenes]

    log.info(f"Template Orchestrator v6: {len(scenes)} scenes, "
             f"{len(all_templates)} base templates, TF-IDF matching enabled")

    generated = []
    used_templates = []

    # Always start with silent intro (template_32) if first scene is intro/hook
    first_concept = (scenes[0].get("scene_name", "") + scenes[0].get("concept", "")).lower()
    if any(kw in first_concept for kw in ["intro", "hook", "scene_1", "scene1"]):
        silent_intro = os.path.join(template_dir, "template_32.py")
        if os.path.exists(silent_intro):
            try:
                with open(silent_intro, "r", encoding="utf-8") as f:
                    intro_code = f.read()
                intro_code = _inject_narration(intro_code, scenes[0], "SilentIntro")
                intro_code = _fix_sync_and_overflow(intro_code)
                generated.append(intro_code)
                used_templates.append(silent_intro)
                log.info("Scene 0: SilentIntro → template_32.py (silent cinematic opener)")
            except Exception:
                pass

    for idx, scene in enumerate(scenes):
        scene_name = scene.get("scene_name", f"Scene{idx}")
        scene_name = re.sub(r'[^A-Za-z0-9_]', '_', scene_name)
        if not scene_name[0].isalpha():
            scene_name = "Scene_" + scene_name

        # Smart template selection
        selected = _pick_template_smart(scene, used_templates, all_templates)
        used_templates.append(selected)

        try:
            # Try dynamic generation for complex scenes
            specialized_code = None
            storyboard = scene.get("storyboard_plan", {})
            visual_reqs = storyboard.get("key_animations", [])
            mood = storyboard.get("color_arc", "curious and engaging")

            if visual_reqs and len(str(visual_reqs)) > 30:
                try:
                    from agents.template_generator import generate_specialized_template
                    specialized_code = generate_specialized_template(
                        base_template_path=selected,
                        concept=scene.get("concept", ""),
                        visual_requirements=" | ".join(visual_reqs) if isinstance(visual_reqs, list) else str(visual_reqs),
                        mood=str(mood),
                        objects_needed=storyboard.get("opening_visual", ""),
                    )
                except Exception as gen_exc:
                    log.debug(f"Dynamic generation skipped: {gen_exc}")

            if specialized_code:
                code = specialized_code
                log.info(f"Scene {idx+1}: {scene_name} → GENERATED variant of {os.path.basename(selected)}")
            else:
                with open(selected, "r", encoding="utf-8") as f:
                    code = f.read()
                log.info(f"Scene {idx+1}: {scene_name} → {os.path.basename(selected)}")

            code = _inject_narration(code, scene, scene_name)
            code = _fix_sync_and_overflow(code)
            generated.append(code)

        except Exception as exc:
            log.error(f"Template failed for {scene_name}: {exc}")
            generated.append(_guaranteed_simple_fallback(scene))

    return generated


def _guaranteed_simple_fallback(scene: dict) -> str:
    """Minimal working fallback."""
    name = re.sub(r'[^A-Za-z0-9_]', '_', scene.get("scene_name", "FallbackScene"))
    if not name[0].isalpha():
        name = "Scene_" + name
    concept = scene.get("concept", "Physics").replace('"', "'")
    sentences = scene.get("sentences", [f"Let's explore {concept}."])
    blocks = []
    for i, s in enumerate(sentences):
        s_safe = s.replace('"', "'").replace("\\", "\\\\")
        blocks.append(f'''        self.clear()
        with self.voiceover(text="{s_safe}") as tracker:
            t = latin_text(
                "{concept[:28]}",
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
