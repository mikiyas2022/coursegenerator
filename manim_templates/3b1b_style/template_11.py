"""
Template 11 — BULLET REVEAL: Animated text bullets fly in one by one
Pattern: BulletPoint 1 → slide in → Bullet 2 → slide in → accent bar
Use for: Lists of facts, properties, steps, summary slides, key takeaways
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        bullets = [
            "First: the key insight",
            "Second: the mechanism",
            "Third: the practical example",
            "Fourth: the beautiful conclusion",
        ]

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:
            hdr = latin_text("Key Points", font_size=FONT_SIZE_HEADER, color=TEAL_ACCENT)
            hdr.to_edge(UP, buff=0.5)
            underline = Line(LEFT * 3, RIGHT * 3, color=TEAL_ACCENT, stroke_width=3)
            underline.next_to(hdr, DOWN, buff=0.15)
            self.play(FadeIn(hdr, shift=DOWN * 0.3), run_time=tracker.duration * 0.5)
            self.play(Create(underline), run_time=tracker.duration * 0.3)
            self.wait(tracker.duration * 0.2)

        bullet_mobs = []
        start_y = 1.8
        for i, b in enumerate(bullets[:3]):
            with self.voiceover(text=f"<NARRATION_PLACEHOLDER_{i+1}>") as tracker:
                accent = Rectangle(width=0.08, height=0.4,
                                  fill_color=TEAL_ACCENT, fill_opacity=1,
                                  stroke_width=0)
                accent.move_to(LEFT * 5.5 + UP * (start_y - i * 1.0))
                txt = latin_text(b, font_size=FONT_SIZE_LABEL, color=TEXT_COLOR)
                txt.next_to(accent, RIGHT, buff=0.3)
                clamp_to_screen(txt)
                self.play(FadeIn(accent, shift=RIGHT * 0.4),
                         FadeIn(txt, shift=RIGHT * 0.4),
                         run_time=tracker.duration * 0.6)
                if i > 0:
                    self.play(Indicate(txt, color=STAR_YELLOW, scale_factor=1.04),
                             run_time=tracker.duration * 0.3)
                bullet_mobs.extend([accent, txt])
                self.wait(tracker.duration * 0.1)

        self.wait(0.5)
