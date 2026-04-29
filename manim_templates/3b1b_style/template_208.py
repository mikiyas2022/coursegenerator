"""
Template 208 — MORPH: Square→RegularPolygon
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:
            s1 = Square(color=TEAL_ACCENT, fill_opacity=0.15, stroke_width=3)
            s1.move_to(LEFT*2)
            s2 = RegularPolygon(color=STAR_YELLOW, fill_opacity=0.15, stroke_width=3)
            s2.move_to(RIGHT*2)
            self.play(Create(s1), run_time=tracker.duration*0.25)
            self.play(ReplacementTransform(s1.copy(), s2), run_time=tracker.duration*0.45)
            self.play(Indicate(s2, color=STAR_YELLOW), run_time=tracker.duration*0.2)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_1>") as tracker:
            fb = formula_box("<NARRATION_PLACEHOLDER_0>", color=TEAL_ACCENT)
            fb.move_to(ORIGIN)
            self.play(FadeIn(fb, scale=0.5), run_time=tracker.duration*0.45)
            self.play(Circumscribe(fb, color=STAR_YELLOW, time_width=2), run_time=tracker.duration*0.35)
            dot = glow_dot(fb.get_corner(UR), color=STAR_YELLOW)
            self.play(FadeIn(dot, scale=4), run_time=tracker.duration*0.15)

        self.wait(0.5)
