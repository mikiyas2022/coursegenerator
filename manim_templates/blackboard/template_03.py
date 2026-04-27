from manim import *
from manim_config.blackboard_theme import *

class Blackboard_03_DrawDiagram(BlackboardScene):
    def construct(self):
        title = Text("<DIAGRAM_TITLE>", font="Inter", color=BB_CHALK_WHITE, font_size=32).to_edge(UP)
        self.write_step(title, run_time=1.5)
        
        # Diagram elements
        base_line = Line(LEFT*3, RIGHT*3, color=BB_CHALK_WHITE, stroke_width=4).shift(DOWN*2)
        self.write_step(base_line, run_time=1.0)
        
        box = Square(side_length=1.5, color=BB_CHALK_YELLOW).next_to(base_line, UP, buff=0)
        self.write_step(box, run_time=1.5)
        
        label = Text("<LABEL>", font="Inter", color=BB_CHALK_BLUE, font_size=24).move_to(box)
        self.write_step(label, run_time=1.0)
        
        self.wait(2.0)
