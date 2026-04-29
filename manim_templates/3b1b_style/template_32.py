"""
Template 32 — SILENT INTRO: Cinematic title card with NO narration
Pattern: Dark → logo pulse → topic title fades up → subtitle → 1s hold → fade out
Use for: Episode openers, course intros, chapter starts. NO VOICEOVER on this scene.
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        # Silent intro — no voiceover block
        self.clear()
        # Logo dot
        dot = Dot(ORIGIN, radius=0.06, color=TEAL_ACCENT)
        self.play(FadeIn(dot, scale=0.1), run_time=0.3)
        self.play(dot.animate.scale(8), run_time=0.5, rate_func=rush_from)
        self.play(FadeOut(dot), run_time=0.3)

        # Title
        title = latin_text("<NARRATION_PLACEHOLDER_0>", font_size=FONT_SIZE_TITLE, color=TEXT_COLOR)
        title.move_to(UP * 0.5)
        clamp_to_screen(title)
        underline = Line(LEFT * 3.5, RIGHT * 3.5, color=TEAL_ACCENT, stroke_width=4)
        underline.next_to(title, DOWN, buff=0.2)

        self.play(FadeIn(title, shift=UP * 0.3), run_time=0.8)
        self.play(Create(underline), run_time=0.5)

        sub = latin_text("A 3Blue1Brown-Style Exploration", font_size=FONT_SIZE_SMALL, color=MUTED_COLOR)
        sub.next_to(underline, DOWN, buff=0.3)
        clamp_to_screen(sub)
        self.play(FadeIn(sub, shift=UP * 0.15), run_time=0.5)

        self.wait(1.2)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.6)
        self.wait(0.3)
