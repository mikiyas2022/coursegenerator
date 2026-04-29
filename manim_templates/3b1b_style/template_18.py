"""
Template 18 — LISSAJOUS / SPIRAL: Parametric curve traces a beautiful pattern
Pattern: Dot traces spiral/lissajous → mesmerizing → snap to formula
Use for: Parametric equations, circular motion, 2D kinematics, Fourier series
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:
            plane = branded_axes([-3.5, 3.5, 1], [-2.5, 2.5, 1]).scale(0.68)
            self.play(Create(plane), run_time=tracker.duration * 0.25)
            t = ValueTracker(0)
            trace_dot = always_redraw(lambda: Dot(
                plane.c2p(2.5 * np.cos(t.get_value()), 2.0 * np.sin(2 * t.get_value())),
                radius=0.1, color=STAR_YELLOW
            ))
            trail = TracedPath(trace_dot.get_center, stroke_color=TEAL_ACCENT,
                              stroke_width=3, dissipating_time=None)
            self.add(trail, trace_dot)
            self.play(t.animate.set_value(TAU), run_time=tracker.duration * 0.7, rate_func=linear)
            self.wait(tracker.duration * 0.05)

        with self.voiceover(text="<NARRATION_PLACEHOLDER_1>") as tracker:
            beauty_lbl = latin_text("Parametric beauty!", font_size=FONT_SIZE_LABEL, color=ROSE_COLOR)
            beauty_lbl.to_corner(UR).shift(LEFT * 0.5 + DOWN * 0.3)
            self.play(FadeIn(beauty_lbl, shift=LEFT * 0.3), run_time=tracker.duration * 0.4)
            self.play(t.animate.set_value(2 * TAU), run_time=tracker.duration * 0.45, rate_func=linear)
            self.play(Indicate(beauty_lbl, color=STAR_YELLOW), run_time=tracker.duration * 0.15)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_2>") as tracker:
            fb = formula_box("x=Acos(t), y=Bsin(2t)", color=TEAL_ACCENT)
            fb.move_to(ORIGIN)
            self.play(FadeIn(fb, scale=0.6), run_time=tracker.duration * 0.5)
            self.play(Circumscribe(fb, color=STAR_YELLOW), run_time=tracker.duration * 0.35)
            dot = glow_dot(fb.get_corner(UR), color=STAR_YELLOW)
            self.play(FadeIn(dot, scale=4), run_time=tracker.duration * 0.15)

        self.wait(0.5)
