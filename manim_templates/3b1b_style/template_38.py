"""
Template 38 — WAVE INTERFERENCE: Two waves combine to show constructive/destructive
Pattern: Wave A → Wave B → sum wave appears → peaks glow
Use for: Superposition, sound waves, light interference, Fourier concepts
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:
            axes = branded_axes([-5, 5, 1], [-2, 2, 1]).scale(0.55)
            axes.move_to(ORIGIN)
            self.play(Create(axes), run_time=tracker.duration * 0.15)
            import math
            w1 = axes.plot(lambda x: math.sin(x * 1.5), x_range=[-4.5, 4.5], color=TEAL_ACCENT, stroke_width=2.5)
            w2 = axes.plot(lambda x: math.sin(x * 1.5 + 1.2), x_range=[-4.5, 4.5], color=ROSE_COLOR, stroke_width=2.5)
            l1 = latin_text("Wave A", font_size=FONT_SIZE_CAPTION, color=TEAL_ACCENT).next_to(axes, UP, buff=0.15).shift(LEFT*2)
            l2 = latin_text("Wave B", font_size=FONT_SIZE_CAPTION, color=ROSE_COLOR).next_to(axes, UP, buff=0.15).shift(RIGHT*2)
            self.play(Create(w1), FadeIn(l1), run_time=tracker.duration * 0.2)
            self.play(Create(w2), FadeIn(l2), run_time=tracker.duration * 0.2)
            # Sum
            wsum = axes.plot(lambda x: math.sin(x*1.5) + math.sin(x*1.5+1.2), x_range=[-4.5,4.5], color=STAR_YELLOW, stroke_width=4)
            ls = latin_text("A + B", font_size=FONT_SIZE_SMALL, color=STAR_YELLOW).next_to(axes, DOWN, buff=0.15)
            self.play(Create(wsum), FadeIn(ls), run_time=tracker.duration * 0.3)
            self.play(Indicate(wsum, color=STAR_YELLOW), run_time=tracker.duration * 0.15)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_1>") as tracker:
            fb = formula_box("y = sin(x) + sin(x + φ)", color=TEAL_ACCENT)
            fb.move_to(ORIGIN)
            self.play(FadeIn(fb, scale=0.6), run_time=tracker.duration * 0.5)
            self.play(Circumscribe(fb, color=STAR_YELLOW), run_time=tracker.duration * 0.35)
            self.wait(tracker.duration * 0.15)

        self.wait(0.5)
