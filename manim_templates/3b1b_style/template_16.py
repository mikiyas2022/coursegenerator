"""
Template 16 — HUMOROUS ANALOGY: Playful visual metaphor with bouncing elements
Pattern: Everyday object → bounces/grows → transforms into physics concept
Use for: Analogy scenes, intro hooks, humanizing abstract concepts
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:
            ball = Circle(radius=0.5, fill_color=TEAL_ACCENT, fill_opacity=0.8,
                         stroke_color=TEAL_ACCENT, stroke_width=3)
            ball.move_to(UP * 2.5)
            shadow = Ellipse(width=1.2, height=0.3, fill_color=MUTED_COLOR,
                            fill_opacity=0.3, stroke_width=0)
            shadow.move_to(DOWN * 2.5)
            face_l = Dot(ball.get_center() + LEFT * 0.15 + UP * 0.1,
                        radius=0.07, color=BG_COLOR)
            face_r = Dot(ball.get_center() + RIGHT * 0.15 + UP * 0.1,
                        radius=0.07, color=BG_COLOR)
            self.play(FadeIn(ball), FadeIn(shadow), FadeIn(face_l), FadeIn(face_r),
                     run_time=tracker.duration * 0.5)
            for _ in range(2):
                self.play(ball.animate.move_to(DOWN * 1.8).scale(1.3),
                         shadow.animate.scale(1.8), run_time=0.2, rate_func=rush_into)
                self.play(ball.animate.move_to(UP * 2.5).scale(1/1.3),
                         shadow.animate.scale(1/1.8), run_time=0.3, rate_func=rush_from)

        with self.voiceover(text="<NARRATION_PLACEHOLDER_1>") as tracker:
            concept_txt = latin_text("Just like bouncing:", font_size=FONT_SIZE_LABEL, color=TEXT_COLOR)
            concept_txt.move_to(LEFT * 2 + UP * 0.3)
            clamp_to_screen(concept_txt)
            self.play(Write(concept_txt), run_time=tracker.duration * 0.4)
            fb = formula_box("<NARRATION_PLACEHOLDER_0>", color=STAR_YELLOW)
            fb.move_to(RIGHT * 2 + DOWN * 0.3)
            self.play(FadeIn(fb, shift=LEFT * 0.3), run_time=tracker.duration * 0.4)
            playful_bounce(self, fb)
            self.wait(tracker.duration * 0.2)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_2>") as tracker:
            final = formula_box("<NARRATION_PLACEHOLDER_0>", color=TEAL_ACCENT)
            final.move_to(ORIGIN)
            self.play(FadeIn(final, scale=0.6), run_time=tracker.duration * 0.5)
            self.play(Circumscribe(final, color=STAR_YELLOW, time_width=2), run_time=tracker.duration * 0.3)
            dot = glow_dot(final.get_corner(UR) + UP * 0.1, color=STAR_YELLOW)
            self.play(FadeIn(dot, scale=4), run_time=tracker.duration * 0.2)

        self.wait(0.5)
