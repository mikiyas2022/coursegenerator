"""
Template 333 — TEXT: TEAL_ACCENT FONT_SIZE_LABEL anim1 extra0
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:
            obj = latin_text("<NARRATION_PLACEHOLDER_0>", font_size=FONT_SIZE_LABEL, color=TEAL_ACCENT)
            obj.move_to(ORIGIN)
            clamp_to_screen(obj)
            self.play(FadeIn(obj, scale=0.5), run_time=tracker.duration*0.5)
            self.play(Indicate(obj, color=STAR_YELLOW), run_time=tracker.duration*0.3)
            self.wait(tracker.duration*0.1)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_1>") as tracker:
            obj = formula_box("<NARRATION_PLACEHOLDER_1>", color=STAR_YELLOW)
            obj.move_to(ORIGIN)
            self.play(Create(obj), run_time=tracker.duration*0.5)
            self.play(Circumscribe(obj, color=TEAL_ACCENT, time_width=2), run_time=tracker.duration*0.3)
            dot = glow_dot(obj.get_corner(UR), color=TEAL_ACCENT)
            self.play(FadeIn(dot, scale=4), run_time=tracker.duration*0.1)
            self.wait(tracker.duration*0.1)

        self.wait(0.5)
