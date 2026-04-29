"""
Template 12 — GEOMETRIC GROWTH: Shape scales/grows with ValueTracker + number
Pattern: Circle → scale with ValueTracker → display area formula → AHA
Use for: Area, volume, scaling laws, exponential growth, proportionality
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:
            r = ValueTracker(0.5)
            circ = always_redraw(lambda: Circle(
                radius=r.get_value(),
                color=TEAL_ACCENT, fill_color=TEAL_ACCENT, fill_opacity=0.18,
                stroke_width=4
            ).move_to(ORIGIN))
            r_lbl = always_redraw(lambda: latin_text(
                f"r = {r.get_value():.1f}", font_size=FONT_SIZE_LABEL, color=STAR_YELLOW
            ).to_corner(UR).shift(LEFT * 0.5 + DOWN * 0.3))
            self.add(circ, r_lbl)
            self.play(r.animate.set_value(2.0), run_time=tracker.duration * 0.7, rate_func=smooth)
            self.wait(tracker.duration * 0.3)

        with self.voiceover(text="<NARRATION_PLACEHOLDER_1>") as tracker:
            area_lbl = always_redraw(lambda: latin_text(
                f"A = π·{r.get_value():.1f}² = {3.14159 * r.get_value()**2:.2f}",
                font_size=FONT_SIZE_LABEL, color=TEXT_COLOR
            ).to_edge(DOWN, buff=0.6))
            self.add(area_lbl)
            self.play(r.animate.set_value(1.2), run_time=tracker.duration * 0.4, rate_func=smooth)
            self.play(r.animate.set_value(2.5), run_time=tracker.duration * 0.4, rate_func=smooth)
            self.play(Indicate(area_lbl, color=STAR_YELLOW), run_time=tracker.duration * 0.2)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_2>") as tracker:
            fb = formula_box("<NARRATION_PLACEHOLDER_0>", color=TEAL_ACCENT)
            fb.move_to(ORIGIN)
            self.play(FadeIn(fb, scale=0.7), run_time=tracker.duration * 0.5)
            self.play(Circumscribe(fb, color=STAR_YELLOW, time_width=2), run_time=tracker.duration * 0.3)
            playful_bounce(self, fb)
            self.wait(tracker.duration * 0.2)

        self.wait(0.5)
