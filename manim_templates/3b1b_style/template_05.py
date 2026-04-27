from manim import *
from manim_config.theme import *

class SceneTemplate05_PlayfulExplosion(AmharicEduScene):
    def construct(self):
        setup_scene(self)
        with self.voiceover(text="<NARRATION_PLACEHOLDER>") as tracker:
            self.clear()
            title = title_card("<AMHARIC_TITLE>", "Concept Explosion")
            self.play(FadeIn(title, shift=UP), run_time=tracker.duration * 0.1)
            
            center_circle = branded_circle(radius=1.0, color=TEAL_ACCENT)
            center_text = amharic_text("<CENTER_CONCEPT>", font_size=FONT_SIZE_LABEL).move_to(center_circle)
            self.play(Create(center_circle), Write(center_text), run_time=tracker.duration * 0.3)
            
            dots = [glow_dot(point=UP*2).rotate(i * TAU/5, about_point=ORIGIN) for i in range(5)]
            labels = [amharic_text(f"<CONCEPT_{i+1}>", font_size=FONT_SIZE_SMALL).next_to(dots[i], UP).rotate(-i*TAU/5) for i in range(5)]
            
            self.play(
                *[TransformFromCopy(center_circle, d) for d in dots],
                run_time=tracker.duration * 0.3
            )
            self.play(*[Write(l) for l in labels], run_time=tracker.duration * 0.2)
            
            self.wait(tracker.duration * 0.1)
