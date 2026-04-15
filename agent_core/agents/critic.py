"""
agents/critic.py — Self-Healing Critic Agent

Executes Manim code in a sandboxed subprocess. On failure, extracts the
traceback and returns it to the orchestrator for re-routing to the
Manim Coder for self-healing.

On success, returns the path to the rendered preview video.
"""

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import VENV_MANIM, MANIM_ENV_PATCH, MAX_CRITIC_RETRIES
from agents.manim_coder import MMS_SERVICE_HEADER


def _build_env() -> dict:
    """Build the subprocess environment with all required Manim paths."""
    env = os.environ.copy()
    env.update(MANIM_ENV_PATCH)
    return env


def _extract_scene_names(code: str) -> list[str]:
    """Parse class names from the generated Python code."""
    return re.findall(r"^class\s+(\w+)\s*\(", code, re.MULTILINE)


def _find_rendered_video(output_folder: str, scene_name: str, quality: str) -> str | None:
    """Locate the rendered MP4 produced by Manim."""
    # Manim puts output at: <output_folder>/videos/<script_stem>/480p15/<SceneName>.mp4
    for root, _, files in os.walk(output_folder):
        for f in files:
            if f.endswith(".mp4") and scene_name in f:
                return os.path.join(root, f)
    return None


def run_critic(
    code_classes: list[str],
    output_folder: str,
    retry_count: int = 0,
) -> dict:
    """
    Write code to a temp file, run Manim -ql (low quality, fast), and
    return success/failure + error text or preview path.

    Args:
        code_classes:   List of Python class strings from manim_coder.
        output_folder:  Where to write the script and media output.
        retry_count:    Current retry iteration (for logging).

    Returns:
        {"success": True,  "preview_path": str}
        {"success": False, "error": str}
    """
    os.makedirs(output_folder, exist_ok=True)

    # Assemble the full script: header + all scene classes
    full_script = MMS_SERVICE_HEADER + "\n\n" + "\n\n".join(code_classes)
    script_path = os.path.join(output_folder, "generated_lesson.py")

    with open(script_path, "w", encoding="utf-8") as f:
        f.write(full_script)

    # Only render the FIRST scene class for the preview (fastest feedback loop)
    scene_names = _extract_scene_names(full_script)
    if not scene_names:
        return {
            "success": False,
            "error": "No class definitions found in generated code. The LLM returned non-class output.",
        }

    first_scene = scene_names[0]
    env = _build_env()

    cmd = [
        VENV_MANIM,
        "-ql",                  # low quality — fast preview
        "--disable_caching",
        "--media_dir", output_folder,
        script_path,
        first_scene,
    ]

    print(
        f"  [critic] Attempt {retry_count + 1}/{MAX_CRITIC_RETRIES + 1} — "
        f"rendering {first_scene} (low quality)…",
        flush=True,
    )

    try:
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            timeout=300,
        )
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Manim rendering timed out after 5 minutes."}
    except FileNotFoundError:
        return {
            "success": False,
            "error": f"Manim binary not found at {VENV_MANIM}. Run rebuild_venv.sh.",
        }

    combined_output = (result.stdout or "") + (result.stderr or "")

    if result.returncode != 0:
        # Extract the traceback for the self-healer
        error_text = _extract_traceback(combined_output) or combined_output[-2000:]
        print(f"  [critic] FAILED. Traceback:\n{error_text[:400]}", flush=True)
        return {"success": False, "error": error_text}

    # Success — find the rendered file
    preview_path = _find_rendered_video(output_folder, first_scene, "480p15")
    if not preview_path:
        # Manim succeeded but we couldn't locate the file — still a soft success
        preview_path = output_folder

    print(f"  [critic] SUCCESS → {preview_path}", flush=True)
    return {"success": True, "preview_path": preview_path}


def run_final_render(
    output_folder: str,
    orientation: str = "landscape",
) -> dict:
    """
    Re-render ALL scene classes in high quality (1080p60 or 1080x1920).

    Called separately after user approves the preview.
    """
    script_path = os.path.join(output_folder, "generated_lesson.py")
    if not os.path.exists(script_path):
        return {"success": False, "error": "generated_lesson.py not found. Run preview first."}

    with open(script_path, encoding="utf-8") as f:
        content = f.read()

    scene_names = _extract_scene_names(content)
    if not scene_names:
        return {"success": False, "error": "No scene classes found."}

    env    = _build_env()
    res_flag = ["--resolution", "1080,1920"] if orientation == "portrait" else []

    rendered_paths = []
    for scene in scene_names:
        cmd = [
            VENV_MANIM,
            "-qh",              # high quality
            "--disable_caching",
            *res_flag,
            "--media_dir", output_folder,
            script_path,
            scene,
        ]
        print(f"  [critic-final] Rendering {scene} (high quality)…", flush=True)
        result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=600)
        if result.returncode != 0:
            return {"success": False, "error": result.stderr[-1500:]}
        path = _find_rendered_video(output_folder, scene, "1080p60")
        if path:
            rendered_paths.append(path)

    return {"success": True, "rendered_paths": rendered_paths}


def _extract_traceback(output: str) -> str:
    """Pull just the Python traceback lines from Manim's verbose output."""
    lines    = output.splitlines()
    tb_start = None
    for i, line in enumerate(lines):
        if "Traceback (most recent call last)" in line or "Error:" in line:
            tb_start = i
            break
    if tb_start is not None:
        return "\n".join(lines[tb_start:tb_start + 60])
    return output[-1500:]
