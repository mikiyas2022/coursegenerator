from manim import *
from agent_core.manim_config.blackboard_theme import *

class Blackboard_08_Variation(BlackboardScene):
    def construct(self):
        # Silent blackboard writing
        q_text = Text("<QUESTION_TEXT>", font="Inter", color=BB_CHALK_WHITE, font_size=28).to_edge(UP, buff=1.0)
        self.write_step(q_text, run_time=3.0)
        
        step1 = Text("Variation 8", font="Inter", color=BB_CHALK_YELLOW, font_size=32).next_to(q_text, DOWN, buff=1.0).align_to(q_text, LEFT)
        self.write_step(step1, run_time=2.0)
        
        step2 = Text("<STEP_2>", font="Inter", color=BB_CHALK_BLUE, font_size=32).next_to(step1, DOWN, buff=0.5).align_to(q_text, LEFT)
        self.write_step(step2, run_time=2.0)
        
        self.wait(2.0)
