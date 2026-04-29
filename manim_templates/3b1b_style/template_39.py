"""
Template 39 — STEP-BY-STEP SOLVE: Multi-line equation solving, each step appears
Pattern: Line 1 → arrow → Line 2 → arrow → Line 3 → final box glow
Use for: Algebra solving, proofs, derivations, step-by-step reasoning
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:
            steps = ["2x + 4 = 10", "2x = 6", "x = 3"]
            mobs = []
            for i, s in enumerate(steps):
                t = latin_text(s, font_size=FONT_SIZE_BODY, color=TEAL_ACCENT if i < 2 else STAR_YELLOW)
                t.move_to(UP * (1.5 - i * 1.2))
                clamp_to_screen(t)
                mobs.append(t)
            time_each = tracker.duration * 0.25
            for i, m in enumerate(mobs):
                self.play(FadeIn(m, shift=RIGHT * 0.3), run_time=time_each)
                if i < len(mobs) - 1:
                    arr = Arrow(m.get_bottom(), mobs[i+1].get_top(), buff=0.12,
                               color=MUTED_COLOR, stroke_width=2, max_tip_length_to_length_ratio=0.15)
                    self.play(GrowArrow(arr), run_time=time_each * 0.3)
            self.play(Indicate(mobs[-1], color=STAR_YELLOW), run_time=tracker.duration * 0.1)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_1>") as tracker:
            fb = formula_box("x = 3  ✓", color=STAR_YELLOW)
            fb.move_to(ORIGIN)
            self.play(FadeIn(fb, scale=0.5), run_time=tracker.duration * 0.45)
            self.play(Circumscribe(fb, color=STAR_YELLOW, time_width=2), run_time=tracker.duration * 0.35)
            playful_bounce(self, fb)
            self.wait(tracker.duration * 0.2)

        self.wait(0.5)
