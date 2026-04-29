#!/usr/bin/env python3
"""
Build 500+ pre-made Manim templates by combining visual patterns.
Run once: python3 scripts/build_templates.py
"""
import os, random

OUT = os.path.join(os.path.dirname(__file__), "..", "manim_templates", "3b1b_style")
os.makedirs(OUT, exist_ok=True)

# ── Building blocks ──────────────────────────────────────────────────────────

COLORS = ["TEAL_ACCENT","STAR_YELLOW","VECTOR_COLOR","FORCE_COLOR","ROSE_COLOR","SUCCESS_COLOR","ERROR_COLOR"]
ACCENTS = ["STAR_YELLOW","TEAL_ACCENT","SUCCESS_COLOR"]
FONTS = ["FONT_SIZE_BODY","FONT_SIZE_LABEL","FONT_SIZE_HEADER"]
ANIMS_IN = [
    'FadeIn({obj}, shift=UP*0.3)',
    'FadeIn({obj}, scale=0.5)',
    'Write({obj})',
    'Create({obj})',
    'FadeIn({obj}, shift=RIGHT*0.3)',
    'FadeIn({obj}, shift=LEFT*0.3)',
    'FadeIn({obj}, shift=DOWN*0.2)',
]
ANIMS_ACCENT = [
    'Indicate({obj}, color={col})',
    'Circumscribe({obj}, color={col}, time_width=2)',
    '{obj}.animate.set_color({col})',
]
OBJECTS_SIMPLE = [
    ('latin_text("<NARRATION_PLACEHOLDER_{pi}>", font_size={fs}, color={c})', '{obj}.move_to(ORIGIN)\n            clamp_to_screen({obj})'),
    ('formula_box("<NARRATION_PLACEHOLDER_{pi}>", color={c})', '{obj}.move_to(ORIGIN)'),
    ('latin_text("<NARRATION_PLACEHOLDER_{pi}>", font_size={fs}, color={c})', '{obj}.move_to(UP*0.5)\n            clamp_to_screen({obj})'),
]
# Extra visual additions per block
EXTRAS = [
    '',
    '\n            dot = glow_dot({obj}.get_corner(UR), color={ac})\n            self.play(FadeIn(dot, scale=4), run_time=tracker.duration*0.1)',
    '\n            playful_bounce(self, {obj})',
    '\n            ul = Line({obj}.get_left(), {obj}.get_right(), color={ac}, stroke_width=3)\n            ul.next_to({obj}, DOWN, buff=0.15)\n            self.play(Create(ul), run_time=tracker.duration*0.15)',
]

# Complex visual patterns for variety
COMPLEX_BLOCKS = []

def _axes_curve(func_str, label, curve_color, idx):
    return f'''            axes = branded_axes([-4,4,1],[-2,3,1]).scale(0.6)
            axes.move_to(DOWN*0.2)
            self.play(Create(axes), run_time=tracker.duration*0.25)
            import math
            curve = axes.plot(lambda x: {func_str}, x_range=[-3.5,3.5], color={curve_color}, stroke_width=3)
            lbl = latin_text("{label}", font_size=FONT_SIZE_CAPTION, color={curve_color})
            lbl.next_to(axes, UP, buff=0.1)
            clamp_to_screen(lbl)
            self.play(Create(curve), FadeIn(lbl), run_time=tracker.duration*0.45)
            self.play(Indicate(curve, color=STAR_YELLOW), run_time=tracker.duration*0.2)'''

def _vt_numberline(start, end, color):
    return f'''            nl = NumberLine(x_range=[{start},{end},1], length=8, color=AXIS_COLOR,
                           include_numbers=True, font_size=FONT_SIZE_CAPTION)
            nl.move_to(DOWN*0.5)
            t = ValueTracker({start})
            marker = always_redraw(lambda: Triangle(fill_color={color}, fill_opacity=1,
                stroke_width=0).scale(0.15).next_to(nl.n2p(t.get_value()), UP, buff=0.08))
            val_lbl = always_redraw(lambda: latin_text(f"{{t.get_value():.1f}}",
                font_size=FONT_SIZE_CAPTION, color={color}).next_to(nl.n2p(t.get_value()), UP, buff=0.35))
            self.play(Create(nl), run_time=tracker.duration*0.2)
            self.add(marker, val_lbl)
            self.play(t.animate.set_value({end}), run_time=tracker.duration*0.6, rate_func=smooth)
            self.wait(tracker.duration*0.1)'''

def _shape_morph(shape1, shape2, col1, col2):
    return f'''            s1 = {shape1}(color={col1}, fill_opacity=0.15, stroke_width=3)
            s1.move_to(LEFT*2)
            s2 = {shape2}(color={col2}, fill_opacity=0.15, stroke_width=3)
            s2.move_to(RIGHT*2)
            self.play(Create(s1), run_time=tracker.duration*0.25)
            self.play(ReplacementTransform(s1.copy(), s2), run_time=tracker.duration*0.45)
            self.play(Indicate(s2, color=STAR_YELLOW), run_time=tracker.duration*0.2)'''

def _vector_diagram(angle_expr, color):
    return f'''            axes = branded_axes([-3,3,1],[-3,3,1]).scale(0.55)
            axes.move_to(ORIGIN)
            self.play(Create(axes), run_time=tracker.duration*0.2)
            angle_t = ValueTracker(0)
            vec = always_redraw(lambda: Arrow(
                axes.c2p(0,0), axes.c2p(2*np.cos({angle_expr}), 2*np.sin({angle_expr})),
                buff=0, color={color}, stroke_width=5, max_tip_length_to_length_ratio=0.15))
            self.add(vec)
            self.play(angle_t.animate.set_value(PI), run_time=tracker.duration*0.55, rate_func=smooth)
            self.play(Indicate(vec, color=STAR_YELLOW), run_time=tracker.duration*0.15)'''

def _side_by_side(left_txt, right_txt, lcol, rcol):
    return f'''            div = DashedLine(UP*2.5, DOWN*2.5, color=MUTED_COLOR, stroke_width=1.5)
            lt = latin_text("{left_txt}", font_size=FONT_SIZE_LABEL, color={lcol})
            lt.move_to(LEFT*3)
            clamp_to_screen(lt)
            rt = latin_text("{right_txt}", font_size=FONT_SIZE_LABEL, color={rcol})
            rt.move_to(RIGHT*3)
            clamp_to_screen(rt)
            self.play(Create(div), run_time=tracker.duration*0.15)
            self.play(FadeIn(lt, shift=LEFT*0.2), run_time=tracker.duration*0.25)
            self.play(FadeIn(rt, shift=RIGHT*0.2), run_time=tracker.duration*0.25)
            arr = Arrow(lt.get_right(), rt.get_left(), buff=0.3, color=STAR_YELLOW, stroke_width=3)
            self.play(GrowArrow(arr), run_time=tracker.duration*0.2)'''

def _bar_chart(n_bars, color):
    return f'''            bars = VGroup()
            for i in range({n_bars}):
                h = 0.3 + random.random()*2.0
                bar = Rectangle(width=0.6, height=h, fill_color={color},
                    fill_opacity=0.5+i*0.05, stroke_color={color}, stroke_width=2)
                bar.move_to(LEFT*{(n_bars-1)*0.45}+RIGHT*i*0.9+UP*(h/2-1))
                bars.add(bar)
            self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.06),
                     run_time=tracker.duration*0.55)
            mean_line = DashedLine(LEFT*{n_bars*0.5}, RIGHT*{n_bars*0.5}, color=STAR_YELLOW, stroke_width=2)
            mean_line.move_to(UP*0.3)
            self.play(Create(mean_line), run_time=tracker.duration*0.2)'''

def _concentric_rings(n, color):
    return f'''            rings = VGroup()
            for r in [0.4*i for i in range(1,{n}+1)]:
                ring = Circle(radius=r, color={color}, stroke_width=1.5, stroke_opacity=0.3+r*0.1)
                rings.add(ring)
            self.play(LaggedStart(*[Create(r) for r in rings], lag_ratio=0.06),
                     run_time=tracker.duration*0.5)
            center_dot = glow_dot(ORIGIN, color=STAR_YELLOW)
            self.play(FadeIn(center_dot, scale=5), run_time=tracker.duration*0.2)
            self.play(Indicate(rings[-1], color=STAR_YELLOW), run_time=tracker.duration*0.2)'''

FUNCTIONS = [
    ("x**2*0.2", "y = 0.2x²"),
    ("math.sin(x)", "y = sin(x)"),
    ("math.cos(x)", "y = cos(x)"),
    ("math.exp(x*0.3)", "y = e^(0.3x)"),
    ("x**3*0.05", "y = 0.05x³"),
    ("abs(x)", "y = |x|"),
    ("2/(1+math.exp(-x))-1", "sigmoid"),
    ("math.sin(x*2)*0.8", "y = 0.8sin(2x)"),
    ("x*0.5+0.5", "y = 0.5x+0.5"),
    ("math.log(abs(x)+1)", "y = ln(|x|+1)"),
]
SHAPES = ["Circle","Square","Triangle","RegularPolygon"]

random.seed(42)  # reproducible

def make_simple_template(idx, doc, block1_code, block2_code):
    return f'''"""
Template {idx:03d} — {doc}
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:
{block1_code}

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_1>") as tracker:
{block2_code}

        self.wait(0.5)
'''

def make_3block_template(idx, doc, b1, b2, b3):
    return f'''"""
Template {idx:03d} — {doc}
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:
{b1}

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_1>") as tracker:
{b2}

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_2>") as tracker:
{b3}

        self.wait(0.5)
'''

def text_block(placeholder_i, color, font, anim_style, accent_col, extra_idx):
    obj_code, pos_code = OBJECTS_SIMPLE[placeholder_i % len(OBJECTS_SIMPLE)]
    c = color
    obj_code = obj_code.replace("{c}", c).replace("{fs}", font).replace("{pi}", str(placeholder_i))
    pos_code = pos_code.replace("{obj}", "obj")
    anim = ANIMS_IN[anim_style % len(ANIMS_IN)].replace("{obj}", "obj")
    accent = ANIMS_ACCENT[placeholder_i % len(ANIMS_ACCENT)].replace("{obj}", "obj").replace("{col}", accent_col)
    extra = EXTRAS[extra_idx % len(EXTRAS)].replace("{obj}", "obj").replace("{ac}", accent_col)
    return f'''            obj = {obj_code}
            {pos_code}
            self.play({anim}, run_time=tracker.duration*0.5)
            self.play({accent}, run_time=tracker.duration*0.3){extra}
            self.wait(tracker.duration*0.1)'''

def formula_reveal_block(color, accent):
    return f'''            fb = formula_box("<NARRATION_PLACEHOLDER_0>", color={color})
            fb.move_to(ORIGIN)
            self.play(FadeIn(fb, scale=0.5), run_time=tracker.duration*0.45)
            self.play(Circumscribe(fb, color={accent}, time_width=2), run_time=tracker.duration*0.35)
            dot = glow_dot(fb.get_corner(UR), color={accent})
            self.play(FadeIn(dot, scale=4), run_time=tracker.duration*0.15)'''

# ── Generate templates ───────────────────────────────────────────────────────

count = 42  # start after existing 42

# Category A: Curve plots (80 templates)
for func_str, label in FUNCTIONS:
    for curve_col in COLORS[:5]:
        for accent in ACCENTS[:2]:
            count += 1
            b1 = _axes_curve(func_str, label, curve_col, count)
            b2 = formula_reveal_block(curve_col, accent)
            t = make_simple_template(count, f"CURVE PLOT: {label} with {curve_col}", b1, b2)
            with open(os.path.join(OUT, f"template_{count:03d}.py"), "w") as f:
                f.write(t)

# Category B: NumberLine ValueTracker (40 templates)
for start, end in [(-5,5),(-10,10),(0,20),(0,100),(-3,3)]:
    for col in COLORS[:5]:
        for accent in ACCENTS[:2]:
            count += 1
            # clamp to prevent too many
            if count > 192: break
            b1 = _vt_numberline(start, end, col)
            b2 = text_block(1, col, "FONT_SIZE_BODY", count, accent, count)
            t = make_simple_template(count, f"NUMBER LINE: [{start},{end}] {col}", b1, b2)
            with open(os.path.join(OUT, f"template_{count:03d}.py"), "w") as f:
                f.write(t)
        if count > 192: break
    if count > 192: break

# Category C: Shape morphs (40 templates)
for s1 in SHAPES:
    for s2 in SHAPES:
        if s1 == s2: continue
        for c1, c2 in [(COLORS[0],COLORS[1]),(COLORS[1],COLORS[0]),(COLORS[4],COLORS[0])]:
            count += 1
            if count > 232: break
            b1 = _shape_morph(s1, s2, c1, c2)
            b2 = formula_reveal_block(c1, c2)
            t = make_simple_template(count, f"MORPH: {s1}→{s2}", b1, b2)
            with open(os.path.join(OUT, f"template_{count:03d}.py"), "w") as f:
                f.write(t)
        if count > 232: break
    if count > 232: break

# Category D: Vector diagrams (30 templates)
for angle_expr in ["angle_t.get_value()","angle_t.get_value()*2","angle_t.get_value()+PI/4"]:
    for col in COLORS[:5]:
        count += 1
        if count > 262: break
        b1 = _vector_diagram(angle_expr, col)
        b2 = text_block(1, col, "FONT_SIZE_BODY", count, "STAR_YELLOW", count)
        t = make_simple_template(count, f"VECTOR: angle={angle_expr[:15]} {col}", b1, b2)
        with open(os.path.join(OUT, f"template_{count:03d}.py"), "w") as f:
            f.write(t)
    if count > 262: break

# Category E: Side-by-side (30 templates)
pairs = [("Before","After"),("Cause","Effect"),("Simple","Complex"),("Input","Output"),
         ("Old","New"),("Hypothesis","Result"),("Theory","Practice")]
for lt, rt in pairs:
    for lc, rc in [(COLORS[0],COLORS[1]),(COLORS[1],COLORS[4]),(COLORS[5],COLORS[0])]:
        count += 1
        if count > 292: break
        b1 = _side_by_side(lt, rt, lc, rc)
        b2 = formula_reveal_block(lc, rc)
        t = make_simple_template(count, f"COMPARE: {lt} vs {rt}", b1, b2)
        with open(os.path.join(OUT, f"template_{count:03d}.py"), "w") as f:
            f.write(t)
    if count > 292: break

# Category F: Bar charts (30 templates)
for n_bars in [4,5,6,7,8]:
    for col in COLORS[:4]:
        count += 1
        if count > 322: break
        b1 = _bar_chart(n_bars, col)
        b2 = text_block(1, col, "FONT_SIZE_BODY", count, "STAR_YELLOW", count)
        t = make_simple_template(count, f"BAR CHART: {n_bars} bars {col}", b1, b2)
        with open(os.path.join(OUT, f"template_{count:03d}.py"), "w") as f:
            f.write(t)
    if count > 322: break

# Category G: Concentric rings (20 templates)
for n in [4,5,6,7]:
    for col in COLORS[:4]:
        count += 1
        if count > 342: break
        b1 = _concentric_rings(n, col)
        b2 = formula_reveal_block(col, "STAR_YELLOW")
        t = make_simple_template(count, f"RINGS: {n} rings {col}", b1, b2)
        with open(os.path.join(OUT, f"template_{count:03d}.py"), "w") as f:
            f.write(t)
    if count > 342: break

# Category H: Text-only with varied animations (80 templates)
for ci, color in enumerate(COLORS):
    for fi, font in enumerate(FONTS):
        for ai in range(len(ANIMS_IN)):
            for ei in range(len(EXTRAS)):
                count += 1
                if count > 422: break
                b1 = text_block(0, color, font, ai, ACCENTS[ci%len(ACCENTS)], ei)
                b2 = text_block(1, ACCENTS[ci%len(ACCENTS)], "FONT_SIZE_BODY", (ai+2)%len(ANIMS_IN), color, (ei+1)%len(EXTRAS))
                t = make_simple_template(count, f"TEXT: {color} {font} anim{ai} extra{ei}", b1, b2)
                with open(os.path.join(OUT, f"template_{count:03d}.py"), "w") as f:
                    f.write(t)
            if count > 422: break
        if count > 422: break
    if count > 422: break

# Category I: 3-block deep-dive (80 templates) – hook + concept + formula
for func_str, label in FUNCTIONS[:8]:
    for col in COLORS[:5]:
        for accent in ACCENTS[:2]:
            count += 1
            if count > 502: break
            b1 = text_block(0, col, "FONT_SIZE_HEADER", count%len(ANIMS_IN), accent, count%len(EXTRAS))
            b2 = _axes_curve(func_str, label, col, count)
            b3 = formula_reveal_block(col, accent)
            t = make_3block_template(count, f"DEEP DIVE: {label} {col}", b1, b2, b3)
            with open(os.path.join(OUT, f"template_{count:03d}.py"), "w") as f:
                f.write(t)
        if count > 502: break
    if count > 502: break

print(f"Generated {count - 42} new templates (total: {count})")
