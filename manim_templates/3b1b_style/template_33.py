"""
Template 33 — ALWAYS_REDRAW TRACKER: Live-updating label follows a moving point
Pattern: Axes + dot on curve + always_redraw label shows coords → ValueTracker sweeps
Use for: Parametric motion, real-time readouts, dynamic systems, slope trackers
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:
            axes = branded_axes([-4, 4, 1], [-2, 4, 1]).scale(0.65)
            axes.move_to(DOWN * 0.3)
            self.play(Create(axes), run_time=tracker.duration * 0.3)

            t_val = ValueTracker(-3.0)

            moving_dot = always_redraw(lambda: glow_dot(
                axes.c2p(t_val.get_value(), t_val.get_value()**2 * 0.15),
                color=STAR_YELLOW, radius=0.1
            ))
            coord_label = always_redraw(lambda: latin_text(
                f"({t_val.get_value():.1f}, {t_val.get_value()**2 * 0.15:.1f})",
                font_size=FONT_SIZE_SMALL, color=STAR_YELLOW
            ).next_to(axes.c2p(t_val.get_value(), t_val.get_value()**2 * 0.15), UR, buff=0.15))

            curve = axes.plot(lambda x: x**2 * 0.15, x_range=[-3.5, 3.5], color=TEAL_ACCENT, stroke_width=3)
            self.play(Create(curve), run_time=tracker.duration * 0.2)
            self.add(moving_dot, coord_label)
            self.play(t_val.animate.set_value(3.0), run_time=tracker.duration * 0.4, rate_func=smooth)
            self.wait(tracker.duration * 0.1)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_1>") as tracker:
            fb = formula_box("y = 0.15x²", color=TEAL_ACCENT)
            fb.move_to(ORIGIN)
            self.play(FadeIn(fb, scale=0.7), run_time=tracker.duration * 0.5)
            self.play(Circumscribe(fb, color=STAR_YELLOW), run_time=tracker.duration * 0.35)
            playful_bounce(self, fb)
            self.wait(tracker.duration * 0.15)

        self.wait(0.5)
