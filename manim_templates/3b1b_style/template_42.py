"""
Template 42 — CROSS-SECTION REVEAL: Object sliced to show internal structure
Pattern: Shape appears → slice line sweeps → interior fills → labels pop
Use for: Cross sections, anatomy of formulas, internal structure, layers
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:
            outer = Circle(radius=2.0, color=TEAL_ACCENT, stroke_width=3, fill_opacity=0.08, fill_color=TEAL_ACCENT)
            inner = Circle(radius=1.0, color=STAR_YELLOW, stroke_width=2, fill_opacity=0.15, fill_color=STAR_YELLOW)
            core = Dot(ORIGIN, radius=0.15, color=ERROR_COLOR)
            self.play(Create(outer), run_time=tracker.duration * 0.2)
            self.play(Create(inner), run_time=tracker.duration * 0.15)
            self.play(FadeIn(core, scale=0.3), run_time=tracker.duration * 0.1)
            # Slice line
            sl = DashedLine(LEFT * 3, RIGHT * 3, color=MUTED_COLOR, stroke_width=1.5)
            self.play(Create(sl), run_time=tracker.duration * 0.15)
            # Labels
            l1 = latin_text("Outer", font_size=FONT_SIZE_CAPTION, color=TEAL_ACCENT).next_to(outer, UR, buff=0.1)
            l2 = latin_text("Inner", font_size=FONT_SIZE_CAPTION, color=STAR_YELLOW).next_to(inner, RIGHT, buff=0.15)
            l3 = latin_text("Core", font_size=FONT_SIZE_CAPTION, color=ERROR_COLOR).next_to(core, DOWN, buff=0.2)
            self.play(FadeIn(l1), FadeIn(l2), FadeIn(l3), run_time=tracker.duration * 0.2)
            self.play(Indicate(core, color=ERROR_COLOR, scale_factor=2), run_time=tracker.duration * 0.2)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_1>") as tracker:
            fb = formula_box("<NARRATION_PLACEHOLDER_0>", color=TEAL_ACCENT)
            fb.move_to(ORIGIN)
            self.play(FadeIn(fb, scale=0.6), run_time=tracker.duration * 0.5)
            self.play(Circumscribe(fb, color=STAR_YELLOW), run_time=tracker.duration * 0.35)
            dot = glow_dot(fb.get_corner(UR), color=STAR_YELLOW)
            self.play(FadeIn(dot, scale=4), run_time=tracker.duration * 0.15)

        self.wait(0.5)
