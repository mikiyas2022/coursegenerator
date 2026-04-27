"""
video_postprod/subtitles.py — Auto-generate SRT subtitle files from scene narration.

Creates both:
  - A separate .srt file for use with video players
  - The subtitle data needed for burned-in captions via FFmpeg
"""

import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "agent_core"))
try:
    from logger import get_logger
    log = get_logger("subtitles")
except ImportError:
    import logging
    log = logging.getLogger("subtitles")


def _seconds_to_srt_timestamp(seconds: float) -> str:
    """Convert float seconds to SRT timestamp: HH:MM:SS,mmm"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def generate_srt(scenes: list[dict], output_path: str, avg_words_per_second: float = 2.5) -> str:
    """
    Generate a .srt subtitle file from scene sentence data.

    Args:
        scenes: List of scene dicts with 'sentences' key
        output_path: Where to write the .srt file
        avg_words_per_second: TTS speaking rate estimate

    Returns:
        Path to the generated .srt file
    """
    srt_entries = []
    current_time = 0.0
    idx = 1

    for scene in scenes:
        sentences = scene.get("sentences", [])
        if not sentences and scene.get("amharic_script"):
            script = scene["amharic_script"]
            sentences = [s.strip() + "።" for s in script.split("།") if s.strip()]

        for sentence in sentences:
            # Estimate duration from word count
            word_count = max(len(sentence.split()), 3)
            duration = max(word_count / avg_words_per_second, 1.5)

            start = current_time
            end = current_time + duration

            # Clean up sentence for display
            display = sentence.strip()
            if len(display) > 80:
                # Wrap long lines
                words = display.split()
                mid = len(words) // 2
                display = " ".join(words[:mid]) + "\n" + " ".join(words[mid:])

            srt_entries.append(
                f"{idx}\n"
                f"{_seconds_to_srt_timestamp(start)} --> {_seconds_to_srt_timestamp(end)}\n"
                f"{display}\n"
            )
            idx += 1
            current_time = end + 0.2  # small gap between sentences

    srt_content = "\n".join(srt_entries)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(srt_content)

    log.info(f"Generated SRT with {len(srt_entries)} entries → {output_path}")
    return output_path


def generate_english_srt(scenes: list[dict], output_path: str) -> str:
    """Generate an English subtitle file from sentences_english field."""
    english_scenes = []
    for scene in scenes:
        en_sentences = scene.get("sentences_english", [])
        if en_sentences:
            english_scenes.append({**scene, "sentences": en_sentences})
        else:
            english_scenes.append(scene)
    return generate_srt(english_scenes, output_path)
