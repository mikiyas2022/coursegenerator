"""
Template 04 — FORMULA REVEAL: Box appears → terms highlight one-by-one → glow
Pattern: Draw rect → Write formula → Indicate each term → Circumscribe → glow_dot
Use for: Equations with multiple terms, laws, physical constants
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:
            fb = formula_box("<NARRATION_PLACEHOLDER_0>", color=TEAL_ACCENT)
            fb.scale(1.1).move_to(ORIGIN)
            self.play(Create(fb[0]), run_time=tracker.duration * 0.3)
            self.play(Write(fb[1]), run_time=tracker.duration * 0.5)
            self.play(fb.animate.shift(UP * 0.5), run_time=tracker.duration * 0.2)

        with self.voiceover(text="<NARRATION_PLACEHOLDER_1>") as tracker:
            lhs = latin_text("Each term matters.", font_size=FONT_SIZE_LABEL, color=MUTED_COLOR)
            lhs.next_to(fb, DOWN, buff=0.5)
            clamp_to_screen(lhs)
            self.play(FadeIn(lhs, shift=UP * 0.2), run_time=tracker.duration * 0.4)
            self.play(Circumscribe(fb, color=STAR_YELLOW, time_width=1.8), run_time=tracker.duration * 0.4)
            dot = glow_dot(fb.get_top() + UP * 0.2, color=STAR_YELLOW)
            self.play(FadeIn(dot, scale=4), run_time=tracker.duration * 0.2)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_2>") as tracker:
            explosion = VGroup(*[
                Arrow(ORIGIN, rotate_vector(RIGHT * 1.5, i * TAU / 8),
                      buff=0, color=STAR_YELLOW, stroke_width=4,
                      max_tip_length_to_length_ratio=0.15)
                for i in range(8)
            ]).move_to(ORIGIN)
            self.play(LaggedStart(*[Create(a) for a in explosion], lag_ratio=0.05),
                      run_time=tracker.duration * 0.5)
            aha = latin_text("AHA!", font_size=FONT_SIZE_TITLE, color=STAR_YELLOW)
            aha.move_to(ORIGIN)
            self.play(FadeIn(aha, scale=0.3), run_time=tracker.duration * 0.3)
            playful_bounce(self, aha)
            self.wait(tracker.duration * 0.2)

        self.wait(0.5)
