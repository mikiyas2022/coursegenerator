# 3B1B English Course Factory

> **Autonomous production of Grant Sanderson–quality STEM explainer videos.**  
> One topic in → cinematic, narrated, animated masterclass out.

---

## What This Is

A fully autonomous pipeline that transforms any STEM topic into a **3Blue1Brown-style educational video** — complete with:

- 🎬 **42 distinct animation templates** (geometry, calculus, physics, algebra, probability, 3D, flowcharts…)
- 🗣️ **Kokoro ONNX TTS** — fast, high-quality English narration with precise timing
- 🧠 **Multi-agent orchestration** — Researcher → Scriptwriter → Visual Designer → Template Orchestrator → Critic → Post-Production
- 🎨 **True 3B1B aesthetics** — dark navy (#1C1C2E), teal accents, gold highlights, Inter font, buttery-smooth transforms

## Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Researcher  │────▶│ Scriptwriter │────▶│Visual Designer│
│ (scene plan) │     │ (narration)  │     │(choreography)│
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                  │
                     ┌──────────────┐     ┌───────▼───────┐
                     │    Critic    │◀────│  Template     │
                     │ (verify AST)│     │ Orchestrator  │
                     └──────┬───────┘     └───────────────┘
                            │
                     ┌──────▼───────┐     ┌───────────────┐
                     │ Manim + TTS  │────▶│Post-Production│
                     │  (render)    │     │(sync + grade) │
                     └──────────────┘     └───────────────┘
```

## Storytelling Philosophy

Every video follows the Grant Sanderson arc:

1. **Hook** — A surprising question or visual that sparks curiosity
2. **Intuition Building** — Gentle buildup with analogies and metaphors
3. **Core Concept** — The key idea, introduced with fluid transforms
4. **Worked Example #1** — Step-by-step numerical walkthrough
5. **Deeper Insight** — "But here's the beautiful part…"
6. **Worked Example #2** — A harder problem that reinforces understanding
7. **Aha! Moment** — The emotional payoff — everything clicks
8. **Summary + Teaser** — Recap with a hook for what's next

## 42 Animation Templates

| # | Name | Visual Pattern |
|---|------|---------------|
| 01 | Hook Intro | Title reveal + curiosity burst |
| 02 | Vector Sweep | Rotating arrow decomposition |
| 03 | Parabolic Trace | TracedPath projectile |
| 04 | Formula Reveal | Boxed equation + explosion |
| 05 | Number Ticker | Animated counter on NumberLine |
| 06 | Sine Wave | Phase-shifting wave |
| 07 | Circle Morph | Shape → formula transform |
| 08 | Worked Example | Side panel step-by-step |
| 09 | Side-by-Side | A vs B comparison |
| 10 | Graph Transform | Parameter slider |
| 11 | Bullet Reveal | Key takeaways list |
| 12 | Geometric Growth | Live area labels |
| 13 | Force Diagram | Free-body arrows |
| 14 | Camera Zoom | Scale reveal |
| 15 | Energy Bars | KE/PE conservation |
| 16 | Bouncing Analogy | Playful metaphor |
| 17 | Derivative | Tangent line tracker |
| 18 | Lissajous/Spiral | Parametric trace |
| 19 | Riemann Sum | Rectangle → integral |
| 20 | Summary Closer | Checklist + gold stars |
| 21 | Exponential | Growth curve |
| 22 | Matrix Grid | Linear transform |
| 23 | Pythagorean Proof | Visual geometry proof |
| 24 | Probability Tree | Branching outcomes |
| 25 | Circuit | Glowing bulb + current |
| 26 | Pendulum | SHM oscillation |
| 27 | Doppler | Expanding wavefronts |
| 28 | Histogram | Bars + mean line |
| 29 | Unit Circle | Trig sweep |
| 30 | Grand Finale | Orbit collapse |
| 31 | 3D Surface | Concentric ring approximation |
| 32 | Silent Intro | Cinematic title (no narration) |
| 33 | Always-Redraw | Live coordinate tracker |
| 34 | Venn Diagram | Set intersection highlight |
| 35 | Before/After | Split-screen comparison |
| 36 | Taylor Series | Successive approximations |
| 37 | Flowchart | Decision tree branching |
| 38 | Wave Interference | Superposition of waves |
| 39 | Step-by-Step Solve | Multi-line equation |
| 40 | Area Under Curve | Integral fill animation |
| 41 | Chapter Card | Episode divider (silent) |
| 42 | Cross-Section | Layered structure reveal |

## Quick Start

### Prerequisites
- Python 3.11+ with ManimCE
- Kokoro ONNX (auto-downloaded)
- Ollama with `llama3.1` model
- Node.js 18+ (for web UI)

### Run

```bash
# Start everything (orchestrator + web UI)
./run_all.sh

# Open http://localhost:3015
# Enter a topic → click "Generate 3B1B Course" → wait ~5 min
```

### Demo Command

```bash
# Generate a single episode from the command line
curl -X POST http://localhost:8205/generate-full \
  -H "Content-Type: application/json" \
  -d '{"topic": "Why does the Pythagorean theorem work?"}'
```

### Example Topics That Work Beautifully

- "Why does e^(iπ) = -1? The most beautiful equation."
- "Fourier series: how to draw anything with circles"
- "Newton's Laws of Motion: from apples to rockets"
- "The beauty of complex numbers"
- "What is a derivative, really?"
- "How does RSA encryption actually work?"
- "The Central Limit Theorem explained visually"

## Audio-Visual Sync

The pipeline ensures perfect lip-sync:

1. **Template-level**: `self.clear()` always executes **before** `with self.voiceover()` — never inside
2. **Post-production**: FFmpeg `apad` extends audio to match video duration
3. **Normalization**: -14 LUFS broadcast-standard loudness
4. **Color grading**: Warm tones, 3B1B contrast/saturation boost

## Stack

| Component | Technology |
|-----------|-----------|
| Animation | ManimCE 0.20.1 |
| TTS | Kokoro ONNX (local, fast) |
| LLM | Ollama (llama3.1 / deepseek-r1) |
| Web UI | Next.js 14 |
| Post-prod | FFmpeg |
| Orchestrator | Python FastAPI |

## License

MIT
