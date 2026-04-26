"""
agents/scriptwriter.py — World-Class Amharic Scriptwriter Agent (v3)

Takes the pedagogical scene list from the Researcher and writes
deeply expressive, engaging, native Amharic (Ge'ez script) narration.

v3 changes:
  - 8-12 sentences per scene (was 4) for proper multi-minute videos
  - Each sentence paired with a visual cue for animation synchronization
  - Richer, more expressive narration style
"""

import json
import re
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import get_llm, SCRIPTWRITER_MODEL

from langchain_core.messages import HumanMessage, SystemMessage
from utils import safe_json_loads


from deep_translator import GoogleTranslator

SYSTEM_PROMPT = """You are a world-class STEM educational scriptwriter.
You write deeply expressive, engaging narrations for educational video scenes in English.
Your scripts must feel like a gifted teacher who captivates students — using vivid metaphors,
relatable everyday examples, smooth flowing language, and emotional resonance.

ABSOLUTE RULES:
1. Write ONLY in English. We will translate later.
2. Each scene must feel DIFFERENT — vary the opening mood, pace, and tone.
3. Keep individual sentences naturally paced for TTS voiceover.
4. Write 8 to 12 sentences per scene. Each sentence should be its own complete thought.
The narration should cover:
  - Opening hook (1-2 sentences)
  - Core explanation (4-6 sentences)
  - Visual reference (1-2 sentences)
  - Closing insight (1-2 sentences)

OUTPUT FORMAT: Output ONLY a valid JSON object. Start IMMEDIATELY with { — no markdown, no preamble.
{
  "scene_name": "Scene1_Intro",
  "sentences_english": ["Sentence 1.", "Sentence 2.", "...", "Sentence 10."],
  "animation_directive": "A concise directive for what to animate during this scene (e.g. 'Show a circle growing while x increases')."
}"""


# Context-aware fallback openers — unique per scene type/position
_FALLBACK_BY_TYPE = {
    "intro":   "በአእምሮአችን ዓይን የማይታየውን ዓለም ለማየት ዝግጁ ናችሁ? ሳይንስ ሁሌም ከሚታየው ባሻገር ያለውን ያሳየናል።",
    "core":    "ልብ ይበሉ — ይህ ጽንሰ ሐሳብ ሁሉን ነገር ይቀይራል። ከዚህ በፊት ያላየነውን ነገር አሁን እናያለን።",
    "example": "በየቀኑ ሕይወታችን ውስጥ ይህን ብዙ ጊዜ እናደርጋለን። ግን ሳይንስ ከኋላው ምን እንዳለ አስበን አናውቅም።",
    "deep":    "ሳይንስ ለምን ትሰራ እንደሆነ ለመረዳት ትንሽ ዝቅ ብለን እንመልከት። ምስጢሩ በዝርዝሩ ውስጥ ነው የተደበቀው።",
    "visual":  "ሥዕሉን በጥንቃቄ ተመልከቱ — ዐይናችሁ ገና ያላየውን ነገር ሊያሳያችሁ ነው። ቅርጾቹ ታሪክ ይናገራሉ።",
    "apply":   "ይህን ዕውቀት ወደ ሥራ ላይ ለማዋል ጊዜው አሁን ነው። ከንድፈ ሐሳብ ወደ ተግባር እንሸጋገር።",
    "summary": "ምን ተማርን? ዋና ዋና ነጥቦቹን አንድ ላይ እናስቀምጥ። ይህ ዕውቀት የናንተ ነው — ጥሩ አድርጋችሁ ያዙት።",
    "closing": "ይህ ሁሉ ለምን ይደንቀናል? ምክንያቱ ገና ብዙ ያልታወቀ ስላለ ነው። እናንተ ደግሞ ይህን ልታገኙት ትችላላችሁ።",
}
_FALLBACK_LIST = list(_FALLBACK_BY_TYPE.values())


def _get_fallback_opener(scene_name: str) -> str:
    """Return a unique, context-appropriate opener per scene using the scene name."""
    name = scene_name.lower()
    if any(k in name for k in ["intro", "_1", "scene1"]):
        return _FALLBACK_BY_TYPE["intro"]
    if any(k in name for k in ["summary", "takeaway", "recap", "conclusion"]):
        return _FALLBACK_BY_TYPE["summary"]
    if any(k in name for k in ["example", "apply", "practice"]):
        return _FALLBACK_BY_TYPE["apply"]
    if any(k in name for k in ["visual", "diagram", "graph", "plot"]):
        return _FALLBACK_BY_TYPE["visual"]
    if any(k in name for k in ["deep", "advanced", "detail"]):
        return _FALLBACK_BY_TYPE["deep"]
    if any(k in name for k in ["core", "principle", "concept", "foundation"]):
        return _FALLBACK_BY_TYPE["core"]
    h = sum(ord(c) for c in scene_name) % len(_FALLBACK_LIST)
    return _FALLBACK_LIST[h]



def _build_rich_fallback(scene: dict, scene_name: str) -> dict:
    """Build a rich 8-sentence fallback instead of the old 2-sentence stub."""
    opener = _get_fallback_opener(scene_name)
    concept = scene.get("concept", "ሳይንስ")
    explanation = scene.get("explanation", "")

    sentences = [
        opener.split("።")[0] + "።" if "።" in opener else opener,
    ]

    # Add concept-specific fallback sentences
    if opener.count("።") > 1:
        parts = [s.strip() + "።" for s in opener.split("።") if s.strip()]
        sentences = parts[:2]

    sentences.extend([
        f"ዛሬ ስለ {concept} በጥልቀት እንማራለን።",
        "ይህ ጽንሰ ሐሳብ በሕይወታችን ውስጥ ትልቅ ሚና ይጫወታል።",
        "ቅርጾቹንና ቁጥሮቹን በጥንቃቄ ተመልከቱ።",
        "እያንዳንዱ ክፍል ከሌላው ጋር ተያይዞ ይሰራል።",
        "ይህ የሳይንስ ውበት ነው — ሁሉም ነገር ተያያዘ ነው።",
        "ከዚህ ቀን ጀምሮ ይህን ፅንሰ ሐሳብ ጥሩ አድርጋችሁ ትረዱታላችሁ።",
        "ደጋግማችሁ ተለማመዱ — ተማሪ ማለት ሁሌ የሚያድግ ማለት ነው።",
    ])

    # Take first 8 unique sentences
    sentences = sentences[:8]
    full_script = " ".join(sentences)

    return {
        **scene,
        "amharic_script": full_script,
        "sentences":      sentences,
    }


def run_scriptwriter(scenes: list[dict], style: str, source_material: str = "") -> list[dict]:
    """
    Write world-class Amharic narration for each scene with Llama 3.1.
    v3: 8-12 sentences per scene for proper multi-minute videos.
    Outputs native Ge'ez script directly.
    """
    llm = get_llm(model_name=SCRIPTWRITER_MODEL, temperature=0.3, max_tokens=1500)
    source_excerpt = source_material.strip()[:800] if source_material and source_material.strip() else ""

    enriched = []

    for idx, scene in enumerate(scenes):
        scene_name  = scene.get("scene_name", f"Scene_{idx+1}")
        concept     = scene.get("concept", "")
        explanation = scene.get("explanation", "")
        hook        = scene.get("narrative_hook", "")

        print(f"  [scriptwriter] Writing rich 8-12 sentence Amharic script for {scene_name} using Llama 3.1…", flush=True)

        source_line = f"\nSOURCE MATERIAL GROUNDING: {source_excerpt}" if source_excerpt else ""

        user_prompt = f"""Write an expressive, detailed educational narration for this video scene.
THE ENTIRE NARRATION MUST BE IN ENGLISH. We will translate it later.

Narrative Style: {style}
SCENE NAME: {scene_name}
CONCEPT: {concept}
WHAT TO EXPLAIN: {explanation}
NARRATIVE HOOK: {hook}{source_line}

CONSTRAINTS:
1. Write exactly 8 to 12 DIFFERENT sentences in ENGLISH. 
2. Use professional, clear, and pedagogical language.
3. Structure: 2 opening hook sentences → 4-6 teaching sentences → 2 closing/summary sentences.
4. Provide a high-level animation directive for the scene.
5. Output ONLY this JSON format. DO NOT use raw newlines inside the JSON strings — use `\\n` for line breaks.
{{
  "scene_name": "{scene_name}",
  "sentences_english": ["Sentence 1.", "Sentence 2.", "...", "Sentence N"],
  "animation_directive": "High-level animation instructions for this scene."
}}"""

        result = None
        for attempt in range(3):
            try:
                response = llm.invoke([
                    SystemMessage(content="You are a world-class STEM educational scriptwriter."),
                    HumanMessage(content=user_prompt),
                ])
                script_data = safe_json_loads(response.content.strip())

                en_sentences = script_data.get("sentences_english", [])
                
                if not en_sentences:
                    raise ValueError("No English sentences found in response")

                # Translate English sentences to Amharic
                print(f"  [scriptwriter] Translating {len(en_sentences)} sentences to Amharic...", flush=True)
                am_sentences = []
                translator = GoogleTranslator(source='en', target='am')
                for sent in en_sentences:
                    try:
                        am_sent = translator.translate(sent)
                        am_sentences.append(am_sent)
                    except Exception as e:
                        print(f"  [scriptwriter] Translation error: {e}", flush=True)
                        am_sentences.append(sent) # Fallback to English if translation fails
                        
                am_script = " ".join(am_sentences)

                result = {
                    **scene,
                    "amharic_script": am_script,
                    "sentences":      am_sentences,
                    "manim_visual_instructions": script_data.get("animation_directive", scene.get("visual", "")),
                }
                break

            except Exception as exc:
                print(f"  [scriptwriter] Attempt {attempt+1} failed on {scene_name}: {exc}", flush=True)

        if result is None:
            # Final fallback to a themed template if Llama 3.1 totally glitches
            print(f"  [scriptwriter] CRITICAL FAIL on {scene_name} — using local fallback", flush=True)
            result = _build_rich_fallback(scene, scene_name)

        enriched.append(result)
        print(f"  [scriptwriter] OK {scene_name} — {len(result.get('sentences', []))} sentences.", flush=True)

    return enriched



