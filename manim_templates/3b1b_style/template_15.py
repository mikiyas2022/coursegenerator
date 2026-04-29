"""
Template 15 — ENERGY CONSERVATION: Bar chart / energy level diagram
Pattern: Bars animate height → total stays constant → color shift KE/PE
Use for: Energy conservation, thermodynamics, chemical potential, economics
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:
            ke_val = ValueTracker(3.0)
            pe_val = ValueTracker(0.0)
            baseline = Line(LEFT * 5, RIGHT * 5, color=AXIS_COLOR, stroke_width=2)
            baseline.to_edge(DOWN, buff=0.8)
            ke_bar = always_redraw(lambda: Rectangle(
                width=1.8, height=ke_val.get_value(),
                fill_color=TEAL_ACCENT, fill_opacity=0.8,
                stroke_width=2, color=TEAL_ACCENT
            ).next_to(baseline, UP, buff=0).shift(LEFT * 2).align_to(baseline, DOWN))
            pe_bar = always_redraw(lambda: Rectangle(
                width=1.8, height=3.0 - ke_val.get_value(),
                fill_color=ROSE_COLOR, fill_opacity=0.8,
                stroke_width=2, color=ROSE_COLOR
            ).next_to(baseline, UP, buff=0).shift(RIGHT * 2).align_to(baseline, DOWN))
            ke_lbl = latin_text("KE", font_size=FONT_SIZE_LABEL, color=TEAL_ACCENT)
            ke_lbl.next_to(baseline, DOWN, buff=0.1).shift(LEFT * 2)
            pe_lbl = latin_text("PE", font_size=FONT_SIZE_LABEL, color=ROSE_COLOR)
            pe_lbl.next_to(baseline, DOWN, buff=0.1).shift(RIGHT * 2)
            self.play(Create(baseline), FadeIn(ke_lbl), FadeIn(pe_lbl), run_time=tracker.duration * 0.3)
            self.add(ke_bar, pe_bar)
            self.wait(tracker.duration * 0.7)

        with self.voiceover(text="<NARRATION_PLACEHOLDER_1>") as tracker:
            self.play(ke_val.animate.set_value(0.1), run_time=tracker.duration * 0.7, rate_func=smooth)
            total_lbl = latin_text("Total = constant!", font_size=FONT_SIZE_LABEL, color=STAR_YELLOW)
            total_lbl.to_edge(UP, buff=0.5)
            self.play(FadeIn(total_lbl, shift=DOWN * 0.3), run_time=tracker.duration * 0.3)

        with self.voiceover(text="<NARRATION_PLACEHOLDER_2>") as tracker:
            self.play(ke_val.animate.set_value(3.0), run_time=tracker.duration * 0.5, rate_func=smooth)
            fb = formula_box("KE + PE = const", color=STAR_YELLOW)
            fb.move_to(UP * 1.5)
            self.play(FadeIn(fb, shift=DOWN * 0.2), run_time=tracker.duration * 0.3)
            self.play(Circumscribe(fb, color=STAR_YELLOW), run_time=tracker.duration * 0.2)

        self.wait(0.5)
