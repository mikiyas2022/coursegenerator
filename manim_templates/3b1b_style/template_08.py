"""
Template 08 — WORKED EXAMPLE PANEL: Step-by-step calculation with real numbers
Pattern: Left panel = problem statement → Right panel = solution steps appear one by one
Use for: Worked problems, numerical calculations, solving equations
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:
            divider = Line(UP * 3.2, DOWN * 3.2, color=MUTED_COLOR, stroke_width=1.5,
                          stroke_opacity=0.4)
            given_hdr = latin_text("GIVEN", font_size=FONT_SIZE_LABEL, color=TEAL_ACCENT)
            given_hdr.to_corner(UL).shift(RIGHT * 0.3 + DOWN * 0.2)
            self.play(Create(divider), run_time=tracker.duration * 0.2)
            self.play(FadeIn(given_hdr, shift=RIGHT * 0.3), run_time=tracker.duration * 0.3)
            g1 = latin_text("• v₀ = 20 m/s", font_size=FONT_SIZE_SMALL, color=TEXT_COLOR)
            g1.next_to(given_hdr, DOWN, buff=0.25, aligned_edge=LEFT)
            g2 = latin_text("• θ = 45°", font_size=FONT_SIZE_SMALL, color=TEXT_COLOR)
            g2.next_to(g1, DOWN, buff=0.18, aligned_edge=LEFT)
            self.play(FadeIn(g1, shift=RIGHT * 0.2), run_time=tracker.duration * 0.2)
            self.play(FadeIn(g2, shift=RIGHT * 0.2), run_time=tracker.duration * 0.3)

        with self.voiceover(text="<NARRATION_PLACEHOLDER_1>") as tracker:
            find_hdr = latin_text("FIND", font_size=FONT_SIZE_LABEL, color=STAR_YELLOW)
            find_hdr.to_corner(UR).shift(LEFT * 2.5 + DOWN * 0.2)
            self.play(FadeIn(find_hdr, shift=LEFT * 0.3), run_time=tracker.duration * 0.2)
            s1 = latin_text("Step 1: vx = v₀cos(45°)", font_size=FONT_SIZE_SMALL, color=X_COLOR)
            s1.next_to(find_hdr, DOWN, buff=0.25, aligned_edge=LEFT)
            s2 = latin_text("= 20 × 0.707 = 14.1 m/s", font_size=FONT_SIZE_SMALL, color=TEXT_COLOR)
            s2.next_to(s1, DOWN, buff=0.18, aligned_edge=LEFT)
            s3 = latin_text("Step 2: vy = v₀sin(45°)", font_size=FONT_SIZE_SMALL, color=Y_COLOR)
            s3.next_to(s2, DOWN, buff=0.25, aligned_edge=LEFT)
            s4 = latin_text("= 20 × 0.707 = 14.1 m/s", font_size=FONT_SIZE_SMALL, color=TEXT_COLOR)
            s4.next_to(s3, DOWN, buff=0.18, aligned_edge=LEFT)
            for step in [s1, s2, s3, s4]:
                self.play(FadeIn(step, shift=LEFT * 0.2), run_time=tracker.duration * 0.2)

        with self.voiceover(text="<NARRATION_PLACEHOLDER_2>") as tracker:
            ans_box = formula_box("R = 40.8 m", color=STAR_YELLOW)
            ans_box.to_edge(DOWN, buff=0.5)
            self.play(Create(ans_box[0]), Write(ans_box[1]), run_time=tracker.duration * 0.5)
            self.play(Circumscribe(ans_box, color=STAR_YELLOW, time_width=2), run_time=tracker.duration * 0.35)
            playful_bounce(self, ans_box)
            self.wait(tracker.duration * 0.15)

        self.wait(0.5)
