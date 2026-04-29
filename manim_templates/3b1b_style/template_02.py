"""
Template 02 — VECTOR SWEEP: Rotating vector on plane with angle tracker
Pattern: Axes → Arrow always_redraw → ValueTracker angle sweep → label appears
Use for: Trigonometry, forces, velocity decomposition, rotation
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:
            angle_t = ValueTracker(0)
            plane = branded_axes([-4, 4, 1], [-3, 3, 1]).scale(0.72)
            vec = always_redraw(lambda: Arrow(
                start=plane.c2p(0, 0),
                end=plane.c2p(2.8 * np.cos(angle_t.get_value()), 2.8 * np.sin(angle_t.get_value())),
                buff=0, color=VECTOR_COLOR, stroke_width=7,
                max_tip_length_to_length_ratio=0.13
            ))
            self.play(Create(plane), run_time=tracker.duration * 0.3)
            self.add(vec)
            self.play(angle_t.animate.set_value(PI / 3), run_time=tracker.duration * 0.55, rate_func=smooth)
            self.play(Indicate(vec, color=STAR_YELLOW), run_time=tracker.duration * 0.15)

        with self.voiceover(text="<NARRATION_PLACEHOLDER_1>") as tracker:
            x_comp = always_redraw(lambda: Arrow(
                start=plane.c2p(0, 0),
                end=plane.c2p(2.8 * np.cos(angle_t.get_value()), 0),
                buff=0, color=X_COLOR, stroke_width=5, max_tip_length_to_length_ratio=0.13
            ))
            y_comp = always_redraw(lambda: Arrow(
                start=plane.c2p(2.8 * np.cos(angle_t.get_value()), 0),
                end=plane.c2p(2.8 * np.cos(angle_t.get_value()), 2.8 * np.sin(angle_t.get_value())),
                buff=0, color=Y_COLOR, stroke_width=5, max_tip_length_to_length_ratio=0.13
            ))
            self.add(x_comp, y_comp)
            self.play(angle_t.animate.set_value(PI / 4), run_time=tracker.duration * 0.6, rate_func=smooth)
            lbl = latin_text("decomposed!", font_size=FONT_SIZE_LABEL, color=STAR_YELLOW)
            lbl.to_corner(UR).shift(LEFT * 0.5)
            self.play(FadeIn(lbl, shift=LEFT * 0.3), run_time=tracker.duration * 0.4)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_2>") as tracker:
            fb = formula_box("<NARRATION_PLACEHOLDER_0>", color=TEAL_ACCENT)
            fb.move_to(ORIGIN)
            self.play(Create(fb[0]), Write(fb[1]), run_time=tracker.duration * 0.5)
            self.play(Circumscribe(fb, color=STAR_YELLOW, time_width=2.0), run_time=tracker.duration * 0.3)
            dot = glow_dot(fb.get_corner(UR) + UP * 0.15, color=STAR_YELLOW)
            self.play(FadeIn(dot, scale=3), run_time=tracker.duration * 0.2)

        self.wait(0.5)
