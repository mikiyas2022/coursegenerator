from manim import *
from manim_config.theme import *

class Blackboard_06_FinalAnswerBox(BlackboardScene):
    def construct(self):
        steps = VGroup(
            MathTex("<STEP_1>", color=BB_CHALK_WHITE),
            MathTex("<STEP_2>", color=BB_CHALK_WHITE),
            MathTex("<FINAL_ANSWER>", color=BB_CHALK_YELLOW, font_size=56)
        ).arrange(DOWN, buff=1.0)
        
        for step in steps:
            self.write_step(step, run_time=1.5)
            
        box = SurroundingRectangle(steps[-1], color=BB_CHALK_RED, stroke_width=6)
        self.play(Create(box), run_time=1.5)
        
        self.wait(3.0)
