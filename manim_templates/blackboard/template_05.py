from manim import *
from agent_core.manim_config.blackboard_theme import *

class Blackboard_05_PanZoom(BlackboardScene, MovingCameraScene):
    def construct(self):
        group = VGroup(
            Text("<PART_A>", font="Inter", color=BB_CHALK_YELLOW).shift(LEFT*3),
            Text("<PART_B>", font="Inter", color=BB_CHALK_BLUE).shift(RIGHT*3)
        )
        self.write_step(group[0], run_time=1.5)
        self.write_step(group[1], run_time=1.5)
        
        self.play(
            self.camera.frame.animate.move_to(group[0]).set(width=5),
            run_time=2.0
        )
        self.wait(1.0)
        
        self.play(
            self.camera.frame.animate.move_to(group[1]),
            run_time=2.0
        )
        self.wait(1.0)
        
        self.play(self.camera.frame.animate.to_default_state(), run_time=1.5)
        self.wait(2.0)
