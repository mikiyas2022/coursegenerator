# Course: Exam Generator (Template-Powered STEM Pipeline)

This platform automatically produces high-quality educational STEM videos using local LLMs (Ollama) and Manim.

## 🚀 Features

It supports two main video production modes:

### 1. 3B1B-Style Explanatory Videos
Fun, playful, colorful, and engaging videos exactly like Grant Sanderson.
- Uses curated Manim templates for flawless execution
- High-quality English EdgeTTS narration
- Smooth animations (morphs, bounces, zoom-ins)
- Warm color grading and auto-subtitles
- One-click end-to-end generation

### 2. Q&A Blackboard Videos (NEW)
Silent, realistic step-by-step solutions for Ethiopian University Entrance Exam (EUEE) questions (Grade 12 level).
- Realistic dark green blackboard background
- Stroke-by-stroke chalk writing simulation
- Camera panning to follow the solution
- Clean boxed final answers
- High-resolution, smooth 60fps feel

---

## 🛠️ Requirements & Installation

1. Install [Docker](https://docs.docker.com/get-docker/) and `docker-compose`.
2. Make sure you have the required models available in your local Ollama instance:
   - `llama3.1:latest`
   - `qwen3-coder:30b`

### One-Command Run (Docker Compose)
```bash
docker-compose up --build -d
```

This will spin up:
- Ollama (LLM backend)
- Orchestrator (Port 8205)
- Next.js Web UI (Port 3000)

## 🎯 Usage

### Web UI
Open your browser to `http://localhost:3000`. You will see two buttons:
- **⚡ 3B1B Mode**: For full storytelling videos.
- **✍️ Blackboard Q&A**: For silent exam solutions.

### CLI Example
Generate a silent blackboard solution for a physics question:
```bash
./generate_blackboard.sh "A 10kg block slides down a 30 degree incline. What is its acceleration?"
```

## 📁 Architecture
- `agent_core/agents/template_orchestrator.py`: Injects topics into curated Manim templates to prevent LLM hallucination.
- `manim_templates/3b1b_style/`: Library of playful 3B1B templates.
- `manim_templates/blackboard/`: Library of step-by-step blackboard templates.
- `video_postprod/pipeline.py`: Automatically runs color-grading, TTS processing, and final rendering via FFmpeg.
