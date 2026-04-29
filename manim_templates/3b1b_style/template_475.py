"""
Template 475 — DEEP DIVE: y = |x| TEAL_ACCENT
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:
            obj = latin_text("<NARRATION_PLACEHOLDER_0>", font_size=FONT_SIZE_HEADER, color=TEAL_ACCENT)
            obj.move_to(ORIGIN)
            clamp_to_screen(obj)
            self.play(FadeIn(obj, shift=DOWN*0.2), run_time=tracker.duration*0.5)
            self.play(Indicate(obj, color=TEAL_ACCENT), run_time=tracker.duration*0.3)
            ul = Line(obj.get_left(), obj.get_right(), color=TEAL_ACCENT, stroke_width=3)
            ul.next_to(obj, DOWN, buff=0.15)
            self.play(Create(ul), run_time=tracker.duration*0.15)
            self.wait(tracker.duration*0.1)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_1>") as tracker:
            axes = branded_axes([-4,4,1],[-2,3,1]).scale(0.6)
            axes.move_to(DOWN*0.2)
            self.play(Create(axes), run_time=tracker.duration*0.25)
            import math
            curve = axes.plot(lambda x: abs(x), x_range=[-3.5,3.5], color=TEAL_ACCENT, stroke_width=3)
            lbl = latin_text("y = |x|", font_size=FONT_SIZE_CAPTION, color=TEAL_ACCENT)
            lbl.next_to(axes, UP, buff=0.1)
            clamp_to_screen(lbl)
            self.play(Create(curve), FadeIn(lbl), run_time=tracker.duration*0.45)
            self.play(Indicate(curve, color=STAR_YELLOW), run_time=tracker.duration*0.2)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_2>") as tracker:
            fb = formula_box("<NARRATION_PLACEHOLDER_0>", color=TEAL_ACCENT)
            fb.move_to(ORIGIN)
            self.play(FadeIn(fb, scale=0.5), run_time=tracker.duration*0.45)
            self.play(Circumscribe(fb, color=TEAL_ACCENT, time_width=2), run_time=tracker.duration*0.35)
            dot = glow_dot(fb.get_corner(UR), color=TEAL_ACCENT)
            self.play(FadeIn(dot, scale=4), run_time=tracker.duration*0.15)

        self.wait(0.5)
