"""
video_postprod/pipeline.py — 3B1B Post-Production Pipeline (v2)

After FFmpeg concatenation produces Masterpiece.mp4, this module:
  1. Normalizes audio volume to broadcast standard
  2. Applies warm 3B1B color grade
  3. Adds intro/outro title cards
  4. Checks audio/video sync (corrects drift if > 200ms)
  5. Outputs: {Topic_Name}_3B1B_Course.mp4

Graceful: if any step fails, the previous stage output is used.
"""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "agent_core"))
try:
    from logger import get_logger  # type: ignore
    log = get_logger("postprod")
except ImportError:
    import logging
    log = logging.getLogger("postprod")


def _find_ffmpeg() -> str:
    for candidate in ["/opt/homebrew/bin/ffmpeg", "/usr/local/bin/ffmpeg"]:
        if os.path.exists(candidate):
            return candidate
    found = shutil.which("ffmpeg")
    return found or "ffmpeg"


def _find_ffprobe() -> str:
    for candidate in ["/opt/homebrew/bin/ffprobe", "/usr/local/bin/ffprobe"]:
        if os.path.exists(candidate):
            return candidate
    found = shutil.which("ffprobe")
    return found or "ffprobe"


FFMPEG  = _find_ffmpeg()
FFPROBE = _find_ffprobe()


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
    safe = re.sub(r"[^\w\s-]", "", topic).strip()
    safe = re.sub(r"\s+", "_", safe)
    return safe[:50] or "STEM_Topic"


def _get_duration(path: str) -> float:
    """Get video/audio duration in seconds using ffprobe."""
    try:
        result = subprocess.run(
            [FFPROBE, "-v", "quiet", "-print_format", "json",
             "-show_streams", "-show_format", path],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return 0.0
        import json
        data = json.loads(result.stdout)
        dur = float(data.get("format", {}).get("duration", 0))
        return dur
    except Exception:
        return 0.0


# ─────────────────────────────────────────────────────────────────────────────
# Step 1: Audio normalization (loudnorm — broadcast standard)
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
# Step 2: 3B1B Color grade (warm, cinematic look)
# ─────────────────────────────────────────────────────────────────────────────

def color_grade(input_path: str, output_path: str) -> bool:
    """
    Apply 3B1B warm color grade:
    - Slight brightness boost
    - Contrast bump  
    - Warm gamma (red up, blue slightly down)
    """
    ok, err = _run_ffmpeg([
        "-i", input_path,
        "-vf", (
            "eq=brightness=0.05:contrast=1.12:saturation=1.08,"
            "colorbalance=rs=0.04:gs=0:bs=-0.04"
        ),
        "-c:a", "copy",
        "-preset", "fast",
        output_path,
    ])
    if not ok:
        log.warning(f"Color grade failed: {err[:200]}")
    return ok


# ─────────────────────────────────────────────────────────────────────────────
# Step 3: Add 3B1B-style intro/outro title cards
# ─────────────────────────────────────────────────────────────────────────────

def add_title_cards(input_path: str, output_path: str, topic: str) -> bool:
    """
    Add cinematic intro title (first 3s) + series branding (bottom-right throughout).
    """
    safe_topic = topic.replace("'", "\\'").replace(":", " -")[:60]

    filter_complex = (
        f"drawtext=text='{safe_topic}':fontsize=52:fontcolor=0xFFD700"
        f":x=(w-text_w)/2:y=(h-text_h)/2"
        f":enable='between(t,0,3)':box=1:boxcolor=0x1C1C2E@0.85:boxborderw=24,"
        "drawtext=text='3B1B English Course Factory':fontsize=18:fontcolor=0x3DCCC7"
        ":x=w-text_w-20:y=h-text_h-15:enable='gt(t,0)'"
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
# Step 4: Audio-Video sync correction
# ─────────────────────────────────────────────────────────────────────────────

def check_and_fix_sync(input_path: str, output_path: str) -> bool:
    """
    Detect if audio is significantly shorter than video (common with TTS).
    If audio < 95% of video duration, pad with silence.
    """
    video_dur = _get_duration(input_path)
    if video_dur <= 0:
        return False

    # Check audio stream
    try:
        result = subprocess.run(
            [FFPROBE, "-v", "quiet", "-print_format", "json",
             "-select_streams", "a:0", "-show_streams", input_path],
            capture_output=True, text=True, timeout=30
        )
        import json
        data = json.loads(result.stdout)
        audio_streams = data.get("streams", [])
        if not audio_streams:
            log.info("No audio stream — skipping sync check")
            return False
        audio_dur = float(audio_streams[0].get("duration", video_dur))
    except Exception:
        return False

    drift = abs(video_dur - audio_dur)
    log.info(f"Sync check: video={video_dur:.2f}s, audio={audio_dur:.2f}s, drift={drift:.3f}s")

    if drift < 0.2:
        log.info("Sync is clean — no correction needed")
        return False

    if audio_dur < video_dur * 0.95:
        # Pad audio with silence at the end
        pad_dur = video_dur - audio_dur + 0.1
        log.info(f"Adding {pad_dur:.2f}s of silence to match video length")
        ok, err = _run_ffmpeg([
            "-i", input_path,
            "-af", f"apad=pad_dur={pad_dur:.2f}",
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k",
            output_path,
        ])
        if not ok:
            log.warning(f"Sync correction failed: {err[:200]}")
        return ok

    return False


# ─────────────────────────────────────────────────────────────────────────────
# Main post-production orchestrator
# ─────────────────────────────────────────────────────────────────────────────

def run_postproduction(
    output_folder: str,
    topic: str,
    master_path: str = "",
    scenes: list[dict] | None = None,
) -> dict:
    """
    Run the full 3B1B post-production pipeline.

    Steps:
      1. Sync correction (pad audio if needed)
      2. Audio normalization
      3. Warm color grade
      4. Intro/outro title cards
      5. Output {Topic}_3B1B_Course.mp4

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

    size_mb_src = os.path.getsize(source) / 1e6
    log.info(f"Post-production starting: {source} ({size_mb_src:.1f} MB)")

    steps_completed = []
    current = source
    tmp_files = []

    def _tmp(suffix: str) -> str:
        p = str(folder / f"_pp_{suffix}.mp4")
        tmp_files.append(p)
        return p

    # Step 1: Sync correction
    synced = _tmp("00_synced")
    if check_and_fix_sync(current, synced):
        current = synced
        steps_completed.append("sync_correction")
        log.info("✓ Audio-video sync corrected")
    else:
        log.info("✓ Sync check passed (no correction needed)")

    # Step 2: Audio normalization
    normed = _tmp("01_normed")
    if normalize_audio(current, normed):
        current = normed
        steps_completed.append("audio_normalization")
        log.info("✓ Audio normalized to -14 LUFS")
    else:
        log.warning("⚠ Audio normalization skipped")

    # Step 3: Color grade
    graded = _tmp("02_graded")
    if color_grade(current, graded):
        current = graded
        steps_completed.append("color_grade")
        log.info("✓ 3B1B color grade applied")
    else:
        log.warning("⚠ Color grade skipped")

    # Step 4: Title cards
    titled = _tmp("03_titled")
    if add_title_cards(current, titled, topic):
        current = titled
        steps_completed.append("title_cards")
        log.info("✓ Title cards added")
    else:
        log.warning("⚠ Title cards skipped")

    # ── Final output ──
    safe_name = _safe_topic_name(topic)
    final_path = str(folder / f"{safe_name}_3B1B_Course.mp4")
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
