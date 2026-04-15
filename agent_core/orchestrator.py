#!/usr/bin/env python3
"""
orchestrator.py — Agentic Video Production Orchestrator
========================================================
LangGraph state machine linking: Researcher → Scriptwriter → Manim Coder → Critic
Serves SSE (Server-Sent Events) at http://127.0.0.1:8200

Endpoints:
  POST /create         — submit job, receive SSE stream of production phases
  POST /render_final   — trigger 4K re-render after preview approval
  GET  /health         — liveness check
"""

import asyncio
import json
import os
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, AsyncGenerator, TypedDict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

sys.path.insert(0, os.path.dirname(__file__))
from config import MAX_CRITIC_RETRIES, ORCHESTRATOR_PORT
from agents.researcher  import run_researcher
from agents.scriptwriter import run_scriptwriter
from agents.manim_coder  import run_manim_coder
from agents.critic       import run_critic, run_final_render

# LangGraph
from langgraph.graph import StateGraph, END


# ─────────────────────────────────────────────────────────────────────────────
# State
# ─────────────────────────────────────────────────────────────────────────────

class VideoProductionState(TypedDict):
    # Inputs
    topic:            str
    audience:         str
    style:            str
    metaphor:         str
    source_material:  str
    persona_id:       int
    output_folder:    str
    orientation:      str

    # Pipeline data
    learning_steps:   list[dict]
    script_scenes:    list[dict]
    manim_classes:    list[str]

    # Self-healing
    render_error:     str
    retry_count:      int

    # Outputs
    preview_path:     str

    # Internal event log (for SSE streaming)
    events:           list[dict]


# ─────────────────────────────────────────────────────────────────────────────
# Graph Nodes
# ─────────────────────────────────────────────────────────────────────────────

def researcher_node(state: VideoProductionState) -> dict:
    steps = run_researcher(
        topic=state["topic"],
        audience=state["audience"],
        style=state["style"],
        metaphor=state["metaphor"],
        source_material=state.get("source_material", ""),
    )
    return {
        "learning_steps": steps,
        "events": state.get("events", []) + [{
            "phase": "researcher",
            "data": steps,
            "message": f"✅ Identified {len(steps)} learning steps",
        }],
    }


def scriptwriter_node(state: VideoProductionState) -> dict:
    scenes = run_scriptwriter(
        scenes=state["learning_steps"],
        style=state["style"],
    )
    return {
        "script_scenes": scenes,
        "events": state.get("events", []) + [{
            "phase": "scriptwriter",
            "data": scenes,
            "message": f"✅ Amharic script written for {len(scenes)} scenes",
        }],
    }


def manim_coder_node(state: VideoProductionState) -> dict:
    classes = run_manim_coder(
        scenes=state["script_scenes"],
        persona_id=state.get("persona_id", 1),
        error_context=state.get("render_error", ""),
        previous_code=state.get("manim_classes") or None,
    )
    return {
        "manim_classes": classes,
        "render_error":  "",          # clear previous error after regen
        "events": state.get("events", []) + [{
            "phase": "manim_coder",
            "data": {"classes_count": len(classes)},
            "message": f"✅ Manim code generated ({len(classes)} scene classes)",
        }],
    }


def critic_node(state: VideoProductionState) -> dict:
    result = run_critic(
        code_classes=state["manim_classes"],
        output_folder=state["output_folder"],
        retry_count=state.get("retry_count", 0),
    )
    if result["success"]:
        return {
            "preview_path": result.get("preview_path", ""),
            "render_error": "",
            "events": state.get("events", []) + [{
                "phase": "critic",
                "data": {"success": True, "preview_path": result.get("preview_path")},
                "message": "🎬 Preview rendered successfully!",
            }],
        }
    else:
        new_retry = state.get("retry_count", 0) + 1
        return {
            "render_error": result["error"],
            "retry_count":  new_retry,
            "events": state.get("events", []) + [{
                "phase": "critic",
                "data": {"success": False, "error": result["error"][:300], "attempt": new_retry},
                "message": f"🔧 Self-healing attempt {new_retry}/{MAX_CRITIC_RETRIES}…",
            }],
        }


def should_continue(state: VideoProductionState) -> str:
    """Routing function: retry if there's an error and retries remain."""
    if state.get("render_error") and state.get("retry_count", 0) < MAX_CRITIC_RETRIES:
        return "retry"
    return "done"


# ─────────────────────────────────────────────────────────────────────────────
# Build Graph
# ─────────────────────────────────────────────────────────────────────────────

_workflow = StateGraph(VideoProductionState)
_workflow.add_node("researcher",   researcher_node)
_workflow.add_node("scriptwriter", scriptwriter_node)
_workflow.add_node("manim_coder",  manim_coder_node)
_workflow.add_node("critic",       critic_node)

_workflow.set_entry_point("researcher")
_workflow.add_edge("researcher",   "scriptwriter")
_workflow.add_edge("scriptwriter", "manim_coder")
_workflow.add_edge("manim_coder",  "critic")
_workflow.add_conditional_edges("critic", should_continue, {"retry": "manim_coder", "done": END})

graph = _workflow.compile()
executor = ThreadPoolExecutor(max_workers=2)


# ─────────────────────────────────────────────────────────────────────────────
# FastAPI App
# ─────────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="STEM AI Video Orchestrator",
    description="LangGraph-powered agentic video production for Amharic STEM education.",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class CreateJobRequest(BaseModel):
    topic:           str
    audience:        str  = "High School"
    style:           str  = "Inquiry-Based/3b1b"
    metaphor:        str  = ""
    source_material: str  = ""
    persona_id:      int  = 1
    orientation:     str  = "landscape"
    output_folder:   str  = ""


class FinalRenderRequest(BaseModel):
    output_folder: str
    orientation:   str = "landscape"


def _sse(event_type: str, payload: Any) -> str:
    return f"data: {json.dumps({'type': event_type, 'payload': payload}, ensure_ascii=False)}\n\n"


async def _stream_pipeline(req: CreateJobRequest) -> AsyncGenerator[str, None]:
    output_folder = req.output_folder or os.path.join(
        tempfile.gettempdir(), "stem_output", f"job_{int(time.time())}"
    )
    os.makedirs(output_folder, exist_ok=True)

    yield _sse("status", {
        "message": "🔬 Researcher is analyzing your topic…",
        "phase": "researcher",
        "output_folder": output_folder,
    })

    initial_state: VideoProductionState = {
        "topic":           req.topic,
        "audience":        req.audience,
        "style":           req.style,
        "metaphor":        req.metaphor,
        "source_material": req.source_material,
        "persona_id":      req.persona_id,
        "output_folder":   output_folder,
        "orientation":     req.orientation,
        "learning_steps":  [],
        "script_scenes":   [],
        "manim_classes":   [],
        "render_error":    "",
        "retry_count":     0,
        "preview_path":    "",
        "events":          [],
    }

    loop    = asyncio.get_event_loop()
    q: asyncio.Queue = asyncio.Queue()

    def run_graph():
        try:
            for step_output in graph.stream(initial_state):
                q.put_nowait(("step", step_output))
            q.put_nowait(("done", None))
        except Exception as exc:
            q.put_nowait(("error", str(exc)))

    loop.run_in_executor(executor, run_graph)

    while True:
        kind, payload = await q.get()

        if kind == "error":
            yield _sse("error", {"message": str(payload)})
            break

        if kind == "done":
            yield _sse("complete", {
                "message": "🚀 Production pipeline complete! Review your preview.",
                "output_folder": output_folder,
            })
            break

        if kind == "step":
            node_name  = list(payload.keys())[0]
            node_state = payload[node_name]
            events     = node_state.get("events", [])
            if events:
                ev = events[-1]
                phase   = ev.get("phase")
                data    = ev.get("data")
                message = ev.get("message", "")

                if phase == "researcher":
                    yield _sse("researcher_done", {"message": message, "steps": data})

                elif phase == "scriptwriter":
                    yield _sse("script_done", {"message": message, "scenes": data})

                elif phase == "manim_coder":
                    yield _sse("code_done", {"message": message, **data})

                elif phase == "critic":
                    if data.get("success"):
                        yield _sse("preview_ready", {
                            "message":      message,
                            "preview_path": data.get("preview_path"),
                            "output_folder": output_folder,
                        })
                    else:
                        yield _sse("self_healing", {
                            "message":      message,
                            "error_snippet": data.get("error", "")[:300],
                            "attempt":       data.get("attempt", 1),
                            "max_retries":   MAX_CRITIC_RETRIES,
                        })
            await asyncio.sleep(0)   # yield to event loop


@app.post("/create")
async def create_video(req: CreateJobRequest):
    return StreamingResponse(
        _stream_pipeline(req),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.post("/render_final")
def render_final(req: FinalRenderRequest):
    """Trigger 4K high-quality render after user approves the preview."""
    result = run_final_render(req.output_folder, req.orientation)
    return result


@app.get("/health")
def health():
    return {"status": "ok", "service": "orchestrator", "port": ORCHESTRATOR_PORT}


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "orchestrator:app",
        host="127.0.0.1",
        port=ORCHESTRATOR_PORT,
        log_level="info",
        reload=False,
    )
