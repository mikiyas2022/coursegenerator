"""
Template 35 — BEFORE/AFTER SPLIT: Vertical split screen comparison
Pattern: Left panel shows "before" → right panel shows "after" → arrow connects insight
Use for: Transformations, simplifications, before/after proofs, cause & effect
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:
            divider = DashedLine(UP * 2.8, DOWN * 2.8, color=MUTED_COLOR, stroke_width=1.5)
            lbl_before = latin_text("Before", font_size=FONT_SIZE_SMALL, color=MUTED_COLOR)
            lbl_before.move_to(UP * 2.6 + LEFT * 3)
            lbl_after = latin_text("After", font_size=FONT_SIZE_SMALL, color=MUTED_COLOR)
            lbl_after.move_to(UP * 2.6 + RIGHT * 3)
            self.play(Create(divider), FadeIn(lbl_before), FadeIn(lbl_after),
                     run_time=tracker.duration * 0.25)

            # Before side — messy equation
            eq_before = formula_box("2x + 4 = 10", color=MUTED_COLOR)
            eq_before.scale(0.75).move_to(LEFT * 3 + UP * 0.3)
            clamp_to_screen(eq_before)
            self.play(FadeIn(eq_before, shift=UP * 0.2), run_time=tracker.duration * 0.25)

            # After side — clean result
            eq_after = formula_box("x = 3", color=STAR_YELLOW)
            eq_after.scale(0.75).move_to(RIGHT * 3 + UP * 0.3)
            clamp_to_screen(eq_after)
            self.play(FadeIn(eq_after, shift=UP * 0.2), run_time=tracker.duration * 0.25)

            arrow = Arrow(eq_before.get_right(), eq_after.get_left(), color=TEAL_ACCENT, stroke_width=4,
                         max_tip_length_to_length_ratio=0.15, buff=0.3)
            self.play(GrowArrow(arrow), run_time=tracker.duration * 0.15)
            self.play(Indicate(eq_after, color=STAR_YELLOW), run_time=tracker.duration * 0.1)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_1>") as tracker:
            insight = latin_text("Simplify step by step.", font_size=FONT_SIZE_BODY, color=TEAL_ACCENT)
            insight.move_to(ORIGIN)
            clamp_to_screen(insight)
            self.play(Write(insight), run_time=tracker.duration * 0.55)
            self.play(insight.animate.set_color(STAR_YELLOW), run_time=tracker.duration * 0.3)
            playful_bounce(self, insight)
            self.wait(tracker.duration * 0.15)

        self.wait(0.5)
