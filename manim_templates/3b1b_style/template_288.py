"""
Template 288 — RINGS: 4 rings FORCE_COLOR
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:
            rings = VGroup()
            for r in [0.4*i for i in range(1,4+1)]:
                ring = Circle(radius=r, color=FORCE_COLOR, stroke_width=1.5, stroke_opacity=0.3+r*0.1)
                rings.add(ring)
            self.play(LaggedStart(*[Create(r) for r in rings], lag_ratio=0.06),
                     run_time=tracker.duration*0.5)
            center_dot = glow_dot(ORIGIN, color=STAR_YELLOW)
            self.play(FadeIn(center_dot, scale=5), run_time=tracker.duration*0.2)
            self.play(Indicate(rings[-1], color=STAR_YELLOW), run_time=tracker.duration*0.2)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_1>") as tracker:
            fb = formula_box("<NARRATION_PLACEHOLDER_0>", color=FORCE_COLOR)
            fb.move_to(ORIGIN)
            self.play(FadeIn(fb, scale=0.5), run_time=tracker.duration*0.45)
            self.play(Circumscribe(fb, color=STAR_YELLOW, time_width=2), run_time=tracker.duration*0.35)
            dot = glow_dot(fb.get_corner(UR), color=STAR_YELLOW)
            self.play(FadeIn(dot, scale=4), run_time=tracker.duration*0.15)

        self.wait(0.5)
