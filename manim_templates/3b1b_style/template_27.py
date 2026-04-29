"""
Template 27 — DOPPLER EFFECT: Wavefronts compress/expand with moving source
Pattern: Concentric rings → source moves → rings bunch up → frequency label
Use for: Doppler effect, wave phenomena, sound, light redshift
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:
            source = Dot(ORIGIN, radius=0.15, color=TEAL_ACCENT)
            source_lbl = latin_text("🔊", font_size=FONT_SIZE_LABEL)
            source_lbl.move_to(ORIGIN + UP * 0.4)
            self.play(FadeIn(source), Write(source_lbl), run_time=tracker.duration * 0.4)
            rings = []
            for r in [0.5, 1.0, 1.5, 2.0, 2.5]:
                ring = Circle(radius=r, color=TEAL_ACCENT, stroke_width=2, stroke_opacity=0.7)
                rings.append(ring)
            self.play(LaggedStart(*[Create(r) for r in rings], lag_ratio=0.15),
                     run_time=tracker.duration * 0.6)

        with self.voiceover(text="<NARRATION_PLACEHOLDER_1>") as tracker:
            # Move source to the right, show rings bunching up
            moving_source = Dot(LEFT * 3, radius=0.15, color=ROSE_COLOR)
            moving_lbl = latin_text("moving →", font_size=FONT_SIZE_SMALL, color=ROSE_COLOR)
            moving_lbl.next_to(moving_source, DOWN, buff=0.1)
            compressed_rings = VGroup(*[
                Ellipse(width=r * 0.6, height=r, color=ROSE_COLOR,
                       stroke_width=2, stroke_opacity=0.7).shift(RIGHT * r * 0.2)
                for r in [0.4, 0.8, 1.2, 1.6]
            ])
            self.play(FadeIn(moving_source), Write(moving_lbl), run_time=tracker.duration * 0.3)
            self.play(Create(compressed_rings), run_time=tracker.duration * 0.4)
            higher = latin_text("Higher freq! →", font_size=FONT_SIZE_LABEL, color=STAR_YELLOW)
            higher.to_corner(UR).shift(LEFT * 0.5 + DOWN * 0.3)
            self.play(FadeIn(higher, shift=LEFT * 0.3), run_time=tracker.duration * 0.3)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_2>") as tracker:
            fb = formula_box("f' = f·(v+vo)/(v+vs)", color=TEAL_ACCENT)
            fb.move_to(ORIGIN)
            self.play(FadeIn(fb, scale=0.6), run_time=tracker.duration * 0.5)
            self.play(Circumscribe(fb, color=STAR_YELLOW), run_time=tracker.duration * 0.35)
            dot = glow_dot(fb.get_corner(UR), color=STAR_YELLOW)
            self.play(FadeIn(dot, scale=4), run_time=tracker.duration * 0.15)

        self.wait(0.5)
