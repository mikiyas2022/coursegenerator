from manim import *
from manim_config.theme import *

class Blackboard_04_EraseAndHighlight(BlackboardScene):
    def construct(self):
        eq1 = MathTex("<INITIAL_EQ>", color=BB_CHALK_WHITE, font_size=48)
        self.write_step(eq1, run_time=2.0)
        
        # Highlight
        box = SurroundingRectangle(eq1, color=BB_CHALK_YELLOW, buff=0.2)
        self.play(Create(box), run_time=1.5)
        
        # Erase and rewrite
        self.play(FadeOut(eq1), FadeOut(box), run_time=1.0) # Erase
        
        eq2 = MathTex("<FINAL_EQ>", color=BB_CHALK_BLUE, font_size=48)
        self.write_step(eq2, run_time=2.0)
        
        self.wait(2.0)
