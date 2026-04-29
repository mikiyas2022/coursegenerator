"""
Template 34 — VENN DIAGRAM: Overlapping circles showing set relationships
Pattern: Two circles slide in → overlap region highlights → labels animate
Use for: Set theory, probability, logic, classification, comparing concepts
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:
            left_c = Circle(radius=1.6, color=TEAL_ACCENT, fill_opacity=0.12, stroke_width=3)
            right_c = Circle(radius=1.6, color=STAR_YELLOW, fill_opacity=0.12, stroke_width=3)
            left_c.shift(LEFT * 1.1)
            right_c.shift(RIGHT * 1.1)

            lbl_l = latin_text("A", font_size=FONT_SIZE_LABEL, color=TEAL_ACCENT)
            lbl_l.move_to(left_c.get_center() + LEFT * 0.7)
            lbl_r = latin_text("B", font_size=FONT_SIZE_LABEL, color=STAR_YELLOW)
            lbl_r.move_to(right_c.get_center() + RIGHT * 0.7)

            self.play(
                Create(left_c), Create(right_c),
                FadeIn(lbl_l, shift=LEFT * 0.2), FadeIn(lbl_r, shift=RIGHT * 0.2),
                run_time=tracker.duration * 0.5
            )
            # Highlight intersection
            inter = Intersection(left_c, right_c, fill_color=SUCCESS_COLOR, fill_opacity=0.35, stroke_width=0)
            lbl_inter = latin_text("A ∩ B", font_size=FONT_SIZE_SMALL, color=SUCCESS_COLOR)
            lbl_inter.move_to(ORIGIN)
            self.play(FadeIn(inter), Write(lbl_inter), run_time=tracker.duration * 0.35)
            self.play(Indicate(lbl_inter, color=STAR_YELLOW), run_time=tracker.duration * 0.15)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_1>") as tracker:
            fb = formula_box("P(A ∩ B) = P(A) · P(B|A)", color=TEAL_ACCENT)
            fb.move_to(ORIGIN)
            self.play(FadeIn(fb, scale=0.6), run_time=tracker.duration * 0.5)
            self.play(Circumscribe(fb, color=STAR_YELLOW, time_width=2), run_time=tracker.duration * 0.35)
            dot = glow_dot(fb.get_corner(UR), color=STAR_YELLOW)
            self.play(FadeIn(dot, scale=4), run_time=tracker.duration * 0.15)

        self.wait(0.5)
