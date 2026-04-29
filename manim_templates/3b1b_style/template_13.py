"""
Template 13 — FORCE DIAGRAM: FBD with multiple arrows + labels
Pattern: Rectangle body → multiple Force arrows → label each → net force
Use for: Newton's laws, free body diagrams, equilibrium, mechanics
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:
            body = Rectangle(width=1.8, height=1.2, fill_color=SURFACE_COLOR,
                            fill_opacity=0.7, color=TEAL_ACCENT, stroke_width=3)
            body.move_to(ORIGIN)
            mass_lbl = latin_text("m = 5 kg", font_size=FONT_SIZE_SMALL, color=TEXT_COLOR)
            mass_lbl.move_to(body.get_center())
            self.play(DrawBorderThenFill(body), Write(mass_lbl), run_time=tracker.duration * 0.6)
            self.wait(tracker.duration * 0.4)

        with self.voiceover(text="<NARRATION_PLACEHOLDER_1>") as tracker:
            f_applied = Arrow(LEFT * 2.5, body.get_left(), buff=0,
                             color=FORCE_COLOR, stroke_width=6,
                             max_tip_length_to_length_ratio=0.15)
            f_lbl = latin_text("F = 30 N →", font_size=FONT_SIZE_SMALL, color=FORCE_COLOR)
            f_lbl.next_to(f_applied, UP, buff=0.1)
            weight = Arrow(body.get_bottom(), body.get_bottom() + DOWN * 1.8,
                          buff=0, color=ERROR_COLOR, stroke_width=6,
                          max_tip_length_to_length_ratio=0.15)
            w_lbl = latin_text("W = 49 N ↓", font_size=FONT_SIZE_SMALL, color=ERROR_COLOR)
            w_lbl.next_to(weight, RIGHT, buff=0.1)
            normal = Arrow(body.get_top(), body.get_top() + UP * 1.8,
                          buff=0, color=Y_COLOR, stroke_width=6,
                          max_tip_length_to_length_ratio=0.15)
            n_lbl = latin_text("N = 49 N ↑", font_size=FONT_SIZE_SMALL, color=Y_COLOR)
            n_lbl.next_to(normal, LEFT, buff=0.1)
            self.play(Create(f_applied), Write(f_lbl), run_time=tracker.duration * 0.3)
            self.play(Create(weight), Write(w_lbl), run_time=tracker.duration * 0.3)
            self.play(Create(normal), Write(n_lbl), run_time=tracker.duration * 0.3)
            self.wait(tracker.duration * 0.1)

        with self.voiceover(text="<NARRATION_PLACEHOLDER_2>") as tracker:
            net_arrow = Arrow(body.get_right(), body.get_right() + RIGHT * 2.2,
                             buff=0, color=STAR_YELLOW, stroke_width=8,
                             max_tip_length_to_length_ratio=0.15)
            net_lbl = latin_text("Fnet = 30 N", font_size=FONT_SIZE_LABEL, color=STAR_YELLOW)
            net_lbl.next_to(net_arrow, UP, buff=0.15)
            self.play(Create(net_arrow), Write(net_lbl), run_time=tracker.duration * 0.4)
            self.play(Indicate(net_arrow, color=STAR_YELLOW), run_time=tracker.duration * 0.3)
            fb = formula_box("a = F/m = 6 m/s²", color=STAR_YELLOW)
            fb.to_edge(DOWN, buff=0.4)
            self.play(FadeIn(fb, shift=UP * 0.3), run_time=tracker.duration * 0.3)

        self.wait(0.5)
