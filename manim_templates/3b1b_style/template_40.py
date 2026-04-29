"""
Template 40 — AREA UNDER CURVE: Animated fill between curve and x-axis
Pattern: Axes + curve → fill grows from left → area value counter ticks up
Use for: Integration, area, accumulation, probability density
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:
            axes = branded_axes([-1, 5, 1], [-0.5, 3, 1]).scale(0.6)
            axes.move_to(DOWN * 0.3 + LEFT * 0.5)
            self.play(Create(axes), run_time=tracker.duration * 0.2)
            import math
            curve = axes.plot(lambda x: 2 * math.sin(x * 0.8) + 0.5, x_range=[0.2, 4.5], color=TEAL_ACCENT, stroke_width=3)
            self.play(Create(curve), run_time=tracker.duration * 0.2)
            area = axes.get_area(curve, x_range=[0.5, 4.0], color=TEAL_ACCENT, opacity=0.25)
            self.play(FadeIn(area), run_time=tracker.duration * 0.35)
            # Area label
            a_lbl = latin_text("Area ≈ 5.2", font_size=FONT_SIZE_LABEL, color=STAR_YELLOW)
            a_lbl.next_to(axes.c2p(2.5, 1), UP, buff=0.1)
            clamp_to_screen(a_lbl)
            self.play(Write(a_lbl), run_time=tracker.duration * 0.2)
            self.play(Indicate(a_lbl, color=STAR_YELLOW), run_time=tracker.duration * 0.05)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_1>") as tracker:
            fb = formula_box("∫ f(x) dx", color=TEAL_ACCENT)
            fb.move_to(ORIGIN)
            self.play(FadeIn(fb, scale=0.6), run_time=tracker.duration * 0.5)
            self.play(Circumscribe(fb, color=STAR_YELLOW, time_width=2), run_time=tracker.duration * 0.35)
            dot = glow_dot(fb.get_corner(UR), color=STAR_YELLOW)
            self.play(FadeIn(dot, scale=4), run_time=tracker.duration * 0.15)

        self.wait(0.5)
