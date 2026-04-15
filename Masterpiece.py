import os
import subprocess
import hashlib
from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.base import SpeechService

# Fix macOS Sandboxing HF cache issue globally
os.environ['HF_HOME'] = '/tmp/huggingface_cache'

# Enforce macOS Homebrew and LaTeX dependencies logically
os.environ['PATH'] = f"/Library/TeX/texbin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:{os.environ.get('PATH', '')}"
os.environ['LIBGS'] = '/opt/homebrew/lib/libgs.dylib'
tex_dist = '/opt/homebrew/Cellar/texlive/20260301/share/texmf-dist'
os.environ['TEXMFCNF'] = f'{tex_dist}/web2c'
os.environ['TEXMFDIST'] = tex_dist
os.environ['TEXMFMAIN'] = tex_dist

class EdgeTTSService(SpeechService):
    """Custom Service to directly use Microsoft Edge's Neural TTS for Amharic in manim-voiceover."""
    def __init__(self, voice="am-ET-MekdesNeural", **kwargs):
        self.voice = voice
        super().__init__(**kwargs)

    def generate_from_text(self, text: str, cache_dir: str = None, path: str = None, **kwargs) -> dict:
        if cache_dir is None:
            cache_dir = self.cache_dir
            
        # Create unique hash for caching
        input_data = text + self.voice
        data_hash = hashlib.sha256(input_data.encode('utf-8')).hexdigest()
        
        filename = f"{data_hash}.mp3"
        if path is None:
            path = os.path.join(cache_dir, filename)
            
        if not os.path.exists(path):
            edge_cmd = [
                "/tmp/stem_venv/bin/edge-tts", 
                "--voice", self.voice, 
                "--text", text, 
                "--write-media", path
            ]
            subprocess.run(edge_cmd, check=True, stdout=subprocess.DEVNULL)
            
        return {"original_audio": filename}

class PhysicsEpisode(VoiceoverScene, MovingCameraScene):
    def construct(self):
        self.camera.frame.save_state()
        # 1. Provide the EdgeTTSService to handle Amharic Voiceover directly
        self.set_speech_service(EdgeTTSService(voice="am-ET-MekdesNeural"))
        
        # Masterpiece Global Styling
        self.camera.background_color = "#141414"
        Text.set_default(font="Inter", weight=BOLD)
        MathTex.set_default(font_size=48)
        
        # Grid Background for strict physics context
        grid = NumberPlane(
            x_range=[-1, 8, 1], y_range=[-1, 5, 1],
            background_line_style={"stroke_opacity": 0.15, "stroke_width": 2, "stroke_color": TEAL}
        ).set_opacity(0.4).shift(UP * 0.5)
        
        # Origin and core visual variables
        origin = grid.c2p(0, 0)
        theta_tracker = ValueTracker(35 * DEGREES)
        force_magnitude = 5.0
        
        # ---------------------------------------------------------
        # SECTION 1: Introduction to the Force Vector
        # ---------------------------------------------------------
        self.next_section("Introduction to Vector Resolution")
        
        self.play(Create(grid), run_time=1.5)
        
        # Always redraw vector to automatically update when tracker changes
        vector = always_redraw(lambda: Arrow(
            start=origin,
            end=grid.c2p(
                force_magnitude * np.cos(theta_tracker.get_value()),
                force_magnitude * np.sin(theta_tracker.get_value())
            ),
            buff=0, color=RED, stroke_width=6, max_tip_length_to_length_ratio=0.1
        ))

        # Always redraw the angle arc
        arc = always_redraw(lambda: Arc(
            radius=1.0, start_angle=0, angle=theta_tracker.get_value(),
            arc_center=origin, color=YELLOW, stroke_width=4
        ))

        # Always redraw Theta label
        theta_label = always_redraw(lambda: MathTex(r"\theta", color=YELLOW)
            .next_to(arc, RIGHT, buff=0.1)
            .shift(UP * 0.2))
            
        force_label = always_redraw(lambda: MathTex(r"\vec{F}", color=RED)
            .next_to(vector.get_end(), UR, buff=0.1))

        intro_text = "ሰላም ተማሪዎች፣ ዛሬ አንድን ሀይል ወደ ኤክስ እና ዋይ አቅጣጫዎች እንዴት እንደምንከፍል እናያለን። ይህን ቀይ የሀይል ቬክተር ተመልከቱ።"
        with self.voiceover(text=intro_text) as tracker:
            self.play(GrowArrow(vector), run_time=tracker.duration * 0.5)
            self.play(Create(arc), Write(theta_label), Write(force_label), run_time=tracker.duration * 0.4)
        
        # ---------------------------------------------------------
        # SECTION 2: Dynamic Angle Sweep
        # ---------------------------------------------------------
        self.next_section("Dynamic Angle Transition")
        
        sweep_text = "የቬክተሩ ማእዘን ወይም ቴታ ሲቀየር፣ የሀይሉ አቅጣጫም አብሮ ይለወጣል። ቬክተሩ እንዴት እንደሚንቀሳቀስ በደንብ አስተውሉ።"
        with self.voiceover(text=sweep_text) as tracker:
            # Emphasize theta using subtle FocusOn and camera push-in
            self.play(self.camera.frame.animate.scale(0.6).move_to(origin + RIGHT*1.5 + UP*1.0), run_time=1.0)
            self.play(Circumscribe(theta_label, color=YELLOW_C, time_width=2.0), run_time=1.0)
            
            # Sweeping tracker to visually demonstrate change in Force vector
            # The always_redraw() automatically updates vector, arc, and labels!
            self.play(
                theta_tracker.animate.set_value(65 * DEGREES),
                rate_func=there_and_back,
                run_time=tracker.duration - 1.0
            )

        # ---------------------------------------------------------
        # SECTION 3: Resolving X Component
        # ---------------------------------------------------------
        self.next_section("X Component Resolution")
        
        # Dashed x-projection
        dashed_x = always_redraw(lambda: DashedLine(
            start=grid.c2p(force_magnitude * np.cos(theta_tracker.get_value()), force_magnitude * np.sin(theta_tracker.get_value())),
            end=grid.c2p(force_magnitude * np.cos(theta_tracker.get_value()), 0),
            color=GRAY_C
        ))
        
        # F_x vector (Blue)
        vec_x = always_redraw(lambda: Arrow(
            start=origin,
            end=grid.c2p(force_magnitude * np.cos(theta_tracker.get_value()), 0),
            buff=0, color=BLUE, stroke_width=6
        ))
        
        label_x = MathTex(r"F_x", color=BLUE).next_to(grid.c2p(2.5, 0), DOWN)

        x_text = "አሁን ቬክተሩን ወደ ቀኝ ወይም ኤክስ አቅጣጫ እንከፍለዋለን። የኤክስ አቅጣጫ ሀይል እኩል ነው፣ ዋናው ሀይል ሲባዛ ኮሳይን ቴታ።"
        with self.voiceover(text=x_text) as tracker:
            self.play(self.camera.frame.animate.scale(1.5).move_to(origin + RIGHT*2.5 + UP*1), run_time=1.0)
            self.play(Create(dashed_x), run_time=tracker.duration * 0.25)
            self.play(TransformFromCopy(vec_x, label_x), run_time=tracker.duration * 0.4)
            self.play(Wiggle(label_x), run_time=0.5)

        # Equation Morphing for F_x
        # Reset camera to fit equations cleanly
        self.play(self.camera.frame.animate.restore(), run_time=1.0)
        
        eq_x_1 = MathTex("F_x", "=", "F", "\\cos(\\theta)").to_corner(UL).shift(DOWN * 0.5 + RIGHT * 0.5)
        eq_x_1[0].set_color(BLUE)
        eq_x_1[2].set_color(RED)
        eq_x_1[3].set_color(YELLOW)

        with self.voiceover(text="ማለትም፣ ኤፍ ኤክስ እኩል ነው ኤፍ ኮሳይን ቴታ።") as tracker:
            self.play(TransformMatchingTex(label_x.copy(), eq_x_1), run_time=tracker.duration)
            self.play(Circumscribe(eq_x_1, color=BLUE_C), run_time=1.0)

        # ---------------------------------------------------------
        # SECTION 4: Resolving Y Component
        # ---------------------------------------------------------
        self.next_section("Y Component Resolution")

        # Dashed y-projection
        dashed_y = always_redraw(lambda: DashedLine(
            start=grid.c2p(force_magnitude * np.cos(theta_tracker.get_value()), force_magnitude * np.sin(theta_tracker.get_value())),
            end=grid.c2p(0, force_magnitude * np.sin(theta_tracker.get_value())),
            color=GRAY_C
        ))
        
        # F_y vector (Green)
        vec_y = always_redraw(lambda: Arrow(
            start=origin,
            end=grid.c2p(0, force_magnitude * np.sin(theta_tracker.get_value())),
            buff=0, color=GREEN, stroke_width=6
        ))
        
        label_y = MathTex(r"F_y", color=GREEN).next_to(grid.c2p(0, 2.5), LEFT)

        y_text = "በመቀጠል ደግሞ ወደ ላይ ወይም ዋይ አቅጣጫ ያለውን ሀይል እንፈልግ። የዋይ አቅጣጫ ሀይል እኩል ነው፣ ዋናው ሀይል ሲባዛ ሳይን ቴታ።"
        with self.voiceover(text=y_text) as tracker:
            self.play(Create(dashed_y), run_time=tracker.duration * 0.25)
            self.play(TransformFromCopy(vec_y, label_y), run_time=tracker.duration * 0.4)
            self.play(Wiggle(label_y), run_time=0.5)

        # Equation Morphing for F_y
        eq_y_1 = MathTex("F_y", "=", "F", "\\sin(\\theta)").next_to(eq_x_1, DOWN, buff=0.5, aligned_edge=LEFT)
        eq_y_1[0].set_color(GREEN)
        eq_y_1[2].set_color(RED)
        eq_y_1[3].set_color(YELLOW)

        with self.voiceover(text="ማለትም፣ ኤፍ ዋይ እኩል ነው ኤፍ ሳይን ቴታ። ይህ የፊዚክስ ውበት ነው!") as tracker:
            # Math pieces fly in cleanly
            self.play(TransformMatchingTex(label_y.copy(), eq_y_1), run_time=tracker.duration * 0.5)
            self.play(Indicate(eq_x_1, color=WHITE), Indicate(eq_y_1, color=WHITE), run_time=tracker.duration * 0.4)

        # Wait gracefully before ending
        self.wait(3)

if __name__ == "__main__":
    import sys
    # Example execution hook for CLI usage:
    # manim -pqh Masterpiece.py PhysicsEpisode
    pass
