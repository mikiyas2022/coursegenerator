"""
Template 06 — SINE WAVE: Animated sin/cos graph with peak marker + phase shift
Pattern: Axes → plot sin → Create → peak glow_dot → phase ValueTracker shift
Use for: Wave motion, oscillations, periodic functions, AC circuits, sound
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:
            plane = branded_axes([-0.5, 7.5, 1], [-2.5, 2.5, 1]).scale(0.7).shift(DOWN * 0.1)
            self.play(Create(plane), run_time=tracker.duration * 0.25)
            phase = ValueTracker(0)
            graph = always_redraw(lambda: plane.plot(
                lambda x: 1.8 * np.sin(x + phase.get_value()),
                x_range=[0, 6.8], color=TEAL_ACCENT, stroke_width=4
            ))
            self.add(graph)
            self.play(phase.animate.set_value(TAU), run_time=tracker.duration * 0.6, rate_func=linear)
            peak = glow_dot(plane.c2p(PI / 2 - phase.get_value() % TAU, 1.8), color=STAR_YELLOW)
            self.play(FadeIn(peak, scale=3), run_time=tracker.duration * 0.15)

        with self.voiceover(text="<NARRATION_PLACEHOLDER_1>") as tracker:
            amp_lbl = latin_text("Amplitude = 1.8", font_size=FONT_SIZE_LABEL, color=STAR_YELLOW)
            amp_lbl.to_corner(UL).shift(DOWN * 0.3 + RIGHT * 0.3)
            period_lbl = latin_text("Period = 2π", font_size=FONT_SIZE_LABEL, color=TEAL_ACCENT)
            period_lbl.next_to(amp_lbl, DOWN, buff=0.25, aligned_edge=LEFT)
            self.play(FadeIn(amp_lbl, shift=RIGHT * 0.4), run_time=tracker.duration * 0.3)
            self.play(FadeIn(period_lbl, shift=RIGHT * 0.4), run_time=tracker.duration * 0.3)
            self.play(Indicate(peak, color=ROSE_COLOR), run_time=tracker.duration * 0.4)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_2>") as tracker:
            fb = formula_box("<NARRATION_PLACEHOLDER_0>", color=TEAL_ACCENT)
            fb.move_to(ORIGIN)
            self.play(Create(fb[0]), Write(fb[1]), run_time=tracker.duration * 0.5)
            self.play(Circumscribe(fb, color=STAR_YELLOW, time_width=2), run_time=tracker.duration * 0.35)
            dot = glow_dot(fb.get_corner(UR) + UP * 0.1, color=STAR_YELLOW)
            self.play(FadeIn(dot, scale=3), run_time=tracker.duration * 0.15)

        self.wait(0.5)
