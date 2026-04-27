# STEM AI Studio — Autonomous Amharic 3B1B Video Generator

> **Zero-touch** production of Grant Sanderson–quality educational videos in Amharic (Ge'ez script) from any STEM topic.

---

## ⚡ One-Command Demo

```bash
./demo_3b1b.sh "Why does gravity feel like acceleration?"
```

This generates a complete, polished Amharic video in the style of 3Blue1Brown — fully automatically.

---

## 🏗️ Architecture

```
Topic Input
    │
    ▼
┌─────────────────┐
│   Researcher    │  ← Structures topic into 4-6 pedagogical scene beats (llama3.1)
└────────┬────────┘
         ▼
┌─────────────────┐
│  Scriptwriter   │  ← Writes rich Amharic narration (8-12 sentences/scene, humor + aha! moments)
└────────┬────────┘
         ▼
┌─────────────────┐
│ Visual Designer │  ← Creates 3B1B storyboard: metaphors, morphs, camera moves, humor beats ← NEW
└────────┬────────┘
         ▼
┌─────────────────┐
│ Math Verifier   │  ← SymPy checks all LaTeX formulas (graceful, never blocks) ← NEW
└────────┬────────┘
         ▼
┌─────────────────────────────────────────┐
│  Manim Coder (parallel, per scene)      │  ← Generates 3B1B-style ManimCE v0.20.1 code
│  + Critic Auto-Healing Loop             │  ← Syntax check + VL visual check + self-heal
└────────┬────────────────────────────────┘
         ▼
┌─────────────────┐
│  FFmpeg Concat  │  ← Merges scene renders into Masterpiece.mp4
└────────┬────────┘
         ▼
┌─────────────────────────────────────────┐
│  Post-Production (video_postprod/)      │  ← NEW ← NEW ← NEW
│  • Audio normalization (-14 LUFS)       │
│  • Amharic subtitle burn-in (.srt)      │
│  • Warm color grade (3B1B look)         │
│  • Title cards & series branding        │
│  Output: {Topic}_3B1B_Style.mp4         │
└─────────────────────────────────────────┘
```

---

## 🎨 How it Achieves 3B1B Quality

### 1. Visual Designer Agent
Before any Manim code is written, a dedicated **Visual Designer Agent** creates a rich storyboard plan per scene:
- **Metaphor chain**: which everyday object represents the concept
- **Morph sequence**: which shapes transform into what (and why)
- **Camera choreography**: zoom-in moments, pans, restores
- **Humor beats**: bouncing numbers, surprised reveals, playful micro-animations
- **Color arc**: emotional journey from confusion (blues) to mastery (gold/teal)
- **"Aha!" moment**: explicitly defined gold-glow moment

### 2. 3B1B Global Theme (`manim_config/theme.py`)
Every scene uses a **shared style system**:
- **Colors**: Deep navy `#1C1C2E`, teal `#3DCCC7`, golden `#FFD700` — exact 3B1B palette
- **Animation helpers**: `playful_bounce()`, `morph_shape()`, `number_ticker()`, `glow_dot()`
- **Typography**: Nyala (Amharic) + Inter (Latin)
- **Canvas enforcement**: all objects kept in `[-5.5, 5.5] × [-3.0, 3.0]`

### 3. Production-Grade Manim Code
The Manim Coder receives the storyboard plan and generates code that:
- Uses `always_redraw` + `ValueTracker` for live dynamic animations
- Adds `playful_bounce()` humor beats
- Uses `STAR_YELLOW` glow for the "aha!" moment
- Maintains perfect voiceover sync (1 sentence = 1 `with voiceover()` block)

### 4. Critic Loop (Syntax + Visual)
- **Stage 1**: Renders each scene at `-ql` quality; captures full traceback on failure
- **Stage 2**: Captures last frame PNG → Qwen3-VL visual inspection
- **Auto-healing**: LLM rewrites broken code up to 3 times; guaranteed fallback always renders

### 5. Post-Production Polish
- 🔊 Audio normalized to -14 LUFS broadcast standard
- 📝 Amharic subtitles burned in + separate English `.srt` generated
- 🎨 Warm color grade (slight brightness + contrast + warm gamma)
- 🎬 Intro title cards with topic + series branding

---

## 🚀 Setup

### Option A: Local (macOS)

```bash
# 1. Install Ollama and pull models
brew install ollama
ollama pull llama3.1
ollama pull qwen3-coder:30b
ollama pull qwen3:8b

# 2. Build the Python venv
./rebuild_venv.sh

# 3. Start everything
./run_all.sh

# 4. Open the UI
open http://localhost:3000

# 5. Or run a demo directly
./demo_3b1b.sh "The Pythagorean Theorem"
```

### Option B: Docker (one command)

```bash
docker compose up --build
open http://localhost:3000
```

---

## ⚙️ Configuration

All settings in `agent_core/.env` (or environment variables):

| Variable | Default | Description |
|---|---|---|
| `AUTO_APPROVE` | `true` | Skip storyboard review, fully automated |
| `RESEARCHER_MODEL` | `llama3.1:latest` | Research & planning LLM |
| `SCRIPTWRITER_MODEL` | `llama3.1:latest` | Narration LLM |
| `VISUAL_DESIGNER_MODEL` | `llama3.1:latest` | Storyboard planning LLM |
| `MANIM_CODER_MODEL` | `qwen3-coder:30b` | Code generation LLM (best quality) |
| `CRITIC_MODEL` | `qwen3:8b` | Code review LLM |
| `VL_MODEL_NAME` | `qwen3-vl:8b` | Visual frame inspection model |
| `MAX_CRITIC_RETRIES` | `3` | Auto-healing retry limit |
| `ORCHESTRATOR_PORT` | `8205` | Backend API port |
| `TTS_SERVER_URL` | `http://127.0.0.1:8102` | Amharic TTS server |

---

## 📁 Project Structure

```
.
├── agent_core/
│   ├── manim_config/
│   │   └── theme.py          # Global 3B1B style system ← UPGRADED
│   ├── agents/
│   │   ├── researcher.py
│   │   ├── scriptwriter.py   # SSML-aware, humor beats ← UPGRADED
│   │   ├── visual_designer.py # Storyboard planner ← NEW
│   │   ├── math_verifier.py  # SymPy formula check ← NEW
│   │   ├── manim_coder.py    # 3B1B few-shot prompting ← UPGRADED
│   │   └── critic.py
│   ├── config.py             # Dynamic paths, AUTO_APPROVE ← UPGRADED
│   ├── logger.py             # Centralized logging ← NEW
│   └── orchestrator.py       # /generate_full endpoint ← UPGRADED
├── video_postprod/            # ← NEW MODULE
│   ├── pipeline.py           # Full post-production chain
│   └── subtitles.py          # SRT generation
├── video_compiler/
│   └── compiler.py
├── web_app/                  # Next.js UI
│   └── src/app/
│       ├── page.tsx          # ⚡ Full Auto button ← UPGRADED
│       └── api/generate-full/ # New API proxy ← NEW
├── logs/                     # Pipeline logs ← NEW
├── demo_3b1b.sh              # One-command demo ← NEW
├── Dockerfile
├── docker-compose.yml        # Full stack ← NEW
└── README.md
```

---

## 🎬 Output

Each run produces in `Local_Video_Output/{job_id}/`:
- `{Topic}_3B1B_Style.mp4` — final polished video
- `Masterpiece.mp4` — pre-post-production master
- `subtitles_am.srt` — Amharic subtitles
- `subtitles_en.srt` — English subtitles
- `generated_lesson.py` — the full Manim source

---

*Built with ❤️ using ManimCE, LangGraph, Ollama, EdgeTTS, and FFmpeg.*
