from manim import *
from agent_core.manim_config.theme import *

class SceneTemplate06_CameraChoreography(AmharicEduScene):
    def construct(self):
        setup_scene(self)
        with self.voiceover(text="<NARRATION_PLACEHOLDER>") as tracker:
            self.clear()
            title = title_card("<AMHARIC_TITLE>", "Deep Dive")
            self.play(FadeIn(title, shift=UP), run_time=tracker.duration * 0.1)
            
            group = VGroup(
                Square(color=TEAL_ACCENT).shift(LEFT*2),
                Circle(color=ROSE_COLOR).shift(RIGHT*2)
            )
            self.play(Create(group), run_time=tracker.duration * 0.2)
            
            camera_zoom_to(self, group[1], zoom=0.5, run_time=tracker.duration * 0.3)
            
            detail = amharic_text("<DETAIL_TEXT>", font_size=FONT_SIZE_SMALL, color=STAR_YELLOW).move_to(group[1].get_center() + UP)
            self.play(Write(detail), run_time=tracker.duration * 0.2)
            
            camera_restore(self, run_time=tracker.duration * 0.1)
            self.wait(tracker.duration * 0.1)
