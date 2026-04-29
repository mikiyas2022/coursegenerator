"""
agents/template_orchestrator.py — Template-Powered Manim Orchestrator
=====================================================================
Replaces Manim Coder for both 3B1B and Blackboard modes.
- 3B1B mode: picks random 3b1b_style template, fills narration placeholders
- Blackboard mode: generates a DETERMINISTIC, silent, step-by-step Q&A scene
  using BlackboardScene (NO voiceover, NO TTS, NO audio)
  Now with RICH content: real equations, calculations, diagrams.
"""

import os
import re
import glob
import random
import sys
import textwrap

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
    1. Writes the full question on the board stroke-by-stroke
    2. Shows step-by-step solution with REAL calculations
    3. Boxes the final answer
    All silent — no voiceover, no TTS.
    """
    generated = []

    for idx, scene in enumerate(scenes):
        scene_name = scene.get("scene_name", f"BB_Scene{idx}")
        question = scene.get("question", scene.get("topic", scene.get("concept", "Solve the problem")))
        answer = scene.get("correct_answer", scene.get("answer", ""))
        subject = scene.get("subject_grade", scene.get("metaphor", ""))

        # Extract sentences/steps — these come from blackboard_solver.py
        sentences = scene.get("sentences", [])
        if not sentences:
            script = scene.get("amharic_script", "")
            if script:
                sentences = [s.strip() for s in script.split(".") if s.strip()]

        # CRITICAL: if sentences are empty or all generic, log a warning
        if not sentences or len(sentences) < 2:
            log.warning(f"Scene {scene_name} has no solving steps! Using fallback.")
            sentences = _emergency_steps(question, answer)

        # Build the step-by-step solution code
        code = _build_blackboard_scene(scene_name, question, answer, subject, sentences)
        generated.append(code)

    return generated


def _emergency_steps(question: str, answer: str) -> list[str]:
    """Last-resort steps when the solver completely fails."""
    import re as _re
    numbers = _re.findall(r'[\d.]+\s*(?:cm|m|kg|N|g|s|Hz|J|W|V|A|Ω|°|%|km|mm)?', question)
    nums_str = ', '.join(n.strip() for n in numbers) if numbers else 'see question'
    steps = [
        f"Given: {nums_str}",
        f"Required: Find the answer",
    ]
    if answer:
        steps.append(f"Solution: Working toward {answer}")
        steps.append(f"∴ Answer: {answer}")
    else:
        steps.append("Applying the relevant formula...")
        steps.append("Calculating...")
    return steps


def _safe(text: str) -> str:
    """Escape text for Python string literals."""
    return text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def _wrap_text(text: str, max_chars: int = 70) -> list[str]:
    """Break long text into multiple lines for the blackboard."""
    if len(text) <= max_chars:
        return [text]
    return textwrap.wrap(text, width=max_chars)


def _is_equation_line(text: str) -> bool:
    """Detect if a line contains equations/math (should use larger font and highlighting)."""
    # Lines with = signs and numbers are equations
    has_equals = '=' in text
    has_numbers = bool(re.search(r'\d', text))
    has_math_symbols = any(c in text for c in ['×', '÷', '/', '+', '²', '³', 'π', '∴', 'η', 'Σ'])
    # "Given:" lines with numbers are data lines
    starts_with_step = bool(re.match(r'^(Step\s*\d|Given|Find|Required|Formula|VR|MA|η|∴|Answer)', text, re.IGNORECASE))

    return (has_equals and has_numbers) or has_math_symbols or starts_with_step


def _is_final_answer(text: str) -> bool:
    """Detect if this is the final answer line."""
    lower = text.lower().strip()
    return (
        lower.startswith("∴") or
        lower.startswith("answer:") or
        lower.startswith("final answer") or
        lower.startswith("∴ answer") or
        "✓" in text or
        "✔" in text
    )


def _build_blackboard_scene(
    scene_name: str,
    question: str,
    answer: str,
    subject: str,
    steps: list[str],
) -> str:
    """
    Build a complete BlackboardScene class as a Python string.
    This produces RICH, teacher-like solving with proper layout.
    Handles scrolling when content exceeds screen height.
    """
    q_safe = _safe(question[:300])
    a_safe = _safe(answer[:150]) if answer else ""
    subj_safe = _safe(subject[:80]) if subject else ""

    # ── Break the question into wrapped lines ──
    q_lines = _wrap_text(question[:300], max_chars=65)

    # ── Build question-writing code ──
    q_write_blocks = []
    for i, line in enumerate(q_lines):
        line_safe = _safe(line)
        if i == 0:
            q_write_blocks.append(f'''
        q_line_{i} = Text("{line_safe}", font="Inter", color=BB_CHALK_WHITE, font_size=24)
        if q_line_{i}.width > 12.0:
            q_line_{i}.scale_to_fit_width(12.0)
        q_line_{i}.next_to(q_header, DOWN, buff=0.25)
        q_line_{i}.to_edge(LEFT, buff=0.8)
        self.write_step(q_line_{i}, run_time=2.0)''')
        else:
            q_write_blocks.append(f'''
        q_line_{i} = Text("{line_safe}", font="Inter", color=BB_CHALK_WHITE, font_size=24)
        if q_line_{i}.width > 12.0:
            q_line_{i}.scale_to_fit_width(12.0)
        q_line_{i}.next_to(q_line_{i-1}, DOWN, buff=0.15)
        q_line_{i}.to_edge(LEFT, buff=0.8)
        self.write_step(q_line_{i}, run_time=1.5)''')

    q_code = "\n".join(q_write_blocks)
    last_q_var = f"q_line_{len(q_lines)-1}"

    # ── Build solution steps ──
    step_blocks = []
    chalk_colors = {
        "given": "BB_CHALK_YELLOW",
        "equation": "BB_CHALK_BLUE",
        "calculation": "BB_CHALK_WHITE",
        "answer": "BB_CHALK_YELLOW",
        "label": "BB_CHALK_RED",
    }

    # Track vertical position — if too many steps, we need to scroll
    total_steps = len(steps)
    needs_scroll = total_steps > 5  # More than 5 steps likely overflows

    for i, step_text in enumerate(steps[:10]):  # Max 10 steps
        step_safe = _safe(step_text.strip()[:160])  # Allow longer lines
        is_eq = _is_equation_line(step_text)
        is_final = _is_final_answer(step_text)

        # Choose color based on content
        if is_final:
            color = "BB_CHALK_YELLOW"
            font_size = 28
        elif is_eq:
            color = "BB_CHALK_BLUE"
            font_size = 26
        elif step_text.lower().startswith("given"):
            color = "BB_CHALK_YELLOW"
            font_size = 24
        elif re.match(r'^step\s*\d', step_text, re.IGNORECASE):
            color = "BB_CHALK_WHITE"
            font_size = 24
        else:
            color = "BB_CHALK_WHITE"
            font_size = 24

        # Wrap long step text
        wrapped = _wrap_text(step_text.strip(), max_chars=70)

        if len(wrapped) == 1:
            # Single line step
            run_time = max(1.5, min(3.5, len(step_safe) / 40))
            if i == 0:
                step_blocks.append(f'''
        # ── Step {i+1} ──
        step{i} = Text("{step_safe}", font="Inter", color={color}, font_size={font_size})
        if step{i}.width > 12.5:
            step{i}.scale_to_fit_width(12.5)
        step{i}.next_to(prev, DOWN, buff=0.3)
        step{i}.to_edge(LEFT, buff=0.8)
        self.write_step(step{i}, run_time={run_time:.1f})
        self.wait(0.4)
        prev = step{i}''')
            else:
                # If we need scrolling and we're past step 4, scroll up
                scroll_code = ""
                if needs_scroll and i >= 4:
                    scroll_code = f"""
        # Scroll content up to make room
        all_content = Group(*[m for m in self.mobjects if m is not None])
        self.play(all_content.animate.shift(UP * 0.6), run_time=0.4)"""

                step_blocks.append(f'''{scroll_code}
        # ── Step {i+1} ──
        step{i} = Text("{step_safe}", font="Inter", color={color}, font_size={font_size})
        if step{i}.width > 12.5:
            step{i}.scale_to_fit_width(12.5)
        step{i}.next_to(prev, DOWN, buff=0.3)
        step{i}.to_edge(LEFT, buff=0.8)
        self.write_step(step{i}, run_time={run_time:.1f})
        self.wait(0.4)
        prev = step{i}''')
        else:
            # Multi-line step — write each sub-line
            sub_blocks = []
            for j, sub_line in enumerate(wrapped[:3]):  # Max 3 sub-lines per step
                sub_safe = _safe(sub_line)
                sub_run_time = max(1.0, len(sub_line) / 40)
                if i == 0 and j == 0:
                    sub_blocks.append(f'''
        step{i}_{j} = Text("{sub_safe}", font="Inter", color={color}, font_size={font_size})
        if step{i}_{j}.width > 12.5:
            step{i}_{j}.scale_to_fit_width(12.5)
        step{i}_{j}.next_to(prev, DOWN, buff=0.3)
        step{i}_{j}.to_edge(LEFT, buff=0.8)
        self.write_step(step{i}_{j}, run_time={sub_run_time:.1f})''')
                elif j == 0:
                    sub_blocks.append(f'''
        step{i}_{j} = Text("{sub_safe}", font="Inter", color={color}, font_size={font_size})
        if step{i}_{j}.width > 12.5:
            step{i}_{j}.scale_to_fit_width(12.5)
        step{i}_{j}.next_to(prev, DOWN, buff=0.3)
        step{i}_{j}.to_edge(LEFT, buff=0.8)
        self.write_step(step{i}_{j}, run_time={sub_run_time:.1f})''')
                else:
                    sub_blocks.append(f'''
        step{i}_{j} = Text("{sub_safe}", font="Inter", color={color}, font_size={font_size})
        if step{i}_{j}.width > 12.5:
            step{i}_{j}.scale_to_fit_width(12.5)
        step{i}_{j}.next_to(step{i}_{j-1}, DOWN, buff=0.12)
        step{i}_{j}.to_edge(LEFT, buff=0.8)
        self.write_step(step{i}_{j}, run_time={sub_run_time:.1f})''')

            last_sub = f"step{i}_{len(wrapped[:3])-1}"
            step_blocks.append(f'''
        # ── Step {i+1} (multi-line) ──
{"".join(sub_blocks)}
        self.wait(0.4)
        prev = {last_sub}''')

    steps_code = "\n".join(step_blocks)

    # ── Final answer box ──
    answer_code = ""
    if a_safe:
        answer_code = f'''
        # ── Final Answer (boxed) ──
        self.wait(0.5)
        # Scroll up if needed
        all_final = Group(*[m for m in self.mobjects if m is not None])
        if prev.get_bottom()[1] < -2.5:
            self.play(all_final.animate.shift(UP * 1.0), run_time=0.5)
        ans_text = Text("Answer: {a_safe}", font="Inter", color=BB_CHALK_YELLOW, font_size=32)
        if ans_text.width > 10.0:
            ans_text.scale_to_fit_width(10.0)
        ans_text.next_to(prev, DOWN, buff=0.6)
        ans_text.to_edge(LEFT, buff=1.2)
        ans_box = SurroundingRectangle(ans_text, color=BB_CHALK_YELLOW, buff=0.25, corner_radius=0.05, stroke_width=3)
        self.write_step(ans_text, run_time=1.5)
        self.play(Create(ans_box), run_time=0.8)
        self.wait(2.5)'''
    else:
        answer_code = '''
        # ── End ──
        self.wait(2.5)'''

    # Subject header
    subject_line = ""
    if subj_safe:
        subject_line = f'''
        # Subject header
        subj = Text("{subj_safe}", font="Inter", color=BB_CHALK_BLUE, font_size=20)
        subj.to_corner(UR, buff=0.3)
        self.play(FadeIn(subj), run_time=0.5)'''

    return f'''class {scene_name}(BlackboardScene):
    def construct(self):
        # ── Blackboard Q&A — SILENT (no TTS, no voiceover) ──
{subject_line}

        # ── Write the full question ──
        q_header = Text("Question:", font="Inter", color=BB_CHALK_RED, font_size=28)
        q_header.to_edge(UP, buff=0.4).to_edge(LEFT, buff=0.8)
        self.write_step(q_header, run_time=0.8)
{q_code}
        self.wait(1.0)

        # ── Divider ──
        divider = Line(LEFT * 6, RIGHT * 6, color=BB_CHALK_WHITE, stroke_width=1, stroke_opacity=0.4)
        divider.next_to({last_q_var}, DOWN, buff=0.3)
        self.play(Create(divider), run_time=0.4)

        # ── Solution header ──
        sol_header = Text("Solution:", font="Inter", color=BB_CHALK_RED, font_size=26)
        sol_header.next_to(divider, DOWN, buff=0.25)
        sol_header.to_edge(LEFT, buff=0.8)
        self.write_step(sol_header, run_time=0.6)
        prev = sol_header

        # ── Step-by-step solution with real calculations ──
{steps_code}
{answer_code}
'''


run_blackboard_orchestrator = run_template_orchestrator  # alias
