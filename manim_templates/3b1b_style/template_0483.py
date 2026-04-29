"""
Template 0483 — TEXT: TEAL_ACCENT FONT_SIZE_LABEL a5 e2
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:
            obj = latin_text("<NARRATION_PLACEHOLDER_0>", font_size=FONT_SIZE_LABEL, color=TEAL_ACCENT)
            obj.move_to(ORIGIN)
            clamp_to_screen(obj)
            self.play(FadeIn(obj, shift=LEFT*0.3), run_time=tracker.duration*0.5)
            self.play(Indicate(obj, color=STAR_YELLOW), run_time=tracker.duration*0.3)
            playful_bounce(self, obj)
            self.wait(tracker.duration*0.1)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_1>") as tracker:
            obj = latin_text("<NARRATION_PLACEHOLDER_1>", font_size=FONT_SIZE_BODY, color=STAR_YELLOW)
            obj.move_to(ORIGIN)
            clamp_to_screen(obj)
            self.play(FadeIn(obj, shift=UP*0.3), run_time=tracker.duration*0.5)
            self.play(Circumscribe(obj, color=TEAL_ACCENT, time_width=2), run_time=tracker.duration*0.3)
            ul = Line(obj.get_left(), obj.get_right(), color=TEAL_ACCENT, stroke_width=3)
            ul.next_to(obj, DOWN, buff=0.15)
            self.play(Create(ul), run_time=tracker.duration*0.15)
            self.wait(tracker.duration*0.1)

        self.wait(0.5)
