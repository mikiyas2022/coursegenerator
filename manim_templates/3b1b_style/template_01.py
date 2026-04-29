"""
Template 01 — HOOK INTRO: Cinematic title reveal + question hook
Pattern: Big title card → underline animate → curiosity question pops in → glow burst
Use for: Episode openers, surprising questions, "did you ever wonder?" moments
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:
            tc = title_card("", "")
            underline = Line(LEFT * 4, RIGHT * 4, color=TEAL_ACCENT, stroke_width=5)
            underline.next_to(tc, DOWN, buff=0.18)
            self.play(FadeIn(tc, shift=UP * 0.4), run_time=tracker.duration * 0.45)
            self.play(Create(underline), run_time=tracker.duration * 0.35)
            self.play(Indicate(tc, color=STAR_YELLOW, scale_factor=1.05), run_time=tracker.duration * 0.2)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_1>") as tracker:
            q = latin_text("?", font_size=FONT_SIZE_TITLE, color=STAR_YELLOW)
            q.move_to(ORIGIN)
            self.play(FadeIn(q, scale=0.1), run_time=tracker.duration * 0.5, rate_func=rush_from)
            dot = glow_dot(ORIGIN + UP * 0.1, color=STAR_YELLOW)
            self.play(FadeIn(dot, scale=5), run_time=tracker.duration * 0.3)
            self.play(Indicate(q, color=TEAL_ACCENT), run_time=tracker.duration * 0.2)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_2>") as tracker:
            hook = latin_text("<NARRATION_PLACEHOLDER_0>", font_size=FONT_SIZE_LABEL, color=TEXT_COLOR)
            hook.move_to(ORIGIN)
            clamp_to_screen(hook)
            self.play(Write(hook), run_time=tracker.duration * 0.7)
            self.play(hook.animate.set_color(TEAL_ACCENT), run_time=tracker.duration * 0.3)

        self.wait(0.5)
