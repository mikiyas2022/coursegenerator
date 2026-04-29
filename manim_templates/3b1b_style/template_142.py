"""
Template 142 — CURVE PLOT: y = ln(|x|+1) with ROSE_COLOR
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:
            axes = branded_axes([-4,4,1],[-2,3,1]).scale(0.6)
            axes.move_to(DOWN*0.2)
            self.play(Create(axes), run_time=tracker.duration*0.25)
            import math
            curve = axes.plot(lambda x: math.log(abs(x)+1), x_range=[-3.5,3.5], color=ROSE_COLOR, stroke_width=3)
            lbl = latin_text("y = ln(|x|+1)", font_size=FONT_SIZE_CAPTION, color=ROSE_COLOR)
            lbl.next_to(axes, UP, buff=0.1)
            clamp_to_screen(lbl)
            self.play(Create(curve), FadeIn(lbl), run_time=tracker.duration*0.45)
            self.play(Indicate(curve, color=STAR_YELLOW), run_time=tracker.duration*0.2)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_1>") as tracker:
            fb = formula_box("<NARRATION_PLACEHOLDER_0>", color=ROSE_COLOR)
            fb.move_to(ORIGIN)
            self.play(FadeIn(fb, scale=0.5), run_time=tracker.duration*0.45)
            self.play(Circumscribe(fb, color=TEAL_ACCENT, time_width=2), run_time=tracker.duration*0.35)
            dot = glow_dot(fb.get_corner(UR), color=TEAL_ACCENT)
            self.play(FadeIn(dot, scale=4), run_time=tracker.duration*0.15)

        self.wait(0.5)
