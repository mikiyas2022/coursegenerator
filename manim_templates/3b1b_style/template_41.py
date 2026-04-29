"""
Template 41 — CHAPTER CARD: Episode divider with chapter number + title
Pattern: Fade to dark → chapter number pulses → title slides in → fade out
Use for: Multi-episode courses, section dividers, chapter transitions
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        # Silent — no voiceover
        self.clear()
        ch_num = latin_text("Chapter 1", font_size=FONT_SIZE_SMALL, color=MUTED_COLOR)
        ch_num.move_to(UP * 0.8)
        ch_title = latin_text("<NARRATION_PLACEHOLDER_0>", font_size=FONT_SIZE_HEADER, color=TEXT_COLOR)
        ch_title.move_to(ORIGIN)
        clamp_to_screen(ch_title)
        line = Line(LEFT * 2.5, RIGHT * 2.5, color=TEAL_ACCENT, stroke_width=3)
        line.next_to(ch_title, DOWN, buff=0.2)

        self.play(FadeIn(ch_num, shift=DOWN * 0.2), run_time=0.5)
        self.play(FadeIn(ch_title, shift=UP * 0.2), run_time=0.6)
        self.play(Create(line), run_time=0.4)
        self.wait(1.0)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.5)
        self.wait(0.2)
