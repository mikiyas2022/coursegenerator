"""
Template 0272 — COMPARE: Before vs After STAR_YELLOW
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:
            div = DashedLine(UP*2.5, DOWN*2.5, color=MUTED_COLOR, stroke_width=1.5)
            lt = latin_text("Before", font_size=FONT_SIZE_LABEL, color=STAR_YELLOW)
            lt.move_to(LEFT*3)
            clamp_to_screen(lt)
            rt = latin_text("After", font_size=FONT_SIZE_LABEL, color=FORCE_COLOR)
            rt.move_to(RIGHT*3)
            clamp_to_screen(rt)
            self.play(Create(div), run_time=tracker.duration*0.15)
            self.play(FadeIn(lt, shift=LEFT*0.2), run_time=tracker.duration*0.25)
            self.play(FadeIn(rt, shift=RIGHT*0.2), run_time=tracker.duration*0.25)
            arr = Arrow(lt.get_right(), rt.get_left(), buff=0.3, color=STAR_YELLOW, stroke_width=3)
            self.play(GrowArrow(arr), run_time=tracker.duration*0.2)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_1>") as tracker:
            fb = formula_box("<NARRATION_PLACEHOLDER_0>", color=STAR_YELLOW)
            fb.move_to(ORIGIN)
            self.play(FadeIn(fb, scale=0.5), run_time=tracker.duration*0.45)
            self.play(Circumscribe(fb, color=FORCE_COLOR, time_width=2), run_time=tracker.duration*0.35)
            dot = glow_dot(fb.get_corner(UR), color=FORCE_COLOR)
            self.play(FadeIn(dot, scale=4), run_time=tracker.duration*0.15)

        self.wait(0.5)
