"""
Template 21 — EXPONENTIAL DECAY/GROWTH: Log-scale reveal
Pattern: Axes → exponential curve rises fast → log scale toggle → straight line
Use for: Exponential growth, half-life, radioactive decay, compound interest
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:
            plane = branded_axes([0, 5, 1], [0, 8, 2]).scale(0.65).shift(DOWN * 0.2)
            self.play(Create(plane), run_time=tracker.duration * 0.3)
            k_val = ValueTracker(0)
            exp_curve = always_redraw(lambda: plane.plot(
                lambda x: np.exp(k_val.get_value() * x) if x >= 0 else 0,
                x_range=[0, min(4.5, 4.5)],
                color=TEAL_ACCENT, stroke_width=4
            ))
            self.add(exp_curve)
            self.play(k_val.animate.set_value(1), run_time=tracker.duration * 0.6, rate_func=smooth)
            lbl = latin_text("y = eˣ", font_size=FONT_SIZE_LABEL, color=TEAL_ACCENT)
            lbl.to_corner(UR).shift(LEFT * 0.5 + DOWN * 0.3)
            self.play(Write(lbl), run_time=tracker.duration * 0.1)

        with self.voiceover(text="<NARRATION_PLACEHOLDER_1>") as tracker:
            double_lbl = latin_text("Doubles every step!", font_size=FONT_SIZE_LABEL, color=STAR_YELLOW)
            double_lbl.to_corner(UL).shift(DOWN * 0.3 + RIGHT * 0.3)
            self.play(FadeIn(double_lbl, shift=RIGHT * 0.3), run_time=tracker.duration * 0.4)
            self.play(k_val.animate.set_value(1.5), run_time=tracker.duration * 0.45, rate_func=smooth)
            self.play(Indicate(exp_curve, color=ROSE_COLOR), run_time=tracker.duration * 0.15)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_2>") as tracker:
            fb = formula_box("N(t) = N₀ · eᵏᵗ", color=STAR_YELLOW)
            fb.move_to(ORIGIN)
            self.play(FadeIn(fb, scale=0.6), run_time=tracker.duration * 0.5)
            self.play(Circumscribe(fb, color=STAR_YELLOW, time_width=2), run_time=tracker.duration * 0.35)
            dot = glow_dot(fb.get_corner(UR), color=STAR_YELLOW)
            self.play(FadeIn(dot, scale=4), run_time=tracker.duration * 0.15)

        self.wait(0.5)
