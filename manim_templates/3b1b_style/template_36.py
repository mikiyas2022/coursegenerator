"""
Template 36 — TAYLOR SERIES: Successive polynomial approximations converging
Pattern: Original curve → degree-1 line → degree-2 parabola → … → near-perfect fit
Use for: Taylor series, approximations, convergence, limits, calculus
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:
            axes = branded_axes([-4, 4, 1], [-2, 4, 1]).scale(0.6)
            axes.move_to(DOWN * 0.2)
            self.play(Create(axes), run_time=tracker.duration * 0.2)

            # Target function
            import math
            target = axes.plot(lambda x: math.exp(x * 0.3), x_range=[-3.5, 3.5], color=STAR_YELLOW, stroke_width=3)
            target_lbl = latin_text("e^(0.3x)", font_size=FONT_SIZE_SMALL, color=STAR_YELLOW)
            target_lbl.next_to(axes.c2p(3, math.exp(0.9)), UR, buff=0.1)
            clamp_to_screen(target_lbl)
            self.play(Create(target), FadeIn(target_lbl), run_time=tracker.duration * 0.25)

            # Successive approximations
            approxes = [
                lambda x: 1 + 0.3 * x,
                lambda x: 1 + 0.3 * x + 0.045 * x**2,
                lambda x: 1 + 0.3 * x + 0.045 * x**2 + 0.0045 * x**3,
            ]
            colors = [MUTED_COLOR, TEAL_ACCENT, SUCCESS_COLOR]
            labels_text = ["n=1", "n=2", "n=3"]
            prev_curve = None
            time_each = tracker.duration * 0.15
            for fn, col, ltxt in zip(approxes, colors, labels_text):
                curve = axes.plot(fn, x_range=[-3.5, 3.5], color=col, stroke_width=2.5)
                lbl = latin_text(ltxt, font_size=FONT_SIZE_CAPTION, color=col)
                lbl.next_to(axes.c2p(3.2, fn(3.2)), RIGHT, buff=0.1)
                clamp_to_screen(lbl)
                if prev_curve:
                    self.play(ReplacementTransform(prev_curve, curve), FadeIn(lbl), run_time=time_each)
                else:
                    self.play(Create(curve), FadeIn(lbl), run_time=time_each)
                prev_curve = curve

            self.wait(tracker.duration * 0.1)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_1>") as tracker:
            fb = formula_box("f(x) ≈ Σ f⁽ⁿ⁾(0) xⁿ / n!", color=TEAL_ACCENT)
            fb.move_to(ORIGIN)
            self.play(FadeIn(fb, scale=0.6), run_time=tracker.duration * 0.5)
            self.play(Circumscribe(fb, color=STAR_YELLOW, time_width=2), run_time=tracker.duration * 0.35)
            dot = glow_dot(fb.get_corner(UR), color=STAR_YELLOW)
            self.play(FadeIn(dot, scale=4), run_time=tracker.duration * 0.15)

        self.wait(0.5)
