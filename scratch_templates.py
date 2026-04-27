import os

os.makedirs("manim_templates/3b1b_style", exist_ok=True)
os.makedirs("manim_templates/blackboard", exist_ok=True)

# Generate 3B1B templates
for i in range(1, 21):
    with open(f"manim_templates/3b1b_style/template_{i:02d}.py", "w") as f:
        f.write(f'''from manim import *
from agent_core.theme import *

class SceneTemplate{i:02d}(AmharicEduScene):
    def construct(self):
        setup_scene(self)
        # Template {i:02d} implementation
        with self.voiceover(text="<NARRATION_PLACEHOLDER>") as tracker:
            self.clear()
            title = title_card("Template {i}", "3B1B Style")
            self.play(FadeIn(title, shift=UP), run_time=tracker.duration * 0.5)
            # Add dynamic animations here
            self.wait(tracker.duration * 0.5)
''')

# Generate Blackboard templates
blackboard_names = [
    "write_text", "write_equation", "draw_diagram", "erase_section", 
    "highlight_step", "step_by_step_solver", "draw_circle", "draw_triangle",
    "draw_force_vectors", "draw_graph", "write_list", "box_final_answer",
    "scroll_down", "zoom_in", "pan_right"
]

for name in blackboard_names:
    with open(f"manim_templates/blackboard/blackboard_{name}.py", "w") as f:
        f.write(f'''from manim import *
from agent_core.manim_config.blackboard_theme import *

class Blackboard_{name.title().replace("_", "")}(BlackboardScene):
    def construct(self):
        setup_blackboard(self)
        # Stroke-by-stroke realism
        # <CONTENT_PLACEHOLDER>
        self.wait(1)
''')

print("Generated templates.")
