"""
agents/scriptwriter.py — English Scriptwriter Agent (v6 — No Translation)
==========================================================================
Writes expressive English narration scripts for 3B1B-style educational videos.
No translation — scripts go directly to EdgeTTS English neural voice.
"""

import json
import re
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import get_llm, SCRIPTWRITER_MODEL
from logger import get_logger
from langchain_core.messages import HumanMessage, SystemMessage
from utils import safe_json_loads

log = get_logger("scriptwriter")


# ─────────────────────────────────────────────────────────────────────────────
# System prompt for narration generation
# ─────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are Grant Sanderson (3Blue1Brown). Write narration for a visual math/physics explainer.

YOUR VOICE:
- Warm, curious, intellectually playful — like a brilliant friend explaining at a whiteboard
- Use ONE vivid real-world analogy per scene ("think of velocity like the speedometer in your car")
- Add ONE humor beat: a funny observation, exaggerated surprise, or absurd comparison
- Build toward an "aha!" moment — the satisfying click of understanding
- Be SPECIFIC: use real numbers, concrete examples, actual calculations

EMOTIONAL ARC PER SCENE:
  Hook (1-2 sentences) → Spark curiosity with a question or surprising fact
  Explanation (3-5 sentences) → Build understanding with clear steps and vivid imagery  
  Worked example (1-2 sentences) → Show the math with REAL NUMBERS
  Aha! + Closing (1-2 sentences) → The beautiful insight, the satisfying conclusion

CRITICAL RULES:
1. Every scene MUST include at least one worked example with specific numbers
2. Analogies must be VISUAL — things we can animate (not abstract comparisons)
3. 8-12 sentences per scene. Each sentence < 25 words.
4. Each sentence must be a COMPLETE thought — natural for text-to-speech
5. Include specific formulas and numerical values in the narration

OUTPUT FORMAT: Valid JSON only. No markdown. Start with {
{
  "scene_name": "Scene1_Intro",
  "sentences_english": ["Sentence 1.", "Sentence 2.", ..., "Sentence N."],
  "animation_directive": "Detailed animation instruction: what to show, how to animate, what numbers to plot",
  "humor_beat": 2,
  "aha_index": 9,
  "worked_example": "Brief description of the concrete calculation in this scene",
  "key_visual": "The ONE most important visual element to show"
}"""


def _build_rich_fallback(scene: dict) -> dict:
    concept = scene.get("concept", "Physics")
    formulas = scene.get("latex_formulas", ["F = ma"])
    formula = formulas[0] if formulas else "F = ma"
    sentences = [
        f"Let's explore one of the most beautiful ideas in physics: {concept}.",
        "At first glance, it might seem complicated — but there's an elegant simplicity hiding underneath.",
        "Scientists spent centuries trying to understand this. The answer? Mathematics.",
        f"The key equation is {formula}. Let's see what each part means.",
        "Watch what happens when we plug in real numbers.",
        "For example, with a value of 10, the result is surprisingly elegant.",
        "See how the graph changes? That's the insight right there!",
        "And that beautiful connection — that's what makes physics so satisfying.",
        f"Now you truly understand {concept}. Pretty cool, right?",
    ]
    return {
        **scene,
        "sentences": sentences,
        "sentences_english": sentences,
        "manim_visual_instructions": scene.get("visual", "Show branded axes and formula box."),
        "humor_beat_idx": 1,
        "aha_idx": 7,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def run_scriptwriter(scenes: list[dict], style: str, source_material: str = "") -> list[dict]:
    """
    Write expressive English narration for each scene.
    v6: Pure English — no translation needed. Direct to EdgeTTS.
    """
    llm = get_llm(model_name=SCRIPTWRITER_MODEL, temperature=0.35, max_tokens=2000)
    source_excerpt = source_material.strip()[:800] if source_material else ""

    enriched = []

    for idx, scene in enumerate(scenes):
        scene_name  = scene.get("scene_name", f"Scene_{idx+1}")
        concept     = scene.get("concept", "")
        explanation = scene.get("explanation", "")
        hook        = scene.get("narrative_hook", "")
        formulas    = scene.get("latex_formulas", [])
        storyboard  = scene.get("storyboard_plan", {})
        metaphor_hint = storyboard.get("metaphor_chain", "")
        humor_hint    = (storyboard.get("humor_beats") or [""])[0]

        log.info(f"Writing script for {scene_name}…")

        source_line = f"\nSOURCE GROUNDING: {source_excerpt}" if source_excerpt else ""

        user_prompt = f"""Write an expressive 3B1B-style educational narration for this video scene.

Style: {style}
SCENE: {scene_name}
CONCEPT: {concept}
WHAT TO EXPLAIN: {explanation}
HOOK: {hook}
FORMULAS: {', '.join(formulas) if formulas else 'derive from concept'}
METAPHOR TO USE: {metaphor_hint or "choose a vivid, visual, animatable metaphor"}
HUMOR BEAT: {humor_hint or "add one playful/funny observation"}
{source_line}

CRITICAL: Include at least ONE worked example with SPECIFIC NUMBERS.
Write 8-12 sentences. Output ONLY the JSON object."""

        result = None
        for attempt in range(3):
            try:
                response = llm.invoke([
                    SystemMessage(content=SYSTEM_PROMPT),
                    HumanMessage(content=user_prompt),
                ])
                data = safe_json_loads(response.content.strip())
                en_sentences = data.get("sentences_english", [])
                if not en_sentences or len(en_sentences) < 4:
                    raise ValueError(f"Too few sentences: {len(en_sentences)}")

                result = {
                    **scene,
                    "sentences":                 en_sentences,
                    "sentences_english":         en_sentences,
                    "manim_visual_instructions": data.get("animation_directive", scene.get("visual", "")),
                    "humor_beat_idx":            int(data.get("humor_beat", 1)),
                    "aha_idx":                   int(data.get("aha_index", len(en_sentences) - 2)),
                    "worked_example":            data.get("worked_example", ""),
                    "key_visual":                data.get("key_visual", ""),
                }
                break

            except Exception as exc:
                log.warning(f"Scriptwriter attempt {attempt+1} failed on {scene_name}: {exc}")
                time.sleep(2)

        if result is None:
            log.error(f"All attempts failed for {scene_name} — using rich fallback")
            result = _build_rich_fallback(scene)

        enriched.append(result)
        log.info(f"✓ {scene_name} — {len(result.get('sentences', []))} sentences.")

    return enriched
