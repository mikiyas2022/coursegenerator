"""
Template 22 — MATRIX TRANSFORM: Grid morphs under linear transformation
Pattern: NumberPlane → animate transform → eigenvectors highlighted
Use for: Linear algebra, matrix multiplication, transformations, eigenvectors
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:
            plane = NumberPlane(
                x_range=[-4, 4, 1], y_range=[-3, 3, 1],
                background_line_style={"stroke_color": GRID_COLOR,
                                      "stroke_width": 1, "stroke_opacity": 0.5}
            ).scale(0.72)
            v1 = Arrow(ORIGIN, plane.c2p(1, 0), buff=0,
                      color=X_COLOR, stroke_width=6, max_tip_length_to_length_ratio=0.15)
            v2 = Arrow(ORIGIN, plane.c2p(0, 1), buff=0,
                      color=Y_COLOR, stroke_width=6, max_tip_length_to_length_ratio=0.15)
            self.play(Create(plane), run_time=tracker.duration * 0.4)
            self.play(Create(v1), Create(v2), run_time=tracker.duration * 0.4)
            lbl = latin_text("Identity", font_size=FONT_SIZE_LABEL, color=TEXT_COLOR)
            lbl.to_corner(UR).shift(LEFT * 0.5 + DOWN * 0.3)
            self.play(Write(lbl), run_time=tracker.duration * 0.2)

        with self.voiceover(text="<NARRATION_PLACEHOLDER_1>") as tracker:
            matrix = [[2, 1], [0, 1]]
            self.play(
                plane.animate.apply_matrix(matrix),
                v1.animate.put_start_and_end_on(ORIGIN, plane.c2p(2, 0)),
                v2.animate.put_start_and_end_on(ORIGIN, plane.c2p(1, 1)),
                run_time=tracker.duration * 0.7, rate_func=smooth
            )
            new_lbl = latin_text("Sheared!", font_size=FONT_SIZE_LABEL, color=STAR_YELLOW)
            new_lbl.to_corner(UR).shift(LEFT * 0.5 + DOWN * 0.3)
            self.play(ReplacementTransform(lbl, new_lbl), run_time=tracker.duration * 0.3)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_2>") as tracker:
            fb = formula_box("T(v) = Mv", color=TEAL_ACCENT)
            fb.move_to(ORIGIN)
            self.play(FadeIn(fb, scale=0.7), run_time=tracker.duration * 0.5)
            self.play(Circumscribe(fb, color=STAR_YELLOW), run_time=tracker.duration * 0.35)
            dot = glow_dot(fb.get_corner(UR), color=STAR_YELLOW)
            self.play(FadeIn(dot, scale=4), run_time=tracker.duration * 0.15)

        self.wait(0.5)
