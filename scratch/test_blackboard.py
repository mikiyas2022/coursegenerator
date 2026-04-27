#!/usr/bin/env python3
"""
Test: Blackboard Q&A mode end-to-end (without needing the web server).
Generates a blackboard scene, renders it, confirms it's silent.
"""
import os, sys
project_root = "/Users/bin/Documents/Course:Exam Generator"
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "agent_core"))

from agents.template_orchestrator import run_template_orchestrator
from agents.critic import _build_script
from agents.manim_coder import BLACKBOARD_HEADER_TEMPLATE

# 1. Build scene dict (same as orchestrator would for blackboard mode)
scene = {
    "scene_name": "BB_Solution",
    "concept": "A wheel and axle has an effort arm of 40 cm and a load arm of 8 cm. What is the ideal mechanical advantage?",
    "topic": "A wheel and axle has an effort arm of 40 cm and a load arm of 8 cm. What is the ideal mechanical advantage?",
    "question": "A wheel and axle has an effort arm of 40 cm and a load arm of 8 cm. What is the ideal mechanical advantage?",
    "correct_answer": "IMA = 40/8 = 5",
    "answer": "IMA = 40/8 = 5",
    "subject_grade": "Physics Grade 12 EUEE 2025",
    "sentences": [],  # SILENT
}

# 2. Run template orchestrator in blackboard mode
print("=" * 60)
print("STEP 1: Template Orchestrator (blackboard mode)")
print("=" * 60)
code_classes = run_template_orchestrator(scenes=[scene], mode="blackboard")
print(f"Generated {len(code_classes)} classes")
print(code_classes[0][:500])
print("...")

# 3. Build the full script with blackboard header
print("\n" + "=" * 60)
print("STEP 2: Build full script with BLACKBOARD header (no TTS)")
print("=" * 60)
full_script = _build_script(code_classes, mode="blackboard")

# Verify no TTS imports
has_voiceover = "VoiceoverScene" in full_script
has_edgetts = "EdgeTTS" in full_script
has_blackboard = "BlackboardScene" in full_script
print(f"  VoiceoverScene in script: {has_voiceover}  (should be False)")
print(f"  EdgeTTS in script: {has_edgetts}  (should be False)")
print(f"  BlackboardScene in script: {has_blackboard}  (should be True)")

# 4. Write the script and render
output_folder = os.path.join(project_root, "Local_Video_Output", "blackboard_test")
os.makedirs(output_folder, exist_ok=True)
script_path = os.path.join(output_folder, "generated_lesson.py")
with open(script_path, "w") as f:
    f.write(full_script)
print(f"\n  Script written to: {script_path}")

# 5. Try rendering
print("\n" + "=" * 60)
print("STEP 3: Rendering with Manim (low quality for speed)")
print("=" * 60)
import subprocess
cmd = [
    "/tmp/stem_venv/bin/manim",
    "-ql",
    "--disable_caching",
    "--media_dir", output_folder,
    script_path,
    "BB_Solution",
]
result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
if result.returncode == 0:
    print("  ✅ RENDER SUCCESS!")
    # Find the output file
    for root, dirs, files in os.walk(output_folder):
        for f in files:
            if f.endswith(".mp4"):
                full = os.path.join(root, f)
                size = os.path.getsize(full) / 1024
                print(f"  → {full} ({size:.0f} KB)")
else:
    print("  ❌ RENDER FAILED!")
    print(result.stderr[-1000:])
