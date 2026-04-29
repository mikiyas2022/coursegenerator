#!/usr/bin/env python3
"""
Build 1000+ pre-made Manim templates. Run once: python3 scripts/build_templates.py
"""
import os, random, itertools

OUT = os.path.join(os.path.dirname(__file__), "..", "manim_templates", "3b1b_style")
os.makedirs(OUT, exist_ok=True)

COLORS = ["TEAL_ACCENT","STAR_YELLOW","VECTOR_COLOR","FORCE_COLOR","ROSE_COLOR","SUCCESS_COLOR","ERROR_COLOR"]
ACCENTS = ["STAR_YELLOW","TEAL_ACCENT","SUCCESS_COLOR"]
FONTS = ["FONT_SIZE_BODY","FONT_SIZE_LABEL","FONT_SIZE_HEADER"]
ANIMS_IN = [
    'FadeIn({obj}, shift=UP*0.3)','FadeIn({obj}, scale=0.5)','Write({obj})',
    'Create({obj})','FadeIn({obj}, shift=RIGHT*0.3)','FadeIn({obj}, shift=LEFT*0.3)',
    'FadeIn({obj}, shift=DOWN*0.2)',
]
ANIMS_ACCENT = [
    'Indicate({obj}, color={col})','Circumscribe({obj}, color={col}, time_width=2)',
    '{obj}.animate.set_color({col})',
]
EXTRAS = [
    '',
    '\n            dot = glow_dot({obj}.get_corner(UR), color={ac})\n            self.play(FadeIn(dot, scale=4), run_time=tracker.duration*0.1)',
    '\n            playful_bounce(self, {obj})',
    '\n            ul = Line({obj}.get_left(), {obj}.get_right(), color={ac}, stroke_width=3)\n            ul.next_to({obj}, DOWN, buff=0.15)\n            self.play(Create(ul), run_time=tracker.duration*0.15)',
]
FUNCTIONS = [
    ("x**2*0.2","y=0.2x²"),("math.sin(x)","y=sin(x)"),("math.cos(x)","y=cos(x)"),
    ("math.exp(x*0.3)","y=e^0.3x"),("x**3*0.05","y=0.05x³"),("abs(x)","y=|x|"),
    ("2/(1+math.exp(-x))-1","sigmoid"),("math.sin(x*2)*0.8","y=0.8sin2x"),
    ("x*0.5+0.5","y=0.5x+0.5"),("math.log(abs(x)+1)","y=ln|x|+1"),
    ("-x**2*0.15+2","inverted parabola"),("math.sin(x)*math.cos(x*0.5)","beat pattern"),
    ("math.tanh(x)","tanh"),("1/(1+x**2)","Lorentzian"),
]
SHAPES = ["Circle","Square","Triangle","RegularPolygon"]
PAIRS = [("Before","After"),("Cause","Effect"),("Simple","Complex"),("Input","Output"),
         ("Old","New"),("Hypothesis","Result"),("Theory","Practice"),("Question","Answer"),
         ("Problem","Solution"),("Start","End")]

random.seed(42)

def T2(idx, doc, b1, b2):
    return f'"""\nTemplate {idx:04d} — {doc}\n"""\nclass SceneTemplate(AmharicEduScene):\n    def construct(self):\n        setup_scene(self)\n\n        self.clear()\n        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:\n{b1}\n\n        self.clear()\n        with self.voiceover(text="<NARRATION_PLACEHOLDER_1>") as tracker:\n{b2}\n\n        self.wait(0.5)\n'

def T3(idx, doc, b1, b2, b3):
    return f'"""\nTemplate {idx:04d} — {doc}\n"""\nclass SceneTemplate(AmharicEduScene):\n    def construct(self):\n        setup_scene(self)\n\n        self.clear()\n        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:\n{b1}\n\n        self.clear()\n        with self.voiceover(text="<NARRATION_PLACEHOLDER_1>") as tracker:\n{b2}\n\n        self.clear()\n        with self.voiceover(text="<NARRATION_PLACEHOLDER_2>") as tracker:\n{b3}\n\n        self.wait(0.5)\n'

def txt(pi, c, fs, ai, ac, ei):
    a = ANIMS_IN[ai%len(ANIMS_IN)].replace("{obj}","obj")
    acc = ANIMS_ACCENT[pi%len(ANIMS_ACCENT)].replace("{obj}","obj").replace("{col}",ac)
    ex = EXTRAS[ei%len(EXTRAS)].replace("{obj}","obj").replace("{ac}",ac)
    return f'            obj = latin_text("<NARRATION_PLACEHOLDER_{pi}>", font_size={fs}, color={c})\n            obj.move_to(ORIGIN)\n            clamp_to_screen(obj)\n            self.play({a}, run_time=tracker.duration*0.5)\n            self.play({acc}, run_time=tracker.duration*0.3){ex}\n            self.wait(tracker.duration*0.1)'

def formula(c, ac):
    return f'            fb = formula_box("<NARRATION_PLACEHOLDER_0>", color={c})\n            fb.move_to(ORIGIN)\n            self.play(FadeIn(fb, scale=0.5), run_time=tracker.duration*0.45)\n            self.play(Circumscribe(fb, color={ac}, time_width=2), run_time=tracker.duration*0.35)\n            dot = glow_dot(fb.get_corner(UR), color={ac})\n            self.play(FadeIn(dot, scale=4), run_time=tracker.duration*0.15)'

def curve(fn, lbl, cc):
    return f'            axes = branded_axes([-4,4,1],[-2,3,1]).scale(0.6)\n            axes.move_to(DOWN*0.2)\n            self.play(Create(axes), run_time=tracker.duration*0.25)\n            import math\n            curve = axes.plot(lambda x: {fn}, x_range=[-3.5,3.5], color={cc}, stroke_width=3)\n            lbl = latin_text("{lbl}", font_size=FONT_SIZE_CAPTION, color={cc})\n            lbl.next_to(axes, UP, buff=0.1)\n            clamp_to_screen(lbl)\n            self.play(Create(curve), FadeIn(lbl), run_time=tracker.duration*0.45)\n            self.play(Indicate(curve, color=STAR_YELLOW), run_time=tracker.duration*0.2)'

def numline(s, e, c):
    return f'            nl = NumberLine(x_range=[{s},{e},1], length=8, color=AXIS_COLOR, include_numbers=True, font_size=FONT_SIZE_CAPTION)\n            nl.move_to(DOWN*0.5)\n            t = ValueTracker({s})\n            marker = always_redraw(lambda: Triangle(fill_color={c}, fill_opacity=1, stroke_width=0).scale(0.15).next_to(nl.n2p(t.get_value()), UP, buff=0.08))\n            val_lbl = always_redraw(lambda: latin_text(f"{{t.get_value():.1f}}", font_size=FONT_SIZE_CAPTION, color={c}).next_to(nl.n2p(t.get_value()), UP, buff=0.35))\n            self.play(Create(nl), run_time=tracker.duration*0.2)\n            self.add(marker, val_lbl)\n            self.play(t.animate.set_value({e}), run_time=tracker.duration*0.6, rate_func=smooth)\n            self.wait(tracker.duration*0.1)'

def morph(s1, s2, c1, c2):
    return f'            s1 = {s1}(color={c1}, fill_opacity=0.15, stroke_width=3)\n            s1.move_to(LEFT*2)\n            s2 = {s2}(color={c2}, fill_opacity=0.15, stroke_width=3)\n            s2.move_to(RIGHT*2)\n            self.play(Create(s1), run_time=tracker.duration*0.25)\n            self.play(ReplacementTransform(s1.copy(), s2), run_time=tracker.duration*0.45)\n            self.play(Indicate(s2, color=STAR_YELLOW), run_time=tracker.duration*0.2)'

def vec(expr, c):
    return f'            axes = branded_axes([-3,3,1],[-3,3,1]).scale(0.55)\n            axes.move_to(ORIGIN)\n            self.play(Create(axes), run_time=tracker.duration*0.2)\n            angle_t = ValueTracker(0)\n            vec = always_redraw(lambda: Arrow(axes.c2p(0,0), axes.c2p(2*np.cos({expr}), 2*np.sin({expr})), buff=0, color={c}, stroke_width=5, max_tip_length_to_length_ratio=0.15))\n            self.add(vec)\n            self.play(angle_t.animate.set_value(PI), run_time=tracker.duration*0.55, rate_func=smooth)\n            self.play(Indicate(vec, color=STAR_YELLOW), run_time=tracker.duration*0.15)'

def compare(lt, rt, lc, rc):
    return f'            div = DashedLine(UP*2.5, DOWN*2.5, color=MUTED_COLOR, stroke_width=1.5)\n            lt = latin_text("{lt}", font_size=FONT_SIZE_LABEL, color={lc})\n            lt.move_to(LEFT*3)\n            clamp_to_screen(lt)\n            rt = latin_text("{rt}", font_size=FONT_SIZE_LABEL, color={rc})\n            rt.move_to(RIGHT*3)\n            clamp_to_screen(rt)\n            self.play(Create(div), run_time=tracker.duration*0.15)\n            self.play(FadeIn(lt, shift=LEFT*0.2), run_time=tracker.duration*0.25)\n            self.play(FadeIn(rt, shift=RIGHT*0.2), run_time=tracker.duration*0.25)\n            arr = Arrow(lt.get_right(), rt.get_left(), buff=0.3, color=STAR_YELLOW, stroke_width=3)\n            self.play(GrowArrow(arr), run_time=tracker.duration*0.2)'

def bars(n, c):
    return f'            import random as _r\n            _r.seed({n*7})\n            bars = VGroup()\n            for i in range({n}):\n                h = 0.3+_r.random()*2.0\n                bar = Rectangle(width=0.6, height=h, fill_color={c}, fill_opacity=0.5+i*0.05, stroke_color={c}, stroke_width=2)\n                bar.move_to(LEFT*{(n-1)*0.45}+RIGHT*i*0.9+UP*(h/2-1))\n                bars.add(bar)\n            self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.06), run_time=tracker.duration*0.55)\n            mean_line = DashedLine(LEFT*{n*0.5}, RIGHT*{n*0.5}, color=STAR_YELLOW, stroke_width=2)\n            mean_line.move_to(UP*0.3)\n            self.play(Create(mean_line), run_time=tracker.duration*0.2)'

def rings(n, c):
    return f'            rings = VGroup()\n            for r in [0.4*i for i in range(1,{n}+1)]:\n                ring = Circle(radius=r, color={c}, stroke_width=1.5, stroke_opacity=0.3+r*0.1)\n                rings.add(ring)\n            self.play(LaggedStart(*[Create(r) for r in rings], lag_ratio=0.06), run_time=tracker.duration*0.5)\n            center_dot = glow_dot(ORIGIN, color=STAR_YELLOW)\n            self.play(FadeIn(center_dot, scale=5), run_time=tracker.duration*0.2)\n            self.play(Indicate(rings[-1], color=STAR_YELLOW), run_time=tracker.duration*0.2)'

def venn(c1, c2, cc):
    return f'            left_c = Circle(radius=1.5, color={c1}, fill_opacity=0.1, stroke_width=3).shift(LEFT*1)\n            right_c = Circle(radius=1.5, color={c2}, fill_opacity=0.1, stroke_width=3).shift(RIGHT*1)\n            self.play(Create(left_c), Create(right_c), run_time=tracker.duration*0.35)\n            inter = Intersection(left_c, right_c, fill_color={cc}, fill_opacity=0.3, stroke_width=0)\n            lbl = latin_text("A ∩ B", font_size=FONT_SIZE_SMALL, color={cc})\n            lbl.move_to(ORIGIN)\n            self.play(FadeIn(inter), Write(lbl), run_time=tracker.duration*0.35)\n            self.play(Indicate(lbl, color=STAR_YELLOW), run_time=tracker.duration*0.2)'

def steps(lines, c):
    code = f'            steps = {lines}\n            mobs = []\n            for i, s in enumerate(steps):\n                t = latin_text(s, font_size=FONT_SIZE_LABEL, color={c} if i<len(steps)-1 else STAR_YELLOW)\n                t.move_to(UP*(1.5-i*1.0))\n                clamp_to_screen(t)\n                mobs.append(t)\n            time_each = tracker.duration*0.2\n            for i, m in enumerate(mobs):\n                self.play(FadeIn(m, shift=RIGHT*0.3), run_time=time_each)\n                if i<len(mobs)-1:\n                    arr = Arrow(m.get_bottom(), mobs[i+1].get_top(), buff=0.1, color=MUTED_COLOR, stroke_width=2, max_tip_length_to_length_ratio=0.15)\n                    self.play(GrowArrow(arr), run_time=time_each*0.3)\n            self.play(Indicate(mobs[-1], color=STAR_YELLOW), run_time=tracker.duration*0.1)'
    return code

# ── GENERATE ─────────────────────────────────────────────────────────────────
count = 42  # start after hand-crafted

# A: Curve plots (14 funcs × 7 colors = 98)
for fn, lbl in FUNCTIONS:
    for cc in COLORS:
        count += 1
        with open(os.path.join(OUT, f"template_{count:04d}.py"), "w") as f:
            f.write(T2(count, f"CURVE: {lbl} {cc}", curve(fn, lbl, cc), formula(cc, "STAR_YELLOW")))

# B: NumberLine (5 ranges × 7 colors = 35)
for s, e in [(-5,5),(-10,10),(0,20),(0,50),(-3,3)]:
    for c in COLORS:
        count += 1
        with open(os.path.join(OUT, f"template_{count:04d}.py"), "w") as f:
            f.write(T2(count, f"NUMLINE: [{s},{e}] {c}", numline(s,e,c), txt(1,c,"FONT_SIZE_BODY",count,"STAR_YELLOW",count)))

# C: Shape morphs (4×3×5 = 60)
for s1, s2 in itertools.permutations(SHAPES, 2):
    for c1, c2 in [(COLORS[i], COLORS[(i+1)%len(COLORS)]) for i in range(5)]:
        count += 1
        with open(os.path.join(OUT, f"template_{count:04d}.py"), "w") as f:
            f.write(T2(count, f"MORPH: {s1}→{s2} {c1}", morph(s1,s2,c1,c2), formula(c1,c2)))

# D: Vectors (5 exprs × 7 colors = 35)
for expr in ["angle_t.get_value()","angle_t.get_value()*2","angle_t.get_value()+PI/4","angle_t.get_value()*0.5","angle_t.get_value()+PI/2"]:
    for c in COLORS:
        count += 1
        with open(os.path.join(OUT, f"template_{count:04d}.py"), "w") as f:
            f.write(T2(count, f"VECTOR: {expr[:12]} {c}", vec(expr,c), txt(1,c,"FONT_SIZE_BODY",count,"STAR_YELLOW",count)))

# E: Comparisons (10 pairs × 5 color combos = 50)
for lt, rt in PAIRS:
    for i in range(5):
        lc, rc = COLORS[i], COLORS[(i+2)%len(COLORS)]
        count += 1
        with open(os.path.join(OUT, f"template_{count:04d}.py"), "w") as f:
            f.write(T2(count, f"COMPARE: {lt} vs {rt} {lc}", compare(lt,rt,lc,rc), formula(lc,rc)))

# F: Bar charts (5 sizes × 7 colors = 35)
for n in [4,5,6,7,8]:
    for c in COLORS:
        count += 1
        with open(os.path.join(OUT, f"template_{count:04d}.py"), "w") as f:
            f.write(T2(count, f"BARS: {n}bars {c}", bars(n,c), txt(1,c,"FONT_SIZE_BODY",count,"STAR_YELLOW",count)))

# G: Rings (5 sizes × 7 colors = 35)
for n in [4,5,6,7,8]:
    for c in COLORS:
        count += 1
        with open(os.path.join(OUT, f"template_{count:04d}.py"), "w") as f:
            f.write(T2(count, f"RINGS: {n}rings {c}", rings(n,c), formula(c,"STAR_YELLOW")))

# H: Venn (7×6/2 = 21)
for i in range(len(COLORS)):
    for j in range(i+1, len(COLORS)):
        count += 1
        with open(os.path.join(OUT, f"template_{count:04d}.py"), "w") as f:
            f.write(T2(count, f"VENN: {COLORS[i]} {COLORS[j]}", venn(COLORS[i],COLORS[j],"SUCCESS_COLOR"), formula(COLORS[i],COLORS[j])))

# I: Step-solve (7 color variants × 3 step sets = 21)
STEP_SETS = [
    '["2x+4=10","2x=6","x=3"]',
    '["a²+b²=c²","a²=c²-b²","a=√(c²-b²)"]',
    '["F=ma","a=F/m","a=20/5=4"]',
]
for ss in STEP_SETS:
    for c in COLORS:
        count += 1
        with open(os.path.join(OUT, f"template_{count:04d}.py"), "w") as f:
            f.write(T2(count, f"STEPS: {c}", steps(ss,c), formula(c,"STAR_YELLOW")))

# J: Text combos (7col × 3font × 7anim = 147, take ~120)
for ci, c in enumerate(COLORS):
    for fi, fs in enumerate(FONTS):
        for ai in range(len(ANIMS_IN)):
            for ei in [0,1,2,3]:
                if count >= 999: break
                count += 1
                ac = ACCENTS[ci%len(ACCENTS)]
                with open(os.path.join(OUT, f"template_{count:04d}.py"), "w") as f:
                    f.write(T2(count, f"TEXT: {c} {fs} a{ai} e{ei}",
                        txt(0,c,fs,ai,ac,ei),
                        txt(1,ac,"FONT_SIZE_BODY",(ai+2)%len(ANIMS_IN),c,(ei+1)%len(EXTRAS))))
            if count >= 999: break
        if count >= 999: break
    if count >= 999: break

# K: 3-block deep dives to reach 1000+
for fn, lbl in FUNCTIONS:
    for c in COLORS[:3]:
        ac = ACCENTS[COLORS.index(c)%len(ACCENTS)] if c in COLORS else "STAR_YELLOW"
        count += 1
        with open(os.path.join(OUT, f"template_{count:04d}.py"), "w") as f:
            f.write(T3(count, f"DEEP: {lbl} {c}",
                txt(0,c,"FONT_SIZE_HEADER",count%len(ANIMS_IN),ac,count%len(EXTRAS)),
                curve(fn,lbl,c),
                formula(c,ac)))

print(f"Generated {count-42} new templates (total: {count})")
