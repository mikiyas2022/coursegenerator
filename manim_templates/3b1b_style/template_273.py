"""
Template 273 — BAR CHART: 6 bars TEAL_ACCENT
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:
            bars = VGroup()
            for i in range(6):
                h = 0.3 + random.random()*2.0
                bar = Rectangle(width=0.6, height=h, fill_color=TEAL_ACCENT,
                    fill_opacity=0.5+i*0.05, stroke_color=TEAL_ACCENT, stroke_width=2)
                bar.move_to(LEFT*2.25+RIGHT*i*0.9+UP*(h/2-1))
                bars.add(bar)
            self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.06),
                     run_time=tracker.duration*0.55)
            mean_line = DashedLine(LEFT*3.0, RIGHT*3.0, color=STAR_YELLOW, stroke_width=2)
            mean_line.move_to(UP*0.3)
            self.play(Create(mean_line), run_time=tracker.duration*0.2)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_1>") as tracker:
            obj = formula_box("<NARRATION_PLACEHOLDER_1>", color=TEAL_ACCENT)
            obj.move_to(ORIGIN)
            self.play(FadeIn(obj, shift=UP*0.3), run_time=tracker.duration*0.5)
            self.play(Circumscribe(obj, color=STAR_YELLOW, time_width=2), run_time=tracker.duration*0.3)
            dot = glow_dot(obj.get_corner(UR), color=STAR_YELLOW)
            self.play(FadeIn(dot, scale=4), run_time=tracker.duration*0.1)
            self.wait(tracker.duration*0.1)

        self.wait(0.5)
