#!/usr/bin/env python3
"""
tts_server.py — Local Amharic TTS Microservice
================================================
Powered by Meta's facebook/mms-tts-amh (VITS model).
Runs on http://127.0.0.1:8100

Endpoints:
  POST /generate_audio  — synthesise Amharic text with chosen persona
  GET  /personas        — list all voice personas
  GET  /health          — liveness check

5 Voice Personas (all derived from the same MMS model via pydub audio
manipulation — pitch shift + tempo change applied after synthesis):

  1  Mekdes   — Default female, unaltered (warm tutor)
  2  Ameha    — Deep male   (pitch -300 ¢, tempo -16%)
  3  Dawit    — Energetic   (pitch +100 ¢, tempo +15%)
  4  Selamawit — Patient    (pitch -150 ¢, tempo -10%)
  5  Tigist   — Bright      (pitch +300 ¢, tempo unchanged)

Technical note on the pydub frame-rate trick
---------------------------------------------
pydub stores raw PCM + frame_rate metadata.  Changing frame_rate without
resampling is equivalent to playing a vinyl record at a different RPM — it
shifts both pitch and tempo simultaneously.

  combined_factor = tempo_factor × 2^(cents / 1200)
  audio._spawn(data, {"frame_rate": int(orig_rate × combined_factor)})
        .set_frame_rate(orig_rate)

  → result is shorter/faster (tempo_factor > 1) and higher-pitched
    (cents > 0), or longer/slower/lower for the inverse.  The effect
    is subtle for small values and produces distinctly different
    sounding voices, which is the goal for educational personas.
"""

import os
import uuid
import tempfile
import time
os.environ["HF_HOME"] = "/tmp/huggingface_cache"
import numpy as np
import torch
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from transformers import VitsModel, AutoTokenizer
from pydub import AudioSegment
import uvicorn


# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

MODEL_NAME = "facebook/mms-tts-amh"
TTS_PORT   = 8100
OUTPUT_DIR = Path(tempfile.gettempdir()) / "stem_tts_output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# Persona Definitions
# ─────────────────────────────────────────────────────────────────────────────

PERSONAS: dict[int, dict] = {
    1: {
        "name":        "👩‍🏫 Mekdes — The Warm Tutor (Default)",
        "description": "Unaltered MMS voice. Natural, intimate Amharic female. "
                       "Paces carefully so no student is left behind.",
        "pitch_cents": 0,
        "tempo_factor": 1.0,
    },
    2: {
        "name":        "👨‍🏫 Ameha — The Deep Expert",
        "description": "Pitch shifted down 300 ¢ + slightly slower. "
                       "Deep, authoritative — like a senior scientist at a conference.",
        "pitch_cents": -300,
        "tempo_factor": 0.84,
    },
    3: {
        "name":        "⚡ Dawit — The Energetic Coach",
        "description": "15% faster, pitch up 100 ¢. "
                       "Upbeat and motivating — turns dry physics into an exciting challenge.",
        "pitch_cents": 100,
        "tempo_factor": 1.15,
    },
    4: {
        "name":        "📖 Selamawit — The Patient Professor",
        "description": "10% slower, pitch down 150 ¢. "
                       "Deliberate and methodical — every word lands precisely.",
        "pitch_cents": -150,
        "tempo_factor": 0.90,
    },
    5: {
        "name":        "🎓 Tigist — The Bright Tutor",
        "description": "Pitch up 300 ¢, speed unchanged. "
                       "Younger, warmer, brighter female — great for younger grades.",
        "pitch_cents": 300,
        "tempo_factor": 1.0,
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# Uroman: Ge'ez → Latin romanisation
# ─────────────────────────────────────────────────────────────────────────────

def romanize_amharic(text: str) -> str:
    """
    Convert Amharic Ge'ez script to Latin script using the uroman package.
    Meta's MMS tokenizer expects romanised input for Amharic.
    Falls back to raw text if uroman is unavailable (quality will be reduced).
    """
    try:
        import uroman as ur  # pip install uroman
        romanizer = ur.Uroman()
        romanized = romanizer.romanize_string(text, lcode="amh")
        print(f"  [uroman] '{text[:30]}' → '{romanized[:40]}'", flush=True)
        return romanized
    except ImportError:
        print("  [uroman] Package not found. Install with: pip install uroman", flush=True)
        print("  [uroman] Falling back to raw Ge'ez text (quality degraded).", flush=True)
        return text
    except Exception as exc:
        print(f"  [uroman] Romanisation failed ({exc}). Using raw text.", flush=True)
        return text


# ─────────────────────────────────────────────────────────────────────────────
# Audio Post-processing: Persona Manipulation
# ─────────────────────────────────────────────────────────────────────────────

def apply_persona(
    waveform_np: np.ndarray,
    sample_rate: int,
    persona_id: int,
) -> AudioSegment:
    """
    Convert a raw numpy float32 waveform to a pydub AudioSegment and
    apply the pitch / tempo transformation for the requested persona.

    Implementation uses the pydub "frame-rate trick":
      combined_factor = tempo × 2^(cents/1200)
      Change frame_rate metadata → set_frame_rate resamples back.
      Net effect: audio played faster/slower and at higher/lower pitch.
    """
    persona = PERSONAS.get(persona_id, PERSONAS[1])
    pitch_cents  = persona["pitch_cents"]
    tempo_factor = persona["tempo_factor"]

    # numpy float32 [-1, 1]  →  16-bit signed PCM
    pcm_16 = (np.clip(waveform_np, -1.0, 1.0) * 32767).astype(np.int16)
    audio = AudioSegment(
        data=pcm_16.tobytes(),
        sample_width=2,   # 16-bit = 2 bytes
        frame_rate=sample_rate,
        channels=1,
    )

    if pitch_cents == 0 and tempo_factor == 1.0:
        return audio  # Persona 1 — no transformation needed

    # Combined modification factor
    pitch_factor     = 2.0 ** (pitch_cents / 1200.0)
    combined_factor  = tempo_factor * pitch_factor

    # Apply: change frame_rate metadata (reinterprets samples), then resample
    modified_rate = max(1, int(sample_rate * combined_factor))
    audio = audio._spawn(
        audio.raw_data,
        overrides={"frame_rate": modified_rate}
    )
    # Resample back to standard 16 kHz — the tempo+pitch shift is baked in
    audio = audio.set_frame_rate(sample_rate)

    return audio


# ─────────────────────────────────────────────────────────────────────────────
# TTS Engine
# ─────────────────────────────────────────────────────────────────────────────

class AmharicTTSEngine:
    """
    Loads facebook/mms-tts-amh once at startup.
    All synthesis calls are synchronous (CPU-safe) under the GIL.
    """

    def __init__(self):
        self.model: VitsModel | None      = None
        self.tokenizer: AutoTokenizer | None = None
        self.sample_rate: int             = 16_000
        self._load()

    def _load(self) -> None:
        start = time.time()
        print(f"[TTS] Loading model {MODEL_NAME} …", flush=True)
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        self.model     = VitsModel.from_pretrained(MODEL_NAME)
        self.model.eval()
        self.sample_rate = self.model.config.sampling_rate
        elapsed = time.time() - start
        print(f"[TTS] Ready ✓  ({elapsed:.1f}s, sample_rate={self.sample_rate}Hz)", flush=True)

    def synthesize(self, text: str) -> tuple[np.ndarray, int]:
        """
        Synthesise text (Ge'ez Amharic) and return (waveform_np, sample_rate).
        Romanisation via uroman is applied automatically.
        """
        romanized = romanize_amharic(text)

        inputs = self.tokenizer(romanized, return_tensors="pt")
        if inputs["input_ids"].shape[1] == 0:
            raise RuntimeError(
                "Tokenizer returned empty tensor. "
                "Check that uroman is installed: pip install uroman"
            )

        with torch.no_grad():
            waveform = self.model(**inputs).waveform

        return waveform.squeeze().cpu().numpy(), self.sample_rate


# ─────────────────────────────────────────────────────────────────────────────
# FastAPI App
# ─────────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Amharic MMS TTS Server",
    description=(
        "Local Meta MMS-based Amharic speech synthesis.\n\n"
        "POST `/generate_audio` with `{\"text\": \"…\", \"persona_id\": 1}` "
        "to receive a path to the generated WAV file."
    ),
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global engine — loaded once on startup
_engine: AmharicTTSEngine | None = None


@app.on_event("startup")
def _startup():
    global _engine
    _engine = AmharicTTSEngine()


# ── Request / Response Schemas ────────────────────────────────────────────────

class GenerateRequest(BaseModel):
    text:        str       = Field(..., description="Amharic Ge'ez text to synthesise.")
    persona_id:  int       = Field(1, ge=1, le=5, description="Voice persona (1–5).")
    output_path: str | None = Field(
        None,
        description="Optional absolute path for the output WAV. "
                    "Auto-generated UUID path used if omitted."
    )


class PersonaInfo(BaseModel):
    id:          int
    name:        str
    description: str


class GenerateResponse(BaseModel):
    status:           str
    output_path:      str
    duration_seconds: float
    persona:          PersonaInfo


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.post("/generate_audio", response_model=GenerateResponse)
def generate_audio(req: GenerateRequest):
    """Synthesise Amharic text and return a WAV file path."""
    if _engine is None:
        raise HTTPException(503, "TTS engine not initialised yet.")

    if not req.text.strip():
        raise HTTPException(400, "text field cannot be empty.")

    if req.persona_id not in PERSONAS:
        raise HTTPException(400, f"persona_id must be 1–5, got {req.persona_id}.")

    # Determine output path
    out_path = req.output_path or str(OUTPUT_DIR / f"{uuid.uuid4().hex}.wav")
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)

    try:
        t0 = time.time()
        waveform_np, sample_rate = _engine.synthesize(req.text)
        audio = apply_persona(waveform_np, sample_rate, req.persona_id)
        audio.export(out_path, format="wav")
        elapsed = time.time() - t0

        duration = len(audio) / 1000.0  # pydub duration in ms → seconds
        persona  = PERSONAS[req.persona_id]

        print(
            f"  [TTS] persona={req.persona_id} | {duration:.2f}s audio | "
            f"synthesis+export={elapsed:.1f}s | → {out_path}",
            flush=True,
        )

        return GenerateResponse(
            status="success",
            output_path=out_path,
            duration_seconds=duration,
            persona=PersonaInfo(
                id=req.persona_id,
                name=persona["name"],
                description=persona["description"],
            ),
        )

    except Exception as exc:
        print(f"  [TTS] ERROR: {exc}", flush=True)
        raise HTTPException(500, str(exc))


@app.get("/personas")
def list_personas():
    """Return all available voice personas."""
    return {
        pid: {
            "name":         info["name"],
            "description":  info["description"],
            "pitch_cents":  info["pitch_cents"],
            "tempo_factor": info["tempo_factor"],
        }
        for pid, info in PERSONAS.items()
    }


@app.get("/health")
def health():
    """Liveness / readiness check."""
    return {
        "status":       "ok",
        "model":        MODEL_NAME,
        "engine_ready": _engine is not None,
        "sample_rate":  _engine.sample_rate if _engine else None,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run(
        "tts_server:app",
        host="127.0.0.1",
        port=TTS_PORT,
        log_level="info",
        reload=False,
    )
