"""
agents/visual_designer.py — Visual Storyboard Director Agent (v4 — 42 Templates)

Runs AFTER Scriptwriter, BEFORE Template Orchestrator.
Produces detailed visual plans per scene, guiding the context-aware template selection.
Now aware of all 42 base templates + dynamic generation capability.
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
# System prompt — full 42-template vocabulary + camera choreography
# ─────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a world-class visual storyboard director for 3Blue1Brown–quality educational videos.
Your job: write a richly detailed VISUAL PLAN per scene. NOT Manim code — a DIRECTOR'S BRIEF.

AVAILABLE TEMPLATE CATEGORIES (42 templates — choose ONE per scene, vary across episode):
01-HOOK: Cinematic title, big ?, curiosity burst
02-VECTOR: Rotating arrow decomposition, angle sweep
03-TRAJECTORY: Parabolic TracedPath, projectile
04-FORMULA: Box → highlight → circumscribe → burst
05-NUMBER: NumberLine + sliding marker + count-up
06-WAVE: Sine/cosine phase ValueTracker
07-CIRCLE MORPH: Circle→formula ReplacementTransform
08-WORKED EXAMPLE: Two-panel step-by-step
09-COMPARISON: Side-by-side with bridge arrow
10-GRAPH TRANSFORM: ValueTracker parameter slider
11-BULLETS: Animated text list with accents
12-GEOMETRIC GROWTH: Circle + area ValueTracker
13-FORCE DIAGRAM: Rectangle + Arrow forces
14-CAMERA ZOOM: Zoom in → reveal → pull back
15-ENERGY BARS: KE/PE bars animate
16-ANALOGY: Bouncing object → concept morph
17-DERIVATIVE: Moving tangent line on curve
18-PARAMETRIC: Lissajous/spiral TracedPath
19-RIEMANN: Bars → integral convergence
20-SUMMARY: Checklist + finale explosion
21-EXPONENTIAL: Growing curve
22-MATRIX: apply_matrix grid transform
23-PYTHAGOREAN: Triangle + squares proof
24-PROBABILITY TREE: Branching outcomes
25-CIRCUIT: Battery → wire → glowing bulb
26-PENDULUM: Swinging bob always_redraw
27-DOPPLER: Expanding wavefronts
28-HISTOGRAM: Bars + mean line
29-UNIT CIRCLE: Angle sweep, sin/cos
30-FINALE: Orbiting formulas → collapse
31-3D SURFACE: Concentric rings, field visualization
32-SILENT INTRO: Cinematic title card (NO narration)
33-TRACKER: always_redraw live coordinate labels
34-VENN: Overlapping circles, set intersection
35-BEFORE/AFTER: Split-screen comparison
36-TAYLOR: Successive polynomial approximations
37-FLOWCHART: Decision tree with branches
38-WAVE INTERFERENCE: Superposition of two waves
39-STEP-BY-STEP: Multi-line equation solving
40-AREA FILL: Integral fill under curve
41-CHAPTER CARD: Silent section divider
42-CROSS-SECTION: Layered structure reveal

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
  "color_arc": "Emotional color journey with specific theme colors",
  "aha_moment": "Exact visual description of the aha moment",
  "key_animations": [
    "Specific ManimCE animation type and object"
  ],
  "timing_note": "Which parts are fast vs slow"
}

RULES:
1. VARY templates — no two consecutive scenes use same template
2. Be SPECIFIC — name exact Manim objects, colors, coordinates
3. Every scene needs ONE humor beat and ONE explicit aha moment
4. First scene should use template_32 (silent intro) for cinematic opening
5. Last scene should use template_20 or template_30 (summary/finale)
6. Use at least 8 DIFFERENT templates across an episode
7. Output ONLY a JSON array. No markdown. No explanation."""


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
    idx = hash(concept) % 42 + 1
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
