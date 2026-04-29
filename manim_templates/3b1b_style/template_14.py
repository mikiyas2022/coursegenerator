"""
Template 14 — CAMERA ZOOM: Moving camera zoom + pull-back reveal
Pattern: Object appears → camera zooms in tight → reveals hidden detail → pull back
Use for: Scale reveals, microscopic/macroscopic, "zoom in on this" moments
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:
            big_world = branded_axes([-5, 5, 1], [-3, 3, 1]).scale(0.9)
            detail_dot = glow_dot(ORIGIN, color=STAR_YELLOW, radius=0.08)
            detail_ring = Circle(radius=0.2, color=STAR_YELLOW, stroke_width=2)
            detail_ring.move_to(ORIGIN)
            self.play(Create(big_world), run_time=tracker.duration * 0.4)
            self.play(FadeIn(detail_dot), Create(detail_ring), run_time=tracker.duration * 0.4)
            self.play(self.camera.frame.animate.set_width(3).move_to(ORIGIN),
                     run_time=tracker.duration * 0.2, rate_func=smooth)

        with self.voiceover(text="<NARRATION_PLACEHOLDER_1>") as tracker:
            detail_txt = latin_text("KEY DETAIL", font_size=FONT_SIZE_SMALL, color=STAR_YELLOW)
            detail_txt.next_to(detail_dot, UP, buff=0.3)
            self.play(Write(detail_txt), run_time=tracker.duration * 0.5)
            self.play(Indicate(detail_dot, color=TEAL_ACCENT, scale_factor=2.0),
                     run_time=tracker.duration * 0.5)

        with self.voiceover(text="<NARRATION_PLACEHOLDER_2>") as tracker:
            self.play(self.camera.frame.animate.to_default_state(),
                     run_time=tracker.duration * 0.35, rate_func=smooth)
            fb = formula_box("<NARRATION_PLACEHOLDER_0>", color=TEAL_ACCENT)
            fb.move_to(ORIGIN)
            self.play(FadeIn(fb, scale=0.6), run_time=tracker.duration * 0.4)
            self.play(Circumscribe(fb, color=STAR_YELLOW), run_time=tracker.duration * 0.25)

        self.wait(0.5)
