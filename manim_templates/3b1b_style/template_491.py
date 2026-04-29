"""
Template 491 — DEEP DIVE: sigmoid FORCE_COLOR
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:
            obj = latin_text("<NARRATION_PLACEHOLDER_0>", font_size=FONT_SIZE_HEADER, color=FORCE_COLOR)
            obj.move_to(ORIGIN)
            clamp_to_screen(obj)
            self.play(FadeIn(obj, scale=0.5), run_time=tracker.duration*0.5)
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
            curve = axes.plot(lambda x: 2/(1+math.exp(-x))-1, x_range=[-3.5,3.5], color=FORCE_COLOR, stroke_width=3)
            lbl = latin_text("sigmoid", font_size=FONT_SIZE_CAPTION, color=FORCE_COLOR)
            lbl.next_to(axes, UP, buff=0.1)
            clamp_to_screen(lbl)
            self.play(Create(curve), FadeIn(lbl), run_time=tracker.duration*0.45)
            self.play(Indicate(curve, color=STAR_YELLOW), run_time=tracker.duration*0.2)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_2>") as tracker:
            fb = formula_box("<NARRATION_PLACEHOLDER_0>", color=FORCE_COLOR)
            fb.move_to(ORIGIN)
            self.play(FadeIn(fb, scale=0.5), run_time=tracker.duration*0.45)
            self.play(Circumscribe(fb, color=TEAL_ACCENT, time_width=2), run_time=tracker.duration*0.35)
            dot = glow_dot(fb.get_corner(UR), color=TEAL_ACCENT)
            self.play(FadeIn(dot, scale=4), run_time=tracker.duration*0.15)

        self.wait(0.5)
