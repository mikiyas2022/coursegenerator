"""
Template 03 — PARABOLIC TRACE: Animated dot traces trajectory on axes
Pattern: Axes → TracedPath + always_redraw dot → velocity labels appear
Use for: Projectile motion, quadratic functions, optimization
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:
            plane = branded_axes([-0.5, 6.5, 1], [-0.5, 4.5, 1]).scale(0.65).shift(DOWN * 0.3)
            self.play(Create(plane), run_time=tracker.duration * 0.3)
            t_param = ValueTracker(0)
            trace_dot = always_redraw(lambda: Dot(
                point=plane.c2p(5 * t_param.get_value(),
                                4 * t_param.get_value() - 4 * t_param.get_value() ** 2),
                radius=0.13, color=STAR_YELLOW
            ))
            trail = TracedPath(trace_dot.get_center, stroke_color=TEAL_ACCENT, stroke_width=3.5,
                               dissipating_time=None)
            self.add(trail, trace_dot)
            self.play(t_param.animate.set_value(1), run_time=tracker.duration * 0.65, rate_func=linear)
            playful_bounce(self, trace_dot)

        with self.voiceover(text="<NARRATION_PLACEHOLDER_1>") as tracker:
            peak_dot = glow_dot(plane.c2p(2.5, 4.0), color=STAR_YELLOW)
            peak_lbl = latin_text("MAX", font_size=FONT_SIZE_LABEL, color=STAR_YELLOW)
            peak_lbl.next_to(peak_dot, UP, buff=0.2)
            self.play(FadeIn(peak_dot, scale=4), run_time=tracker.duration * 0.35)
            self.play(Write(peak_lbl), run_time=tracker.duration * 0.35)
            self.play(Circumscribe(peak_dot, color=ROSE_COLOR, time_width=2), run_time=tracker.duration * 0.3)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_2>") as tracker:
            fb = formula_box("<NARRATION_PLACEHOLDER_0>", color=STAR_YELLOW)
            fb.move_to(ORIGIN)
            self.play(FadeIn(fb, scale=0.7), run_time=tracker.duration * 0.5)
            self.play(Indicate(fb, color=TEAL_ACCENT, scale_factor=1.08), run_time=tracker.duration * 0.3)
            dot2 = glow_dot(fb.get_corner(UR) + UP * 0.1, color=STAR_YELLOW)
            self.play(FadeIn(dot2, scale=3), run_time=tracker.duration * 0.2)

        self.wait(0.5)
