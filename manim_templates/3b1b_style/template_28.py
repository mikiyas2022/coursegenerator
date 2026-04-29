"""
Template 28 — HISTOGRAM / BAR CHART: Data visualization with animated bars
Pattern: Empty axes → bars grow up one by one → mean line appears → normal approx
Use for: Statistics, distributions, data analysis, mean/median/mode
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:
            baseline = Line(LEFT * 5, RIGHT * 5, color=AXIS_COLOR, stroke_width=2)
            baseline.shift(DOWN * 2.5)
            yax = Arrow(DOWN * 2.5 + LEFT * 5, UP * 2 + LEFT * 5, buff=0,
                       color=AXIS_COLOR, stroke_width=2,
                       max_tip_length_to_length_ratio=0.05)
            self.play(Create(baseline), Create(yax), run_time=tracker.duration * 0.4)
            # Build histogram bars
            data = [1.5, 2.8, 3.5, 3.2, 2.0, 1.2]
            colors = [TEAL_ACCENT, TEAL_ACCENT, STAR_YELLOW, STAR_YELLOW, TEAL_ACCENT, TEAL_ACCENT]
            bars = VGroup()
            for i, (h, c) in enumerate(zip(data, colors)):
                bar = Rectangle(
                    width=1.3, height=h,
                    fill_color=c, fill_opacity=0.75,
                    stroke_color=c, stroke_width=2
                )
                bar.next_to(baseline, UP, buff=0).shift(RIGHT * (i * 1.5 - 3.75))
                bar.align_to(baseline, DOWN)
                bars.add(bar)
            self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.1),
                     run_time=tracker.duration * 0.6)

        with self.voiceover(text="<NARRATION_PLACEHOLDER_1>") as tracker:
            mean_h = sum(data) / len(data)
            mean_line = DashedLine(
                LEFT * 5 + UP * (mean_h - 2.5), RIGHT * 5 + UP * (mean_h - 2.5),
                color=STAR_YELLOW, stroke_width=2.5, stroke_opacity=0.8
            )
            mean_lbl = latin_text(f"mean = {mean_h:.1f}", font_size=FONT_SIZE_LABEL, color=STAR_YELLOW)
            mean_lbl.next_to(mean_line, RIGHT, buff=0.2)
            self.play(Create(mean_line), Write(mean_lbl), run_time=tracker.duration * 0.6)
            self.play(Indicate(mean_lbl, color=STAR_YELLOW), run_time=tracker.duration * 0.4)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_2>") as tracker:
            fb = formula_box("μ = Σxᵢ / n", color=TEAL_ACCENT)
            fb.move_to(ORIGIN)
            self.play(FadeIn(fb, scale=0.7), run_time=tracker.duration * 0.5)
            self.play(Circumscribe(fb, color=STAR_YELLOW), run_time=tracker.duration * 0.35)
            dot = glow_dot(fb.get_corner(UR), color=STAR_YELLOW)
            self.play(FadeIn(dot, scale=4), run_time=tracker.duration * 0.15)

        self.wait(0.5)
