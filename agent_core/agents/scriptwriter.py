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
    Write Amharic narration for each scene from the researcher's output.

    Returns enriched scene dicts with 'amharic_script' and 'sentences' keys.
    """
    llm = get_llm(temperature=0.3)

    scenes_json = json.dumps(scenes, ensure_ascii=False, indent=2)

    user_prompt = f"""Write Amharic narration for each of these educational video scenes.
Narrative Style: {style}

SCENES:
{scenes_json}

Follow the schema exactly. Output the JSON array."""

    try:
        response = llm.invoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ])
        raw = response.content.strip()
        raw = re.sub(r"```(?:json)?", "", raw).strip().rstrip("```").strip()

        scripts = json.loads(raw)
        if not isinstance(scripts, list):
            raise ValueError("Non-list JSON from LLM")

        # Merge script data back into the original scene dicts
        script_map = {s["scene_name"]: s for s in scripts}
        enriched = []
        for scene in scenes:
            name = scene["scene_name"]
            script_data = script_map.get(name, {})
            enriched.append({
                **scene,
                "amharic_script": script_data.get("amharic_script", "ምንም ዓይነት ንግግር አልተሰጠም።"),
                "sentences":      script_data.get("sentences", []),
            })

        print(f"  [scriptwriter] Scripts written for {len(enriched)} scenes.", flush=True)
        return enriched

    except Exception as exc:
        print(f"  [scriptwriter] LLM error ({exc}). Using placeholder scripts.", flush=True)
        # Fallback: add placeholder Amharic to each scene
        return [
            {
                **scene,
                "amharic_script": f"ዛሬ {scene.get('concept', 'ትምህርት')} እናያለን።",
                "sentences":      [f"ዛሬ {scene.get('concept', 'ትምህርት')} እናያለን።"],
            }
            for scene in scenes
        ]
