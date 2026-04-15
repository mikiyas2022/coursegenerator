import sys
import json
import os
import subprocess
import wave
import struct
import numpy as np
from pathlib import Path

# Fix macOS Sandboxing HF cache issue globally
os.environ['HF_HOME'] = '/tmp/huggingface_cache'

sys.path.append('/tmp/stem_venv/lib/python3.11/site-packages')
sys.path.append('/tmp/stem_venv/lib/python3.13/site-packages')


# ════════════════════════════════════════════════════════════════════════════
# Voice Personas
# ════════════════════════════════════════════════════════════════════════════
# Edge-TTS Amharic voices: am-ET-MekdesNeural (Female), am-ET-AmehaNeural (Male)
# Personas are crafted via --rate (speech speed) and --pitch (voice pitch)
#   rate: -50% to +200%, pitch: -50Hz to +50Hz

VOICE_PERSONAS = {
    # ── Female Personas ──────────────────────────────────────────────────────
    "mekdes": {
        "label":       "👩‍🏫 Mekdes — The Warm Tutor (Default)",
        "description": "Intimate, warm, and encouraging. Feels like a trusted one-on-one tutor. Paces carefully so no student is left behind.",
        "voice":       "am-ET-MekdesNeural",
        "rate":        "-18%",
        "pitch":       "+0Hz",
        "gender":      "female",
    },
    "tigist": {
        "label":       "🎓 Tigist — The Confident Lecturer",
        "description": "Clear, authoritative, and crisp. Sounds like a confident university lecturer commanding the room.",
        "voice":       "am-ET-MekdesNeural",
        "rate":        "-5%",
        "pitch":       "-3Hz",
        "gender":      "female",
    },
    "selamawit": {
        "label":       "📖 Selamawit — The Patient Professor",
        "description": "Slow, deliberate, and methodical. Every word lands precisely — ideal for difficult derivations where students need time to absorb.",
        "voice":       "am-ET-MekdesNeural",
        "rate":        "-30%",
        "pitch":       "+4Hz",
        "gender":      "female",
    },
    # ── Male Personas ────────────────────────────────────────────────────────
    "ameha": {
        "label":       "👨‍🏫 Ameha — The Expert",
        "description": "Deep, professional, and authoritative. Like a senior scientist presenting at a national conference.",
        "voice":       "am-ET-AmehaNeural",
        "rate":        "-12%",
        "pitch":       "-2Hz",
        "gender":      "male",
    },
    "dawit": {
        "label":       "⚡ Dawit — The Energetic Coach",
        "description": "Upbeat, dynamic, and motivating. Turns dry physics into an exciting challenge. Students feel engaged and energised.",
        "voice":       "am-ET-AmehaNeural",
        "rate":        "+5%",
        "pitch":       "+5Hz",
        "gender":      "male",
    },
}

DEFAULT_PERSONA = "mekdes"


# ════════════════════════════════════════════════════════════════════════════
# Intro / transition timing constants (must match the Manim script exactly)
# ════════════════════════════════════════════════════════════════════════════
INTRO_DURATION  = 4.8   # Create(banner)=0.8 + scale+FadeIn=1.0 + Write+FadeIn=1.2 + wait=1.0 + FadeOut=0.8
PAN_DURATION    = 1.2   # camera.frame.animate.shift() between every scene


# ════════════════════════════════════════════════════════════════════════════
# Audio Utilities
# ════════════════════════════════════════════════════════════════════════════

def synthesize_amharic(text: str, out_wav: str, persona_key: str = DEFAULT_PERSONA):
    """Synthesise Amharic using Edge-TTS with the chosen voice persona."""
    persona  = VOICE_PERSONAS.get(persona_key, VOICE_PERSONAS[DEFAULT_PERSONA])
    edge_bin = '/tmp/stem_venv/bin/edge-tts'

    if os.path.exists(edge_bin):
        temp_mp3 = out_wav.replace('.wav', '_tmp.mp3')
        try:
            edge_cmd = [
                edge_bin,
                '--voice',  persona['voice'],
                '--rate',   persona['rate'],
                '--pitch',  persona['pitch'],
                '--text',   text,
                '--write-media', temp_mp3,
            ]
            subprocess.run(edge_cmd, check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            # Normalise to 16kHz mono WAV
            subprocess.run([
                '/opt/homebrew/bin/ffmpeg', '-y',
                '-i', temp_mp3, '-ar', '16000', '-ac', '1',
                out_wav
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if os.path.exists(temp_mp3):
                os.remove(temp_mp3)
            print(f"  [edge-tts][{persona['gender']}][{persona_key}] {out_wav}")
            return
        except Exception as e:
            print(f"  [edge-tts] Failed ({e}), falling back to MMS...")

    # ── Fallback: MMS ─────────────────────────────────────────────────────
    import torch
    from transformers import VitsModel, AutoTokenizer
    import scipy.io.wavfile

    model     = VitsModel.from_pretrained("facebook/mms-tts-amh")
    tokenizer = AutoTokenizer.from_pretrained("facebook/mms-tts-amh")
    inputs    = tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        waveform = model(**inputs).waveform.squeeze().cpu().numpy()
    scipy.io.wavfile.write(out_wav, rate=model.config.sampling_rate, data=waveform)
    print(f"  [mms-fallback] {out_wav}")


def make_silence_wav(duration_sec: float, out_path: str, sample_rate: int = 16000):
    """Write a silent WAV of exact duration."""
    n_frames = int(sample_rate * duration_sec)
    with wave.open(out_path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(b'\x00\x00' * n_frames)


def get_wav_duration(wav_path: str) -> float:
    try:
        with wave.open(wav_path, 'r') as wf:
            return wf.getnframes() / float(wf.getframerate())
    except Exception:
        return 3.0


def concatenate_wavs(wav_paths: list, out_path: str):
    """Concatenate multiple WAVs (all must be 16kHz mono) into one master track."""
    all_frames = []
    target_rate = 16000
    for p in wav_paths:
        tmp = p + '.cat.wav'
        subprocess.run([
            '/opt/homebrew/bin/ffmpeg', '-y', '-i', p,
            '-ar', str(target_rate), '-ac', '1', '-f', 'wav', tmp
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        with wave.open(tmp, 'rb') as wf:
            all_frames.append(wf.readframes(wf.getnframes()))
        os.remove(tmp)

    with wave.open(out_path, 'wb') as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(target_rate)
        out.writeframes(b''.join(all_frames))
    print(f"  [audio] Master audio -> {out_path}  ({sum(len(f) for f in all_frames)/(target_rate*2):.1f}s)")


def escape_latex(formula: str) -> str:
    formula = formula.strip()
    while formula.startswith('$') and formula.endswith('$') and len(formula) > 2:
        formula = formula[1:-1].strip()
    return formula


# ════════════════════════════════════════════════════════════════════════════
# Animation block builders
# Each builder must consume EXACTLY `duration` seconds of scene time
# ════════════════════════════════════════════════════════════════════════════

def block_text_reveal(obj_name, escaped, x_offset, duration):
    anim_t = max(min(duration * 0.85, duration - 0.1), 0.3)
    wait_t = max(duration - anim_t, 0.05)
    return f"""
        {obj_name} = MathTex(r"{escaped}", font_size=60, color=WHITE).shift(RIGHT * {x_offset})
        self.play(Write({obj_name}), run_time={anim_t:.3f}, rate_func=smooth)
        self.wait({wait_t:.3f})
"""


def block_formula_morph(obj_name, escaped, highlight_var, x_offset, duration, prev_obj_name):
    anim_t = max(min(duration * 0.85, duration - 0.1), 0.3)
    wait_t = max(duration - anim_t, 0.05)
    lines  = [f"""
        {obj_name} = MathTex(r"{escaped}", font_size=70).shift(RIGHT * {x_offset})"""]
    if highlight_var:
        lines.append(f'        {obj_name}.set_color_by_tex(r"{highlight_var}", YELLOW_C)')
    if prev_obj_name:
        lines.append(f"""        self.play(ReplacementTransform({prev_obj_name}.copy(), {obj_name}),
                  run_time={anim_t:.3f}, path_arc=np.pi / 4)""")
    else:
        lines.append(f"        self.play(Write({obj_name}), run_time={anim_t:.3f})")
    lines.append(f"        self.wait({wait_t:.3f})")
    return '\n'.join(lines)


def block_draw_2d_vector(obj_name, escaped, x_offset, duration):
    create_t = min(duration * 0.25, 1.0)
    grow_t   = max(duration - create_t - 0.2, 0.3)
    wait_t   = max(duration - create_t - grow_t, 0.05)
    return f"""
        plane_{obj_name}      = NumberPlane(background_line_style={{"stroke_opacity": 0.2}}).set_opacity(0.4).shift(RIGHT * {x_offset})
        vec_end_{obj_name}    = np.array([3 + {x_offset}, 2, 0])
        origin_pt_{obj_name}  = np.array([0 + {x_offset}, 0, 0])
        vector_{obj_name}     = Arrow(origin_pt_{obj_name}, vec_end_{obj_name}, buff=0, color=BLUE_D, stroke_width=8)
        vec_label_{obj_name}  = MathTex(r"{escaped}", color=YELLOW_C).next_to(vec_end_{obj_name}, UR, buff=0.2)
        {obj_name} = VGroup(plane_{obj_name}, vector_{obj_name}, vec_label_{obj_name})
        self.play(Create(plane_{obj_name}), run_time={create_t:.3f})
        self.play(GrowArrow(vector_{obj_name}), Write(vec_label_{obj_name}), run_time={grow_t:.3f}, rate_func=linear)
        self.wait({wait_t:.3f})
"""


def block_projectile_arc(obj_name, x_offset, duration):
    axis_t   = min(duration * 0.28, 1.5)
    move_t   = max(duration - axis_t - 0.2, 0.3)
    wait_t   = max(duration - axis_t - move_t, 0.05)
    return f"""
        axes_{obj_name}   = Axes(x_range=[0, 10, 1], y_range=[0, 6, 1], axis_config={{"include_tip": True, "stroke_opacity": 0.5}}).shift(RIGHT * {x_offset})
        labels_{obj_name} = axes_{obj_name}.get_axis_labels(x_label="x", y_label="y")
        path_{obj_name}   = axes_{obj_name}.plot(lambda x: -0.15*(x-5)**2 + 3.75, x_range=[0, 10], color=YELLOW_C)
        dot_{obj_name}    = Dot(color=RED_C).move_to(axes_{obj_name}.c2p(0, 0))
        tracer_{obj_name} = TracedPath(dot_{obj_name}.get_center, stroke_color=BLUE_B, stroke_width=4)
        {obj_name} = VGroup(axes_{obj_name}, labels_{obj_name}, tracer_{obj_name}, dot_{obj_name})
        self.add(axes_{obj_name}, labels_{obj_name}, tracer_{obj_name}, dot_{obj_name})
        self.play(Create(axes_{obj_name}), Write(labels_{obj_name}), run_time={axis_t:.3f})
        self.play(MoveAlongPath(dot_{obj_name}, path_{obj_name}), run_time={move_t:.3f}, rate_func=linear)
        self.wait({wait_t:.3f})
"""


def block_draw_base(obj_name, latex_formula, escaped, x_offset, duration):
    if r'\vec' in latex_formula or 'vec' in latex_formula.lower():
        create_t = min(duration * 0.28, 1.4)
        grow_t   = max(duration - create_t - 0.2, 0.3)
        wait_t   = max(duration - create_t - grow_t, 0.05)
        return f"""
        plane_{obj_name}     = NumberPlane(x_range=[-1, 8, 1], y_range=[-1, 5, 1],
            background_line_style={{"stroke_opacity": 0.15, "stroke_color": TEAL}}).set_opacity(0.3).shift(RIGHT * {x_offset})
        origin_{obj_name}    = plane_{obj_name}.c2p(0, 0)
        vec_end_{obj_name}   = plane_{obj_name}.c2p(4, 3)
        arrow_{obj_name}     = Arrow(origin_{obj_name}, vec_end_{obj_name}, buff=0, color=RED_C,
                                     stroke_width=8, max_tip_length_to_length_ratio=0.1)
        vec_label_{obj_name} = MathTex(r"{escaped}", color=YELLOW_C, font_size=60).next_to(vec_end_{obj_name}, UR, buff=0.2)
        {obj_name} = VGroup(plane_{obj_name}, arrow_{obj_name}, vec_label_{obj_name})
        self.play(Create(plane_{obj_name}), run_time={create_t:.3f})
        self.play(GrowArrow(arrow_{obj_name}), Write(vec_label_{obj_name}), run_time={grow_t:.3f}, rate_func=smooth)
        self.wait({wait_t:.3f})
"""
    else:
        axis_t  = min(duration * 0.5, 2.0)
        label_t = max(duration - axis_t - 0.2, 0.3)
        wait_t  = max(duration - axis_t - label_t, 0.05)
        return f"""
        axes_{obj_name}       = Axes(x_range=[0, 10, 1], y_range=[0, 6, 1],
            axis_config={{"include_tip": True, "stroke_color": WHITE, "stroke_width": 3}}).shift(RIGHT * {x_offset})
        ax_labels_{obj_name}  = axes_{obj_name}.get_axis_labels(x_label="x", y_label="y")
        base_label_{obj_name} = MathTex(r"{escaped}", color=YELLOW_C, font_size=52).next_to(axes_{obj_name}, UP, buff=0.3)
        {obj_name} = VGroup(axes_{obj_name}, ax_labels_{obj_name}, base_label_{obj_name})
        self.play(Create(axes_{obj_name}), Write(ax_labels_{obj_name}), run_time={axis_t:.3f})
        self.play(Write(base_label_{obj_name}), run_time={label_t:.3f}, rate_func=smooth)
        self.wait({wait_t:.3f})
"""


def block_write_text(obj_name, escaped, highlight_var, x_offset, duration, prev_formula_name):
    anim_t = max(min(duration * 0.85, duration - 0.1), 0.3)
    wait_t = max(duration - anim_t, 0.05)
    lines  = [f"""
        formula_{obj_name} = MathTex(r"{escaped}", font_size=70).shift(RIGHT * {x_offset})"""]
    if highlight_var:
        lines.append(f'        formula_{obj_name}.set_color_by_tex(r"{highlight_var}", YELLOW_C)')
    if prev_formula_name:
        lines.append(f"        self.play(TransformMatchingTex({prev_formula_name}.copy(), formula_{obj_name}), run_time={anim_t:.3f}, rate_func=smooth)")
    else:
        lines.append(f"        self.play(Write(formula_{obj_name}), run_time={anim_t:.3f}, rate_func=smooth)")
    lines.append(f"        self.wait({wait_t:.3f})")
    lines.append(f"        {obj_name} = formula_{obj_name}")
    return '\n'.join(lines)


def block_highlight_concept(obj_name, escaped, focus, x_offset, duration):
    write_t  = max(min(duration * 0.35, 1.5), 0.3)
    ind_t    = max(min(duration * 0.28, 1.2), 0.3)
    wiggle_t = max(min(duration * 0.2, 0.8), 0.2)
    wait_t   = max(duration - write_t - ind_t - wiggle_t, 0.05)
    return f"""
        hl_formula_{obj_name} = MathTex(r"{escaped}", font_size=70).shift(RIGHT * {x_offset})
        self.play(Write(hl_formula_{obj_name}), run_time={write_t:.3f}, rate_func=smooth)
        try:
            focus_part_{obj_name} = hl_formula_{obj_name}.get_part_by_tex(r"{focus}")
            self.play(Indicate(focus_part_{obj_name}, color=YELLOW, scale_factor=1.6), run_time={ind_t:.3f})
            self.play(Wiggle(focus_part_{obj_name}), run_time={wiggle_t:.3f})
        except Exception:
            self.play(Indicate(hl_formula_{obj_name}, color=RED_C, scale_factor=1.3), run_time={ind_t:.3f})
        self.wait({wait_t:.3f})
        {obj_name} = hl_formula_{obj_name}
"""


# ════════════════════════════════════════════════════════════════════════════
# Main pipeline
# ════════════════════════════════════════════════════════════════════════════

def generate_video(script_data_path, output_folder, orientation='landscape'):
    with open(script_data_path, 'r', encoding='utf-8') as f:
        script_data = json.load(f)

    orientation  = script_data.get('orientation', orientation)
    persona_key  = script_data.get('persona', DEFAULT_PERSONA)
    blocks       = script_data.get('blocks', [])
    title        = script_data.get('title', 'Lesson').replace('_', ' ')
    subject      = script_data.get('subject', 'STEM')
    grade        = script_data.get('grade', '')
    episode_number = script_data.get('episodeNumber', '1')

    persona = VOICE_PERSONAS.get(persona_key, VOICE_PERSONAS[DEFAULT_PERSONA])
    print(f"=== Voice Persona: {persona['label']} ===")

    # ── Phase 1: Synthesise all scene audio ───────────────────────────────
    print("=== Phase 1: Synthesising narration ===")
    scene_wavs = []
    durations  = []

    for i, block in enumerate(blocks):
        amharic_text = block.get('amharicText', '').strip() or "ምንም ዓይነት ንግግር አልተሰጠም"
        wav_path     = os.path.join(output_folder, f"scene_{i + 1}.wav")
        synthesize_amharic(amharic_text, wav_path, persona_key)
        scene_wavs.append(wav_path)
        durations.append(get_wav_duration(wav_path))
        print(f"  Scene {i+1}: {durations[-1]:.2f}s")

    # ── Phase 2: Build master audio with sync-accurate silence padding ────
    # Layout: [INTRO_SILENCE] [scene_1] [PAN_SILENCE] [scene_2] [PAN_SILENCE] ... [scene_N]
    print("=== Phase 2: Building sync-accurate master audio ===")
    padded_wavs = []

    # Intro silence
    intro_sil = os.path.join(output_folder, "sil_intro.wav")
    make_silence_wav(INTRO_DURATION, intro_sil)
    padded_wavs.append(intro_sil)

    for i, wav in enumerate(scene_wavs):
        padded_wavs.append(wav)
        # Camera pan silence between scenes (not after the last one)
        if i < len(scene_wavs) - 1:
            pan_sil = os.path.join(output_folder, f"sil_pan_{i}.wav")
            make_silence_wav(PAN_DURATION, pan_sil)
            padded_wavs.append(pan_sil)

    master_audio = os.path.join(output_folder, "master_audio.wav")
    concatenate_wavs(padded_wavs, master_audio)

    # ── Phase 3: Build Manim render script ───────────────────────────────
    print("=== Phase 3: Building render script ===")
    scene_lines = []
    scene_lines.append("""from manim import *
import numpy as np
import pydub
pydub.AudioSegment.converter = "/opt/homebrew/bin/ffmpeg"
pydub.utils.get_prober_name = lambda: "/opt/homebrew/bin/ffprobe"

class AutoLesson(MovingCameraScene):
    def construct(self):
        self.camera.background_color = "#141414"
        Text.set_default(font="Inter", weight=BOLD)
        MathTex.set_default(font_size=50)
        self.camera.frame.save_state()
""")

    # Single master audio add — fires at t=0
    scene_lines.append(f'        # Master audio (pre-padded with silence for sync)\n        self.add_sound(r"{master_audio}")')

    # Intro animation — must take exactly INTRO_DURATION seconds
    scene_lines.append(f"""
        # --- Intro ({INTRO_DURATION}s) ---
        banner       = Rectangle(width=10, height=0.1, color=BLUE_E, fill_opacity=1)
        title_main   = Text("{subject}", font_size=80, color=WHITE).shift(UP * 0.5)
        title_sub    = Text("Grade {grade} - Episode {episode_number}", font_size=40, color=GRAY_A).next_to(title_main, DOWN, buff=0.4)
        title_detail = Text("{title}", font_size=32, color=BLUE_B).next_to(title_sub, DOWN, buff=1.2)
        self.play(Create(banner), run_time=0.8)
        self.play(banner.animate.scale(0.1), FadeIn(title_main, shift=UP), run_time=1.0)
        self.play(Write(title_sub), FadeIn(title_detail, shift=DOWN), run_time=1.2)
        self.wait(1.0)
        self.play(FadeOut(VGroup(title_main, title_sub, title_detail, banner)), run_time=0.8)
        # Intro total: 0.8+1.0+1.2+1.0+0.8 = {INTRO_DURATION}s ✓
""".format(subject=subject, grade=grade, episode_number=episode_number, title=title))

    prev_obj_name     = None
    prev_formula_name = None

    for i, block in enumerate(blocks):
        anim_type     = block.get('animationType', 'Text Reveal')
        latex_formula = block.get('latexFormula', '').strip()
        highlight_var = block.get('highlightVar', '').strip()
        escaped       = escape_latex(latex_formula)
        duration      = durations[i]
        obj_name      = f"obj_{i}"
        x_offset      = i * 12

        # Camera pan between scenes — exactly PAN_DURATION seconds
        if prev_obj_name:
            scene_lines.append(
                f"        # Camera pan ({PAN_DURATION}s matches silence padding in master audio)\n"
                f"        self.play(self.camera.frame.animate.shift(RIGHT * 12), run_time={PAN_DURATION})"
            )

        scene_lines.append(f"        # --- Scene {i+1}: {anim_type} | audio={duration:.3f}s ---")

        if anim_type == "Text Reveal":
            code = block_text_reveal(obj_name, escaped, x_offset, duration)
            prev_obj_name = obj_name; prev_formula_name = None

        elif anim_type == "Formula Morph":
            code = block_formula_morph(obj_name, escaped, highlight_var, x_offset, duration, prev_obj_name)
            prev_obj_name = obj_name; prev_formula_name = None

        elif anim_type == "Draw 2D Vector":
            code = block_draw_2d_vector(obj_name, escaped, x_offset, duration)
            prev_obj_name = obj_name; prev_formula_name = None

        elif anim_type == "Projectile Arc":
            code = block_projectile_arc(obj_name, x_offset, duration)
            prev_obj_name = obj_name; prev_formula_name = None

        elif anim_type == "Draw Base":
            code = block_draw_base(obj_name, latex_formula, escaped, x_offset, duration)
            prev_obj_name = obj_name; prev_formula_name = None

        elif anim_type == "Write Text":
            code = block_write_text(obj_name, escaped, highlight_var, x_offset, duration, prev_formula_name)
            prev_obj_name = obj_name; prev_formula_name = f"formula_{obj_name}"

        elif anim_type == "Highlight Concept":
            focus = escape_latex(highlight_var) if highlight_var else escaped
            code  = block_highlight_concept(obj_name, escaped, focus, x_offset, duration)
            prev_obj_name = obj_name

        else:
            code = block_text_reveal(obj_name, escaped, x_offset, duration)
            prev_obj_name = obj_name; prev_formula_name = None

        scene_lines.append(code)

    # Outro
    last_offset = len(blocks) * 12
    scene_lines.append(f"""
        # --- Outro ---
        self.play(self.camera.frame.animate.shift(RIGHT * 12), run_time=1.0)
        final_box  = SurroundingRectangle(Text("EXCELLENCE IN STEM"), color=BLUE_E, buff=0.5).shift(RIGHT * {last_offset})
        final_text = Text("ለተመለከቱት እናመሰግናለን", font_size=50, color=WHITE).shift(RIGHT * {last_offset})
        self.play(Write(final_text), Create(final_box), run_time=2.0)
        self.wait(3.0)
""")

    render_script_path = os.path.join(output_folder, 'render.py')
    with open(render_script_path, 'w') as f:
        f.write('\n'.join(scene_lines))

    # ── Phase 4: Render with Manim ────────────────────────────────────────
    print(f"=== Phase 4: Rendering ({orientation}) ===")
    cwd = os.getcwd()
    os.chdir(output_folder)

    manim_env = os.environ.copy()
    manim_env['PATH'] = (
        f"/Library/TeX/texbin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:"
        f"{manim_env.get('PATH', '')}"
    )
    manim_env['LIBGS']     = '/opt/homebrew/lib/libgs.dylib'
    tex_dist = '/opt/homebrew/Cellar/texlive/20260301/share/texmf-dist'
    manim_env['TEXMFCNF']  = f'{tex_dist}/web2c'
    manim_env['TEXMFDIST'] = tex_dist
    manim_env['TEXMFMAIN'] = tex_dist

    if orientation == 'portrait':
        res_flag  = ['--resolution', '1080,1920']
        quality_dir = '1920p60'
    else:
        res_flag  = []
        quality_dir = '1080p60'

    manim_cmd = [
        '/tmp/stem_venv/bin/manim', '-pqh', '--disable_caching',
        *res_flag,
        render_script_path, 'AutoLesson', '--media_dir', output_folder
    ]
    subprocess.run(manim_cmd, check=True, env=manim_env)

    # ── Phase 5: Mux audio ────────────────────────────────────────────────
    final_dir       = os.path.join(output_folder, 'videos', 'render', quality_dir)
    video_path      = os.path.join(final_dir, 'AutoLesson.mp4')
    internal_audio  = os.path.join(final_dir, 'AutoLesson.wav')
    mux_audio       = internal_audio if os.path.exists(internal_audio) else master_audio
    temp_path       = os.path.join(final_dir, 'AutoLesson_Merged.mp4')

    if os.path.exists(mux_audio) and os.path.exists(video_path):
        print("=== Phase 5: Bonding audio to MP4 ===")
        subprocess.run([
            "/opt/homebrew/bin/ffmpeg", "-y",
            "-i", video_path, "-i", mux_audio,
            "-c:v", "copy", "-c:a", "aac",
            "-map", "0:v:0", "-map", "1:a:0",
            temp_path
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.replace(temp_path, video_path)
        print("  Done!")

    os.chdir(cwd)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit(1)
    _orientation = sys.argv[3] if len(sys.argv) > 3 else 'landscape'
    generate_video(sys.argv[1], sys.argv[2], _orientation)
