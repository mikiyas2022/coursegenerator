import os, sys
import numpy as np
os.environ["PATH"] = (
    "/tmp/stem_venv/bin:/Library/TeX/texbin:"
    "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
)
os.environ["HF_HOME"] = "/tmp/huggingface_cache"

# ── Theme & Manim ─────────────────────────────────────────────────────────────
sys.path.insert(0, "/Users/bin/Documents/Course:Exam Generator/agent_core")
from theme import *          # AmharicEduScene, BG_COLOR, ACCENT_COLOR, ...
from manim import *

# === MONKEYPATCHES ===
# Server lacks LaTeX. Redirect MathTex/Tex to Text.
import manim

def _mock_tex(*args, **kwargs):
    text = " ".join(str(a) for a in args).replace("$","").replace("^\\circ","°")
    kwargs.pop("tex_environment", None)
    return manim.Text(text, font="Inter", font_size=kwargs.get("font_size", FONT_SIZE_MATH), color=kwargs.get("color", FORMULA_COLOR))

manim.MathTex = _mock_tex
manim.Tex = _mock_tex
MathTex = _mock_tex
Tex = _mock_tex

# Prevent hallucinated CurvedBezier class
def CurvedBezier(*args, **kwargs):
    return CurvedArrow(*args, **kwargs)


class Scene1_Kickoff(AmharicEduScene):
    def construct(self):
        self.setup_scene()

        with self.voiceover(text="አረፍተ ነገር 1") as tracker:
            self.title_card("What is Projectile Motion?")
            axes = self.branded_axes()
            field = Rectangle(, fill_color=BLUE, fill_opacity=0.2)
            field.move_to(ORIGIN)
            goal = Rectangle(, fill_color=RED, fill_opacity=0.5)
            goal.move_to((5, 0))
            player = Rectangle(, fill_color=GREEN, fill_opacity=0.5)
            player.move_to((0, 0))
            ball = Dot(color=RED)
            ball.move_to((0, 0))
            self.add(field, goal, player, ball)
            self.wait(tracker.duration * 0.1)

        with self.voiceover(text="አረፍተ ነገር 2") as tracker:
            foot = Rectangle(, fill_color=GREEN, fill_opacity=0.5)
            foot.move_to((0, 0))
            self.play(
                foot.animate.move_to((0.5, 0)),
                run_time=tracker.duration * 0.9
            )
            ball2 = Dot(color=RED)
            ball2.move_to((0, 0))
            self.play(
                ball2.animate.move_to((0.1, 0.1)),
                run_time=tracker.duration * 0.9
            )
            self.clear()

        with self.voiceover(text="አረፍተ ነገር 3") as tracker:
            path = ParametricCurve(
                lambda t: (t, -0.5 * (t - 2.5)**2 + 1.5),
                t_range=(0, 5),
                stroke_width=2,
                color=YELLOW
            )
            ball = Dot(color=RED)
            ball.move_to((0, 0))
            self.play(
                ball.animate.move_along_path(path, run_time=tracker.duration * 0.9)
            )
            self.clear()

        with self.voiceover(text="አረፍተ ነገር 4") as tracker:
            gravity_arrow = Arrow(start=(0,0), end=(0,-1), color=RED, stroke_width=2)
            gravity_label = Text("a = 9.8 m/s^2", color=RED)
            gravity_label.next_to(gravity_arrow, direction=DOWN)
            self.add(gravity_arrow, gravity_label)
            self.wait(tracker.duration * 0.1)

        with self.voiceover(text="አረፍተ ነገር 5") as tracker:
            peak = Dot((2.5, 1.5), color=RED)
            self.play(
                Circumscribe(peak, run_time=tracker.duration * 0.9)
            )
            ball = Dot(color=RED)
            ball.move_to((5, 0))
            self.play(
                ball.animate.move_to((5, 0)),
                run_time=tracker.duration * 0.9
            )
            self.wait(tracker.duration * 0.1)

        with self.voiceover(text="አረፍተ ነገር 6") as tracker:
            self.wait(tracker.duration * 0.1)

class Scene2_Analogies(AmharicEduScene):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup_scene()

    def setup_scene(self):
        pass

    def construct(self):
        self.setup_scene()

        ground = Line(LEFT*5.5, RIGHT*5.5, color=Brown).shift(DOWN*3.0)
        target = Circle(radius=0.5, color=Red).move_to(UP*3.0)

        path_points = [
            (0, -3),
            (0.5, -2.8),
            (1, -2.5),
            (1.5, -2.0),
            (2, -1.0),
            (2.5, 1),
            (3, -1.0),
            (3.5, -2.0),
            (4, -2.5),
            (4.5, -2.8),
            (3, -3)
        ]

        path = VGroup()
        for i in range(len(path_points)-1):
            path.add(Line(path_points[i], path_points[i+1]))

        frisbee = Circle(radius=0.3, color=Blue).move_to((0, -3))

        with self.voiceover(text="አረፍተ ነገር 1") as tracker:
            self.play(
                frisbee.animate.move_to((0.5, -2.8)),
                run_time=tracker.duration * 0.9
            )

        with self.voiceover(text="አረፍተ ነገር 2") as tracker:
            self.play(
                frisbee.animate.move_to((1, -2.5)),
                run_time=tracker.duration * 0.9
            )

        with self.voiceover(text="አረፍተ ነገር 3") as tracker:
            self.clear()
            angle_vector = Arrow(start=(0, -3), end=(0.707, 0.707), color=Blue, buff=0.1)
            self.play(Create(angle_vector))

        with self.voiceover(text="አረፍተ ነገር 4") as tracker:
            constant_speed_text = Text("constant speed", font_size=24).move_to(UP*1.5)
            self.play(
                Write(constant_speed_text),
                run_time=tracker.duration * 0.9
            )

        with self.voiceover(text="አረፍተ ነገር 5") as tracker:
            self.play(
                frisbee.animate.move_to((2.5, 1)),
                frisbee.animate.move_to((3, -1.0)),
                run_time=tracker.duration * 0.9
            )

        with self.voiceover(text="አረፍተ ነገር 6") as tracker:
            self.clear()
            self.play(
                frisbee.animate.move_to((3, -3)),
                run_time=tracker.duration * 0.9
            )
            landing_circle = Circle(radius=0.2, color=Red).move_to((3, -3))
            self.play(Create(landing_circle))

class Scene3_Worked_Example(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        with self.voiceover(text="አረፍተ ነገር 1") as tracker:
            self.clear()
            title = amharic_text("Solving Projectile Motion Problems", font_size=FONT_SIZE_HEADER, color=TEXT_COLOR)
            title.move_to(UP * 2.0)
            underline = Line(LEFT * 3, RIGHT * 3, color=ACCENT_COLOR, stroke_width=3)
            underline.next_to(title, DOWN, buff=0.2)
            self.play(Write(title), run_time=tracker.duration * 0.6)
            self.play(Create(underline), run_time=tracker.duration * 0.3)

        with self.voiceover(text="አረፍተ ነገር 2") as tracker:
            self.clear()
            axes = branded_axes([-4, 4, 1], [-3, 3, 1])
            axes.scale(0.75).move_to(ORIGIN)
            vec = branded_vector(ORIGIN, np.array([2.5, 1.5, 0]), color=VECTOR_COLOR)
            label = latin_text("→ v", font_size=FONT_SIZE_LABEL, color=VECTOR_COLOR)
            label.next_to(vec.get_end(), UP, buff=0.2)
            self.play(Create(axes), run_time=tracker.duration * 0.4)
            self.play(GrowArrow(vec), run_time=tracker.duration * 0.4)
            self.play(Write(label), run_time=tracker.duration * 0.2)

        with self.voiceover(text="አረፍተ ነገር 3") as tracker:
            self.clear()
            f_box = formula_box("h = (v0^2 * sin^2(θ)) / (2*g)")
            f_box.move_to(ORIGIN)
            self.play(Create(f_box[0]), Write(f_box[1]), run_time=tracker.duration * 0.6)
            self.play(Circumscribe(f_box, color=ACCENT_COLOR), run_time=tracker.duration * 0.3)

        with self.voiceover(text="አረፍተ ነገር 4") as tracker:
            explanation = amharic_text("አረፍተ ነገር 4", font_size=FONT_SIZE_LABEL, color=MUTED_COLOR)
            explanation.move_to(DOWN * 2.0)
            self.play(FadeIn(explanation), run_time=tracker.duration * 0.8)

        with self.voiceover(text="አረፍተ ነገር 5") as tracker:
            self.clear()
            label = amharic_text("Solving Projectile Motion Problems", font_size=FONT_SIZE_BODY, color=ACCENT_COLOR)
            label.move_to(ORIGIN)
            circle = branded_circle(1.2, color=HIGHLIGHT_COLOR)
            circle.move_to(LEFT * 2.5)
            self.play(DrawBorderThenFill(circle), run_time=tracker.duration * 0.5)
            self.play(Write(label), run_time=tracker.duration * 0.4)

        with self.voiceover(text="አረፍተ ነገር 6") as tracker:
            explanation = amharic_text("አረፍተ ነገር 6", font_size=FONT_SIZE_LABEL, color=MUTED_COLOR)
            explanation.move_to(DOWN * 2.0)
            self.play(FadeIn(explanation), run_time=tracker.duration * 0.8)

        with self.voiceover(text="አረፍተ ነገር 7") as tracker:
            self.clear()
            label = amharic_text("Solving Projectile Motion Problems", font_size=FONT_SIZE_BODY, color=ACCENT_COLOR)
            label.move_to(ORIGIN)
            circle = branded_circle(1.2, color=HIGHLIGHT_COLOR)
            circle.move_to(LEFT * 2.5)
            self.play(DrawBorderThenFill(circle), run_time=tracker.duration * 0.5)
            self.play(Write(label), run_time=tracker.duration * 0.4)

        with self.voiceover(text="አረፍተ ነገር 8") as tracker:
            explanation = amharic_text("አረፍተ ነገር 8", font_size=FONT_SIZE_LABEL, color=MUTED_COLOR)
            explanation.move_to(DOWN * 2.0)
            self.play(FadeIn(explanation), run_time=tracker.duration * 0.8)

        self.wait(0.5)
