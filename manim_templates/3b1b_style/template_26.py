"""
Template 26 — PENDULUM MOTION: Oscillating pendulum with energy labels
Pattern: Pendulum swings → angle label → KE/PE labels → period formula
Use for: Simple harmonic motion, pendulums, oscillations, restoring forces
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:
            pivot = Dot(UP * 3, radius=0.1, color=MUTED_COLOR)
            self.play(FadeIn(pivot), run_time=tracker.duration * 0.2)
            angle = ValueTracker(PI / 4)
            L = 2.8
            bob = always_redraw(lambda: Circle(
                radius=0.25,
                fill_color=TEAL_ACCENT, fill_opacity=0.9,
                stroke_color=TEAL_ACCENT, stroke_width=3
            ).move_to(pivot.get_center() + L * np.array([
                np.sin(angle.get_value()), -np.cos(angle.get_value()), 0
            ])))
            rod = always_redraw(lambda: Line(
                pivot.get_center(), bob.get_center(),
                color=MUTED_COLOR, stroke_width=3
            ))
            self.add(rod, bob)
            # Swing twice
            for _ in range(2):
                self.play(angle.animate.set_value(-PI / 4), run_time=0.9, rate_func=smooth)
                self.play(angle.animate.set_value(PI / 4), run_time=0.9, rate_func=smooth)
            self.wait(tracker.duration * 0.1)

        with self.voiceover(text="<NARRATION_PLACEHOLDER_1>") as tracker:
            period_lbl = latin_text("T = 2π√(L/g)", font_size=FONT_SIZE_LABEL, color=STAR_YELLOW)
            period_lbl.to_corner(UR).shift(LEFT * 0.5 + DOWN * 0.3)
            self.play(Write(period_lbl), run_time=tracker.duration * 0.4)
            # Show one more swing with formula visible
            self.play(angle.animate.set_value(-PI / 4), run_time=0.9, rate_func=smooth)
            self.play(angle.animate.set_value(PI / 4), run_time=0.9, rate_func=smooth)
            self.play(Indicate(period_lbl, color=STAR_YELLOW), run_time=tracker.duration * 0.1)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_2>") as tracker:
            fb = formula_box("T = 2π√(L/g)", color=TEAL_ACCENT)
            fb.move_to(ORIGIN)
            self.play(FadeIn(fb, scale=0.7), run_time=tracker.duration * 0.5)
            self.play(Circumscribe(fb, color=STAR_YELLOW), run_time=tracker.duration * 0.35)
            playful_bounce(self, fb)
            self.wait(tracker.duration * 0.15)

        self.wait(0.5)
