"""
Template 29 — UNIT CIRCLE: Angle sweeps around, sin/cos labels track live
Pattern: Unit circle → dot sweeps → sin/cos projections follow → trig identity
Use for: Trigonometry, unit circle, sin/cos definitions, angle measurement
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:
            plane = branded_axes([-2, 2, 1], [-1.5, 1.5, 1]).scale(0.8)
            unit_circle = Circle(radius=plane.c2p(1, 0)[0] - plane.c2p(0, 0)[0],
                                color=TEAL_ACCENT, stroke_width=3)
            unit_circle.move_to(plane.c2p(0, 0))
            self.play(Create(plane), Create(unit_circle), run_time=tracker.duration * 0.5)
            # r=1 label
            r_lbl = latin_text("r = 1", font_size=FONT_SIZE_SMALL, color=MUTED_COLOR)
            r_lbl.next_to(plane.c2p(0.5, 0), UP, buff=0.05)
            self.play(Write(r_lbl), run_time=tracker.duration * 0.3)
            self.wait(tracker.duration * 0.2)

        with self.voiceover(text="<NARRATION_PLACEHOLDER_1>") as tracker:
            theta = ValueTracker(0)
            unit_r = plane.c2p(1, 0)[0] - plane.c2p(0, 0)[0]
            moving_dot = always_redraw(lambda: glow_dot(
                plane.c2p(np.cos(theta.get_value()), np.sin(theta.get_value())),
                color=STAR_YELLOW, radius=0.12
            ))
            radius_vec = always_redraw(lambda: Arrow(
                plane.c2p(0, 0),
                plane.c2p(np.cos(theta.get_value()), np.sin(theta.get_value())),
                buff=0, color=VECTOR_COLOR, stroke_width=5,
                max_tip_length_to_length_ratio=0.13
            ))
            sin_line = always_redraw(lambda: Line(
                plane.c2p(np.cos(theta.get_value()), 0),
                plane.c2p(np.cos(theta.get_value()), np.sin(theta.get_value())),
                color=Y_COLOR, stroke_width=3
            ))
            cos_line = always_redraw(lambda: Line(
                plane.c2p(0, 0),
                plane.c2p(np.cos(theta.get_value()), 0),
                color=X_COLOR, stroke_width=3
            ))
            self.add(cos_line, sin_line, radius_vec, moving_dot)
            self.play(theta.animate.set_value(TAU), run_time=tracker.duration * 0.85, rate_func=linear)
            self.wait(tracker.duration * 0.15)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_2>") as tracker:
            fb = formula_box("sin²θ + cos²θ = 1", color=STAR_YELLOW)
            fb.move_to(ORIGIN)
            self.play(FadeIn(fb, scale=0.6), run_time=tracker.duration * 0.5)
            self.play(Circumscribe(fb, color=STAR_YELLOW, time_width=2), run_time=tracker.duration * 0.35)
            playful_bounce(self, fb)
            dot = glow_dot(fb.get_corner(UR) + UP * 0.1, color=STAR_YELLOW)
            self.play(FadeIn(dot, scale=4), run_time=tracker.duration * 0.15)

        self.wait(0.5)
