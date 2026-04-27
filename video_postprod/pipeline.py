"""
video_postprod/pipeline.py — Post-Production Pipeline

After FFmpeg concatenation produces Masterpiece.mp4, this module:
  1. Burns in Amharic subtitles
  2. Adds intro/outro title cards (via FFmpeg drawtext)
  3. Normalizes audio volume
  4. Applies a subtle warm color grade (brightness/contrast)
  5. Outputs: {Topic_Name}_3B1B_Style.mp4

Graceful: if any step fails, the previous stage output is used.
"""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

# ── Logger ────────────────────────────────────────────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "agent_core"))
try:
    from logger import get_logger
    log = get_logger("postprod")
except ImportError:
    import logging
    log = logging.getLogger("postprod")

# ── FFmpeg discovery ──────────────────────────────────────────────────────────
def _find_ffmpeg() -> str:
    for candidate in ["/opt/homebrew/bin/ffmpeg", "/usr/local/bin/ffmpeg"]:
        if os.path.exists(candidate):
            return candidate
    found = shutil.which("ffmpeg")
    return found or "ffmpeg"


FFMPEG = _find_ffmpeg()


def _run_ffmpeg(args: list[str], timeout: int = 600) -> tuple[bool, str]:
    """Run an FFmpeg command. Returns (success, stderr)."""
    cmd = [FFMPEG, "-y"] + args
    log.info(f"FFmpeg: {' '.join(cmd[:6])}…")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if result.returncode != 0:
            return False, (result.stderr or "")[-1000:]
        return True, ""
    except subprocess.TimeoutExpired:
        return False, "FFmpeg timed out"
    except FileNotFoundError:
        return False, f"ffmpeg not found at {FFMPEG}"


def _safe_topic_name(topic: str) -> str:
    """Convert topic to a filesystem-safe filename fragment."""
    safe = re.sub(r"[^\w\s-]", "", topic).strip()
    safe = re.sub(r"\s+", "_", safe)
    return safe[:50] or "STEM_Topic"


# ─────────────────────────────────────────────────────────────────────────────
# Step 1: Audio normalization (loudnorm filter)
# ─────────────────────────────────────────────────────────────────────────────

def normalize_audio(input_path: str, output_path: str) -> bool:
    """Normalize audio to -14 LUFS (broadcast standard)."""
    ok, err = _run_ffmpeg([
        "-i", input_path,
        "-af", "loudnorm=I=-14:TP=-1:LRA=11",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        output_path,
    ])
    if not ok:
        log.warning(f"Audio normalization failed: {err[:200]}")
    return ok


# ─────────────────────────────────────────────────────────────────────────────
# Step 2: Subtitle burn-in (FFmpeg subtitles filter)
# ─────────────────────────────────────────────────────────────────────────────

def burn_subtitles(input_path: str, srt_path: str, output_path: str) -> bool:
    """Burn SRT subtitles into the video."""
    if not os.path.exists(srt_path):
        log.warning(f"SRT file not found: {srt_path}")
        return False

    # Escape path for ffmpeg filter syntax
    escaped_srt = srt_path.replace(":", "\\:").replace("'", "\\'")

    ok, err = _run_ffmpeg([
        "-i", input_path,
        "-vf", (
            f"subtitles='{escaped_srt}':force_style="
            "'FontName=Nyala,FontSize=22,PrimaryColour=&HFFFEF0,OutlineColour=&H001C1C2E,"
            "BorderStyle=1,Outline=2,Shadow=0,Alignment=2'"
        ),
        "-c:a", "copy",
        output_path,
    ], timeout=900)

    if not ok:
        log.warning(f"Subtitle burn-in failed: {err[:200]}")
    return ok


# ─────────────────────────────────────────────────────────────────────────────
# Step 3: Color grade (warm contrast — 3B1B look)
# ─────────────────────────────────────────────────────────────────────────────

def color_grade(input_path: str, output_path: str) -> bool:
    """
    Apply a subtle warm color grade:
    - Slight brightness boost (+0.05)
    - Contrast bump (+0.1)
    - Warm gamma (red slightly up, blue slightly down)
    """
    ok, err = _run_ffmpeg([
        "-i", input_path,
        "-vf", (
            "eq=brightness=0.05:contrast=1.10:saturation=1.05,"
            "colorbalance=rs=0.03:gs=0:bs=-0.03"
        ),
        "-c:a", "copy",
        "-preset", "fast",
        output_path,
    ])
    if not ok:
        log.warning(f"Color grade failed: {err[:200]}")
    return ok


# ─────────────────────────────────────────────────────────────────────────────
# Step 4: Add intro / outro title cards via drawtext
# ─────────────────────────────────────────────────────────────────────────────

def add_title_cards(input_path: str, output_path: str, topic: str) -> bool:
    """
    Add a simple intro title overlay (first 3 seconds) and series branding.
    Uses FFmpeg drawtext — no external video files required.
    """
    safe_topic = topic.replace("'", "'\\''")  # escape for shell

    # Title: first 3 seconds, large centered text
    # Series tag: bottom-left, small, throughout
    filter_complex = (
        f"drawtext=text='{safe_topic}':fontsize=48:fontcolor=0xFFD700:x=(w-text_w)/2:y=(h-text_h)/2"
        f":enable='between(t,0,3)':box=1:boxcolor=0x1C1C2E@0.7:boxborderw=20,"
        "drawtext=text='STEM AI Studio | Amharic 3B1B':fontsize=16:fontcolor=0x8892B0"
        ":x=20:y=h-40:enable='gt(t,0)'"
    )

    ok, err = _run_ffmpeg([
        "-i", input_path,
        "-vf", filter_complex,
        "-c:a", "copy",
        "-preset", "fast",
        output_path,
    ], timeout=900)

    if not ok:
        log.warning(f"Title cards failed: {err[:200]}")
    return ok


# ─────────────────────────────────────────────────────────────────────────────
# Main post-production orchestrator
# ─────────────────────────────────────────────────────────────────────────────

def run_postproduction(
    output_folder: str,
    topic: str,
    master_path: str = "",
    scenes: list[dict] | None = None,
    mode: str = "3b1b",
) -> dict:
    """
    Run the full post-production pipeline on a rendered Masterpiece.mp4.

    Steps:
      1. Normalize audio
      2. Burn in Amharic subtitles (if scenes provided)
      3. Apply warm color grade
      4. Add intro/outro title cards
      5. Output {Topic}_3B1B_Style.mp4

    Returns dict with 'final_video' path and 'steps_completed'.
    """
    folder = Path(output_folder)

    # Find master video
    if master_path and os.path.exists(master_path):
        source = master_path
    else:
        source = str(folder / "Masterpiece.mp4")
    if not os.path.exists(source):
        log.error(f"Source video not found: {source}")
        return {"success": False, "error": "Source video not found", "final_video": source}

    log.info(f"Post-production starting: {source} ({os.path.getsize(source) / 1e6:.1f} MB)")

    steps_completed = []
    current = source
    tmp_files = []

    def _tmp(suffix: str) -> str:
        p = str(folder / f"_pp_{suffix}.mp4")
        tmp_files.append(p)
        return p

    # ── Step 1: Audio normalization ───────────────────────────────────────────
    normed = _tmp("01_normed")
    if normalize_audio(current, normed):
        current = normed
        steps_completed.append("audio_normalization")
        log.info("✓ Audio normalized")
    else:
        log.warning("⚠ Audio normalization skipped")

    # ── Step 2: Subtitle burn-in ──────────────────────────────────────────────
    if scenes:
        from video_postprod.subtitles import generate_srt
        am_srt = str(folder / "subtitles_am.srt")
        generate_srt(scenes, am_srt)
        subbed = _tmp("02_subbed")
        if burn_subtitles(current, am_srt, subbed):
            current = subbed
            steps_completed.append("subtitle_burn")
            log.info("✓ Subtitles burned in")

            # Also generate English .srt alongside (not burned in)
            try:
                from video_postprod.subtitles import generate_english_srt
                en_srt = str(folder / "subtitles_en.srt")
                generate_english_srt(scenes, en_srt)
                steps_completed.append("english_srt")
            except Exception as exc:
                log.warning(f"English SRT: {exc}")
        else:
            log.warning("⚠ Subtitle burn skipped")

    # ── Step 3: Color grade ───────────────────────────────────────────────────
    graded = _tmp("03_graded")
    if color_grade(current, graded):
        current = graded
        steps_completed.append("color_grade")
        log.info("✓ Color graded")
    else:
        log.warning("⚠ Color grade skipped")

    # ── Step 4: Title cards ───────────────────────────────────────────────────
    titled = _tmp("04_titled")
    if add_title_cards(current, titled, topic):
        current = titled
        steps_completed.append("title_cards")
        log.info("✓ Title cards added")
    else:
        log.warning("⚠ Title cards skipped")

    # ── Final output ──────────────────────────────────────────────────────────
    safe_name = _safe_topic_name(topic)
    if mode == "blackboard":
        final_path = str(folder / f"{safe_name}_Blackboard_Solution.mp4")
    else:
        final_path = str(folder / f"{safe_name}_3B1B_Style.mp4")
    shutil.copy2(current, final_path)

    # Clean up temp files
    for tmp in tmp_files:
        try:
            if os.path.exists(tmp) and tmp != final_path:
                os.remove(tmp)
        except Exception:
            pass

    size_mb = os.path.getsize(final_path) / 1_048_576
    log.info(f"Post-production complete: {final_path} ({size_mb:.1f} MB)")
    log.info(f"Steps completed: {steps_completed}")

    return {
        "success": True,
        "final_video": final_path,
        "steps_completed": steps_completed,
        "size_mb": round(size_mb, 1),
    }
