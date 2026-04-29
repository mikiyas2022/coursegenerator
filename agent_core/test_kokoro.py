import os
import sys

# Add project root to path for manim_config
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from manim import *
from kokoro_mv import KokoroService
from manim_voiceover import VoiceoverScene

class TestKokoroScene(VoiceoverScene):
    def construct(self):
        self.set_speech_service(KokoroService(voice="af_sarah", lang="en-us"))
        with self.voiceover(text="Hello! Kokoro TTS is working perfectly.") as tracker:
            text = Text("Testing Kokoro TTS")
            self.play(Write(text), run_time=tracker.duration)
        self.wait(1)

if __name__ == "__main__":
    scene = TestKokoroScene()
    scene.render()
