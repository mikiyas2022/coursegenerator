"""
Template 488 — DEEP DIVE: sigmoid VECTOR_COLOR
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:
            obj = latin_text("<NARRATION_PLACEHOLDER_0>", font_size=FONT_SIZE_HEADER, color=VECTOR_COLOR)
            obj.move_to(ORIGIN)
            clamp_to_screen(obj)
            self.play(FadeIn(obj, shift=LEFT*0.3), run_time=tracker.duration*0.5)
            self.play(Indicate(obj, color=STAR_YELLOW), run_time=tracker.duration*0.3)
            self.wait(tracker.duration*0.1)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_1>") as tracker:
            axes = branded_axes([-4,4,1],[-2,3,1]).scale(0.6)
            axes.move_to(DOWN*0.2)
            self.play(Create(axes), run_time=tracker.duration*0.25)
            import math
            curve = axes.plot(lambda x: 2/(1+math.exp(-x))-1, x_range=[-3.5,3.5], color=VECTOR_COLOR, stroke_width=3)
            lbl = latin_text("sigmoid", font_size=FONT_SIZE_CAPTION, color=VECTOR_COLOR)
            lbl.next_to(axes, UP, buff=0.1)
            clamp_to_screen(lbl)
            self.play(Create(curve), FadeIn(lbl), run_time=tracker.duration*0.45)
            self.play(Indicate(curve, color=STAR_YELLOW), run_time=tracker.duration*0.2)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_2>") as tracker:
            fb = formula_box("<NARRATION_PLACEHOLDER_0>", color=VECTOR_COLOR)
            fb.move_to(ORIGIN)
            self.play(FadeIn(fb, scale=0.5), run_time=tracker.duration*0.45)
            self.play(Circumscribe(fb, color=STAR_YELLOW, time_width=2), run_time=tracker.duration*0.35)
            dot = glow_dot(fb.get_corner(UR), color=STAR_YELLOW)
            self.play(FadeIn(dot, scale=4), run_time=tracker.duration*0.15)

        self.wait(0.5)
