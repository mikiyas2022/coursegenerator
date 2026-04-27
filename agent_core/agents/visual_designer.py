"""
agents/visual_designer.py — Visual Storyboard Designer Agent (NEW)

Runs AFTER the Scriptwriter and BEFORE the Manim Coder.

Its sole job: produce a detailed visual storyboard plan per scene that captures
the 3B1B magic:
  • Which metaphor / object represents the concept
  • Which shapes morph into what (morph_sequence)
  • Camera choreography (zoom-in, pan, restore)
  • Playful humor beats (bouncing numbers, surprised emoji transforms, etc.)
  • Color choices specific to this scene's emotional arc
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
# System prompt
# ─────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a world-class visual storyboard director for educational math/physics videos
in the style of 3Blue1Brown (Grant Sanderson).

Your job is NOT to write Manim code. Your job is to write a rich VISUAL PLAN for each scene.
Think like a film director meets a math educator: every object on screen must MEAN something,
every movement must TEACH something, and every playful moment must make the viewer smile.

For EACH scene, produce a JSON object with these keys:

{
  "scene_name": "...",
  "metaphor_chain": "The everyday object or story that represents this concept. E.g. 'a stretched rubber band' for potential energy.",
  "opening_visual": "What appears first on screen and how. E.g. 'A blank canvas, then a single glowing dot pops in with a bounce.'",
  "morph_sequence": [
    {"from": "Circle", "to": "Ellipse", "meaning": "mass concentrating"},
    {"from": "Arrow pointing UP", "to": "Arrow pointing RIGHT", "meaning": "direction of force changes"}
  ],
  "camera_moves": [
    {"type": "zoom_in", "target": "formula box", "when": "after equation appears"},
    {"type": "pan_right", "target": "graph region", "when": "during velocity buildup"},
    {"type": "restore", "when": "before summary"}
  ],
  "humor_beats": [
    "Numbers bounce in surprise when the acceleration doubles",
    "A tiny running person icon appears below the velocity vector"
  ],
  "color_arc": "Start with cool blues (confusion), transition to warm gold/teal (understanding), end on bright teal (mastery).",
  "aha_moment": "When the two vectors add up to the resultant — the final arrow glows gold for 1 second.",
  "key_animations": [
    "ValueTracker for angle sweep from 0 to 45 degrees",
    "always_redraw for the force decomposition arrows",
    "Circumscribe the final formula in teal"
  ]
}

RULES:
1. Be SPECIFIC — name exact Manim objects (Arrow, Circle, VGroup, NumberPlane, etc.)
2. Be PLAYFUL — add at least one humor beat per scene
3. Be EMOTIONAL — describe the 'aha!' moment explicitly
4. Keep it ACHIEVABLE with ManimCE v0.20.1 constraints (no WebGL, no 3D)
5. Output ONLY a JSON array of scene objects. No markdown. No explanation."""


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def run_visual_designer(scenes: list[dict]) -> list[dict]:
    """
    Enrich each scene with a detailed visual storyboard plan.
    Returns scenes with added 'storyboard_plan' key.
    Graceful: on any failure, passes scene through with a minimal plan.
    """
    llm = get_llm(model_name=VISUAL_DESIGNER_MODEL, temperature=0.4, max_tokens=3000)

    scene_summaries = []
    for s in scenes:
        scene_summaries.append({
            "scene_name": s.get("scene_name", ""),
            "concept": s.get("concept", ""),
            "explanation": s.get("explanation", ""),
            "latex_formulas": s.get("latex_formulas", []),
            "visual_hint": s.get("visual", s.get("manim_visual_instructions", "")),
            "sentences": s.get("sentences", [])[:3],  # first 3 for context
        })

    user_prompt = f"""Here are {len(scenes)} educational scenes about STEM topics.
Create a detailed 3B1B-quality visual storyboard plan for EACH scene.

SCENES:
{json.dumps(scene_summaries, ensure_ascii=False, indent=2)}

For each scene, produce a storyboard object following the schema in your instructions.
Output a JSON ARRAY of {len(scenes)} storyboard objects, in the same order as the input scenes.
Start immediately with [ and end with ]."""

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
        if len(plans) != len(scenes):
            log.warning(
                f"Visual designer returned {len(plans)} plans for {len(scenes)} scenes — padding."
            )
            # Pad or truncate to match
            while len(plans) < len(scenes):
                plans.append(_minimal_plan(scenes[len(plans)]))

        for scene, plan in zip(scenes, plans):
            enriched.append({**scene, "storyboard_plan": plan})

        log.info(f"Visual designer produced storyboard plans for {len(enriched)} scenes.")

    except Exception as exc:
        log.error(f"Visual designer failed ({exc}) — using minimal plans for all scenes.")
        for scene in scenes:
            enriched.append({**scene, "storyboard_plan": _minimal_plan(scene)})

    return enriched


def _minimal_plan(scene: dict) -> dict:
    """Fallback storyboard plan when LLM fails."""
    concept = scene.get("concept", "STEM concept")
    return {
        "scene_name": scene.get("scene_name", "Scene"),
        "metaphor_chain": f"{concept} is like a growing tree — each branch adds to the whole.",
        "opening_visual": "Blank dark canvas. A glowing teal dot appears at center, then expands.",
        "morph_sequence": [
            {"from": "Dot", "to": "Circle", "meaning": "concept growing"},
            {"from": "Circle", "to": "Formula", "meaning": "abstraction emerging"},
        ],
        "camera_moves": [
            {"type": "zoom_in", "target": "key formula", "when": "after equation appears"},
            {"type": "restore", "when": "before summary"},
        ],
        "humor_beats": [
            "Numbers wiggle when they first appear",
            "A tiny star emoji flashes at the 'aha!' moment",
        ],
        "color_arc": "Start with muted blues, peak with bright gold at the aha moment, settle on teal.",
        "aha_moment": "The formula glows golden for 1 second with a Circumscribe animation.",
        "key_animations": [
            "ValueTracker for the main variable",
            "always_redraw for dependent quantities",
            "Circumscribe(formula, color=STAR_YELLOW)",
        ],
    }
