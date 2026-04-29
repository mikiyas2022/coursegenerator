"""
Template 20 — SUMMARY CLOSER: Episode-ending recap with checkmarks + call-to-action
Pattern: Checklist of key concepts → each checks off → "Now you know!" explosion
Use for: Episode endings, section summaries, conclusion scenes
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:
            hdr = latin_text("What we discovered:", font_size=FONT_SIZE_HEADER, color=TEAL_ACCENT)
            hdr.to_edge(UP, buff=0.5)
            underline = Line(LEFT * 4, RIGHT * 4, color=TEAL_ACCENT, stroke_width=3)
            underline.next_to(hdr, DOWN, buff=0.15)
            self.play(FadeIn(hdr, shift=DOWN * 0.3), Create(underline), run_time=tracker.duration * 0.6)
            self.wait(tracker.duration * 0.4)

        items = ["Core concept unlocked ✓", "Worked example complete ✓", "Intuition built ✓"]
        for i, item in enumerate(items):
            with self.voiceover(text=f"<NARRATION_PLACEHOLDER_{i+1}>") as tracker:
                check = latin_text(item, font_size=FONT_SIZE_LABEL,
                                  color=SUCCESS_COLOR if "✓" in item else TEXT_COLOR)
                check.move_to(LEFT * 1 + UP * (1.2 - i * 1.0))
                clamp_to_screen(check)
                self.play(FadeIn(check, shift=RIGHT * 0.5), run_time=tracker.duration * 0.5)
                self.play(Indicate(check, color=STAR_YELLOW, scale_factor=1.04),
                         run_time=tracker.duration * 0.4)
                self.wait(tracker.duration * 0.1)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_4>") as tracker:
            finale = latin_text("Now you KNOW it.", font_size=FONT_SIZE_TITLE, color=STAR_YELLOW)
            finale.move_to(ORIGIN)
            self.play(FadeIn(finale, scale=0.2), run_time=tracker.duration * 0.4)
            playful_bounce(self, finale)
            self.play(finale.animate.set_color(TEAL_ACCENT), run_time=tracker.duration * 0.3)
            dot = glow_dot(finale.get_corner(UR) + UP * 0.15, color=STAR_YELLOW)
            self.play(FadeIn(dot, scale=5), run_time=tracker.duration * 0.3)

        self.wait(0.8)
