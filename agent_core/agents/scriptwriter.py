"""
agents/scriptwriter.py — Amharic Scriptwriter Agent

Takes the pedagogical scene list from the Researcher and writes
a natural, engaging Amharic (Ge'ez script) narration for each scene.

TTS Stability Rules applied automatically:
  - Normalise Amharic homophones (ሀ/ሃ/ኃ → ሀ for common words)
  - Short sentences (≤20 words each) for clean pacing
  - Avoid punctuation that confuses TTS (em-dashes, excessive commas)
"""

import json
import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import get_llm

from langchain_core.messages import HumanMessage, SystemMessage


SYSTEM_PROMPT = """You are an expert Amharic educational scriptwriter for video content.
Your narrations are clear, warm, and engaging. You write ONLY in Amharic (Ge'ez script).

STRICT RULES:
1. Write ONLY Amharic Ge'ez script (አማርኛ). No English, no transliteration.
2. Keep sentences SHORT — maximum 20 Amharic words per sentence.
3. Use natural spoken Amharic, not formal written Amharic.
4. TTS Homophone Normalization — apply these replacements consistently:
   - Use ሀ (not ሃ or ኃ) for the /hä/ sound in common words
   - Use አ (not ዐ) for the glottal vowel in common words
   - Use ሰ (not ሠ) for /sä/ in common words
   - Use ጸ (not ፀ) for /tsä/ where ambiguous
5. End each sentence with ። (Ethiopic full stop) for clean TTS pausing.
6. Match the narrative style provided.

OUTPUT: Valid JSON array ONLY. No markdown, no explanation.

Schema per scene:
{
  "scene_name": "Scene1_Intro",
  "amharic_script": "Full narration as one continuous Amharic string.",
  "sentences": ["First sentence።", "Second sentence።"]
}"""


def run_scriptwriter(scenes: list[dict], style: str) -> list[dict]:
    """
    Write Amharic narration for each scene sequentially. 
    ENFORCES extreme brevity to ensure blazing fast TTFB and generation speeds without losing logic.
    """
    # Extremely low max_tokens guarantees rapid speed and forces the model to not loop.
    llm = get_llm(temperature=0.2, max_tokens=200)

    enriched = []

    for idx, scene in enumerate(scenes):
        scene_name = scene.get("scene_name", f"Scene_{idx+1}")
        print(f"  [scriptwriter] Writing script for {scene_name}...", flush=True)

        user_prompt = f"""Write the Amharic narration for this SINGLE educational video scene.
Narrative Style: {style}

SCENE TO NARRATE:
{json.dumps(scene, ensure_ascii=False, indent=2)}

CRITICAL: You MUST write EXACTLY TWO very short sentences in Amharic. DO NOT write long paragraphs.

Follow the schema exactly. Output ONLY the JSON object. Do not wrap in arrays or markdown.
Schema:
{{
  "scene_name": "{scene_name}",
  "amharic_script": "Short continuous Amharic narration string.",
  "sentences": ["Sentence 1.", "Sentence 2."]
}}"""

        try:
            response = llm.invoke([
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=user_prompt),
            ])
            raw = response.content.strip()
            raw = re.sub(r"```(?:json)?", "", raw).strip().rstrip("```").strip()

            script_data = json.loads(raw)
            if not isinstance(script_data, dict):
                raise ValueError("LLM did not return a JSON dictionary.")

            enriched.append({
                **scene,
                "amharic_script": script_data.get("amharic_script", "ዛሬ ትምህርት እናያለን።"),
                "sentences":      script_data.get("sentences", []),
            })

        except Exception as exc:
            print(f"  [scriptwriter] LLM error on {scene_name} ({exc}). Using placeholder.", flush=True)
            enriched.append({
                **scene,
                "amharic_script": f"ዛሬ {scene.get('concept', 'ትምህርት')} እናያለን።",
                "sentences":      [f"ዛሬ {scene.get('concept', 'ትምህርት')} እናያለን።"],
            })

    print(f"  [scriptwriter] All {len(enriched)} scenes rapidly completed.", flush=True)
    return enriched
