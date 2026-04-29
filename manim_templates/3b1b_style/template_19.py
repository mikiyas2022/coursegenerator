"""
Template 19 — RIEMANN SUM: Bars fill under curve → approximation → exact
Pattern: f(x) curve → n=4 bars → n increases → smooth integral area
Use for: Integration, area under curve, Riemann sums, accumulation
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:
            plane = branded_axes([0, 4, 1], [0, 4, 1]).scale(0.72).shift(DOWN * 0.2)
            self.play(Create(plane), run_time=tracker.duration * 0.3)
            curve = plane.plot(lambda x: -0.5 * x ** 2 + 3 * x - 0.5,
                              x_range=[0.2, 3.8], color=TEAL_ACCENT, stroke_width=4)
            self.play(Create(curve), run_time=tracker.duration * 0.5)
            lbl = latin_text("f(x)", font_size=FONT_SIZE_LABEL, color=TEAL_ACCENT)
            lbl.to_corner(UR).shift(LEFT * 0.5 + DOWN * 0.3)
            self.play(Write(lbl), run_time=tracker.duration * 0.2)

        with self.voiceover(text="<NARRATION_PLACEHOLDER_1>") as tracker:
            n_bars = ValueTracker(4)
            def make_bars(n):
                bars = VGroup()
                step = 3.6 / n
                for i in range(int(n)):
                    x = 0.2 + i * step
                    y = max(0, -0.5 * x**2 + 3*x - 0.5)
                    bar = Rectangle(
                        width=plane.c2p(step, 0)[0] - plane.c2p(0, 0)[0],
                        height=plane.c2p(0, y)[1] - plane.c2p(0, 0)[1],
                        fill_color=TEAL_ACCENT, fill_opacity=0.4,
                        stroke_color=TEAL_ACCENT, stroke_width=1
                    )
                    bar.move_to(plane.c2p(x + step/2, y/2))
                    bars.add(bar)
                return bars
            bars = make_bars(4)
            self.play(FadeIn(bars), run_time=tracker.duration * 0.5)
            n_lbl = latin_text("n = 4 bars", font_size=FONT_SIZE_LABEL, color=STAR_YELLOW)
            n_lbl.to_corner(UL).shift(DOWN * 0.3 + RIGHT * 0.3)
            self.play(FadeIn(n_lbl, shift=RIGHT * 0.3), run_time=tracker.duration * 0.5)

        with self.voiceover(text="<NARRATION_PLACEHOLDER_2>") as tracker:
            for n in [8, 16, 32]:
                new_bars = make_bars(n)
                self.play(ReplacementTransform(bars, new_bars), run_time=0.5)
                bars = new_bars
            fb = formula_box("Area = ∫f(x)dx", color=STAR_YELLOW)
            fb.to_edge(DOWN, buff=0.4)
            self.play(FadeIn(fb, shift=UP * 0.2), run_time=tracker.duration * 0.5)
            self.play(Circumscribe(fb, color=STAR_YELLOW), run_time=tracker.duration * 0.3)

        self.wait(0.5)
