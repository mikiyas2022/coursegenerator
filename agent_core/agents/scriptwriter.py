"""
agents/scriptwriter.py — 3B1B English Scriptwriter Agent (v7 — Masterpiece Quality)
=====================================================================================
Produces Grant Sanderson–quality narration with:
  • Deep intuition building
  • Multiple worked examples with specific numbers
  • Hook → Build → Example → AHA → Summary arc
  • SSML-compatible timing cues embedded in sentences
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
# System prompt — Grant Sanderson voice, detailed timing arc
# ─────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are Grant Sanderson (3Blue1Brown). Write world-class narration for visual math/physics explainer videos.

YOUR VOICE:
- Warm, curious, intellectually playful — like a brilliant friend explaining at a whiteboard
- Use ONE vivid ANIMATABLE real-world analogy per scene (something that can be drawn on screen)
- Add ONE humor beat: a funny observation, exaggerated surprise, or self-deprecating aside
- Build toward a genuine "aha!" moment — the satisfying click of deep understanding
- Be SPECIFIC: use real numbers, concrete examples, actual step-by-step calculations
- Speak naturally — contractions, rhetorical questions, "here's the thing…", "notice that…"

EMOTIONAL ARC (follow strictly):
  HOOK (1-2 sentences): Spark curiosity — a surprising question or mind-bending observation
  BUILD (2-3 sentences): Lay the intuition step-by-step, with a visual metaphor
  WORKED EXAMPLE (2-3 sentences): Show the math with REAL NUMBERS (e.g., "If v=20 m/s and t=3s…")
  AHA MOMENT (1-2 sentences): The beautiful insight — the "oh, that's why!"
  CLOSING (1-2 sentences): Satisfying summary that teases what's next

CRITICAL RULES:
1. Every scene MUST contain a worked numerical example with specific values
2. Analogies MUST be visual — things we can animate (e.g., "imagine a car speeding up on a ramp")
3. 8–12 sentences per scene. Each sentence < 22 words for natural TTS pacing.
4. Each sentence = one complete thought (no run-ons)
5. Include the key formula cited naturally in speech (not "see equation 3")
6. Add <pause> marker after the AHA sentence for dramatic timing
7. Do NOT use phrases: "Let's dive in", "In conclusion", "To sum up", "It's important to note"

OUTPUT FORMAT: Valid JSON only. No markdown. Start with {
{
  "scene_name": "Scene1_Intro",
  "sentences_english": [
    "Hook sentence here — ends with a question or surprise.",
    "Build sentence 1 — lays foundation.",
    "Build sentence 2 — adds intuition with analogy.",
    "Build sentence 3 — connects analogy to math.",
    "Worked example setup — 'If we have a ball at 20 m/s...'",
    "Worked example calculation — 'Then F = 5 × 4 = 20 newtons.'",
    "Aha sentence — the beautiful insight. <pause>",
    "Closing sentence — what this means in the bigger picture.",
    "Teaser — what comes next in the story."
  ],
  "animation_directive": "Extremely detailed: what objects appear, how they move, exact timing, specific numbers to show",
  "humor_beat": 3,
  "aha_index": 6,
  "worked_example": "Describe the concrete numerical calculation shown in this scene",
  "key_visual": "The single most important visual element — be specific (e.g., 'parabolic arc traced by dot from (0,0) to (10,5)')"
}"""


def _build_rich_fallback(scene: dict) -> dict:
    concept = scene.get("concept", "Physics")
    formulas = scene.get("latex_formulas", ["F = ma"])
    formula = formulas[0] if formulas else "F = ma"
    sentences = [
        f"Here's something that always surprised me about {concept}.",
        "At first glance, it seems complicated — but there's an elegant simplicity underneath.",
        "Think of it like water flowing downhill: it always finds the path of least resistance.",
        f"The key equation is {formula} — and each piece of it earns its place.",
        "Let's say we have a 5-kilogram object accelerating at 4 meters per second squared.",
        "Then the net force is exactly 5 times 4, which gives us 20 newtons. Beautiful.",
        "Here's the aha moment: force isn't what keeps things moving — it's what changes motion. <pause>",
        f"That single insight unlocks everything about {concept}.",
        "In the next scene, we'll see exactly how this plays out with a real example.",
    ]
    return {
        **scene,
        "sentences": sentences,
        "sentences_english": sentences,
        "manim_visual_instructions": scene.get("visual", "Show branded axes and formula box."),
        "humor_beat_idx": 2,
        "aha_idx": 6,
        "worked_example": "F = ma with m=5kg, a=4m/s² → F=20N",
        "key_visual": "Formula box F=ma with circumscribe glow",
    }


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def run_scriptwriter(scenes: list[dict], style: str, source_material: str = "") -> list[dict]:
    """
    Write Grant Sanderson–quality English narration for each scene.
    v7: Deep storytelling, worked examples, timing cues for Kokoro sync.
    """
    llm = get_llm(model_name=SCRIPTWRITER_MODEL, temperature=0.38, max_tokens=2400)
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
        aha_hint      = storyboard.get("aha_moment", "")
        worked_eg_hint = scene.get("worked_example", "")

        log.info(f"Writing script for {scene_name}…")

        source_line = f"\nSOURCE GROUNDING: {source_excerpt}" if source_excerpt else ""

        user_prompt = f"""Write a Grant Sanderson–quality 3B1B narration for this educational scene.

Style target: {style}
SCENE NAME: {scene_name}
CONCEPT: {concept}
EXPLANATION: {explanation}
NARRATIVE HOOK: {hook}
KEY FORMULAS: {', '.join(formulas) if formulas else 'derive from concept'}
VISUAL METAPHOR TO USE: {metaphor_hint or 'choose a vivid, animatable analogy'}
HUMOR BEAT: {humor_hint or 'add one genuinely funny or surprising observation'}
AHA MOMENT HINT: {aha_hint or 'the beautiful insight that makes everything click'}
WORKED EXAMPLE HINT: {worked_eg_hint or 'create a concrete numerical example with real values'}
{source_line}

EMOTIONAL ARC REQUIRED: Hook → Build intuition → Visual analogy → Worked example with REAL NUMBERS → AHA moment (add <pause>) → Satisfying closing
SENTENCES: 8–12. Each < 22 words. Natural TTS speech rhythm.

Output ONLY the JSON object, starting with {{"""

        result = None
        for attempt in range(3):
            try:
                response = llm.invoke([
                    SystemMessage(content=SYSTEM_PROMPT),
                    HumanMessage(content=user_prompt),
                ])
                data = safe_json_loads(response.content.strip())
                en_sentences = data.get("sentences_english", [])
                if not en_sentences or len(en_sentences) < 5:
                    raise ValueError(f"Too few sentences: {len(en_sentences)}")

                result = {
                    **scene,
                    "sentences":                 en_sentences,
                    "sentences_english":         en_sentences,
                    "manim_visual_instructions": data.get("animation_directive", scene.get("visual", "")),
                    "humor_beat_idx":            int(data.get("humor_beat", 2)),
                    "aha_idx":                   int(data.get("aha_index", len(en_sentences) - 3)),
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
