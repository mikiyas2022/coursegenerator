"""
Template 09 — SIDE-BY-SIDE COMPARISON: Two concepts shown simultaneously
Pattern: Left object vs Right object → arrow → show relationship → merge
Use for: Before/after, two cases, action/reaction, series vs parallel circuits
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:
            vs_line = Line(UP * 3, DOWN * 3, color=MUTED_COLOR, stroke_width=1.5, stroke_opacity=0.5)
            vs = latin_text("VS", font_size=FONT_SIZE_BODY, color=MUTED_COLOR)
            vs.move_to(ORIGIN)
            left_box = branded_circle(1.2, color=TEAL_ACCENT, fill_opacity=0.15).shift(LEFT * 3)
            right_box = branded_circle(1.2, color=ROSE_COLOR, fill_opacity=0.15).shift(RIGHT * 3)
            left_lbl = latin_text("A", font_size=FONT_SIZE_HEADER, color=TEAL_ACCENT)
            left_lbl.move_to(left_box.get_center())
            right_lbl = latin_text("B", font_size=FONT_SIZE_HEADER, color=ROSE_COLOR)
            right_lbl.move_to(right_box.get_center())
            self.play(Create(vs_line), FadeIn(vs), run_time=tracker.duration * 0.3)
            self.play(DrawBorderThenFill(left_box), DrawBorderThenFill(right_box),
                     run_time=tracker.duration * 0.4)
            self.play(Write(left_lbl), Write(right_lbl), run_time=tracker.duration * 0.3)

        with self.voiceover(text="<NARRATION_PLACEHOLDER_1>") as tracker:
            bridge = DoubleArrow(left_box.get_right(), right_box.get_left(),
                                buff=0.2, color=STAR_YELLOW, stroke_width=4,
                                max_tip_length_to_length_ratio=0.12)
            bridge_lbl = latin_text("connected", font_size=FONT_SIZE_SMALL, color=STAR_YELLOW)
            bridge_lbl.next_to(bridge, UP, buff=0.15)
            self.play(Create(bridge), run_time=tracker.duration * 0.4)
            self.play(Write(bridge_lbl), run_time=tracker.duration * 0.3)
            self.play(Indicate(bridge, color=STAR_YELLOW), run_time=tracker.duration * 0.3)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_2>") as tracker:
            fb = formula_box("<NARRATION_PLACEHOLDER_0>", color=TEAL_ACCENT)
            fb.move_to(ORIGIN)
            self.play(FadeIn(fb, scale=0.6), run_time=tracker.duration * 0.45)
            self.play(Circumscribe(fb, color=STAR_YELLOW), run_time=tracker.duration * 0.35)
            dot = glow_dot(fb.get_corner(UR), color=STAR_YELLOW)
            self.play(FadeIn(dot, scale=4), run_time=tracker.duration * 0.2)

        self.wait(0.5)
