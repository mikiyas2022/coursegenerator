"""
Template 07 — CIRCLE MORPH: Circle transforms into formula box
Pattern: branded_circle → concept text inside → ReplacementTransform → formula_box
Use for: Concept abstraction, area/circumference, circular motion, unit circle
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:
            circ = branded_circle(1.8, color=TEAL_ACCENT, fill_opacity=0.12)
            ctxt = latin_text("concept", font_size=FONT_SIZE_BODY, color=TEXT_COLOR)
            ctxt.move_to(circ.get_center())
            g = VGroup(circ, ctxt)
            self.play(DrawBorderThenFill(circ), run_time=tracker.duration * 0.4)
            self.play(Write(ctxt), run_time=tracker.duration * 0.3)
            self.play(g.animate.shift(LEFT * 2), run_time=tracker.duration * 0.3)

        with self.voiceover(text="<NARRATION_PLACEHOLDER_1>") as tracker:
            fb = formula_box("<NARRATION_PLACEHOLDER_0>", color=STAR_YELLOW)
            fb.move_to(RIGHT * 2)
            arrow = Arrow(g.get_right(), fb.get_left(), buff=0.2,
                         color=MUTED_COLOR, stroke_width=4,
                         max_tip_length_to_length_ratio=0.15)
            self.play(Create(arrow), run_time=tracker.duration * 0.3)
            self.play(FadeIn(fb, shift=LEFT * 0.3), run_time=tracker.duration * 0.4)
            self.play(Indicate(fb, color=STAR_YELLOW, scale_factor=1.06), run_time=tracker.duration * 0.3)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_2>") as tracker:
            circ2 = branded_circle(1.8, color=TEAL_ACCENT, fill_opacity=0.12)
            ctxt2 = latin_text("BEFORE", font_size=FONT_SIZE_LABEL, color=MUTED_COLOR)
            ctxt2.move_to(circ2.get_center())
            fb2 = formula_box("<NARRATION_PLACEHOLDER_0>", color=TEAL_ACCENT)
            fb2.move_to(ORIGIN)
            self.play(DrawBorderThenFill(circ2), Write(ctxt2), run_time=tracker.duration * 0.4)
            self.play(ReplacementTransform(VGroup(circ2, ctxt2), fb2), run_time=tracker.duration * 0.5)
            dot = glow_dot(fb2.get_corner(UR) + UP * 0.1, color=STAR_YELLOW)
            self.play(FadeIn(dot, scale=4), run_time=tracker.duration * 0.1)

        self.wait(0.5)
