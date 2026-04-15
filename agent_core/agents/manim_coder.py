"""
agents/manim_coder.py — Manim Developer Agent

Translates enriched scene dicts (concept + Amharic script + visual plan)
into valid ManimCE Python classes using manim-voiceover with the local
MMS TTS service.

STRICT RULES injected into every LLM call:
  - ManimCE only (no ManimGL / 3b1b syntax)
  - Amharic text → Text("...", font="Nyala") — never Tex() for Ge'ez
  - ALWAYS use tracker.duration for animation timing
  - One Python class per scene (modularity)
  - Use ValueTracker + add_updater for complex continuous animations
"""

import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import get_llm

from langchain_core.messages import HumanMessage, SystemMessage


# ─────────────────────────────────────────────────────────────────────────────
# The LocalMMSService snippet injected as header into every generated script
# ─────────────────────────────────────────────────────────────────────────────
MMS_SERVICE_HEADER = '''import os, sys, hashlib, subprocess, requests
os.environ["PATH"] = (
    "/tmp/stem_venv/bin:/Library/TeX/texbin:"
    "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
)
os.environ["HF_HOME"] = "/tmp/huggingface_cache"

from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.base import SpeechService


class LocalMMSService(SpeechService):
    """Routes manim-voiceover TTS calls to the local Meta MMS server."""

    def __init__(self, persona_id: int = 1, **kwargs):
        self.persona_id = persona_id
        super().__init__(**kwargs)

    def generate_from_text(self, text: str, cache_dir=None, path=None, **kwargs) -> dict:
        if cache_dir is None:
            cache_dir = self.cache_dir or "/tmp/stem_tts_output"
        os.makedirs(cache_dir, exist_ok=True)
        data_hash = hashlib.sha256((text + str(self.persona_id)).encode()).hexdigest()
        if path is None:
            path = os.path.join(cache_dir, f"{data_hash}.wav")
        if not os.path.exists(path):
            resp = requests.post(
                "http://127.0.0.1:8100/generate_audio",
                json={"text": text, "persona_id": self.persona_id, "output_path": path},
                timeout=180,
            )
            resp.raise_for_status()
            path = resp.json().get("output_path", path)
        return {"original_audio": path}

'''

# ─────────────────────────────────────────────────────────────────────────────
# System prompt for the Manim Developer Agent
# ─────────────────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are a senior ManimCE developer writing production-ready animation code.

ABSOLUTE RULES — breaking any rule causes a runtime crash:
1. Import ONLY from `manim` (not manim.opengl, not manimlib, not manimgl)
2. Amharic text MUST use: Text("ሰላም", font="Nyala", font_size=48)
   NEVER use Tex(), MathTex(), or MarkupText() for Ge'ez script
3. Latin/Math formulas use: MathTex(r"F = ma") or Tex(r"$F_x$")
4. Class MUST inherit from VoiceoverScene only
5. ALWAYS call self.set_speech_service(LocalMMSService(persona_id=PERSONA_ID))
   as the FIRST line of construct()
6. camera background: self.camera.background_color = "#0B0E14"
7. ALWAYS use tracker.duration for run_time inside voiceover blocks:
     with self.voiceover(text="...Amharic...") as tracker:
         self.play(Create(obj), run_time=tracker.duration * 0.8)
         self.wait(tracker.duration * 0.2)
8. Use ValueTracker + always_redraw for continuous animations
9. Do NOT import LocalMMSService — it is already defined in the file header
10. Generate ONE class per scene. Name it exactly as given.
11. Output ONLY raw Python code. NO markdown fences. NO explanations.

TEMPLATE (follow this structure):
class Scene1_Example(VoiceoverScene):
    def construct(self):
        self.set_speech_service(LocalMMSService(persona_id=1))
        self.camera.background_color = "#0B0E14"
        Text.set_default(font="Inter", weight=BOLD)

        with self.voiceover(text="ሰላም ልጆች፣ ዛሬ...") as tracker:
            title = Text("Example", font="Nyala", font_size=52, color=WHITE)
            self.play(Write(title), run_time=tracker.duration * 0.85)
            self.wait(tracker.duration * 0.15)
"""


def run_manim_coder(
    scenes: list[dict],
    persona_id: int = 1,
    error_context: str = "",
    previous_code: list[str] | None = None,
) -> list[str]:
    """
    Generate ManimCE Python class code for each scene.

    Args:
        scenes:         Enriched scene dicts from scriptwriter.
        persona_id:     Voice persona (1-5) for LocalMMSService.
        error_context:  Stderr from the Critic (triggers self-healing mode).
        previous_code:  Previous generated classes (for self-healing).

    Returns:
        List of Python class strings (one per scene).
    """
    llm = get_llm(temperature=0.05)  # very low temp for deterministic code

    if error_context and previous_code:
        return _heal_code(llm, previous_code, error_context)

    class_strings = []
    for scene in scenes:
        class_code = _generate_scene_class(llm, scene, persona_id)
        class_strings.append(class_code)

    print(f"  [manim_coder] Generated {len(class_strings)} scene classes.", flush=True)
    return class_strings


def _generate_scene_class(llm, scene: dict, persona_id: int) -> str:
    """Generate a single VoiceoverScene class for one scene."""
    formulas_str = ", ".join(scene.get("latex_formulas", [])) or "None"

    user_prompt = f"""Generate a ManimCE VoiceoverScene class for this scene.

Scene Name (class name): {scene["scene_name"]}
Concept: {scene["concept"]}
Visual Plan: {scene["visual"]}
Amharic Narration: {scene["amharic_script"]}
LaTeX Formulas: {formulas_str}
Voice persona_id: {persona_id}

Follow ALL rules. Output ONLY the Python class code."""

    try:
        response = llm.invoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ])
        code = response.content.strip()
        # Strip any accidental markdown fences
        code = re.sub(r"^```(?:python)?", "", code, flags=re.MULTILINE).strip()
        code = re.sub(r"```$", "", code, flags=re.MULTILINE).strip()
        return code
    except Exception as exc:
        print(f"  [manim_coder] LLM error for {scene['scene_name']}: {exc}", flush=True)
        # Minimal fallback class that won't crash
        name   = scene["scene_name"]
        text   = scene.get("amharic_script", "ምንም ዓይነት ንግግር አልተሰጠም።")[:100]
        return f"""
class {name}(VoiceoverScene):
    def construct(self):
        self.set_speech_service(LocalMMSService(persona_id={persona_id}))
        self.camera.background_color = "#0B0E14"
        with self.voiceover(text="{text}") as tracker:
            label = Text("{scene.get('concept', 'Scene')}", font="Nyala", font_size=48, color=WHITE)
            self.play(Write(label), run_time=tracker.duration)
"""


def _heal_code(llm, previous_classes: list[str], error: str) -> list[str]:
    """
    Self-healing: ask the LLM to fix the code given the Manim traceback.
    Fixes are applied to all classes as a unified block for context.
    """
    print(f"  [manim_coder] Self-healing — error snippet: {error[:150]}", flush=True)

    full_code = "\n\n".join(previous_classes)
    user_prompt = f"""The following ManimCE code produced this error when rendered:

ERROR:
{error[:1500]}

CODE:
{full_code}

Fix ONLY the specific error. Output the complete fixed Python code for ALL classes.
No markdown fences. No explanations."""

    try:
        response = llm.invoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ])
        fixed = response.content.strip()
        fixed = re.sub(r"^```(?:python)?", "", fixed, flags=re.MULTILINE).strip()
        fixed = re.sub(r"```$", "", fixed, flags=re.MULTILINE).strip()

        # Split back into individual classes by "class " declarations
        class_blocks = re.split(r"(?=^class\s+\w+\()", fixed, flags=re.MULTILINE)
        class_blocks = [b.strip() for b in class_blocks if b.strip().startswith("class ")]

        if not class_blocks:
            # LLM returned one big blob — treat as single entry
            return [fixed]

        print(f"  [manim_coder] Healed {len(class_blocks)} class(es).", flush=True)
        return class_blocks

    except Exception as exc:
        print(f"  [manim_coder] Self-healing LLM error ({exc}). Returning original.", flush=True)
        return previous_classes
