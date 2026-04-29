"""
Template 0148 — NUMLINE: [-10,10] TEAL_ACCENT
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:
            nl = NumberLine(x_range=[-10,10,1], length=8, color=AXIS_COLOR, include_numbers=True, font_size=FONT_SIZE_CAPTION)
            nl.move_to(DOWN*0.5)
            t = ValueTracker(-10)
            marker = always_redraw(lambda: Triangle(fill_color=TEAL_ACCENT, fill_opacity=1, stroke_width=0).scale(0.15).next_to(nl.n2p(t.get_value()), UP, buff=0.08))
            val_lbl = always_redraw(lambda: latin_text(f"{t.get_value():.1f}", font_size=FONT_SIZE_CAPTION, color=TEAL_ACCENT).next_to(nl.n2p(t.get_value()), UP, buff=0.35))
            self.play(Create(nl), run_time=tracker.duration*0.2)
            self.add(marker, val_lbl)
            self.play(t.animate.set_value(10), run_time=tracker.duration*0.6, rate_func=smooth)
            self.wait(tracker.duration*0.1)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_1>") as tracker:
            obj = latin_text("<NARRATION_PLACEHOLDER_1>", font_size=FONT_SIZE_BODY, color=TEAL_ACCENT)
            obj.move_to(ORIGIN)
            clamp_to_screen(obj)
            self.play(FadeIn(obj, scale=0.5), run_time=tracker.duration*0.5)
            self.play(Circumscribe(obj, color=STAR_YELLOW, time_width=2), run_time=tracker.duration*0.3)
            self.wait(tracker.duration*0.1)

        self.wait(0.5)
