"""
Template 24 — PROBABILITY TREE: Branching decisions with probability labels
Pattern: Root → branches appear → labels → leaf nodes → final probabilities
Use for: Probability, decision trees, conditional probability, statistics
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:
            root = Dot(LEFT * 4, radius=0.12, color=TEAL_ACCENT)
            root_lbl = latin_text("Start", font_size=FONT_SIZE_SMALL, color=TEXT_COLOR)
            root_lbl.next_to(root, LEFT, buff=0.2)
            self.play(FadeIn(root), Write(root_lbl), run_time=tracker.duration * 0.5)
            # Branch 1: Success
            b1 = Arrow(root.get_center(), LEFT * 1 + UP * 1.5, buff=0.12,
                      color=SUCCESS_COLOR, stroke_width=4,
                      max_tip_length_to_length_ratio=0.12)
            b1_lbl = latin_text("P=0.6", font_size=FONT_SIZE_SMALL, color=SUCCESS_COLOR)
            b1_lbl.move_to(b1.get_center() + UP * 0.2 + LEFT * 0.15)
            b1_dot = Dot(LEFT * 1 + UP * 1.5, radius=0.1, color=SUCCESS_COLOR)
            b1_name = latin_text("Success", font_size=FONT_SIZE_SMALL, color=SUCCESS_COLOR)
            b1_name.next_to(b1_dot, RIGHT, buff=0.15)
            # Branch 2: Fail
            b2 = Arrow(root.get_center(), LEFT * 1 + DOWN * 1.5, buff=0.12,
                      color=ERROR_COLOR, stroke_width=4,
                      max_tip_length_to_length_ratio=0.12)
            b2_lbl = latin_text("P=0.4", font_size=FONT_SIZE_SMALL, color=ERROR_COLOR)
            b2_lbl.move_to(b2.get_center() + DOWN * 0.2 + LEFT * 0.15)
            b2_dot = Dot(LEFT * 1 + DOWN * 1.5, radius=0.1, color=ERROR_COLOR)
            b2_name = latin_text("Fail", font_size=FONT_SIZE_SMALL, color=ERROR_COLOR)
            b2_name.next_to(b2_dot, RIGHT, buff=0.15)
            self.play(Create(b1), Create(b2), run_time=tracker.duration * 0.35)
            self.play(FadeIn(b1_dot), FadeIn(b1_lbl), FadeIn(b1_name),
                     FadeIn(b2_dot), FadeIn(b2_lbl), FadeIn(b2_name),
                     run_time=tracker.duration * 0.3)

        with self.voiceover(text="<NARRATION_PLACEHOLDER_1>") as tracker:
            result_lbl = latin_text("E[X] = 0.6 × 1 + 0.4 × 0 = 0.6",
                                   font_size=FONT_SIZE_LABEL, color=STAR_YELLOW)
            result_lbl.to_edge(DOWN, buff=0.5)
            self.play(Write(result_lbl), run_time=tracker.duration * 0.6)
            self.play(Indicate(result_lbl, color=STAR_YELLOW), run_time=tracker.duration * 0.4)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_2>") as tracker:
            fb = formula_box("E[X] = Σ xᵢ · P(xᵢ)", color=TEAL_ACCENT)
            fb.move_to(ORIGIN)
            self.play(FadeIn(fb, scale=0.6), run_time=tracker.duration * 0.5)
            self.play(Circumscribe(fb, color=STAR_YELLOW), run_time=tracker.duration * 0.35)
            dot = glow_dot(fb.get_corner(UR), color=STAR_YELLOW)
            self.play(FadeIn(dot, scale=4), run_time=tracker.duration * 0.15)

        self.wait(0.5)
