"""
Template 0789 — TEXT: ROSE_COLOR FONT_SIZE_BODY a5 e0
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:
            obj = latin_text("<NARRATION_PLACEHOLDER_0>", font_size=FONT_SIZE_BODY, color=ROSE_COLOR)
            obj.move_to(ORIGIN)
            clamp_to_screen(obj)
            self.play(FadeIn(obj, shift=LEFT*0.3), run_time=tracker.duration*0.5)
            self.play(Indicate(obj, color=TEAL_ACCENT), run_time=tracker.duration*0.3)
            self.wait(tracker.duration*0.1)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_1>") as tracker:
            obj = latin_text("<NARRATION_PLACEHOLDER_1>", font_size=FONT_SIZE_BODY, color=TEAL_ACCENT)
            obj.move_to(ORIGIN)
            clamp_to_screen(obj)
            self.play(FadeIn(obj, shift=UP*0.3), run_time=tracker.duration*0.5)
            self.play(Circumscribe(obj, color=ROSE_COLOR, time_width=2), run_time=tracker.duration*0.3)
            dot = glow_dot(obj.get_corner(UR), color=ROSE_COLOR)
            self.play(FadeIn(dot, scale=4), run_time=tracker.duration*0.1)
            self.wait(tracker.duration*0.1)

        self.wait(0.5)
