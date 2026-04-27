from manim import *
from agent_core.manim_config.blackboard_theme import *

class Blackboard_WriteList(BlackboardScene):
    def construct(self):
        setup_blackboard(self)
        # Stroke-by-stroke realism
        # <CONTENT_PLACEHOLDER>
        self.wait(1)
