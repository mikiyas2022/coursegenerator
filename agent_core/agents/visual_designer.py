"""
agents/visual_designer.py — Visual Storyboard Director Agent (v3 — 3B1B Masterpiece)

Runs AFTER Scriptwriter, BEFORE Manim Coder.
Produces a detailed visual plan per scene, guiding template selection and animation.
Now enforces 30-template vocabulary awareness and MovingCameraScene choreography.
"""

import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import get_llm, VISUAL_DESIGNER_MODEL
from logger import get_logger
from utils import safe_json_loads

from langchain_core.messages import HumanMessage, SystemMessage

log = get_logger("visual_designer")

# ─────────────────────────────────────────────────────────────────────────────
# System prompt — full 30-template vocabulary + camera choreography
# ─────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a world-class visual storyboard director for 3Blue1Brown–quality educational videos.
Your job: write a richly detailed VISUAL PLAN per scene. NOT Manim code — a DIRECTOR'S BRIEF.

AVAILABLE TEMPLATE CATEGORIES (choose ONE per scene, vary across episode):
- HOOK/INTRO: Cinematic title reveal, big question mark, curiosity burst (template_01)
- VECTOR: Rotating vector + decomposition arrows, angle sweep (template_02)
- TRAJECTORY: Parabolic TracedPath, projectile dot, peak glow (template_03)
- FORMULA: Box appears → term highlight → circumscribe → explosion burst (template_04)
- NUMBER: NumberLine + sliding triangle marker + count-up (template_05)
- WAVE: Sine/cosine with phase ValueTracker, amplitude label (template_06)
- CIRCLE MORPH: Circle→formula ReplacementTransform (template_07)
- WORKED EXAMPLE: Two-panel layout, step-by-step calculation (template_08)
- COMPARISON: Side-by-side circles with DoubleArrow bridge (template_09)
- GRAPH TRANSFORM: plot f(x) → ValueTracker 'a' parameter changes shape (template_10)
- BULLETS: Animated text list, accent bars fly in (template_11)
- GEOMETRIC GROWTH: Circle radius ValueTracker + area label (template_12)
- FORCE DIAGRAM: Rectangle body + Arrow forces + labels (template_13)
- CAMERA ZOOM: MovingCamera zoom in → reveal → pull back (template_14)
- ENERGY BAR: KE/PE bars animate with ValueTracker (template_15)
- ANALOGY: Bouncing ball/object → transforms to concept (template_16)
- DERIVATIVE: Moving tangent line on curve (template_17)
- PARAMETRIC: Lissajous/spiral TracedPath (template_18)
- RIEMANN: Bars under curve → n increases → integral (template_19)
- SUMMARY: Checklist + finale explosion (template_20)
- EXPONENTIAL: Growing e^x curve with ValueTracker (template_21)
- MATRIX: NumberPlane apply_matrix transform (template_22)
- PYTHAGOREAN: Right triangle + squares proof (template_23)
- PROBABILITY TREE: Branching diagram with labels (template_24)
- CIRCUIT: Battery → wire → resistor → glowing bulb (template_25)
- PENDULUM: Swinging bob with always_redraw (template_26)
- DOPPLER: Wavefronts with moving source (template_27)
- HISTOGRAM: Animated bars + mean line (template_28)
- UNIT CIRCLE: Angle sweep, sin/cos projections (template_29)
- FINALE: Multiple formulas orbit center → collapse → starburst (template_30)

For EACH scene, output a JSON object:
{
  "scene_name": "...",
  "recommended_template": "template_XX",
  "metaphor_chain": "The everyday animatable object/story that represents this concept",
  "opening_visual": "Exact first frame description: what appears, how, where",
  "morph_sequence": [
    {"from": "Circle", "to": "Formula box", "meaning": "abstraction emerging"}
  ],
  "camera_moves": [
    {"type": "zoom_in", "target": "formula", "when": "after equation appears"},
    {"type": "restore", "when": "before summary"}
  ],
  "humor_beats": [
    "Specific funny moment — exactly what happens on screen"
  ],
  "color_arc": "Emotional color journey: start→peak→end with specific colors from theme",
  "aha_moment": "Exact visual description of the aha moment — what glows, what transforms",
  "key_animations": [
    "Specific ManimCE animation type and object"
  ],
  "timing_note": "Which sentences are fast vs slow, where camera should pause"
}

RULES:
1. VARY templates across scenes — no two consecutive scenes use same template
2. Be SPECIFIC — name exact Manim objects, colors, coordinates
3. Every scene needs ONE humor beat and ONE explicit aha moment
4. Use MovingCameraScene camera moves for at least 2 scenes per episode
5. Output ONLY a JSON array. No markdown. No explanation."""


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def run_visual_designer(scenes: list[dict]) -> list[dict]:
    """
    Enrich each scene with a detailed 3B1B visual storyboard plan.
    Returns scenes with added 'storyboard_plan' key.
    """
    llm = get_llm(model_name=VISUAL_DESIGNER_MODEL, temperature=0.42, max_tokens=3500)

    scene_summaries = []
    for s in scenes:
        scene_summaries.append({
            "scene_name": s.get("scene_name", ""),
            "concept": s.get("concept", ""),
            "explanation": s.get("explanation", ""),
            "latex_formulas": s.get("latex_formulas", []),
            "visual_hint": s.get("visual", s.get("manim_visual_instructions", "")),
            "sentences": s.get("sentences", [])[:4],  # first 4 sentences for context
            "worked_example": s.get("worked_example", ""),
        })

    user_prompt = f"""Here are {len(scenes)} educational scenes about STEM topics.
Create a richly detailed 3B1B-quality visual storyboard plan for EACH scene.
Use a DIFFERENT template category for each consecutive scene.
Include camera choreography for at least 2 scenes.
Ensure every scene has: humor beat, aha moment, specific color arc.

SCENES:
{json.dumps(scene_summaries, ensure_ascii=False, indent=2)}

Output a JSON ARRAY of {len(scenes)} storyboard objects. Start with [ and end with ]."""

    enriched = []
    try:
        response = llm.invoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ])
        raw = response.content.strip()
        plans = safe_json_loads(raw)

        if not isinstance(plans, list):
            raise ValueError(f"Expected list, got {type(plans)}")

        # Pad if needed
        while len(plans) < len(scenes):
            plans.append(_minimal_plan(scenes[len(plans)]))

        for scene, plan in zip(scenes, plans):
            enriched.append({**scene, "storyboard_plan": plan})

        log.info(f"Visual designer produced {len(enriched)} storyboard plans.")

    except Exception as exc:
        log.error(f"Visual designer failed ({exc}) — using minimal plans for all scenes.")
        for scene in scenes:
            enriched.append({**scene, "storyboard_plan": _minimal_plan(scene)})

    return enriched


def _minimal_plan(scene: dict) -> dict:
    """Fallback storyboard plan when LLM fails."""
    concept = scene.get("concept", "STEM concept")
    idx = hash(concept) % 30 + 1
    return {
        "scene_name": scene.get("scene_name", "Scene"),
        "recommended_template": f"template_{idx:02d}",
        "metaphor_chain": f"{concept} is like a river — always flowing toward the lowest point.",
        "opening_visual": "Blank dark canvas. A glowing teal dot appears at center, expands into title.",
        "morph_sequence": [
            {"from": "Dot", "to": "Circle", "meaning": "concept expanding"},
            {"from": "Circle", "to": "Formula box", "meaning": "abstraction emerging"},
        ],
        "camera_moves": [
            {"type": "zoom_in", "target": "key formula", "when": "after equation appears"},
            {"type": "restore", "when": "before summary"},
        ],
        "humor_beats": [
            "Numbers bounce in surprise when the value doubles unexpectedly",
        ],
        "color_arc": "Start with muted blues (confusion), peak with bright gold at aha, settle on teal (mastery).",
        "aha_moment": "The formula glows golden for 1.5 seconds with Circumscribe + glow_dot burst.",
        "key_animations": [
            "ValueTracker for main variable",
            "always_redraw for dependent quantity",
            "Circumscribe(formula, color=STAR_YELLOW)",
        ],
        "timing_note": "Slow down at aha moment. Speed up during number counting.",
    }
