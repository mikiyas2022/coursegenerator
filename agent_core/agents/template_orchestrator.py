"""
agents/template_orchestrator.py — Template-Powered Manim Orchestrator
=====================================================================
Replaces Manim Coder for both 3B1B and Blackboard modes.
- 3B1B mode: picks random 3b1b_style template, fills narration placeholders
- Blackboard mode: generates a DETERMINISTIC, silent, step-by-step Q&A scene
  using BlackboardScene (NO voiceover, NO TTS, NO audio)
"""

import os
import re
import glob
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import get_llm, MANIM_CODER_MODEL
from logger import get_logger

log = get_logger("template_orchestrator")

# Absolute path to project root (the parent of agent_core/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_template_orchestrator(scenes: list[dict], mode: str = "3b1b") -> list[str]:
    """
    Selects templates based on mode.
    - 3b1b: random template from 3b1b_style/, fills narration
    - blackboard: generates a complete silent Q&A solver scene
    Returns list of executable Manim python code strings.
    """
    log.info(f"Template Orchestrator: mode={mode}, {len(scenes)} scenes")

    if mode == "blackboard":
        return _generate_blackboard_scenes(scenes)
    else:
        return _generate_3b1b_scenes(scenes)


# ─────────────────────────────────────────────────────────────────────────────
# 3B1B mode — template-based
# ─────────────────────────────────────────────────────────────────────────────

def _generate_3b1b_scenes(scenes: list[dict]) -> list[str]:
    template_dir = os.path.join(PROJECT_ROOT, "manim_templates", "3b1b_style")
    templates = glob.glob(os.path.join(template_dir, "*.py"))
    generated = []

    for idx, scene in enumerate(scenes):
        scene_name = scene.get("scene_name", f"Scene{idx}")

        if templates:
            selected = random.choice(templates)
            with open(selected, "r") as f:
                code = f.read()

            # Replace class name
            if "class SceneTemplate" in code:
                code = code.replace(
                    code[code.find("class "):code.find("(AmharicEduScene):")],
                    f"class {scene_name}"
                )

            # Replace narration
            if "sentences" in scene and scene["sentences"]:
                narration = " ".join(scene["sentences"])
            else:
                narration = scene.get("concept", "Physics")

            code = code.replace("<NARRATION_PLACEHOLDER>", narration.replace('"', "'"))
            code = code.replace("<CONTENT_PLACEHOLDER>", f'self.write_step(Text("{narration}"))')
            generated.append(code)
        else:
            log.warning("No 3b1b templates found — using fallback")
            generated.append(f'class {scene_name}(AmharicEduScene):\n    def construct(self):\n        pass')

    return generated


# ─────────────────────────────────────────────────────────────────────────────
# Blackboard mode — deterministic Q&A solver (SILENT, no TTS)
# ─────────────────────────────────────────────────────────────────────────────

def _generate_blackboard_scenes(scenes: list[dict]) -> list[str]:
    """
    Generate a single, complete BlackboardScene that:
    1. Writes the question on the board
    2. Shows step-by-step solution
    3. Boxes the final answer
    All silent — no voiceover, no TTS.
    """
    generated = []

    for idx, scene in enumerate(scenes):
        scene_name = scene.get("scene_name", f"BB_Scene{idx}")
        question = scene.get("question", scene.get("topic", scene.get("concept", "Solve the problem")))
        answer = scene.get("correct_answer", scene.get("answer", ""))
        subject = scene.get("subject_grade", scene.get("metaphor", ""))

        # Extract sentences for step content
        sentences = scene.get("sentences", [])
        if not sentences:
            script = scene.get("amharic_script", "")
            if script:
                sentences = [s.strip() for s in script.split(".") if s.strip()]

        # Build the step-by-step solution code
        code = _build_blackboard_scene(scene_name, question, answer, subject, sentences)
        generated.append(code)

    return generated


def _safe(text: str) -> str:
    """Escape text for Python string literals."""
    return text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def _build_blackboard_scene(
    scene_name: str,
    question: str,
    answer: str,
    subject: str,
    steps: list[str],
) -> str:
    """
    Build a complete BlackboardScene class as a Python string.
    This is a DETERMINISTIC template — no LLM involved.
    """
    q_safe = _safe(question[:200])  # Truncate very long questions
    a_safe = _safe(answer[:100]) if answer else ""
    subj_safe = _safe(subject[:80]) if subject else ""

    # If no steps from the pipeline, create generic ones
    if not steps or len(steps) < 2:
        steps = [
            "Given information and known values",
            "Identify the relevant formula",
            "Substitute values into the equation",
            "Calculate the result",
        ]
        if answer:
            steps.append(f"Answer: {answer}")

    # Build step-writing code blocks
    step_blocks = []
    chalk_colors = ["BB_CHALK_YELLOW", "BB_CHALK_BLUE", "BB_CHALK_WHITE", "BB_CHALK_RED"]

    for i, step_text in enumerate(steps[:8]):  # Max 8 steps
        step_safe = _safe(step_text.strip()[:120])
        color = chalk_colors[i % len(chalk_colors)]
        y_offset = 0.8 * (i + 1)

        if i == 0:
            step_blocks.append(f'''
        # Step {i+1}
        step{i+1} = Text("Step {i+1}: {step_safe}", font="Inter", color={color}, font_size=28)
        step{i+1}.next_to(divider, DOWN, buff=0.6)
        step{i+1}.to_edge(LEFT, buff=0.8)
        self.write_step(step{i+1}, run_time=2.0)
        self.wait(0.5)
        prev = step{i+1}''')
        else:
            step_blocks.append(f'''
        # Step {i+1}
        step{i+1} = Text("Step {i+1}: {step_safe}", font="Inter", color={color}, font_size=28)
        step{i+1}.next_to(prev, DOWN, buff=0.4)
        step{i+1}.to_edge(LEFT, buff=0.8)
        self.write_step(step{i+1}, run_time=2.0)
        self.wait(0.5)
        prev = step{i+1}''')

    steps_code = "\n".join(step_blocks)

    # Answer box section
    answer_code = ""
    if a_safe:
        answer_code = f'''
        # ── Final Answer (boxed) ──
        self.wait(0.5)
        ans_text = Text("Answer: {a_safe}", font="Inter", color=BB_CHALK_YELLOW, font_size=36)
        ans_text.next_to(prev, DOWN, buff=0.8)
        ans_box = SurroundingRectangle(ans_text, color=BB_CHALK_YELLOW, buff=0.3, corner_radius=0.05, stroke_width=3)
        self.write_step(ans_text, run_time=1.5)
        self.play(Create(ans_box), run_time=0.8)
        self.wait(2.0)'''
    else:
        answer_code = '''
        # ── End ──
        self.wait(2.0)'''

    # Subject header
    subject_line = ""
    if subj_safe:
        subject_line = f'''
        # Subject header
        subj = Text("{subj_safe}", font="Inter", color=BB_CHALK_BLUE, font_size=22)
        subj.to_corner(UR, buff=0.4)
        self.play(FadeIn(subj), run_time=0.5)'''

    return f'''class {scene_name}(BlackboardScene):
    def construct(self):
        # ── Blackboard Q&A — SILENT (no TTS, no voiceover) ──
{subject_line}

        # ── Write the question ──
        q_header = Text("Question:", font="Inter", color=BB_CHALK_RED, font_size=30)
        q_header.to_edge(UP, buff=0.5).to_edge(LEFT, buff=0.8)
        self.write_step(q_header, run_time=1.0)

        q_text = Text("{q_safe}", font="Inter", color=BB_CHALK_WHITE, font_size=26)
        q_text.next_to(q_header, DOWN, buff=0.3)
        q_text.to_edge(LEFT, buff=0.8)
        self.write_step(q_text, run_time=2.5)
        self.wait(1.0)

        # ── Divider ──
        divider = Line(LEFT * 6, RIGHT * 6, color=BB_CHALK_WHITE, stroke_width=1, stroke_opacity=0.5)
        divider.next_to(q_text, DOWN, buff=0.4)
        self.play(Create(divider), run_time=0.5)

        # ── Step-by-step solution ──
{steps_code}
{answer_code}
'''


run_blackboard_orchestrator = run_template_orchestrator  # alias
