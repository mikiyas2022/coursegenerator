from manim import *
from manim_config.theme import *

class SceneTemplate04_GeometricProof(AmharicEduScene):
    def construct(self):
        setup_scene(self)
        with self.voiceover(text="<NARRATION_PLACEHOLDER>") as tracker:
            self.clear()
            title = title_card("<AMHARIC_TITLE>", "Geometric Proof")
            self.play(FadeIn(title, shift=UP), run_time=tracker.duration * 0.1)
            
            square = Square(side_length=3, color=TEAL_ACCENT, fill_opacity=0.2).move_to(LEFT*2)
            self.play(Create(square), run_time=tracker.duration * 0.2)
            
            formula = formula_box("<FORMULA>", color=STAR_YELLOW).move_to(RIGHT*3)
            self.play(FadeIn(formula), run_time=tracker.duration * 0.2)
            
            # Proof transition
            triangle = Polygon(square.get_corner(DL), square.get_corner(UR), square.get_corner(DR), color=ROSE_COLOR, fill_opacity=0.4)
            self.play(Create(triangle), run_time=tracker.duration * 0.3)
            
            highlight_concept(self, formula)
            self.wait(tracker.duration * 0.2)
