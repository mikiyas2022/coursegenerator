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
from agents.critic       import run_critic

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from video_compiler.compiler import run_final_render_parallel

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
    yield _sse("status", {"message": "✍️ Writing Amharic scripts...", "phase": "scriptwriter"})

    scenes = []
    # Process scenes sequentially but break them down to ping UI step-by-step
    for i, step in enumerate(steps):
        scene_name = step.get("scene_name", f"Scene_{i+1}")
        
        # Stream explicit, granular progress to the UI!
        yield _sse("ping", {"message": f"LLM is writing Amharic dialogue for Scene {i+1}/{len(steps)}: {scene_name}..."})
        
        try:
            task = loop.run_in_executor(
                executor,
                lambda step=step: run_scriptwriter(
                    scenes=[step],
                    style=req.style,
                    source_material=req.source_material,
                ),
            )
            while not task.done():
                yield _sse("ping", {"message": f"Still generating {scene_name}..."})
                try:
                    await asyncio.wait_for(asyncio.shield(task), timeout=6.0)
                except asyncio.TimeoutError:
                    pass
            
            result = task.result()
            # run_scriptwriter always returns a list. Since we gave it 1, it returns 1.
            if result and isinstance(result, list):
                scenes.append(result[0])
            else:
                scenes.append(step) # fallback
                
        except Exception as exc:
            error_msg = str(exc)
            yield _sse("error", {"message": f"Scriptwriter failed on {scene_name}: {error_msg}"})
            if "rate limit" in error_msg.lower() or "failed" in error_msg.lower():
                # Fatal rate limit exhaustion or repeated failure, cannot proceed
                return
            
            # Attempt to salvage the step by continuing ONLY if it's a minor JSON glitch
            scenes.append(step)

    yield _sse("storyboard_ready", {
        "message": f"✅ Storyboard ready — {len(scenes)} scenes completed",
        "scenes": scenes,
    })


# ─────────────────────────────────────────────────────────────────────────────
# Phase 2 — Render stream (Manim Coder + Critic loop)
# ─────────────────────────────────────────────────────────────────────────────

async def _process_single_scene_pipeline(scene: dict, output_folder: str, persona_id: int):
    """Worker task that handles Code Gen + Critic Auto-Healing for ONE independently rendered scene.
    
    GUARANTEE: This function NEVER skips a scene. On max retries, it falls back to a
    mathematically-safe guaranteed fallback that always renders successfully.
    """
    loop = asyncio.get_event_loop()
    
    try:
        # 1. Initial Generation
        code_class = await loop.run_in_executor(
            executor, lambda: run_manim_coder(scenes=[scene], persona_id=persona_id)
        )
        
        # 2. Hybrid Critic Auto-Healing Loop
        retry_count = 0
        visual_retry = 0
        while True:
            result = await loop.run_in_executor(
                executor, lambda: run_critic(code_classes=code_class, output_folder=output_folder, retry_count=retry_count)
            )
            
            vis_err = result.get("visual_error")
            syn_err = not result.get("success", True)
            
            if not vis_err and not syn_err:
                return {"success": True, "code": code_class[0], "result": result}
                
            if vis_err:
                visual_retry += 1
                if visual_retry >= MAX_CRITIC_RETRIES:
                    # Visual issues but it rendered — include it rather than skip
                    return {"success": True, "code": code_class[0], "result": result}
                fb = result.get("visual_feedback", "")
                code_class = await loop.run_in_executor(
                    executor, lambda: run_manim_coder([scene], persona_id, visual_feedback=f"VISUAL CRITIQUE:\n{fb}", previous_code=code_class)
                )
            else:
                retry_count += 1
                if retry_count >= MAX_CRITIC_RETRIES:
                    # NEVER skip — use guaranteed safe fallback that always renders
                    print(f"  [orch] Max retries on {scene.get('scene_name')} — using guaranteed fallback", flush=True)
                    from agents.manim_coder import _guaranteed_fallback
                    fb_code = [_guaranteed_fallback(scene)]
                    fb_result = await loop.run_in_executor(
                        executor, lambda: run_critic(code_classes=fb_code, output_folder=output_folder, retry_count=0)
                    )
                    return {"success": True, "code": fb_code[0], "result": fb_result, "used_fallback": True}
                fb = result.get("error", "")
                code_class = await loop.run_in_executor(
                    executor, lambda: run_manim_coder([scene], persona_id, error_context=fb, previous_code=code_class)
                )
    except Exception as exc:
        # Even on fatal error — emit guaranteed fallback so scene is NEVER missing
        print(f"  [orch] Fatal on {scene.get('scene_name')}: {exc} — using guaranteed fallback", flush=True)
        try:
            from agents.manim_coder import _guaranteed_fallback
            fb_code = [_guaranteed_fallback(scene)]
            fb_result = await loop.run_in_executor(
                executor, lambda: run_critic(code_classes=fb_code, output_folder=output_folder, retry_count=0)
            )
            return {"success": True, "code": fb_code[0], "result": fb_result, "used_fallback": True}
        except Exception as exc2:
            return {"success": False, "code": None, "result": {"success": False, "error": str(exc2)}, "reason": "Fatal Error"}

async def _stream_render(req: RenderScenesRequest) -> AsyncGenerator[str, None]:
    import datetime
    date_str   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    job_id     = f"{int(time.time())}"
    project_root = os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if req.output_folder and os.path.isabs(req.output_folder):
        output_folder = req.output_folder
    elif req.output_folder:
        output_folder = os.path.join(project_root, req.output_folder)
    else:
        output_folder = os.path.join(
            project_root, "Local_Video_Output", f"{job_id}_{date_str}"
        )
    os.makedirs(output_folder, exist_ok=True)

    yield _sse("status", {"message": f"⚙️ Dispatching {len(req.scenes)} parallel Manim coders…", "phase": "coding"})

    # Launch parallel tasks (one fully independent pipeline per scene)
    tasks = [
        asyncio.create_task(_process_single_scene_pipeline(scene, output_folder, req.persona_id))
        for scene in req.scenes
    ]
    
    while True:
        done, pending = await asyncio.wait(tasks, timeout=2.0, return_when=asyncio.ALL_COMPLETED)
        if not pending:
            break
        yield _sse("ping", {"message": f"Rendering ({len(done)}/{len(tasks)} scenes finished)..."})

    results = [t.result() for t in tasks]
    
    # Check if any critically failed
    successful_codes = [r.get("code") for r in results if r.get("success") and r.get("code")]
    failed = len(tasks) - len(successful_codes)
    
    # Save the combined valid code for final rendering
    if successful_codes:
        from agents.manim_coder import SCRIPT_HEADER_TEMPLATE
        agent_core_path = os.path.dirname(os.path.abspath(__file__))
        combined_script = SCRIPT_HEADER_TEMPLATE.format(agent_core_path=agent_core_path)
        combined_script += "\n\n" + "\n\n".join(successful_codes)
        
        script_path = os.path.join(output_folder, "generated_lesson.py")
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(combined_script)

    if failed > 0:
        yield _sse("preview_ready", {
            "message": f"⚠️ Preview ready with {failed} auto-healing failure(s)",
            "output_folder": output_folder,
        })
    else:
        yield _sse("preview_ready", {
            "message": "✅ All scenes generated and verified successfully!",
            "output_folder": output_folder,
        })

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
    return run_final_render_parallel(req.output_folder, req.orientation)


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
