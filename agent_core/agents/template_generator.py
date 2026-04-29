"""
agents/template_generator.py — Dynamic Template Generator Agent (v1)
=====================================================================
Uses the LLM to generate NEW specialized Manim template variants on-the-fly.
Converts the base 42 templates into 1000+ effective variations by:
  1. Analyzing the scene's concept, mood, and visual requirements
  2. Selecting the closest base template
  3. Generating a SPECIALIZED variant with custom objects, colors, animations
  4. Saving successful variants to disk for reuse

This is the key to eliminating repetition without manually writing 1000 files.
"""

import os
import re
import sys
import time
import hashlib

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import get_llm, MANIM_CODER_MODEL
from logger import get_logger

log = get_logger("template_generator")

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GENERATED_DIR = os.path.join(PROJECT_ROOT, "manim_templates", "3b1b_style", "generated")

# Ensure generated directory exists
os.makedirs(GENERATED_DIR, exist_ok=True)

GENERATION_PROMPT = '''You are a SENIOR ManimCE v0.20.1 developer creating a SPECIALIZED animation template.
You must produce a single Python class that inherits AmharicEduScene and uses VoiceoverScene.

BASE TEMPLATE (study this pattern, then SPECIALIZE it for the concept below):
```python
{base_template_code}
```

CONCEPT TO SPECIALIZE FOR: {concept}
VISUAL REQUIREMENTS: {visual_requirements}
MOOD/TONE: {mood}
SPECIFIC OBJECTS NEEDED: {objects_needed}

RULES (CRITICAL — violations = crash):
1. Class name MUST be `SceneTemplate`
2. MUST inherit `AmharicEduScene` (already has VoiceoverScene + MovingCameraScene)
3. MUST call `setup_scene(self)` first
4. Use `<NARRATION_PLACEHOLDER_0>`, `<NARRATION_PLACEHOLDER_1>`, etc. for voiceover text
5. `self.clear()` MUST come BEFORE each `with self.voiceover(...)` block, NEVER inside
6. ALL animations inside voiceover MUST use `run_time=tracker.duration * X` (X between 0.1-0.9)
7. Total run_time fractions inside one voiceover block MUST sum to ≤ 1.0
8. Available helpers: latin_text(), formula_box(), branded_axes(), branded_vector(),
   branded_circle(), glow_dot(), title_card(), clamp_to_screen(), playful_bounce(),
   section_divider(), number_ticker()
9. Available colors: TEAL_ACCENT, STAR_YELLOW, TEXT_COLOR, MUTED_COLOR, SUCCESS_COLOR,
   ERROR_COLOR, VECTOR_COLOR, FORCE_COLOR, ROSE_COLOR, FORMULA_COLOR
10. Font sizes: FONT_SIZE_TITLE, FONT_SIZE_HEADER, FONT_SIZE_BODY, FONT_SIZE_LABEL,
    FONT_SIZE_SMALL, FONT_SIZE_CAPTION
11. Canvas bounds: x in [-5, 5], y in [-2.8, 2.8]
12. NEVER use: thickness=, Arc(ORIGIN,...), self.wait(run_time=X), camera.frame anything
13. Make it VISUALLY DISTINCT from the base template — different layout, animations, objects
14. Include 2-3 voiceover blocks with rich, varied animations in each
15. Use VGroup, always_redraw, ValueTracker for dynamic elements when appropriate

Output ONLY the Python code. No markdown fences. No explanation. Start with the docstring.'''


def generate_specialized_template(
    base_template_path: str,
    concept: str,
    visual_requirements: str = "",
    mood: str = "curious and playful",
    objects_needed: str = "",
) -> str | None:
    """
    Generate a specialized template variant based on a base template.
    Returns the generated code string, or None on failure.
    Also saves successful templates to disk for future reuse.
    """
    try:
        with open(base_template_path, "r", encoding="utf-8") as f:
            base_code = f.read()
    except Exception as exc:
        log.error(f"Cannot read base template {base_template_path}: {exc}")
        return None

    # Check if we already generated one for this concept+base combo
    cache_key = hashlib.md5(f"{base_template_path}:{concept}".encode()).hexdigest()[:12]
    cached_path = os.path.join(GENERATED_DIR, f"gen_{cache_key}.py")
    if os.path.exists(cached_path):
        log.info(f"Cache hit: {cached_path}")
        with open(cached_path, "r", encoding="utf-8") as f:
            return f.read()

    prompt = GENERATION_PROMPT.format(
        base_template_code=base_code,
        concept=concept,
        visual_requirements=visual_requirements or "Rich, varied, non-repetitive animation",
        mood=mood,
        objects_needed=objects_needed or "Derive from concept",
    )

    llm = get_llm(model_name=MANIM_CODER_MODEL, temperature=0.35, max_tokens=3000)

    for attempt in range(2):
        try:
            from langchain_core.messages import HumanMessage, SystemMessage
            response = llm.invoke([HumanMessage(content=prompt)])
            code = response.content.strip()

            # Strip markdown fences if present
            code = re.sub(r'^```python\s*\n?', '', code)
            code = re.sub(r'\n?```\s*$', '', code)

            # Validate basic structure
            if 'class SceneTemplate' not in code:
                raise ValueError("Missing class SceneTemplate")
            if 'self.voiceover' not in code:
                raise ValueError("Missing voiceover blocks")
            if 'setup_scene' not in code:
                raise ValueError("Missing setup_scene call")

            # Fix sync issues — ensure self.clear() is before voiceover blocks
            code = _fix_sync(code)

            # Save to cache
            with open(cached_path, "w", encoding="utf-8") as f:
                f.write(code)
            log.info(f"Generated specialized template: {cached_path}")

            return code

        except Exception as exc:
            log.warning(f"Template generation attempt {attempt+1} failed: {exc}")
            time.sleep(1)

    log.error(f"All template generation attempts failed for concept: {concept}")
    return None


def _fix_sync(code: str) -> str:
    """Move self.clear() from inside voiceover blocks to before them."""
    code = re.sub(
        r'( {8})(with self\.voiceover\(text="[^"]*"\) as tracker:\n)\s{12}self\.clear\(\)\n',
        r'\1self.clear()\n\1\2',
        code,
    )
    code = re.sub(
        r'( {4})(with self\.voiceover\(text="[^"]*"\) as tracker:\n)\s{8}self\.clear\(\)\n',
        r'\1self.clear()\n\1\2',
        code,
    )
    return code


def get_generated_template_count() -> int:
    """Return number of cached generated templates."""
    if not os.path.exists(GENERATED_DIR):
        return 0
    return len([f for f in os.listdir(GENERATED_DIR) if f.endswith(".py")])
