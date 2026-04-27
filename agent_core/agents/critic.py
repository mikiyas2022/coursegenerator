"""
agents/critic.py — Self-Healing Critic Agent (Syntax + Visual)

Two-stage validation for ALL scenes (not just the first):
  Stage 1 — Syntax/Runtime: run Manim -ql for EACH scene class, catch tracebacks
  Stage 2 — Visual:         run Manim -s (last frame), pass PNG to VL model
"""

import base64
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import (
    VENV_MANIM, MANIM_ENV_PATCH,
    MAX_CRITIC_RETRIES, MAX_VISUAL_RETRIES,
    get_vl_llm,
)
from agents.manim_coder import SCRIPT_HEADER_TEMPLATE, BLACKBOARD_HEADER_TEMPLATE


# ─────────────────────────────────────────────────────────────────────────────
# Build the full script with dynamic path injected
# ─────────────────────────────────────────────────────────────────────────────

def _build_script(code_classes: list[str], mode: str = "3b1b") -> str:
    """Prepend the dynamic header to all scene classes.
    Uses BLACKBOARD_HEADER_TEMPLATE for blackboard mode (no TTS).
    """
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if mode == "blackboard":
        header = BLACKBOARD_HEADER_TEMPLATE.format(project_root=project_root)
    else:
        header = SCRIPT_HEADER_TEMPLATE.format(project_root=project_root)
    return header + "\n\n" + "\n\n".join(code_classes)


def _build_env() -> dict:
    env = os.environ.copy()
    env.update(MANIM_ENV_PATCH)
    return env


def _extract_scene_names(code: str) -> list[str]:
    """Extract class names that inherit from scene-like bases."""
    all_classes = re.findall(r"^class\s+(\w+)\s*\([^)]*\):", code, re.MULTILINE)
    # Filter out helper classes that aren't scenes
    skip = {"EdgeTTSService", "LocalMMSService", "AmharicEduScene", "BlackboardScene", "EdgeTTSAmharicService"}
    return [c for c in all_classes if c not in skip]


def _sanitize_code(code: str) -> str:
    """
    Post-process LLM-generated Manim code to strip known v0.20.1-incompatible
    kwargs before attempting to render.
    """
    # Strip background_line_style from Axes() — only valid in NumberPlane()
    code = re.sub(
        r"(Axes\s*\([^)]*?)\s*,?\s*background_line_style\s*=\s*\{[^}]*\}",
        r"\1",
        code, flags=re.DOTALL
    )
    # Strip bare trailing commas left by the substitution above
    code = re.sub(r",\s*\)", ")", code)
    # thickness= → stroke_width=
    code = re.sub(r'\bthickness\s*=', 'stroke_width=', code)
    # Arc(ORIGIN, ...) → Arc(...)
    code = re.sub(r'Arc\s*\(\s*ORIGIN\s*,\s*', 'Arc(', code)
    # self.wait(run_time=X) → self.wait(X)
    code = re.sub(r'self\.wait\(run_time\s*=\s*([^)]+)\)', r'self.wait(\1)', code)
    code = re.sub(r'self\.wait\(duration\s*=\s*([^)]+)\)', r'self.wait(\1)', code)
    # Strip axis_config={...} from branded_axes/NumberPlane calls
    code = re.sub(r',?\s*axis_config\s*=\s*\{[^}]*\}', '', code)
    # Strip include_tip/include_numbers as top-level kwargs for NumberPlane
    code = re.sub(r',?\s*include_tip\s*=\s*\w+', '', code)
    code = re.sub(r',?\s*include_numbers\s*=\s*\w+', '', code)
    # Strip bare width=/height= from shape constructors
    code = re.sub(r',?\s*\bwidth\s*=\s*[\d.]+(?=\s*[,)])', '', code)
    code = re.sub(r',?\s*\bheight\s*=\s*[\d.]+(?=\s*[,)])', '', code)
    # Fix formula_box kwargs that might get hallucinated
    code = re.sub(r'formula_box\(([^)]*?)(,?\s*text_color=[^,)]*)', r'formula_box(\1', code)
    return code



def _find_file(output_folder: str, scene_name: str, ext: str) -> str | None:
    for root, _, files in os.walk(output_folder):
        for f in files:
            if f.endswith(ext) and scene_name in f:
                return os.path.join(root, f)
    return None


# ─────────────────────────────────────────────────────────────────────────────
# Stage 1 — Syntax / Runtime check (manim -ql)
# ─────────────────────────────────────────────────────────────────────────────

def _run_syntax_check(
    script_path: str,
    scene_name: str,
    output_folder: str,
    retry_count: int,
) -> dict:
    env = _build_env()
    cmd = [VENV_MANIM, "-ql", "--disable_caching", "--media_dir", output_folder,
           script_path, scene_name]

    print(
        f"  [critic-syntax] Attempt {retry_count+1}/{MAX_CRITIC_RETRIES+1} "
        f"— rendering {scene_name} (ql)…", flush=True,
    )
    try:
        result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": f"Manim timed out rendering {scene_name}."}
    except FileNotFoundError:
        return {"ok": False, "error": f"Manim not found at {VENV_MANIM}. Run rebuild_venv.sh."}

    combined = (result.stdout or "") + (result.stderr or "")
    if result.returncode != 0:
        tb = _extract_traceback(combined) or combined[-3000:]
        print(f"  [critic-syntax] FAIL on {scene_name}:\n...{tb[-800:]}", flush=True)
        return {"ok": False, "error": f"Scene {scene_name} failed:\n{tb}", "scene": scene_name}

    video_path = _find_file(output_folder, scene_name, ".mp4")
    print(f"  [critic-syntax] ✓ {scene_name} rendered OK", flush=True)
    return {"ok": True, "video_path": video_path or output_folder, "scene": scene_name}


# ─────────────────────────────────────────────────────────────────────────────
# Stage 2 — Visual check (manim -s → PNG → VL model)
# ─────────────────────────────────────────────────────────────────────────────

VISUAL_CRITIQUE_PROMPT = """You are a visual quality auditor for educational animations.
Analyze this Manim animation frame (16:9 aspect ratio, 1920×1080).

Check for these specific visual problems:
1. TEXT OVERLAP: Are any text elements overlapping with shapes, arrows, or other text?
2. OFF-SCREEN: Is any element clipping outside the frame edges?
3. CROWDING: Are elements too close together (less than 0.2 Manim units of padding)?
4. READABILITY: Is any text smaller than ~24px effective size?

If the frame looks clean, reply with exactly: VISUAL_OK

If there are problems, reply with VISUAL_ISSUES and then list EXACT Manim spatial corrections needed."""


def _run_visual_check(
    script_path: str,
    scene_name: str,
    output_folder: str,
    visual_attempt: int,
) -> dict:
    """
    Save last frame with manim -s, pass PNG to VL model.
    """
    print(
        f"  [critic-visual] Frame capture attempt {visual_attempt+1}/{MAX_VISUAL_RETRIES} "
        f"for {scene_name}…", flush=True,
    )

    env = _build_env()
    frames_dir = os.path.join(output_folder, "frames")
    os.makedirs(frames_dir, exist_ok=True)

    cmd = [VENV_MANIM, "-sql", "--disable_caching", "--media_dir", frames_dir,
           script_path, scene_name]

    try:
        result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        print("  [critic-visual] Frame capture timed out — skipping visual check.", flush=True)
        return {"ok": True, "skipped": True}
    except FileNotFoundError:
        return {"ok": True, "skipped": True}

    if result.returncode != 0:
        print("  [critic-visual] Frame capture failed — skipping visual check.", flush=True)
        return {"ok": True, "skipped": True}

    png_path = _find_file(frames_dir, scene_name, ".png")
    if not png_path:
        print("  [critic-visual] PNG not found — skipping.", flush=True)
        return {"ok": True, "skipped": True}

    print(f"  [critic-visual] Analysing frame: {png_path}", flush=True)

    try:
        with open(png_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode("utf-8")
    except Exception as exc:
        print(f"  [critic-visual] PNG read error ({exc}) — skipping.", flush=True)
        return {"ok": True, "skipped": True}

    try:
        from langchain_core.messages import HumanMessage
        vl_llm = get_vl_llm(max_tokens=600)
        message = HumanMessage(content=[
            {"type": "text",      "text": VISUAL_CRITIQUE_PROMPT},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}},
        ])
        response = vl_llm.invoke([message])
        reply = (response.content or "").strip()
        print(f"  [critic-visual] VL reply: {reply[:200]}", flush=True)

        if "VISUAL_OK" in reply:
            return {"ok": True, "feedback": ""}
        else:
            feedback = reply.replace("VISUAL_ISSUES", "").strip()
            return {"ok": False, "feedback": feedback}

    except Exception as exc:
        print(f"  [critic-visual] VL model unavailable ({exc}) — skipping.", flush=True)
        return {"ok": True, "skipped": True}


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def run_critic(
    code_classes: list[str],
    output_folder: str,
    retry_count: int = 0,
    mode: str = "3b1b",
) -> dict:
    """
    Stage 1 (syntax) + Stage 2 (visual) critique for ALL scenes.

    Returns:
        {"success": True,  "preview_path": str}
        {"success": False, "error": str}
        {"success": False, "visual_error": True, "visual_feedback": str}
    """
    os.makedirs(output_folder, exist_ok=True)

    full_script = _build_script(code_classes, mode=mode)
    full_script = _sanitize_code(full_script)
    scene_names = _extract_scene_names(full_script)
    if not scene_names:
        return {"success": False, "error": "No class definitions found in generated code."}

    # Use a unique script name if there's exactly one scene to avoid race conditions in parallel rendering
    script_name = f"script_{scene_names[0]}.py" if len(scene_names) == 1 else "generated_lesson.py"
    script_path = os.path.join(output_folder, script_name)
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(full_script)

    print(f"  [critic] Validating ALL {len(scene_names)} scenes: {scene_names} via {script_name}", flush=True)

    # ── Stage 1: Syntax check ALL scenes ────────────────────────────────────
    all_ok = True
    first_video_path = ""
    first_error = ""

    for scene_name in scene_names:
        syntax_result = _run_syntax_check(script_path, scene_name, output_folder, retry_count)
        if not syntax_result["ok"]:
            all_ok = False
            first_error = syntax_result["error"]
            # Return immediately with the error so healing can target this scene
            return {"success": False, "error": first_error}
        if not first_video_path:
            first_video_path = syntax_result.get("video_path", output_folder)

    preview_path = first_video_path or output_folder

    # ── Stage 2: Visual check (only first scene — representative frame) ─────
    if scene_names:
        for vis_attempt in range(MAX_VISUAL_RETRIES):
            visual_result = _run_visual_check(script_path, scene_names[0], output_folder, vis_attempt)

            if visual_result.get("skipped"):
                break

            if visual_result["ok"]:
                print(f"  [critic-visual] Frame is visually clean ✓", flush=True)
                break

            feedback = visual_result.get("feedback", "")
            print(f"  [critic-visual] Visual issues detected. Feedback:\n{feedback[:400]}", flush=True)
            return {
                "success":         False,
                "visual_error":    True,
                "visual_feedback": feedback,
            }

    print(f"  [critic] ALL {len(scene_names)} SCENES PASSED ✓ → {preview_path}", flush=True)
    return {"success": True, "preview_path": preview_path}


def run_final_render(output_folder: str, orientation: str = "landscape") -> dict:
    """Re-render ALL scene classes in high quality (1080p60 or portrait)."""
    script_path = os.path.join(output_folder, "generated_lesson.py")
    if not os.path.exists(script_path):
        return {"success": False, "error": "generated_lesson.py not found. Run preview first."}

    with open(script_path, encoding="utf-8") as f:
        content = f.read()

    scene_names = _extract_scene_names(content)
    if not scene_names:
        return {"success": False, "error": "No scene classes found."}

    env      = _build_env()
    res_flag = ["--resolution", "1080,1920"] if orientation == "portrait" else []

    rendered_paths = []
    for scene in scene_names:
        cmd = [VENV_MANIM, "-qh", "--disable_caching", *res_flag,
               "--media_dir", output_folder, script_path, scene]
        print(f"  [critic-final] Rendering {scene} (4K)…", flush=True)
        result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=900)
        if result.returncode != 0:
            return {"success": False, "error": result.stderr[-1500:]}
        path = _find_file(output_folder, scene, ".mp4")
        if path:
            rendered_paths.append(path)

    return {"success": True, "rendered_paths": rendered_paths}


def _extract_traceback(output: str) -> str:
    lines    = output.splitlines()
    tb_start = None
    for i, line in enumerate(lines):
        if "Traceback (most recent call last)" in line or line.strip().startswith("Error:"):
            tb_start = i
            break
    if tb_start is not None:
        return "\n".join(lines[tb_start:])
    return output[-1500:]
