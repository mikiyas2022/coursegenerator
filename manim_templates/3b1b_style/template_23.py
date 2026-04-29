"""
Template 23 — PYTHAGOREAN VISUAL: Right triangle + rotating squares area proof
Pattern: Draw right triangle → animate squares on each side → c²=a²+b²
Use for: Pythagorean theorem, geometry proofs, area relationships
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:
            # Right triangle
            a, b = 2.0, 1.5
            c = np.sqrt(a**2 + b**2)
            tri = Polygon(
                ORIGIN, RIGHT * a, RIGHT * a + UP * b,
                fill_color=TEAL_ACCENT, fill_opacity=0.2,
                stroke_color=TEAL_ACCENT, stroke_width=4
            ).shift(LEFT * 1.5 + DOWN * 0.8)
            right_angle = RightAngle(
                Line(tri.get_vertices()[0], tri.get_vertices()[1]),
                Line(tri.get_vertices()[0], tri.get_vertices()[2]),
                length=0.25, color=STAR_YELLOW
            )
            self.play(Create(tri), Create(right_angle), run_time=tracker.duration * 0.7)
            a_lbl = latin_text("a", font_size=FONT_SIZE_LABEL, color=X_COLOR)
            a_lbl.next_to(tri, DOWN, buff=0.1)
            b_lbl = latin_text("b", font_size=FONT_SIZE_LABEL, color=Y_COLOR)
            b_lbl.next_to(tri, RIGHT, buff=0.1)
            self.play(Write(a_lbl), Write(b_lbl), run_time=tracker.duration * 0.3)

        with self.voiceover(text="<NARRATION_PLACEHOLDER_1>") as tracker:
            sq_a = Square(side_length=a, fill_color=X_COLOR, fill_opacity=0.25,
                         stroke_color=X_COLOR, stroke_width=3)
            sq_a.next_to(tri, DOWN, buff=0).align_to(tri, LEFT)
            sq_b = Square(side_length=b, fill_color=Y_COLOR, fill_opacity=0.25,
                         stroke_color=Y_COLOR, stroke_width=3)
            sq_b.next_to(tri, RIGHT, buff=0).align_to(tri, UP)
            self.play(DrawBorderThenFill(sq_a), DrawBorderThenFill(sq_b),
                     run_time=tracker.duration * 0.7)
            a2_lbl = latin_text("a²", font_size=FONT_SIZE_LABEL, color=X_COLOR)
            a2_lbl.move_to(sq_a.get_center())
            b2_lbl = latin_text("b²", font_size=FONT_SIZE_LABEL, color=Y_COLOR)
            b2_lbl.move_to(sq_b.get_center())
            self.play(Write(a2_lbl), Write(b2_lbl), run_time=tracker.duration * 0.3)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_2>") as tracker:
            fb = formula_box("c² = a² + b²", color=STAR_YELLOW)
            fb.move_to(ORIGIN)
            self.play(FadeIn(fb, scale=0.6), run_time=tracker.duration * 0.4)
            self.play(Circumscribe(fb, color=STAR_YELLOW, time_width=2), run_time=tracker.duration * 0.35)
            playful_bounce(self, fb)
            dot = glow_dot(fb.get_corner(UR) + UP * 0.1, color=STAR_YELLOW)
            self.play(FadeIn(dot, scale=4), run_time=tracker.duration * 0.25)

        self.wait(0.5)
