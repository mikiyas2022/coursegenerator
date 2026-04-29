"""
Template 30 — GRAND FINALE: Multi-element composition with full choreography
Pattern: Multiple formulas orbit center → collapse to one → final glow burst
Use for: Course finale, "putting it all together", grand synthesis scenes
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:
            # Multiple concepts orbiting center
            concepts = ["F = ma", "E = mc²", "ΔS ≥ 0", "∇·E = ρ/ε₀"]
            orbit_mobs = []
            for i, c in enumerate(concepts):
                angle = i * TAU / len(concepts)
                pos = 2.8 * np.array([np.cos(angle), np.sin(angle), 0])
                mob = formula_box(c, color=TEAL_ACCENT)
                mob.scale(0.6).move_to(pos)
                orbit_mobs.append(mob)
            self.play(LaggedStart(*[FadeIn(m, scale=0.5) for m in orbit_mobs], lag_ratio=0.15),
                     run_time=tracker.duration * 0.7)
            self.play(LaggedStart(*[Indicate(m, color=STAR_YELLOW) for m in orbit_mobs], lag_ratio=0.1),
                     run_time=tracker.duration * 0.3)

        with self.voiceover(text="<NARRATION_PLACEHOLDER_1>") as tracker:
            # All collapse to center
            center_fb = formula_box("<NARRATION_PLACEHOLDER_0>", color=STAR_YELLOW)
            center_fb.scale(1.2).move_to(ORIGIN)
            self.play(*[m.animate.move_to(ORIGIN).scale(0.1) for m in orbit_mobs],
                     run_time=tracker.duration * 0.5, rate_func=smooth)
            self.play(*[FadeOut(m) for m in orbit_mobs], run_time=0.1)
            self.play(FadeIn(center_fb, scale=0.3), run_time=tracker.duration * 0.4)
            self.wait(tracker.duration * 0.1)

        with self.voiceover(text="<NARRATION_PLACEHOLDER_2>") as tracker:
            self.play(Circumscribe(center_fb, color=STAR_YELLOW, time_width=2),
                     run_time=tracker.duration * 0.35)
            # Starburst
            burst = VGroup(*[
                Arrow(ORIGIN, rotate_vector(RIGHT * 2.5, i * TAU / 12),
                      buff=0, color=STAR_YELLOW, stroke_width=3,
                      max_tip_length_to_length_ratio=0.12)
                for i in range(12)
            ])
            self.play(LaggedStart(*[GrowArrow(a) for a in burst], lag_ratio=0.03),
                     run_time=tracker.duration * 0.45)
            playful_bounce(self, center_fb)
            self.wait(tracker.duration * 0.2)

        self.wait(0.8)
