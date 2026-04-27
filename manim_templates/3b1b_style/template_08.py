from manim import *
from manim_config.theme import *

class SceneTemplate08_Variation(AmharicEduScene):
    def construct(self):
        setup_scene(self)
        with self.voiceover(text="<NARRATION_PLACEHOLDER>") as tracker:
            self.clear()
            title = title_card("<AMHARIC_TITLE>", "Variation 8")
            self.play(FadeIn(title, shift=UP), run_time=tracker.duration * 0.2)
            
            axes = branded_axes(x_range=[-1, 5, 1], y_range=[-1, 4, 1]).shift(DOWN*0.5)
            self.play(Create(axes), run_time=tracker.duration * 0.2)
            
            vec = branded_vector(start=axes.c2p(0,0), end=axes.c2p(3,2), color=VECTOR_COLOR)
            vec_label = latin_text("<VECTOR_LABEL>", font_size=FONT_SIZE_LABEL).next_to(vec.get_end(), UR, buff=0.1)
            self.play(GrowArrow(vec), Write(vec_label), run_time=tracker.duration * 0.2)
            
            vec_x = branded_vector(start=axes.c2p(0,0), end=axes.c2p(3,0), color=X_COLOR)
            vec_y = branded_vector(start=axes.c2p(3,0), end=axes.c2p(3,2), color=Y_COLOR)
            
            self.play(
                TransformFromCopy(vec, vec_x),
                TransformFromCopy(vec, vec_y),
                run_time=tracker.duration * 0.3
            )
            self.wait(tracker.duration * 0.1)
