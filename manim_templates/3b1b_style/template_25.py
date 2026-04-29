"""
Template 25 — CIRCUIT ANALOGY: Visual circuit metaphor for systems
Pattern: Battery → wires → resistor → bulb glows → Ohm's law formula
Use for: Ohm's law, circuits, current, voltage, water analogy
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:
            # Simple visual circuit: battery left, bulb right, wires connecting
            battery_rect = Rectangle(width=0.5, height=1.2,
                                    fill_color=STAR_YELLOW, fill_opacity=0.9,
                                    stroke_color=STAR_YELLOW, stroke_width=3)
            battery_rect.shift(LEFT * 3.5)
            batt_lbl = latin_text("V", font_size=FONT_SIZE_LABEL, color=BG_COLOR)
            batt_lbl.move_to(battery_rect.get_center())
            # Wire top
            wire_top = Line(battery_rect.get_top(), RIGHT * 3.5 + UP * 0.6,
                           color=MUTED_COLOR, stroke_width=4)
            # Resistor (zigzag)
            zz_pts = [LEFT * 0.4, LEFT * 0.2 + UP * 0.15, LEFT * 0.0 + DOWN * 0.15,
                     RIGHT * 0.2 + UP * 0.15, RIGHT * 0.4]
            resistor = VMobject(color=FORCE_COLOR, stroke_width=5)
            resistor.set_points_as_corners([np.array([p[0], p[1], 0]) if len(p)==2
                                           else np.array(p) for p in zz_pts])
            resistor.move_to(UP * 0.6)
            res_lbl = latin_text("R", font_size=FONT_SIZE_LABEL, color=FORCE_COLOR)
            res_lbl.next_to(resistor, UP, buff=0.1)
            # Bulb
            bulb = Circle(radius=0.35, fill_color=STAR_YELLOW, fill_opacity=0.0,
                         stroke_color=MUTED_COLOR, stroke_width=3)
            bulb.shift(RIGHT * 3.5)
            bulb_lbl = latin_text("💡", font_size=FONT_SIZE_LABEL)
            bulb_lbl.move_to(bulb.get_center())
            self.play(DrawBorderThenFill(battery_rect), Write(batt_lbl), run_time=tracker.duration * 0.5)
            self.play(Create(wire_top), Create(resistor), Write(res_lbl), run_time=tracker.duration * 0.3)
            self.play(DrawBorderThenFill(bulb), Write(bulb_lbl), run_time=tracker.duration * 0.2)

        with self.voiceover(text="<NARRATION_PLACEHOLDER_1>") as tracker:
            self.play(bulb.animate.set_fill(STAR_YELLOW, opacity=0.8), run_time=tracker.duration * 0.4)
            current_lbl = latin_text("I = V/R", font_size=FONT_SIZE_BODY, color=TEAL_ACCENT)
            current_lbl.to_edge(DOWN, buff=0.5)
            self.play(Write(current_lbl), run_time=tracker.duration * 0.35)
            playful_bounce(self, bulb_lbl)
            self.wait(tracker.duration * 0.25)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_2>") as tracker:
            fb = formula_box("V = IR  (Ohm's Law)", color=STAR_YELLOW)
            fb.move_to(ORIGIN)
            self.play(FadeIn(fb, scale=0.7), run_time=tracker.duration * 0.5)
            self.play(Circumscribe(fb, color=STAR_YELLOW), run_time=tracker.duration * 0.35)
            dot = glow_dot(fb.get_corner(UR), color=STAR_YELLOW)
            self.play(FadeIn(dot, scale=4), run_time=tracker.duration * 0.15)

        self.wait(0.5)
