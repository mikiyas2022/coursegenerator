"""
agent_core/manim_config/blackboard_theme.py — Q&A Blackboard Theming Engine
=============================================================================
Realistic blackboard simulation for step-by-step EUEE exam solutions.
"""

from manim import Scene, Text, Mobject, Write, linear

# Blackboard Colors
BB_BG_COLOR = "#1A2518"        # Dark green/black texture
BB_CHALK_WHITE = "#F4F4F0"     # Chalk white
BB_CHALK_YELLOW = "#FFF59D"    # Yellow chalk
BB_CHALK_BLUE = "#81D4FA"      # Blue chalk
BB_CHALK_RED = "#EF9A9A"       # Red chalk

def setup_blackboard(scene: Scene) -> None:
    """Setup realistic blackboard background."""
    scene.camera.background_color = BB_BG_COLOR
    Text.set_default(font="Inter", color=BB_CHALK_WHITE)

class BlackboardScene(Scene):
    """Base class for blackboard videos without TTS, realistic writing."""
    def setup(self):
        super().setup()
        setup_blackboard(self)

    def write_step(self, mobject: Mobject, run_time=2.0):
        """Simulates realistic stroke-by-stroke chalk writing."""
        self.play(Write(mobject, run_time=run_time, rate_func=linear))
