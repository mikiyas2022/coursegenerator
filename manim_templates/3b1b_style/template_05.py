"""
Template 05 — NUMBER TICKER: Animated counter + number line + ruler sweep
Pattern: NumberLine → Triangle marker + ValueTracker → count up → label
Use for: Counting concepts, limits, convergence, numerical examples, rate problems
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:
            nl = NumberLine(x_range=[0, 10, 1], length=9, color=AXIS_COLOR,
                           include_numbers=True, font_size=24)
            nl.scale(0.85).shift(DOWN * 0.2)
            t_val = ValueTracker(0)
            marker = Triangle(fill_color=TEAL_ACCENT, fill_opacity=1.0, stroke_width=0).scale(0.2)
            marker.next_to(nl.n2p(0), UP, buff=0.08)
            marker.add_updater(lambda m: m.next_to(nl.n2p(t_val.get_value()), UP, buff=0.08))
            num_disp = always_redraw(lambda: DecimalNumber(
                t_val.get_value(), num_decimal_places=0,
                color=STAR_YELLOW, font_size=FONT_SIZE_HEADER
            ).next_to(nl, UP, buff=0.4))
            self.play(Create(nl), run_time=tracker.duration * 0.3)
            self.add(marker, num_disp)
            self.play(t_val.animate.set_value(7.5), run_time=tracker.duration * 0.55, rate_func=smooth)
            self.play(Indicate(num_disp, color=STAR_YELLOW), run_time=tracker.duration * 0.15)

        with self.voiceover(text="<NARRATION_PLACEHOLDER_1>") as tracker:
            lbl = latin_text("= 7.5 units", font_size=FONT_SIZE_BODY, color=TEXT_COLOR)
            lbl.next_to(num_disp, RIGHT, buff=0.4)
            clamp_to_screen(lbl)
            self.play(FadeIn(lbl, shift=LEFT * 0.3), run_time=tracker.duration * 0.4)
            self.play(t_val.animate.set_value(9), run_time=tracker.duration * 0.4, rate_func=rush_from)
            playful_bounce(self, num_disp)
            self.wait(tracker.duration * 0.2)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_2>") as tracker:
            fb = formula_box("<NARRATION_PLACEHOLDER_0>", color=TEAL_ACCENT)
            fb.move_to(ORIGIN)
            self.play(FadeIn(fb, shift=UP * 0.3), run_time=tracker.duration * 0.5)
            self.play(Circumscribe(fb, color=STAR_YELLOW), run_time=tracker.duration * 0.3)
            dot = glow_dot(fb.get_corner(UR), color=STAR_YELLOW)
            self.play(FadeIn(dot, scale=4), run_time=tracker.duration * 0.2)

        self.wait(0.5)
