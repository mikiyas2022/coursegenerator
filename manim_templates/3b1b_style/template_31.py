"""
Template 31 — 3D SURFACE: ThreeDScene rotating surface plot
Pattern: 3D axes appear → surface renders → camera orbits → cross-section highlight
Use for: Multivariable calculus, electromagnetic fields, 3D geometry, topology
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:
            axes = branded_axes([-3, 3, 1], [-3, 3, 1]).scale(0.7)
            axes.move_to(ORIGIN)
            self.play(Create(axes), run_time=tracker.duration * 0.4)
            # Build a "surface" approximation using concentric circles
            rings = VGroup()
            for r in [0.5, 1.0, 1.5, 2.0, 2.5]:
                ring = Circle(radius=r, color=TEAL_ACCENT, stroke_width=1.5, stroke_opacity=0.4 + r * 0.12)
                rings.add(ring)
            self.play(LaggedStart(*[Create(r) for r in rings], lag_ratio=0.08),
                     run_time=tracker.duration * 0.4)
            self.play(Indicate(rings[-1], color=STAR_YELLOW), run_time=tracker.duration * 0.2)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_1>") as tracker:
            fb = formula_box("<NARRATION_PLACEHOLDER_0>", color=TEAL_ACCENT)
            fb.move_to(ORIGIN)
            self.play(FadeIn(fb, scale=0.6), run_time=tracker.duration * 0.5)
            self.play(Circumscribe(fb, color=STAR_YELLOW, time_width=2), run_time=tracker.duration * 0.35)
            dot = glow_dot(fb.get_corner(UR), color=STAR_YELLOW)
            self.play(FadeIn(dot, scale=4), run_time=tracker.duration * 0.15)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_2>") as tracker:
            summary = latin_text("The shape tells the whole story.", font_size=FONT_SIZE_BODY, color=TEAL_ACCENT)
            summary.move_to(ORIGIN)
            clamp_to_screen(summary)
            self.play(Write(summary), run_time=tracker.duration * 0.6)
            self.play(summary.animate.set_color(STAR_YELLOW), run_time=tracker.duration * 0.4)

        self.wait(0.5)
