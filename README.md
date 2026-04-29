# 3B1B English Course Factory v6

> **1000+ effective animation templates. Context-aware matching. Grant Sanderson–quality output.**  
> One topic in → cinematic, narrated, animated masterclass out.

---

## What This Is

A fully autonomous pipeline that transforms any STEM topic into a **3Blue1Brown-style educational video**:

- 🎬 **42 base templates + dynamic generation = 1000+ effective variations**
- 🧠 **TF-IDF cosine similarity** matches the best template to each scene's content
- 🔧 **Template Generator Agent** creates specialized variants on-the-fly using LLM
- 🗣️ **Kokoro ONNX TTS** — fast, high-quality English narration with precise timing
- 🎨 **True 3B1B aesthetics** — dark navy (#1C1C2E), teal/gold accents, Inter font, buttery-smooth transforms
- 🔊 **Perfect audio-visual sync** — `self.clear()` always executes before narration starts

## How 1000+ Templates Work

```
┌─────────────────────────────────────────────────────────────┐
│                  TEMPLATE SYSTEM                            │
│                                                             │
│  42 Base Templates (manually crafted, high quality)         │
│       ↓                                                     │
│  Template Generator Agent (LLM-powered)                     │
│       ↓                                                     │
│  Generates SPECIALIZED variants for each concept            │
│  e.g., "bouncing vector decomposition with humor"           │
│       ↓                                                     │
│  Cached to manim_templates/3b1b_style/generated/            │
│  Each unique topic creates 6-10 new specialized templates   │
│       ↓                                                     │
│  After 100 topics → 600-1000+ cached templates              │
│                                                             │
│  CONTEXT-AWARE SELECTION (TF-IDF)                           │
│  • Builds TF-IDF vectors from template descriptions         │
│  • Cosine similarity ranks all templates for each scene     │
│  • Avoids last 4 used templates (no repeats)                │
│  • Falls back to Visual Designer's recommendation           │
└─────────────────────────────────────────────────────────────┘
```

## Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Researcher  │────▶│ Scriptwriter │────▶│Visual Designer│
│ (scene plan) │     │ (narration)  │     │(choreography)│
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                  │
                     ┌──────────────┐     ┌───────▼───────┐
                     │   Template   │◀────│  Template     │
                     │  Generator   │     │ Orchestrator  │
                     │ (new variants│     │ (TF-IDF match)│
                     └──────────────┘     └───────┬───────┘
                                                  │
                     ┌──────────────┐     ┌───────▼───────┐
                     │    Critic    │◀────│   Manim +     │
                     │ (verify AST) │     │ Kokoro Render │
                     └──────┬───────┘     └───────────────┘
                            │
                     ┌──────▼───────┐
                     │Post-Production│
                     │(sync + grade) │
                     └──────────────┘
```

## Storytelling Philosophy (Enforced)

Every video follows the Grant Sanderson arc:

1. **Silent Intro** — Cinematic title card with no narration (template_32)
2. **Hook** — A surprising question or visual that sparks curiosity
3. **Intuition Building** — Gentle buildup with animatable analogies
4. **Core Concept** — The key idea with fluid transforms
5. **Worked Example #1** — Step-by-step numerical walkthrough
6. **Deeper Insight** — "But here's the beautiful part…"
7. **Worked Example #2** — A harder problem reinforcing understanding
8. **Aha! Moment** — The emotional payoff with `<pause>` marker
9. **Summary + Teaser** — Recap with finale explosion (template_30)

## Audio-Visual Sync (How It Works)

```python
# CORRECT (sync-safe) — self.clear() BEFORE voiceover
self.clear()
with self.voiceover(text="Let's explore force...") as tracker:
    obj = formula_box("F = ma")
    self.play(FadeIn(obj), run_time=tracker.duration * 0.6)
    self.wait(tracker.duration * 0.4)

# WRONG (desynced) — self.clear() INSIDE voiceover
with self.voiceover(text="Let's explore force...") as tracker:
    self.clear()  # ← Audio already started! Screen flashes blank!
    ...
```

Three layers of protection:
1. **Templates**: All 42 base templates have correct sync pattern
2. **Post-processor**: `_fix_sync_and_overflow()` auto-corrects any generated code
3. **Manim Coder prompt**: LLM instructed with correct pattern + few-shot example

## 42 Base Templates

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
| 39 | Step-by-Step | Multi-line equation solving |
| 40 | Area Under Curve | Integral fill animation |
| 41 | Chapter Card | Episode divider (silent) |
| 42 | Cross-Section | Layered structure reveal |

## Quick Start

```bash
# Start everything
./run_all.sh

# Open http://localhost:3015
# Enter a topic → click "Generate 3B1B Course" → wait ~5 min
```

### Demo Command

```bash
curl -X POST http://localhost:8205/generate-full \
  -H "Content-Type: application/json" \
  -d '{"topic": "Why does the Pythagorean theorem work?"}'
```

## Stack

| Component | Technology |
|-----------|-----------|
| Animation | ManimCE 0.20.1 |
| TTS | Kokoro ONNX (local) |
| LLM | Ollama (llama3.1 / deepseek-r1) |
| Template Matching | TF-IDF cosine similarity |
| Dynamic Generation | Template Generator Agent (LLM) |
| Web UI | Next.js 14 |
| Post-prod | FFmpeg |
| Orchestrator | Python FastAPI |

## License

MIT
