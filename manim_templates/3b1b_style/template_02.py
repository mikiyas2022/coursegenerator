from manim import *
from agent_core.manim_config.theme import *

class SceneTemplate02_GraphTransform(AmharicEduScene):
    def construct(self):
        setup_scene(self)
        with self.voiceover(text="<NARRATION_PLACEHOLDER>") as tracker:
            self.clear()
            title = title_card("<AMHARIC_TITLE>", "Graph Transformation")
            self.play(FadeIn(title, shift=UP), run_time=tracker.duration * 0.2)
            
            axes = branded_axes(x_range=[-4, 4, 1], y_range=[-1, 5, 1]).shift(DOWN*0.5)
            self.play(Create(axes), run_time=tracker.duration * 0.2)
            
            graph1 = axes.plot(lambda x: x**2, color=TEAL_ACCENT)
            self.play(Create(graph1), run_time=tracker.duration * 0.2)
            
            graph2 = axes.plot(lambda x: (x-2)**2 + 1, color=ROSE_COLOR)
            self.play(Transform(graph1, graph2), run_time=tracker.duration * 0.3)
            
            self.wait(tracker.duration * 0.1)
