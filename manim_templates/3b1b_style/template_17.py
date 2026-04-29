"""
Template 17 — DERIVATIVE SLOPE: Tangent line follows curve
Pattern: Plot curve → moving point + tangent line always_redraw → slope label
Use for: Derivatives, rates of change, calculus intro, velocity from position
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:
            plane = branded_axes([-3, 3, 1], [-1, 5, 1]).scale(0.68).shift(DOWN * 0.2)
            self.play(Create(plane), run_time=tracker.duration * 0.3)
            curve = plane.plot(lambda x: x ** 2, x_range=[-2.2, 2.2],
                              color=TEAL_ACCENT, stroke_width=4)
            self.play(Create(curve), run_time=tracker.duration * 0.5)
            lbl = latin_text("f(x) = x²", font_size=FONT_SIZE_LABEL, color=TEAL_ACCENT)
            lbl.to_corner(UR).shift(LEFT * 0.5 + DOWN * 0.3)
            self.play(Write(lbl), run_time=tracker.duration * 0.2)

        with self.voiceover(text="<NARRATION_PLACEHOLDER_1>") as tracker:
            x_tracker = ValueTracker(-2.0)
            dot_on_curve = always_redraw(lambda: glow_dot(
                plane.c2p(x_tracker.get_value(), x_tracker.get_value() ** 2),
                color=STAR_YELLOW, radius=0.1
            ))
            tangent = always_redraw(lambda: plane.get_secant_slope_group(
                x=x_tracker.get_value(), graph=curve, dx=0.01,
                secant_line_length=2.5,
                secant_line_color=STAR_YELLOW,
            ))
            slope_lbl = always_redraw(lambda: latin_text(
                f"slope = {2 * x_tracker.get_value():.1f}",
                font_size=FONT_SIZE_LABEL, color=STAR_YELLOW
            ).to_corner(UL).shift(DOWN * 0.3 + RIGHT * 0.3))
            self.add(dot_on_curve, tangent, slope_lbl)
            self.play(x_tracker.animate.set_value(2.0), run_time=tracker.duration * 0.8, rate_func=smooth)
            self.wait(tracker.duration * 0.2)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_2>") as tracker:
            fb = formula_box("f'(x) = 2x", color=STAR_YELLOW)
            fb.move_to(ORIGIN)
            self.play(FadeIn(fb, scale=0.7), run_time=tracker.duration * 0.5)
            self.play(Circumscribe(fb, color=STAR_YELLOW, time_width=2), run_time=tracker.duration * 0.35)
            dot = glow_dot(fb.get_corner(UR) + UP * 0.1, color=STAR_YELLOW)
            self.play(FadeIn(dot, scale=4), run_time=tracker.duration * 0.15)

        self.wait(0.5)
