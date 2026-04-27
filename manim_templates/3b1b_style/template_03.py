from manim import *
from manim_config.theme import *

class SceneTemplate03_NumberReveal(AmharicEduScene):
    def construct(self):
        setup_scene(self)
        with self.voiceover(text="<NARRATION_PLACEHOLDER>") as tracker:
            self.clear()
            title = title_card("<AMHARIC_TITLE>", "Number Reveal")
            self.play(FadeIn(title, shift=UP), run_time=tracker.duration * 0.2)
            
            num = number_ticker(self, start=0.0, end=<TARGET_NUMBER>, run_time=tracker.duration * 0.5, position=CENTER, color=STAR_YELLOW)
            
            label = amharic_text("<NUMBER_LABEL>", font_size=FONT_SIZE_LABEL, color=MUTED_COLOR).next_to(num, DOWN)
            self.play(Write(label), run_time=tracker.duration * 0.2)
            
            self.wait(tracker.duration * 0.1)
