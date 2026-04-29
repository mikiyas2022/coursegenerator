"""
Template 37 — FLOWCHART: Step-by-step logical flow with decision branches
Pattern: Start box → decision diamond → Yes/No paths → result
Use for: Algorithms, decision processes, problem-solving strategies
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:
            start = RoundedRectangle(
                corner_radius=0.2, width=2.5, height=0.7,
                fill_color=TEAL_ACCENT, fill_opacity=0.2,
                stroke_color=TEAL_ACCENT, stroke_width=2
            ).move_to(UP * 2.4)
            start_lbl = latin_text("Start", font_size=FONT_SIZE_SMALL, color=TEAL_ACCENT)
            start_lbl.move_to(start)
            self.play(Create(start), Write(start_lbl), run_time=tracker.duration * 0.2)

            diamond = Square(side_length=1.1, color=STAR_YELLOW, stroke_width=2,
                           fill_color=STAR_YELLOW, fill_opacity=0.08).rotate(PI/4)
            diamond.move_to(UP * 0.7)
            d_lbl = latin_text("x > 0?", font_size=FONT_SIZE_CAPTION, color=STAR_YELLOW)
            d_lbl.move_to(diamond)
            arr1 = Arrow(start.get_bottom(), diamond.get_top(), buff=0.1,
                        color=MUTED_COLOR, stroke_width=2)
            self.play(GrowArrow(arr1), Create(diamond), Write(d_lbl),
                     run_time=tracker.duration * 0.2)

            yes_box = RoundedRectangle(
                corner_radius=0.15, width=2, height=0.6,
                fill_color=SUCCESS_COLOR, fill_opacity=0.15,
                stroke_color=SUCCESS_COLOR, stroke_width=2
            ).move_to(DOWN * 0.8 + LEFT * 2.5)
            yes_lbl = latin_text("Yes", font_size=FONT_SIZE_CAPTION, color=SUCCESS_COLOR)
            yes_lbl.move_to(yes_box)

            no_box = RoundedRectangle(
                corner_radius=0.15, width=2, height=0.6,
                fill_color=ERROR_COLOR, fill_opacity=0.15,
                stroke_color=ERROR_COLOR, stroke_width=2
            ).move_to(DOWN * 0.8 + RIGHT * 2.5)
            no_lbl = latin_text("No", font_size=FONT_SIZE_CAPTION, color=ERROR_COLOR)
            no_lbl.move_to(no_box)

            arr_y = Arrow(diamond.get_left(), yes_box.get_top(), buff=0.1,
                         color=SUCCESS_COLOR, stroke_width=2)
            arr_n = Arrow(diamond.get_right(), no_box.get_top(), buff=0.1,
                         color=ERROR_COLOR, stroke_width=2)
            self.play(
                GrowArrow(arr_y), Create(yes_box), Write(yes_lbl),
                GrowArrow(arr_n), Create(no_box), Write(no_lbl),
                run_time=tracker.duration * 0.35
            )

            result = RoundedRectangle(
                corner_radius=0.2, width=3, height=0.7,
                fill_color=STAR_YELLOW, fill_opacity=0.15,
                stroke_color=STAR_YELLOW, stroke_width=2
            ).move_to(DOWN * 2.2)
            res_lbl = latin_text("Result", font_size=FONT_SIZE_SMALL, color=STAR_YELLOW)
            res_lbl.move_to(result)
            arr_yr = Arrow(yes_box.get_bottom(), result.get_left(), buff=0.1,
                          color=MUTED_COLOR, stroke_width=2)
            arr_nr = Arrow(no_box.get_bottom(), result.get_right(), buff=0.1,
                          color=MUTED_COLOR, stroke_width=2)
            self.play(
                GrowArrow(arr_yr), GrowArrow(arr_nr),
                Create(result), Write(res_lbl),
                run_time=tracker.duration * 0.2
            )
            self.play(Indicate(result, color=STAR_YELLOW),
                     run_time=tracker.duration * 0.05)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_1>") as tracker:
            summary = latin_text("Every decision leads somewhere.",
                               font_size=FONT_SIZE_BODY, color=TEAL_ACCENT)
            summary.move_to(ORIGIN)
            clamp_to_screen(summary)
            self.play(Write(summary), run_time=tracker.duration * 0.6)
            self.play(summary.animate.set_color(STAR_YELLOW),
                     run_time=tracker.duration * 0.4)

        self.wait(0.5)
