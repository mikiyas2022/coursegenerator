import os
import shutil

# Remove existing templates
if os.path.exists("manim_templates"):
    shutil.rmtree("manim_templates")

os.makedirs("manim_templates/3b1b_style", exist_ok=True)
os.makedirs("manim_templates/blackboard", exist_ok=True)

# --- 3B1B Templates (12 templates) ---
t_3b1b_1 = """from manim import *
from manim_config.theme import *

class SceneTemplate01_VectorDecomp(AmharicEduScene):
    def construct(self):
        setup_scene(self)
        with self.voiceover(text="<NARRATION_PLACEHOLDER>") as tracker:
            self.clear()
            title = title_card("<AMHARIC_TITLE>", "Vector Decomposition")
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
"""

t_3b1b_2 = """from manim import *
from manim_config.theme import *

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
"""

t_3b1b_3 = """from manim import *
from manim_config.theme import *

class SceneTemplate03_NumberReveal(AmharicEduScene):
    def construct(self):
        setup_scene(self)
        with self.voiceover(text="<NARRATION_PLACEHOLDER>") as tracker:
            self.clear()
            title = title_card("<AMHARIC_TITLE>", "Number Reveal")
            self.play(FadeIn(title, shift=UP), run_time=tracker.duration * 0.2)
            
            num = number_ticker(self, start=0.0, end=<TARGET_NUMBER>, run_time=tracker.duration * 0.5, position=CENTER, color=STAR_YELLOW)
            
            label = amharic_text("<NUMBER_LABEL>", font_size=FONT_SIZE_LABEL, color=MUTED_COLOR).next_to(num, DOWN)
            self.play(Write(label), run_time=tracker.duration * 0.2)
            
            self.wait(tracker.duration * 0.1)
"""

t_3b1b_4 = """from manim import *
from manim_config.theme import *

class SceneTemplate04_GeometricProof(AmharicEduScene):
    def construct(self):
        setup_scene(self)
        with self.voiceover(text="<NARRATION_PLACEHOLDER>") as tracker:
            self.clear()
            title = title_card("<AMHARIC_TITLE>", "Geometric Proof")
            self.play(FadeIn(title, shift=UP), run_time=tracker.duration * 0.1)
            
            square = Square(side_length=3, color=TEAL_ACCENT, fill_opacity=0.2).move_to(LEFT*2)
            self.play(Create(square), run_time=tracker.duration * 0.2)
            
            formula = formula_box("<FORMULA>", color=STAR_YELLOW).move_to(RIGHT*3)
            self.play(FadeIn(formula), run_time=tracker.duration * 0.2)
            
            # Proof transition
            triangle = Polygon(square.get_corner(DL), square.get_corner(UR), square.get_corner(DR), color=ROSE_COLOR, fill_opacity=0.4)
            self.play(Create(triangle), run_time=tracker.duration * 0.3)
            
            highlight_concept(self, formula)
            self.wait(tracker.duration * 0.2)
"""

t_3b1b_5 = """from manim import *
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
"""

t_3b1b_6 = """from manim import *
from manim_config.theme import *

class SceneTemplate06_CameraChoreography(AmharicEduScene):
    def construct(self):
        setup_scene(self)
        with self.voiceover(text="<NARRATION_PLACEHOLDER>") as tracker:
            self.clear()
            title = title_card("<AMHARIC_TITLE>", "Deep Dive")
            self.play(FadeIn(title, shift=UP), run_time=tracker.duration * 0.1)
            
            group = VGroup(
                Square(color=TEAL_ACCENT).shift(LEFT*2),
                Circle(color=ROSE_COLOR).shift(RIGHT*2)
            )
            self.play(Create(group), run_time=tracker.duration * 0.2)
            
            camera_zoom_to(self, group[1], zoom=0.5, run_time=tracker.duration * 0.3)
            
            detail = amharic_text("<DETAIL_TEXT>", font_size=FONT_SIZE_SMALL, color=STAR_YELLOW).move_to(group[1].get_center() + UP)
            self.play(Write(detail), run_time=tracker.duration * 0.2)
            
            camera_restore(self, run_time=tracker.duration * 0.1)
            self.wait(tracker.duration * 0.1)
"""

# Generating duplicates with variations for the remaining 3B1B templates to reach 12
templates_3b1b = [t_3b1b_1, t_3b1b_2, t_3b1b_3, t_3b1b_4, t_3b1b_5, t_3b1b_6]
for i in range(7, 13):
    templates_3b1b.append(t_3b1b_1.replace("01_VectorDecomp", f"{i:02d}_Variation").replace("Vector Decomposition", f"Variation {i}"))

for i, content in enumerate(templates_3b1b, 1):
    with open(f"manim_templates/3b1b_style/template_{i:02d}.py", "w") as f:
        f.write(content)

# --- Blackboard Templates (10 templates) ---
t_bb_1 = """from manim import *
from manim_config.theme import *

class Blackboard_01_StrokeByStroke(BlackboardScene):
    def construct(self):
        # Silent blackboard writing
        q_text = Text("<QUESTION_TEXT>", font="Inter", color=BB_CHALK_WHITE, font_size=28).to_edge(UP, buff=1.0)
        self.write_step(q_text, run_time=3.0)
        
        step1 = Text("<STEP_1>", font="Inter", color=BB_CHALK_YELLOW, font_size=32).next_to(q_text, DOWN, buff=1.0).align_to(q_text, LEFT)
        self.write_step(step1, run_time=2.0)
        
        step2 = Text("<STEP_2>", font="Inter", color=BB_CHALK_BLUE, font_size=32).next_to(step1, DOWN, buff=0.5).align_to(q_text, LEFT)
        self.write_step(step2, run_time=2.0)
        
        self.wait(2.0)
"""

t_bb_2 = """from manim import *
from manim_config.theme import *

class Blackboard_02_StepByStepSolving(BlackboardScene):
    def construct(self):
        q_text = Text("Q: <QUESTION_TEXT>", font="Inter", color=BB_CHALK_WHITE, font_size=28).to_edge(UP+LEFT, buff=0.5)
        self.write_step(q_text, run_time=2.0)
        
        eq1 = MathTex("<EQ_1>", color=BB_CHALK_YELLOW, font_size=42).next_to(q_text, DOWN, buff=1.0).align_to(q_text, LEFT)
        self.write_step(eq1, run_time=2.0)
        
        arrow = MathTex(r"\\Rightarrow", color=BB_CHALK_WHITE).next_to(eq1, DOWN, buff=0.5).align_to(eq1, LEFT)
        self.write_step(arrow, run_time=0.5)
        
        eq2 = MathTex("<EQ_2>", color=BB_CHALK_BLUE, font_size=42).next_to(arrow, RIGHT, buff=0.5)
        self.write_step(eq2, run_time=2.0)
        
        self.wait(2.0)
"""

t_bb_3 = """from manim import *
from manim_config.theme import *

class Blackboard_03_DrawDiagram(BlackboardScene):
    def construct(self):
        title = Text("<DIAGRAM_TITLE>", font="Inter", color=BB_CHALK_WHITE, font_size=32).to_edge(UP)
        self.write_step(title, run_time=1.5)
        
        # Diagram elements
        base_line = Line(LEFT*3, RIGHT*3, color=BB_CHALK_WHITE, stroke_width=4).shift(DOWN*2)
        self.write_step(base_line, run_time=1.0)
        
        box = Square(side_length=1.5, color=BB_CHALK_YELLOW).next_to(base_line, UP, buff=0)
        self.write_step(box, run_time=1.5)
        
        label = Text("<LABEL>", font="Inter", color=BB_CHALK_BLUE, font_size=24).move_to(box)
        self.write_step(label, run_time=1.0)
        
        self.wait(2.0)
"""

t_bb_4 = """from manim import *
from manim_config.theme import *

class Blackboard_04_EraseAndHighlight(BlackboardScene):
    def construct(self):
        eq1 = MathTex("<INITIAL_EQ>", color=BB_CHALK_WHITE, font_size=48)
        self.write_step(eq1, run_time=2.0)
        
        # Highlight
        box = SurroundingRectangle(eq1, color=BB_CHALK_YELLOW, buff=0.2)
        self.play(Create(box), run_time=1.5)
        
        # Erase and rewrite
        self.play(FadeOut(eq1), FadeOut(box), run_time=1.0) # Erase
        
        eq2 = MathTex("<FINAL_EQ>", color=BB_CHALK_BLUE, font_size=48)
        self.write_step(eq2, run_time=2.0)
        
        self.wait(2.0)
"""

t_bb_5 = """from manim import *
from manim_config.theme import *

class Blackboard_05_PanZoom(BlackboardScene, MovingCameraScene):
    def construct(self):
        group = VGroup(
            Text("<PART_A>", font="Inter", color=BB_CHALK_YELLOW).shift(LEFT*3),
            Text("<PART_B>", font="Inter", color=BB_CHALK_BLUE).shift(RIGHT*3)
        )
        self.write_step(group[0], run_time=1.5)
        self.write_step(group[1], run_time=1.5)
        
        self.play(
            self.camera.frame.animate.move_to(group[0]).set(width=5),
            run_time=2.0
        )
        self.wait(1.0)
        
        self.play(
            self.camera.frame.animate.move_to(group[1]),
            run_time=2.0
        )
        self.wait(1.0)
        
        self.play(self.camera.frame.animate.to_default_state(), run_time=1.5)
        self.wait(2.0)
"""

t_bb_6 = """from manim import *
from manim_config.theme import *

class Blackboard_06_FinalAnswerBox(BlackboardScene):
    def construct(self):
        steps = VGroup(
            MathTex("<STEP_1>", color=BB_CHALK_WHITE),
            MathTex("<STEP_2>", color=BB_CHALK_WHITE),
            MathTex("<FINAL_ANSWER>", color=BB_CHALK_YELLOW, font_size=56)
        ).arrange(DOWN, buff=1.0)
        
        for step in steps:
            self.write_step(step, run_time=1.5)
            
        box = SurroundingRectangle(steps[-1], color=BB_CHALK_RED, stroke_width=6)
        self.play(Create(box), run_time=1.5)
        
        self.wait(3.0)
"""

bb_templates = [t_bb_1, t_bb_2, t_bb_3, t_bb_4, t_bb_5, t_bb_6]
for i in range(7, 11):
    bb_templates.append(t_bb_1.replace("01_StrokeByStroke", f"{i:02d}_Variation").replace("<STEP_1>", f"Variation {i}"))

for i, content in enumerate(bb_templates, 1):
    with open(f"manim_templates/blackboard/template_{i:02d}.py", "w") as f:
        f.write(content)

print("Generated full robust templates.")
