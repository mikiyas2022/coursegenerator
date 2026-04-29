"""
Template 0391 — VENN: TEAL_ACCENT STAR_YELLOW
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:
            left_c = Circle(radius=1.5, color=TEAL_ACCENT, fill_opacity=0.1, stroke_width=3).shift(LEFT*1)
            right_c = Circle(radius=1.5, color=STAR_YELLOW, fill_opacity=0.1, stroke_width=3).shift(RIGHT*1)
            self.play(Create(left_c), Create(right_c), run_time=tracker.duration*0.35)
            inter = Intersection(left_c, right_c, fill_color=SUCCESS_COLOR, fill_opacity=0.3, stroke_width=0)
            lbl = latin_text("A ∩ B", font_size=FONT_SIZE_SMALL, color=SUCCESS_COLOR)
            lbl.move_to(ORIGIN)
            self.play(FadeIn(inter), Write(lbl), run_time=tracker.duration*0.35)
            self.play(Indicate(lbl, color=STAR_YELLOW), run_time=tracker.duration*0.2)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_1>") as tracker:
            fb = formula_box("<NARRATION_PLACEHOLDER_0>", color=TEAL_ACCENT)
            fb.move_to(ORIGIN)
            self.play(FadeIn(fb, scale=0.5), run_time=tracker.duration*0.45)
            self.play(Circumscribe(fb, color=STAR_YELLOW, time_width=2), run_time=tracker.duration*0.35)
            dot = glow_dot(fb.get_corner(UR), color=STAR_YELLOW)
            self.play(FadeIn(dot, scale=4), run_time=tracker.duration*0.15)

        self.wait(0.5)
