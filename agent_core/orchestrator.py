#!/usr/bin/env python3
"""
orchestrator.py — Agentic Video Production Orchestrator
========================================================
LangGraph state machine (full pipeline) + split SSE endpoints for the
Storyboard feedback loop.

Endpoints:
  POST /storyboard     — Phase 1: Researcher + Scriptwriter → streams scene JSON
  POST /render_scenes  — Phase 2: Manim Coder + Critic (syntax + visual) → streams progress
  POST /render_final   — Phase 3: 4K high-quality re-render
  POST /create         — Legacy: full pipeline in one call
  GET  /health         — Liveness check
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
from agents.researcher   import run_researcher
from agents.scriptwriter import run_scriptwriter
from agents.manim_coder  import run_manim_coder
from agents.critic       import run_critic, run_final_render

# LangGraph (used for the legacy /create endpoint)
from langgraph.graph import StateGraph, END


# ─────────────────────────────────────────────────────────────────────────────
# Request / Response schemas
# ─────────────────────────────────────────────────────────────────────────────

class StoryboardRequest(BaseModel):
    topic:           str
    audience:        str  = "High School (Grade 7–12)"
    style:           str  = "Inquiry-Based / 3b1b Style"
    metaphor:        str  = ""
    source_material: str  = ""


class RenderScenesRequest(BaseModel):
    scenes:        list[dict]         # approved (possibly edited) storyboard
    persona_id:    int   = 1
    orientation:   str   = "landscape"
    output_folder: str   = ""


class FinalRenderRequest(BaseModel):
    output_folder: str
    orientation:   str = "landscape"


class CreateJobRequest(BaseModel):     # legacy
    topic:           str
    audience:        str  = "High School (Grade 7–12)"
    style:           str  = "Inquiry-Based / 3b1b Style"
    metaphor:        str  = ""
    source_material: str  = ""
    persona_id:      int  = 1
    orientation:     str  = "landscape"
    output_folder:   str  = ""


# ─────────────────────────────────────────────────────────────────────────────
# SSE helper
# ─────────────────────────────────────────────────────────────────────────────

def _sse(event_type: str, payload: Any) -> str:
    return f"data: {json.dumps({'type': event_type, 'payload': payload}, ensure_ascii=False)}\n\n"


executor = ThreadPoolExecutor(max_workers=4)


# ─────────────────────────────────────────────────────────────────────────────
# Phase 1 — Storyboard stream (Researcher + Scriptwriter only)
# ─────────────────────────────────────────────────────────────────────────────

async def _stream_storyboard(req: StoryboardRequest) -> AsyncGenerator[str, None]:
    yield _sse("status", {"message": "🔬 Researcher analyzing topic…", "phase": "researcher"})

    loop = asyncio.get_event_loop()

    # Run Researcher in thread pool (blocking LLM call)
    try:
        task = loop.run_in_executor(
            executor,
            lambda: run_researcher(
                topic=req.topic,
                audience=req.audience,
                style=req.style,
                metaphor=req.metaphor,
                source_material=req.source_material,
            ),
        )
        while not task.done():
            yield _sse("ping", {"message": "still researching..."})
            try:
                await asyncio.wait_for(asyncio.shield(task), timeout=10.0)
            except asyncio.TimeoutError:
                pass
        steps = task.result()
    except Exception as exc:
        yield _sse("error", {"message": f"Researcher failed: {exc}"})
        return

    yield _sse("researcher_done", {
        "message": f"✅ Identified {len(steps)} learning steps",
        "steps": steps,
    })
    yield _sse("status", {"message": "✍️ Writing Amharic script…", "phase": "scriptwriter"})

    # Run Scriptwriter in thread pool with keep-alive pings
    try:
        task = loop.run_in_executor(
            executor,
            lambda: run_scriptwriter(scenes=steps, style=req.style),
        )
        while not task.done():
            yield _sse("ping", {"message": "still writing..."})
            try:
                await asyncio.wait_for(asyncio.shield(task), timeout=10.0)
            except asyncio.TimeoutError:
                pass
        scenes = task.result()
    except Exception as exc:
        yield _sse("error", {"message": f"Scriptwriter failed: {exc}"})
        return

    yield _sse("storyboard_ready", {
        "message": f"✅ Storyboard ready — {len(scenes)} scenes",
        "scenes": scenes,
    })


# ─────────────────────────────────────────────────────────────────────────────
# Phase 2 — Render stream (Manim Coder + Critic loop)
# ─────────────────────────────────────────────────────────────────────────────

async def _stream_render(req: RenderScenesRequest) -> AsyncGenerator[str, None]:
    output_folder = req.output_folder or os.path.join(
        tempfile.gettempdir(), "stem_output", f"job_{int(time.time())}"
    )
    os.makedirs(output_folder, exist_ok=True)

    loop = asyncio.get_event_loop()

    yield _sse("status", {"message": "⚙️ Manim Developer generating scene code…", "phase": "coding"})

    # Initial code generation
    try:
        task = loop.run_in_executor(
            executor,
            lambda: run_manim_coder(
                scenes=req.scenes,
                persona_id=req.persona_id,
            ),
        )
        while not task.done():
            yield _sse("ping", {"message": "still coding..."})
            try:
                await asyncio.wait_for(asyncio.shield(task), timeout=10.0)
            except asyncio.TimeoutError:
                pass
        code_classes = task.result()
    except Exception as exc:
        yield _sse("error", {"message": f"Manim Coder failed: {exc}"})
        return

    yield _sse("code_done", {
        "message": f"✅ {len(code_classes)} scene class(es) generated",
        "classes_count": len(code_classes),
    })

    # Self-healing loop (syntax + visual)
    retry_count   = 0
    visual_retry  = 0

    while True:
        yield _sse("status", {
            "message": f"🎞️ Critic rendering preview (attempt {retry_count+1})…",
            "phase": "rendering",
        })

        task = loop.run_in_executor(
            executor,
            lambda cc=code_classes, r=retry_count: run_critic(
                code_classes=cc,
                output_folder=output_folder,
                retry_count=r,
            ),
        )
        while not task.done():
            yield _sse("ping", {"message": "still rendering preview..."})
            try:
                await asyncio.wait_for(asyncio.shield(task), timeout=10.0)
            except asyncio.TimeoutError:
                pass
        result = task.result()

        # ── Visual self-healing ───────────────────────────────────────────
        if result.get("visual_error"):
            visual_retry += 1
            feedback = result.get("visual_feedback", "")
            yield _sse("visual_critique", {
                "message":   f"🖼️ Visual issues detected (pass {visual_retry}/{MAX_CRITIC_RETRIES})",
                "feedback":  feedback,
                "attempt":   visual_retry,
            })
            if visual_retry >= MAX_CRITIC_RETRIES:
                # Give up on visual healing, report what we have
                yield _sse("preview_ready", {
                    "message":       "⚠️ Preview ready (visual issues could not be auto-corrected)",
                    "preview_path":  output_folder,
                    "output_folder": output_folder,
                    "warnings":      feedback,
                })
                break
            # Ask manim_coder to rewrite code with visual corrections
            task = loop.run_in_executor(
                executor,
                lambda cc=code_classes, fb=feedback: run_manim_coder(
                    scenes=req.scenes,
                    persona_id=req.persona_id,
                    visual_feedback=f"VISUAL CRITIQUE: Apply these corrections:\n{fb}",
                    previous_code=cc,
                ),
            )
            while not task.done():
                yield _sse("ping", {"message": "still applying visual feedback..."})
                try:
                    await asyncio.wait_for(asyncio.shield(task), timeout=10.0)
                except asyncio.TimeoutError:
                    pass
            code_classes = task.result()
            continue

        # ── Syntax self-healing ───────────────────────────────────────────
        if not result["success"]:
            retry_count += 1
            error = result.get("error", "Unknown error")
            yield _sse("self_healing", {
                "message":       f"🔧 Self-healing attempt {retry_count}/{MAX_CRITIC_RETRIES}…",
                "error_snippet": error[:300],
                "attempt":       retry_count,
                "max_retries":   MAX_CRITIC_RETRIES,
            })
            if retry_count > MAX_CRITIC_RETRIES:
                yield _sse("error", {
                    "message": f"Max retries reached. Last error:\n{error[:500]}"
                })
                return
            task = loop.run_in_executor(
                executor,
                lambda cc=code_classes, e=error: run_manim_coder(
                    scenes=req.scenes,
                    persona_id=req.persona_id,
                    error_context=e,
                    previous_code=cc,
                ),
            )
            while not task.done():
                yield _sse("ping", {"message": "still fixing syntax error..."})
                try:
                    await asyncio.wait_for(asyncio.shield(task), timeout=10.0)
                except asyncio.TimeoutError:
                    pass
            code_classes = task.result()
            continue

        # ── SUCCESS ───────────────────────────────────────────────────────
        yield _sse("preview_ready", {
            "message":       "🎬 Preview rendered successfully!",
            "preview_path":  result.get("preview_path", output_folder),
            "output_folder": output_folder,
        })
        break

    yield _sse("complete", {
        "message":       "🚀 Done! Approve to render final 4K video.",
        "output_folder": output_folder,
    })


# ─────────────────────────────────────────────────────────────────────────────
# LangGraph state machine (legacy /create endpoint)
# ─────────────────────────────────────────────────────────────────────────────

class VideoProductionState(TypedDict):
    topic: str; audience: str; style: str; metaphor: str; source_material: str
    persona_id: int; output_folder: str; orientation: str
    learning_steps: list[dict]; script_scenes: list[dict]; manim_classes: list[str]
    render_error: str; retry_count: int; preview_path: str; events: list[dict]


def _researcher_node(state): 
    steps = run_researcher(state["topic"], state["audience"], state["style"], state["metaphor"], state.get("source_material",""))
    return {"learning_steps": steps, "events": state.get("events",[]) + [{"phase":"researcher","data":steps,"message":f"✅ {len(steps)} steps"}]}

def _scriptwriter_node(state): 
    scenes = run_scriptwriter(state["learning_steps"], state["style"])
    return {"script_scenes": scenes, "events": state.get("events",[]) + [{"phase":"scriptwriter","data":scenes,"message":f"✅ {len(scenes)} scenes"}]}

def _manim_coder_node(state): 
    classes = run_manim_coder(state["script_scenes"], state.get("persona_id",1), state.get("render_error",""), None if not state.get("render_error") else state.get("manim_classes"))
    return {"manim_classes": classes, "render_error": "", "events": state.get("events",[]) + [{"phase":"manim_coder","data":{"classes_count":len(classes)},"message":f"✅ {len(classes)} classes"}]}

def _critic_node(state): 
    result = run_critic(state["manim_classes"], state["output_folder"], state.get("retry_count",0))
    if result["success"]:
        return {"preview_path": result.get("preview_path",""), "render_error": "", "events": state.get("events",[]) + [{"phase":"critic","data":{"success":True,"preview_path":result.get("preview_path")},"message":"🎬 Preview ready!"}]}
    return {"render_error": result.get("error",""), "retry_count": state.get("retry_count",0)+1, "events": state.get("events",[]) + [{"phase":"critic","data":{"success":False,"error":result.get("error","")[:300]},"message":f"🔧 Self-healing {state.get('retry_count',0)+1}/{MAX_CRITIC_RETRIES}"}]}

def _should_continue(state):
    return "retry" if state.get("render_error") and state.get("retry_count",0) < MAX_CRITIC_RETRIES else "done"

_wf = StateGraph(VideoProductionState)
_wf.add_node("researcher", _researcher_node)
_wf.add_node("scriptwriter", _scriptwriter_node)
_wf.add_node("manim_coder", _manim_coder_node)
_wf.add_node("critic", _critic_node)
_wf.set_entry_point("researcher")
_wf.add_edge("researcher", "scriptwriter")
_wf.add_edge("scriptwriter", "manim_coder")
_wf.add_edge("manim_coder", "critic")
_wf.add_conditional_edges("critic", _should_continue, {"retry": "manim_coder", "done": END})
graph = _wf.compile()


# ─────────────────────────────────────────────────────────────────────────────
# FastAPI App
# ─────────────────────────────────────────────────────────────────────────────

app = FastAPI(title="STEM AI Video Orchestrator", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.post("/storyboard")
async def storyboard(req: StoryboardRequest):
    """Phase 1: Stream researcher + scriptwriter results for UI storyboard display."""
    return StreamingResponse(
        _stream_storyboard(req),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.post("/render_scenes")
async def render_scenes(req: RenderScenesRequest):
    """Phase 2: Stream manim coder + critic (syntax + visual healing) progress."""
    return StreamingResponse(
        _stream_render(req),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.post("/render_final")
def render_final(req: FinalRenderRequest):
    """Phase 3: Trigger 4K high-quality render after user approves preview."""
    return run_final_render(req.output_folder, req.orientation)


@app.post("/create")
async def create_video(req: CreateJobRequest):
    """Legacy: full pipeline in one shot via LangGraph."""
    output_folder = req.output_folder or os.path.join(
        tempfile.gettempdir(), "stem_output", f"job_{int(time.time())}"
    )
    os.makedirs(output_folder, exist_ok=True)

    initial_state: VideoProductionState = {
        "topic": req.topic, "audience": req.audience, "style": req.style,
        "metaphor": req.metaphor, "source_material": req.source_material,
        "persona_id": req.persona_id, "output_folder": output_folder,
        "orientation": req.orientation, "learning_steps": [], "script_scenes": [],
        "manim_classes": [], "render_error": "", "retry_count": 0,
        "preview_path": "", "events": [],
    }

    loop = asyncio.get_event_loop()
    q: asyncio.Queue = asyncio.Queue()

    def run_graph():
        try:
            for step in graph.stream(initial_state):
                q.put_nowait(("step", step))
            q.put_nowait(("done", None))
        except Exception as exc:
            q.put_nowait(("error", str(exc)))

    loop.run_in_executor(executor, run_graph)

    async def _gen():
        while True:
            kind, payload = await q.get()
            if kind == "error":
                yield _sse("error", {"message": payload}); break
            if kind == "done":
                yield _sse("complete", {"message": "🚀 Done!", "output_folder": output_folder}); break
            node_name  = list(payload.keys())[0]
            node_state = payload[node_name]
            events     = node_state.get("events", [])
            if events:
                ev = events[-1]
                yield _sse(ev["phase"] + "_done", {"message": ev["message"], "data": ev.get("data")})
            await asyncio.sleep(0)

    return StreamingResponse(_gen(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.get("/health")
def health():
    return {"status": "ok", "service": "orchestrator", "port": ORCHESTRATOR_PORT, "version": "2.0.0"}

@app.get("/exit")
def force_exit():
    import os
    os._exit(0)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("orchestrator:app", host="127.0.0.1", port=ORCHESTRATOR_PORT,
                log_level="info", reload=False)
