"""
agents/template_orchestrator.py — Massive Library Template Orchestrator (v7)
=============================================================================
500+ pre-made templates. TF-IDF cosine similarity matching.
No on-the-fly generation. Pure library-based selection.
"""

import os, re, glob, random, math, json, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from logger import get_logger

log = get_logger("template_orchestrator")

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TEMPLATE_DIR = os.path.join(PROJECT_ROOT, "manim_templates", "3b1b_style")


# ── TF-IDF Index ─────────────────────────────────────────────────────────────

def _tokenize(text: str) -> list[str]:
    return re.findall(r'[a-z0-9]+', text.lower())


def _build_index():
    """Build TF-IDF index from ALL template docstrings at import time."""
    templates = sorted(glob.glob(os.path.join(TEMPLATE_DIR, "template_*.py")))
    docs = {}
    df = {}
    for path in templates:
        name = os.path.basename(path).replace(".py", "")
        try:
            with open(path, "r", encoding="utf-8") as f:
                head = f.read(500)
            # Extract docstring
            m = re.search(r'"""(.*?)"""', head, re.DOTALL)
            desc = m.group(1).strip() if m else name
        except Exception:
            desc = name
        tokens = _tokenize(desc)
        docs[name] = (tokens, path)
        for t in set(tokens):
            df[t] = df.get(t, 0) + 1

    N = len(docs)
    vectors = {}
    for name, (tokens, path) in docs.items():
        tf = {}
        for t in tokens:
            tf[t] = tf.get(t, 0) + 1
        vec = {}
        for t, count in tf.items():
            idf = math.log(N / (1 + df.get(t, 0)))
            vec[t] = (count / max(len(tokens), 1)) * idf
        vectors[name] = (vec, path)

    return vectors, N


_INDEX, _N_TEMPLATES = _build_index()
log.info(f"TF-IDF index built: {_N_TEMPLATES} templates")


def _cosine(v1: dict, v2: dict) -> float:
    common = set(v1) & set(v2)
    if not common:
        return 0.0
    dot = sum(v1[k] * v2[k] for k in common)
    m1 = math.sqrt(sum(x * x for x in v1.values()))
    m2 = math.sqrt(sum(x * x for x in v2.values()))
    return dot / (m1 * m2) if m1 and m2 else 0.0


def _semantic_match(scene: dict, used: set, top_k: int = 8) -> list[str]:
    """Rank all templates by TF-IDF cosine similarity to scene content."""
    query = " ".join([
        scene.get("concept", ""),
        scene.get("scene_name", ""),
        scene.get("explanation", ""),
        scene.get("visual", ""),
        scene.get("manim_visual_instructions", ""),
        " ".join(scene.get("sentences", [])[:3]),
        scene.get("worked_example", ""),
        json.dumps(scene.get("storyboard_plan", {}))[:200],
    ]).lower()
    tokens = _tokenize(query)
    if not tokens:
        return []
    tf = {}
    for t in tokens:
        tf[t] = tf.get(t, 0) + 1
    qvec = {}
    for t, c in tf.items():
        qvec[t] = (c / len(tokens)) * math.log(_N_TEMPLATES / 2)

    scores = []
    for name, (vec, path) in _INDEX.items():
        if name in used:
            continue
        scores.append((_cosine(qvec, vec), name))
    scores.sort(reverse=True)
    return [n for _, n in scores[:top_k]]


# ── Template selection ────────────────────────────────────────────────────────

def _pick_template(scene: dict, used: set, all_paths: list[str]) -> str:
    """Context-aware selection: storyboard hint → TF-IDF → random unused."""
    plan = scene.get("storyboard_plan", {})
    rec = plan.get("recommended_template", "")
    if rec:
        full = os.path.join(TEMPLATE_DIR, f"{rec}.py")
        if os.path.exists(full) and rec not in used:
            return full

    matches = _semantic_match(scene, used)
    for m in matches:
        full = os.path.join(TEMPLATE_DIR, f"{m}.py")
        if os.path.exists(full):
            return full

    fresh = [t for t in all_paths if os.path.basename(t).replace(".py","") not in used]
    return random.choice(fresh) if fresh else random.choice(all_paths)


# ── Sync/overflow fix ─────────────────────────────────────────────────────────

def _fix_sync(code: str) -> str:
    for iw, ic in [(" {8}", " {12}"), (" {4}", " {8}")]:
        for q in ['"', "'"]:
            pat = rf'({iw})(with self\.voiceover\(text={q}[^{q}]*{q}\) as tracker:\n)\s{ic}self\.clear\(\)\n'
            code = re.sub(pat, r'\1self.clear()\n\1\2', code)
    return code


# ── Narration injection ──────────────────────────────────────────────────────

def _inject(code: str, scene: dict, name: str) -> str:
    code = re.sub(r'class SceneTemplate\b', f'class {name}', code)
    sentences = scene.get("sentences", scene.get("sentences_english", []))
    if not sentences:
        c = scene.get("concept", "Physics")
        sentences = [f"Let's explore {c}.", f"The key idea behind {c} is elegant.", "And that's the beautiful insight."]
    for i, s in enumerate(sentences):
        safe = s.replace('"', "'").replace("\\", "\\\\")
        code = code.replace(f"<NARRATION_PLACEHOLDER_{i}>", safe)
        code = code.replace("<NARRATION_PLACEHOLDER>", safe, 1)
    code = re.sub(r'<NARRATION_PLACEHOLDER_\d+>', "This concept is fascinating.", code)
    code = re.sub(r'<NARRATION_PLACEHOLDER>', "This concept is fascinating.", code)
    return code


# ── Public API ────────────────────────────────────────────────────────────────

def run_template_orchestrator(scenes: list[dict], mode: str = "3b1b") -> list[str]:
    """Select from 500+ pre-made templates using TF-IDF matching."""
    all_templates = sorted(glob.glob(os.path.join(TEMPLATE_DIR, "template_*.py")))
    if not all_templates:
        return [_fallback(s) for s in scenes]

    log.info(f"Orchestrator v7: {len(scenes)} scenes, {len(all_templates)} templates, TF-IDF matching")

    generated = []
    used = set()

    # Silent intro for first scene
    first = (scenes[0].get("scene_name","") + scenes[0].get("concept","")).lower()
    if any(k in first for k in ["intro","hook","scene_1","scene1"]):
        silent = os.path.join(TEMPLATE_DIR, "template_32.py")
        if os.path.exists(silent):
            try:
                with open(silent) as f:
                    code = f.read()
                code = _inject(code, scenes[0], "SilentIntro")
                code = _fix_sync(code)
                generated.append(code)
                used.add("template_32")
                log.info("Scene 0: SilentIntro → template_32.py")
            except Exception:
                pass

    for idx, scene in enumerate(scenes):
        sn = re.sub(r'[^A-Za-z0-9_]', '_', scene.get("scene_name", f"Scene{idx}"))
        if not sn[0].isalpha():
            sn = "S_" + sn

        selected = _pick_template(scene, used, all_templates)
        tname = os.path.basename(selected).replace(".py", "")
        used.add(tname)
        # Keep used set manageable — only block last 6
        if len(used) > 6:
            used = set(list(used)[-6:])

        try:
            with open(selected) as f:
                code = f.read()
            code = _inject(code, scene, sn)
            code = _fix_sync(code)
            generated.append(code)
            log.info(f"Scene {idx+1}: {sn} → {tname}")
        except Exception as e:
            log.error(f"Failed {sn}: {e}")
            generated.append(_fallback(scene))

    return generated


def _fallback(scene: dict) -> str:
    name = re.sub(r'[^A-Za-z0-9_]', '_', scene.get("scene_name", "Fallback"))
    if not name[0].isalpha():
        name = "S_" + name
    concept = scene.get("concept", "Physics").replace('"', "'")
    sentences = scene.get("sentences", [f"Let's explore {concept}."])
    blocks = []
    for s in sentences:
        ss = s.replace('"', "'").replace("\\", "\\\\")
        blocks.append(f'''        self.clear()
        with self.voiceover(text="{ss}") as tracker:
            t = latin_text("{concept[:28]}", font_size=FONT_SIZE_BODY, color=TEAL_ACCENT)
            if t.width > 10.5:
                t.scale_to_fit_width(10.5)
            t.move_to(ORIGIN)
            self.play(FadeIn(t, shift=UP*0.25), run_time=tracker.duration*0.55)
            self.wait(tracker.duration*0.45)''')
    return f'''class {name}(AmharicEduScene):
    def construct(self):
        setup_scene(self)
{chr(10).join(blocks)}
        self.wait(0.5)
'''
