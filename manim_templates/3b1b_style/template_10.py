"""
Template 10 — GRAPH TRANSFORMATION: Plot function then transform it
Pattern: Axes → plot f(x) → shift/scale with ValueTracker → show new curve
Use for: Graph transformations, function families, parameter effects
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:
            plane = branded_axes([-3.5, 3.5, 1], [-1, 4, 1]).scale(0.72).shift(DOWN * 0.2)
            self.play(Create(plane), run_time=tracker.duration * 0.3)
            graph1 = plane.plot(lambda x: x ** 2, x_range=[-2.5, 2.5],
                               color=TEAL_ACCENT, stroke_width=4)
            lbl1 = latin_text("f(x) = x²", font_size=FONT_SIZE_LABEL, color=TEAL_ACCENT)
            lbl1.to_corner(UR).shift(LEFT * 0.5 + DOWN * 0.3)
            self.play(Create(graph1), run_time=tracker.duration * 0.5)
            self.play(Write(lbl1), run_time=tracker.duration * 0.2)

        with self.voiceover(text="<NARRATION_PLACEHOLDER_1>") as tracker:
            a_val = ValueTracker(1)
            graph2 = always_redraw(lambda: plane.plot(
                lambda x: a_val.get_value() * x ** 2,
                x_range=[-2.5, 2.5], color=STAR_YELLOW, stroke_width=4
            ))
            lbl2 = always_redraw(lambda: latin_text(
                f"g(x) = {a_val.get_value():.1f}x²",
                font_size=FONT_SIZE_LABEL, color=STAR_YELLOW
            ).next_to(lbl1, DOWN, buff=0.3, aligned_edge=LEFT))
            self.add(graph2, lbl2)
            self.play(a_val.animate.set_value(2.5), run_time=tracker.duration * 0.5, rate_func=smooth)
            self.play(a_val.animate.set_value(0.4), run_time=tracker.duration * 0.35, rate_func=smooth)
            self.wait(tracker.duration * 0.15)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_2>") as tracker:
            fb = formula_box("<NARRATION_PLACEHOLDER_0>", color=TEAL_ACCENT)
            fb.move_to(ORIGIN)
            self.play(FadeIn(fb, scale=0.7), run_time=tracker.duration * 0.5)
            self.play(Circumscribe(fb, color=STAR_YELLOW, time_width=2), run_time=tracker.duration * 0.35)
            dot = glow_dot(fb.get_corner(UR), color=STAR_YELLOW)
            self.play(FadeIn(dot, scale=4), run_time=tracker.duration * 0.15)

        self.wait(0.5)
