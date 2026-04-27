from manim import *
from manim_config.blackboard_theme import *

class Blackboard_02_StepByStepSolving(BlackboardScene):
    def construct(self):
        q_text = Text("Q: <QUESTION_TEXT>", font="Inter", color=BB_CHALK_WHITE, font_size=28).to_edge(UP+LEFT, buff=0.5)
        self.write_step(q_text, run_time=2.0)
        
        eq1 = MathTex("<EQ_1>", color=BB_CHALK_YELLOW, font_size=42).next_to(q_text, DOWN, buff=1.0).align_to(q_text, LEFT)
        self.write_step(eq1, run_time=2.0)
        
        arrow = MathTex(r"\Rightarrow", color=BB_CHALK_WHITE).next_to(eq1, DOWN, buff=0.5).align_to(eq1, LEFT)
        self.write_step(arrow, run_time=0.5)
        
        eq2 = MathTex("<EQ_2>", color=BB_CHALK_BLUE, font_size=42).next_to(arrow, RIGHT, buff=0.5)
        self.write_step(eq2, run_time=2.0)
        
        self.wait(2.0)
