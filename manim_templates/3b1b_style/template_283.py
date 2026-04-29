"""
Template 283 — BAR CHART: 8 bars VECTOR_COLOR
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:
            bars = VGroup()
            for i in range(8):
                h = 0.3 + random.random()*2.0
                bar = Rectangle(width=0.6, height=h, fill_color=VECTOR_COLOR,
                    fill_opacity=0.5+i*0.05, stroke_color=VECTOR_COLOR, stroke_width=2)
                bar.move_to(LEFT*3.15+RIGHT*i*0.9+UP*(h/2-1))
                bars.add(bar)
            self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.06),
                     run_time=tracker.duration*0.55)
            mean_line = DashedLine(LEFT*4.0, RIGHT*4.0, color=STAR_YELLOW, stroke_width=2)
            mean_line.move_to(UP*0.3)
            self.play(Create(mean_line), run_time=tracker.duration*0.2)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_1>") as tracker:
            obj = formula_box("<NARRATION_PLACEHOLDER_1>", color=VECTOR_COLOR)
            obj.move_to(ORIGIN)
            self.play(Create(obj), run_time=tracker.duration*0.5)
            self.play(Circumscribe(obj, color=STAR_YELLOW, time_width=2), run_time=tracker.duration*0.3)
            ul = Line(obj.get_left(), obj.get_right(), color=STAR_YELLOW, stroke_width=3)
            ul.next_to(obj, DOWN, buff=0.15)
            self.play(Create(ul), run_time=tracker.duration*0.15)
            self.wait(tracker.duration*0.1)

        self.wait(0.5)
