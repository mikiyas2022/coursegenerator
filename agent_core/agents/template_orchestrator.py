"""
agents/template_orchestrator.py — Template-Powered Manim Orchestrator
Replaces Manim Coder to enforce template-based code generation to stop LLM hallucinations.
"""

import os
import glob
import random
from config import get_llm, MANIM_CODER_MODEL
from logger import get_logger

log = get_logger("template_orchestrator")

def run_template_orchestrator(scenes: list[dict], mode: str = "3b1b") -> list[str]:
    """
    Selects templates based on the mode and storyboard_plan.
    Fills in text, equations, and timings.
    Returns executable Manim python code.
    """
    log.info(f"Running Template Orchestrator for mode: {mode}")
    generated_classes = []

    if mode == "3b1b":
        template_dir = os.path.join("manim_templates", "3b1b_style")
    else:
        template_dir = os.path.join("manim_templates", "blackboard")

    templates = glob.glob(os.path.join(template_dir, "*.py"))
    
    for idx, scene in enumerate(scenes):
        scene_name = scene.get("scene_name", f"Scene{idx}")
        
        # Select a template
        # For a full RAG implementation, we would embed templates and match. 
        # Here we do a simplified deterministic match or random select.
        if templates:
            selected_template = random.choice(templates)
            with open(selected_template, "r") as f:
                template_code = f.read()
            
            # Replace placeholder with actual scene name
            if "class SceneTemplate" in template_code:
                template_code = template_code.replace(
                    template_code[template_code.find("class "):template_code.find("(AmharicEduScene):")],
                    f"class {scene_name}"
                )
            if "class Blackboard_" in template_code:
                template_code = template_code.replace(
                    template_code[template_code.find("class "):template_code.find("(BlackboardScene):")],
                    f"class {scene_name}"
                )
            
            # Replace narration placeholder
            if "sentences" in scene and scene["sentences"]:
                narration = " ".join(scene["sentences"])
            else:
                narration = scene.get("concept", "Physics")
            
            template_code = template_code.replace("<NARRATION_PLACEHOLDER>", narration.replace('"', "'"))
            template_code = template_code.replace("<CONTENT_PLACEHOLDER>", f'self.write_step(Text("{narration}"))')

            generated_classes.append(template_code)
        else:
            log.warning("No templates found! Using fallback.")
            generated_classes.append(f"""class {scene_name}(AmharicEduScene):\n    def construct(self):\n        pass""")

    return generated_classes
