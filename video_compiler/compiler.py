"""
video_compiler/compiler.py — Sequential Manim Renderer & FFmpeg Muxer

Renders ALL approved scene classes in HIGH QUALITY sequentially
(parallel Manim runs conflict on the same machine), then concatenates
into a single production-ready Masterpiece.mp4.

Output folder structure:
  {output_folder}/
    generated_lesson.py          ← the multi-class Manim script
    scene_renders/               ← individual scene MP4s
      Scene1_Intro.mp4
      Scene2_Core.mp4
      ...
    Masterpiece.mp4              ← final merged video
"""

import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional, List

# ── Locate dependencies ───────────────────────────────────────────────────────
agent_core_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "agent_core")
sys.path.insert(0, agent_core_path)
try:
    from config import VENV_MANIM, MANIM_ENV_PATCH
except ImportError:
    VENV_MANIM      = "/tmp/stem_venv/bin/manim"
    MANIM_ENV_PATCH = {}

# FFmpeg — prefer homebrew, fall back to system PATH
FFMPEG = (
    "/opt/homebrew/bin/ffmpeg"
    if os.path.exists("/opt/homebrew/bin/ffmpeg")
    else "ffmpeg"
)


def _build_env() -> dict:
    env = os.environ.copy()
    env.update(MANIM_ENV_PATCH)
    # Ensure ffmpeg dir is in PATH so Manim's internal calls also find it
    ffmpeg_dir = os.path.dirname(FFMPEG)
    if ffmpeg_dir and ffmpeg_dir not in env.get("PATH", ""):
        env["PATH"] = ffmpeg_dir + ":" + env.get("PATH", "")
    return env


def _find_mp4(folder: str, scene_name: str) -> Optional[str]:
    """Walk the folder tree and find the MP4 belonging to scene_name."""
    for root, _, files in os.walk(folder):
        for f in sorted(files):
            if f.endswith(".mp4") and scene_name in f:
                return os.path.join(root, f)
    return None


def _extract_scene_names(script_content: str) -> list[str]:
    """Extract all class names regardless of base class name."""
    return re.findall(r"^class\s+(\w+)\s*\([^)]*\):", script_content, re.MULTILINE)


def _render_scene(
    scene_name: str,
    script_path: str,
    render_dir: str,
    resolution: str,
    env: dict,
) -> dict:
    """Render a single scene at high quality and return its MP4 path."""
    print(f"  [compiler] Rendering {scene_name}…", flush=True)

    cmd = [
        VENV_MANIM,
        "-qh",                   # high quality
        "--disable_caching",
        "--media_dir", render_dir,
    ]

    if resolution == "portrait":
        cmd += ["--resolution", "1080,1920"]
    # landscape is Manim's default 1920x1080 at -qh

    cmd += [script_path, scene_name]

    try:
        result = subprocess.run(
            cmd, env=env,
            capture_output=True, text=True,
            timeout=600,
        )
    except subprocess.TimeoutExpired:
        return {"ok": False, "scene": scene_name, "error": "Timed out after 10 min"}

    if result.returncode != 0:
        err = (result.stderr or "") + (result.stdout or "")
        return {"ok": False, "scene": scene_name, "error": err[-2000:]}

    mp4 = _find_mp4(render_dir, scene_name)
    if not mp4:
        return {"ok": False, "scene": scene_name, "error": "MP4 not found after render"}

    print(f"  [compiler] ✓ {scene_name} → {mp4}", flush=True)
    return {"ok": True, "scene": scene_name, "path": mp4}


def run_final_render_parallel(
    output_folder: str,
    orientation: str = "landscape",
    scene_names: Optional[List[str]] = None,
) -> dict:
    """
    Render ALL scenes in the generated_lesson.py sequentially (safe on single host),
    then merge into one production Masterpiece.mp4 via FFmpeg.
    """
    script_path = os.path.join(output_folder, "generated_lesson.py")
    if not os.path.exists(script_path):
        return {"success": False, "error": "generated_lesson.py not found. Run preview first."}

    with open(script_path, encoding="utf-8") as f:
        content = f.read()

    if not scene_names:
        scene_names = _extract_scene_names(content)

    if not scene_names:
        return {"success": False, "error": "No scene classes found in generated_lesson.py."}

    print(f"  [compiler] {len(scene_names)} scenes to render: {scene_names}", flush=True)

    env       = _build_env()
    render_dir = os.path.join(output_folder, "scene_renders")
    os.makedirs(render_dir, exist_ok=True)

    ordered_paths = []
    failed_scenes  = []

    # ── Sequential render — prevents Manim media-dir conflicts ──────────────
    for scene in scene_names:
        res = _render_scene(scene, script_path, render_dir, orientation, env)
        if res["ok"]:
            ordered_paths.append(res["path"])
        else:
            print(f"  [compiler] WARN: {scene} failed — {res['error'][-300:]}", flush=True)
            failed_scenes.append(scene)
            # Continue rendering remaining scenes; we'll build the video from what worked

    if not ordered_paths:
        return {
            "success": False,
            "error": f"All {len(scene_names)} scenes failed to render.\n"
                     + "\n".join(failed_scenes),
        }

    # ── FFmpeg concatenation ─────────────────────────────────────────────────
    print(f"  [compiler] Merging {len(ordered_paths)} scenes into Masterpiece.mp4…", flush=True)

    list_path  = os.path.join(output_folder, "concat_list.txt")
    master_path = os.path.join(output_folder, "Masterpiece.mp4")

    with open(list_path, "w") as f:
        for p in ordered_paths:
            # FFmpeg concat requires escaped single quotes in paths
            safe = p.replace("'", "'\\''")
            f.write(f"file '{safe}'\n")

    ffmpeg_cmd = [
        FFMPEG, "-y",
        "-f",    "concat",
        "-safe", "0",
        "-i",    list_path,
        "-c:v",  "libx264",     # re-encode to guarantee compatibility
        "-preset", "fast",
        "-crf",  "18",          # visually lossless
        "-c:a",  "aac",
        "-b:a",  "192k",
        master_path,
    ]

    try:
        result = subprocess.run(
            ffmpeg_cmd, env=env,
            capture_output=True, text=True,
            timeout=3600,
        )
        if result.returncode != 0:
            return {
                "success": False,
                "error": f"FFmpeg merge failed:\n{(result.stderr or '')[-1500:]}",
            }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "FFmpeg merge timed out (>60 min)"}
    except FileNotFoundError:
        return {"success": False, "error": f"ffmpeg not found at {FFMPEG}"}

    size_mb = os.path.getsize(master_path) / 1_048_576
    print(f"  [compiler] Masterpiece.mp4 ready ({size_mb:.1f} MB) → {master_path}", flush=True)

    return {
        "success":        True,
        "rendered_paths": ordered_paths,
        "failed_scenes":  failed_scenes,
        "master_path":    master_path,
        "size_mb":        round(size_mb, 1),
    }
