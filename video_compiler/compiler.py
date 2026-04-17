"""
video_compiler/compiler.py — Parallel Manim Renderer & FFmpeg Muxer

Replaces legacy sequential AST builder. Executes Manim -qh concurrently
for all approved scenes, then concatenates them into Masterpiece.mp4.
"""

import os
import subprocess
import glob
from concurrent.futures import ThreadPoolExecutor, as_completed

# Try to use config if available, otherwise fallback
import sys
agent_core_path = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(agent_core_path, "agent_core"))
try:
    from config import VENV_MANIM, MANIM_ENV_PATCH
except ImportError:
    VENV_MANIM = "/tmp/stem_venv/bin/manim"
    MANIM_ENV_PATCH = {}

def _build_env() -> dict:
    env = os.environ.copy()
    env.update(MANIM_ENV_PATCH)
    return env

def _find_file(output_folder: str, scene_name: str, ext: str) -> str | None:
    for root, _, files in os.walk(output_folder):
        for f in files:
            if f.endswith(ext) and scene_name in f:
                return os.path.join(root, f)
    return None

def _run_single_manim(scene: str, script_path: str, output_folder: str, res_flag: list, env: dict) -> dict:
    cmd = [VENV_MANIM, "-qh", "--disable_caching", *res_flag, "--media_dir", output_folder, script_path, scene]
    print(f"  [compiler-parallel] Rendering {scene} (4K)…", flush=True)
    result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=900)
    if result.returncode != 0:
        return {"success": False, "scene": scene, "error": result.stderr[-1500:]}
    path = _find_file(output_folder, scene, ".mp4")
    return {"success": True, "scene": scene, "path": path}

def run_final_render_parallel(output_folder: str, orientation: str = "landscape", scene_names: list[str] = None) -> dict:
    """Re-render ALL scene classes in HIGH QUALITY parallelly, then concat with FFmpeg."""
    script_path = os.path.join(output_folder, "generated_lesson.py")
    if not os.path.exists(script_path):
        return {"success": False, "error": "generated_lesson.py not found. Run preview first."}

    # If scene names aren't passed, extract them
    if not scene_names:
        import re
        with open(script_path, encoding="utf-8") as f:
            content = f.read()
        scene_names = re.findall(r"^class\s+(\w+)\s*\([^)]*Scene[^)]*\):", content, re.MULTILINE)

    if not scene_names:
        return {"success": False, "error": "No scene classes found."}

    env = _build_env()
    res_flag = ["--resolution", "1080,1920"] if orientation == "portrait" else []

    rendered_paths = []
    # ── 1. Dispatch Parallel Render ──
    with ThreadPoolExecutor(max_workers=max(2, os.cpu_count() or 4)) as executor:
        futures = [
            executor.submit(_run_single_manim, scene, script_path, output_folder, res_flag, env)
            for scene in scene_names
        ]
        
        # Maintain order based on execution
        results = []
        for future in as_completed(futures):
            res = future.result()
            if not res["success"]:
                return {"success": False, "error": f"Scene {res['scene']} failed: {res['error']}"}
            results.append(res)
            
    # Guarantee chronological order for FFmpeg concat
    ordered_paths = []
    for s in scene_names:
        for r in results:
            if r["scene"] == s and r["path"]:
                ordered_paths.append(r["path"])

    if not ordered_paths:
        return {"success": False, "error": "No valid MP4 paths recovered from rendering."}

    # ── 2. FFmpeg Concatenation ──
    print("  [compiler-ffmpeg] Concatenating scenes into Masterpiece.mp4...", flush=True)
    list_path = os.path.join(output_folder, "concat_list.txt")
    with open(list_path, "w") as f:
        for p in ordered_paths:
            f.write(f"file '{p}'\n")
            
    master_v = os.path.join(output_folder, "Masterpiece.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_path,
        "-c", "copy", master_v
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    return {"success": True, "rendered_paths": ordered_paths, "master_path": master_v}
