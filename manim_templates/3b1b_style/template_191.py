"""
Template 191 — NUMBER LINE: [-3,3] ROSE_COLOR
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:
            nl = NumberLine(x_range=[-3,3,1], length=8, color=AXIS_COLOR,
                           include_numbers=True, font_size=FONT_SIZE_CAPTION)
            nl.move_to(DOWN*0.5)
            t = ValueTracker(-3)
            marker = always_redraw(lambda: Triangle(fill_color=ROSE_COLOR, fill_opacity=1,
                stroke_width=0).scale(0.15).next_to(nl.n2p(t.get_value()), UP, buff=0.08))
            val_lbl = always_redraw(lambda: latin_text(f"{t.get_value():.1f}",
                font_size=FONT_SIZE_CAPTION, color=ROSE_COLOR).next_to(nl.n2p(t.get_value()), UP, buff=0.35))
            self.play(Create(nl), run_time=tracker.duration*0.2)
            self.add(marker, val_lbl)
            self.play(t.animate.set_value(3), run_time=tracker.duration*0.6, rate_func=smooth)
            self.wait(tracker.duration*0.1)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_1>") as tracker:
            obj = formula_box("<NARRATION_PLACEHOLDER_1>", color=ROSE_COLOR)
            obj.move_to(ORIGIN)
            self.play(Write(obj), run_time=tracker.duration*0.5)
            self.play(Circumscribe(obj, color=STAR_YELLOW, time_width=2), run_time=tracker.duration*0.3)
            ul = Line(obj.get_left(), obj.get_right(), color=STAR_YELLOW, stroke_width=3)
            ul.next_to(obj, DOWN, buff=0.15)
            self.play(Create(ul), run_time=tracker.duration*0.15)
            self.wait(tracker.duration*0.1)

        self.wait(0.5)
