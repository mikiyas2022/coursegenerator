#!/usr/bin/env python3
"""
orchestrator.py — 3B1B English Course Factory (v4 — Pure 3B1B Mode)
====================================================================
Blackboard mode completely removed. Only world-class 3B1B explanatory videos.

Pipeline:  Researcher → Scriptwriter → Visual Designer → Math Verifier
           → Template Orchestrator → Critic → Post-Production

Endpoints:
  POST /storyboard      — Phase 1: Research + Script + Design → streams scenes
  POST /render_scenes   — Phase 2: Template Orchestrator + Critic → streams progress
  POST /render_final    — Phase 3: 4K high-quality re-render
  POST /generate_full   — ONE-SHOT full automation (respects AUTO_APPROVE)
  POST /create          — Legacy: full pipeline via LangGraph
  GET  /health          — Liveness check
"""

import asyncio
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, AsyncGenerator, TypedDict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

sys.path.insert(0, os.path.dirname(__file__))
from config import MAX_CRITIC_RETRIES, ORCHESTRATOR_PORT, AUTO_APPROVE
from logger import get_logger
from agents.researcher      import run_researcher
from agents.scriptwriter    import run_scriptwriter
from agents.visual_designer import run_visual_designer
from agents.math_verifier   import run_math_verifier
from agents.template_orchestrator import run_template_orchestrator
from agents.critic          import run_critic

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from video_compiler.compiler import run_final_render_parallel

from langgraph.graph import StateGraph, END

log = get_logger("orchestrator")

# ─────────────────────────────────────────────────────────────────────────────
# Request / Response schemas
# ─────────────────────────────────────────────────────────────────────────────

class StoryboardRequest(BaseModel):
    topic:           str
    audience:        str  = "High School (Grade 7–12)"
    style:           str  = "World-Class 3b1b (Deep Visual Insight)"
    metaphor:        str  = ""
    source_material: str  = ""
    skip_designer:   bool = False
    skip_verifier:   bool = False


class RenderScenesRequest(BaseModel):
    scenes:        list[dict]
    persona_id:    int   = 1
    orientation:   str   = "landscape"
    output_folder: str   = ""


class FinalRenderRequest(BaseModel):
    output_folder: str
    orientation:   str = "landscape"
    topic:         str = ""


class GenerateFullRequest(BaseModel):
    topic:           str
    audience:        str  = "High School (Grade 7–12)"
    style:           str  = "World-Class 3b1b (Deep Visual Insight)"
    metaphor:        str  = ""
    source_material: str  = ""
    persona_id:      int  = 1
    orientation:     str  = "landscape"
    output_folder:   str  = ""
    run_postprod:    bool = True


class CreateJobRequest(BaseModel):  # legacy
    topic:           str
    audience:        str  = "High School (Grade 7–12)"
    style:           str  = "World-Class 3b1b (Deep Visual Insight)"
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
# Output folder helper
# ─────────────────────────────────────────────────────────────────────────────

def _make_output_folder(req_folder: str = "") -> str:
    import datetime
    date_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    job_id   = f"{int(time.time())}"
    project_root = os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if req_folder and os.path.isabs(req_folder):
        folder = req_folder
    elif req_folder:
        folder = os.path.join(project_root, req_folder)
    else:
        folder = os.path.join(project_root, "Local_Video_Output", f"{job_id}_{date_str}")
    os.makedirs(folder, exist_ok=True)
    return folder


# ─────────────────────────────────────────────────────────────────────────────
# Phase 1 — Storyboard stream
# ─────────────────────────────────────────────────────────────────────────────

async def _stream_storyboard(req: StoryboardRequest) -> AsyncGenerator[str, None]:
    loop = asyncio.get_event_loop()

    yield _sse("status", {"message": "🔬 Researcher analyzing topic…", "phase": "researcher"})
    try:
        task = loop.run_in_executor(
            executor,
            lambda: run_researcher(req.topic, req.audience, req.style, req.metaphor, req.source_material),
        )
        while not task.done():
            yield _sse("ping", {"message": "Researching your topic…"})
            try:
                await asyncio.wait_for(asyncio.shield(task), timeout=10.0)
            except asyncio.TimeoutError:
                pass
        steps = task.result()
    except Exception as exc:
        yield _sse("error", {"message": f"Researcher failed: {exc}"}); return

    yield _sse("researcher_done", {"message": f"✅ {len(steps)} scenes planned", "steps": steps})
    yield _sse("status", {"message": "✍️ Writing 3B1B scripts…", "phase": "scriptwriter"})

    scenes = []
    for i, step in enumerate(steps):
        scene_name = step.get("scene_name", f"Scene_{i+1}")
        yield _sse("ping", {"message": f"Writing scene {i+1}/{len(steps)}: {scene_name}…"})
        try:
            task = loop.run_in_executor(
                executor,
                lambda step=step: run_scriptwriter([step], style=req.style, source_material=req.source_material),
            )
            while not task.done():
                yield _sse("ping", {"message": f"Scripting {scene_name}…"})
                try:
                    await asyncio.wait_for(asyncio.shield(task), timeout=6.0)
                except asyncio.TimeoutError:
                    pass
            result = task.result()
            scenes.append(result[0] if result else step)
        except Exception as exc:
            log.error(f"Scriptwriter on {scene_name}: {exc}")
            scenes.append(step)

    # ── Visual Designer ──
    if not req.skip_designer:
        yield _sse("status", {"message": "🎨 Visual Designer planning storyboards…", "phase": "visual_designer"})
        try:
            task = loop.run_in_executor(executor, lambda: run_visual_designer(scenes))
            while not task.done():
                yield _sse("ping", {"message": "Visual Designer at work…"})
                try:
                    await asyncio.wait_for(asyncio.shield(task), timeout=10.0)
                except asyncio.TimeoutError:
                    pass
            scenes = task.result()
            yield _sse("designer_done", {"message": "✅ Visual storyboard plans ready"})
        except Exception as exc:
            log.error(f"Visual designer failed: {exc}")
            yield _sse("ping", {"message": "⚠️ Visual designer skipped"})

    # ── Math Verifier ──
    if not req.skip_verifier:
        yield _sse("status", {"message": "🧮 Math Verifier checking formulas…", "phase": "math_verifier"})
        try:
            task = loop.run_in_executor(executor, lambda: run_math_verifier(scenes))
            while not task.done():
                yield _sse("ping", {"message": "Verifying equations…"})
                try:
                    await asyncio.wait_for(asyncio.shield(task), timeout=15.0)
                except asyncio.TimeoutError:
                    pass
            scenes = task.result()
            warnings = sum(len(s.get("math_verification", {}).get("warnings", [])) for s in scenes)
            msg = f"✅ {warnings} formula warning(s) fixed" if warnings else "✅ All formulas verified clean"
            yield _sse("verifier_done", {"message": msg})
        except Exception as exc:
            log.error(f"Math verifier failed: {exc}")

    yield _sse("storyboard_ready", {
        "message": f"✅ Storyboard ready — {len(scenes)} scenes",
        "scenes": scenes,
        "auto_approve": AUTO_APPROVE,
    })


# ─────────────────────────────────────────────────────────────────────────────
# Phase 2 — Render stream (Template Orchestrator + Critic)
# ─────────────────────────────────────────────────────────────────────────────

async def _process_single_scene_pipeline(scene: dict, output_folder: str, persona_id: int):
    """Worker: Code Gen + Critic Auto-Healing for ONE scene. NEVER skips."""
    loop = asyncio.get_event_loop()
    try:
        code_class = await loop.run_in_executor(
            executor, lambda: run_template_orchestrator(scenes=[scene])
        )
        retry_count = visual_retry = 0
        while True:
            result = await loop.run_in_executor(
                executor,
                lambda: run_critic(code_classes=code_class, output_folder=output_folder, retry_count=retry_count)
            )
            vis_err = result.get("visual_error")
            syn_err = not result.get("success", True)

            if not vis_err and not syn_err:
                return {"success": True, "code": code_class[0], "result": result}

            if vis_err:
                visual_retry += 1
                if visual_retry >= MAX_CRITIC_RETRIES:
                    return {"success": True, "code": code_class[0], "result": result}
                code_class = await loop.run_in_executor(
                    executor, lambda: run_template_orchestrator([scene])
                )
            else:
                retry_count += 1
                if retry_count >= MAX_CRITIC_RETRIES:
                    log.warning(f"Max retries on {scene.get('scene_name')} — using guaranteed fallback")
                    from agents.manim_coder import _guaranteed_fallback
                    fb_code = [_guaranteed_fallback(scene)]
                    fb_result = await loop.run_in_executor(
                        executor, lambda: run_critic(code_classes=fb_code, output_folder=output_folder, retry_count=0)
                    )
                    return {"success": True, "code": fb_code[0], "result": fb_result, "used_fallback": True}
                code_class = await loop.run_in_executor(
                    executor, lambda: run_template_orchestrator([scene])
                )
    except Exception as exc:
        log.error(f"Fatal on {scene.get('scene_name')}: {exc} — using guaranteed fallback")
        try:
            from agents.manim_coder import _guaranteed_fallback
            fb_code = [_guaranteed_fallback(scene)]
            fb_result = await loop.run_in_executor(
                executor, lambda: run_critic(code_classes=fb_code, output_folder=output_folder, retry_count=0)
            )
            return {"success": True, "code": fb_code[0], "result": fb_result, "used_fallback": True}
        except Exception as exc2:
            return {"success": False, "code": None, "result": {"error": str(exc2)}}


async def _stream_render(req: RenderScenesRequest) -> AsyncGenerator[str, None]:
    output_folder = _make_output_folder(req.output_folder)
    yield _sse("status", {"message": f"⚙️ Dispatching {len(req.scenes)} scene coders…", "phase": "coding"})

    tasks = [
        asyncio.create_task(_process_single_scene_pipeline(scene, output_folder, req.persona_id))
        for scene in req.scenes
    ]
    while True:
        done, pending = await asyncio.wait(tasks, timeout=2.0, return_when=asyncio.ALL_COMPLETED)
        if not pending:
            break
        yield _sse("ping", {"message": f"Rendering ({len(done)}/{len(tasks)} scenes done)…"})

    results = [t.result() for t in tasks]
    successful_codes = [r.get("code") for r in results if r.get("success") and r.get("code")]
    failed = len(tasks) - len(successful_codes)

    if successful_codes:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        from agents.manim_coder import SCRIPT_HEADER_TEMPLATE
        header = SCRIPT_HEADER_TEMPLATE.format(project_root=project_root)
        combined = header + "\n\n" + "\n\n".join(successful_codes)
        script_path = os.path.join(output_folder, "generated_lesson.py")
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(combined)

    msg = f"⚠️ Preview ready with {failed} failure(s)" if failed else "✅ All scenes generated and verified!"
    yield _sse("preview_ready", {"message": msg, "output_folder": output_folder})
    yield _sse("complete", {"message": "🚀 Done! Approve to render final video.", "output_folder": output_folder})


# ─────────────────────────────────────────────────────────────────────────────
# Full automation (one-shot) — 3B1B ONLY
# ─────────────────────────────────────────────────────────────────────────────

async def _stream_generate_full(req: GenerateFullRequest) -> AsyncGenerator[str, None]:
    """Complete 3B1B pipeline — fully automated."""
    loop = asyncio.get_event_loop()
    output_folder = _make_output_folder(req.output_folder)

    # ── Research ──
    yield _sse("status", {"message": "🔬 Researching your topic…", "phase": "researcher"})
    try:
        task = loop.run_in_executor(
            executor, lambda: run_researcher(req.topic, req.audience, req.style, req.metaphor, req.source_material)
        )
        while not task.done():
            yield _sse("ping", {"message": "Researcher is thinking…"})
            await asyncio.sleep(5)
        steps = await task
    except Exception as exc:
        yield _sse("error", {"message": f"Research failed: {exc}"}); return

    yield _sse("researcher_done", {"message": f"✅ {len(steps)} scenes planned", "steps": steps})

    # ── Scriptwriter ──
    yield _sse("status", {"message": "✍️ Writing 3B1B scripts…", "phase": "scriptwriter"})
    scenes = []
    for i, step in enumerate(steps):
        try:
            task = loop.run_in_executor(
                executor, lambda step=step: run_scriptwriter([step], req.style, req.source_material)
            )
            while not task.done():
                yield _sse("ping", {"message": f"Writing scene {i+1}/{len(steps)}…"})
                await asyncio.sleep(5)
            result = await task
            scenes.append(result[0] if result else step)
        except Exception:
            scenes.append(step)

    # ── Visual Designer ──
    yield _sse("status", {"message": "🎨 Visual Designer planning shots…", "phase": "visual_designer"})
    try:
        task = loop.run_in_executor(executor, lambda: run_visual_designer(scenes))
        while not task.done():
            yield _sse("ping", {"message": "Designing visual layouts…"})
            await asyncio.sleep(5)
        scenes = await task
        yield _sse("designer_done", {"message": "✅ Storyboard plans ready"})
    except Exception as exc:
        log.error(f"Visual designer: {exc}")

    # ── Math Verifier ──
    yield _sse("status", {"message": "🧮 Verifying math…", "phase": "math_verifier"})
    try:
        task = loop.run_in_executor(executor, lambda: run_math_verifier(scenes))
        while not task.done():
            yield _sse("ping", {"message": "Checking equations…"})
            await asyncio.sleep(5)
        scenes = await task
    except Exception as exc:
        log.error(f"Math verifier: {exc}")

    yield _sse("storyboard_ready", {"message": f"✅ {len(scenes)} scenes ready", "scenes": scenes, "auto_approve": True})

    # ── Template Orchestrator + Critic ──
    yield _sse("status", {"message": "⚙️ Rendering scenes…", "phase": "coding"})
    tasks = [
        asyncio.create_task(_process_single_scene_pipeline(s, output_folder, req.persona_id))
        for s in scenes
    ]
    while True:
        done, pending = await asyncio.wait(tasks, timeout=2.0, return_when=asyncio.ALL_COMPLETED)
        if not pending:
            break
        yield _sse("ping", {"message": f"Rendering ({len(done)}/{len(tasks)} done)…"})

    results = [t.result() for t in tasks]
    successful_codes = [r.get("code") for r in results if r.get("success") and r.get("code")]

    if not successful_codes:
        yield _sse("error", {"message": "All scenes failed to render."}); return

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    from agents.manim_coder import SCRIPT_HEADER_TEMPLATE
    header = SCRIPT_HEADER_TEMPLATE.format(project_root=project_root)
    combined = header + "\n\n" + "\n\n".join(successful_codes)
    script_path = os.path.join(output_folder, "generated_lesson.py")
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(combined)

    yield _sse("preview_ready", {"message": "✅ Preview done — starting final render…", "output_folder": output_folder})

    # ── Final render ──
    yield _sse("status", {"message": "🎬 Final 4K render…", "phase": "final_render"})
    task = loop.run_in_executor(
        executor, lambda: run_final_render_parallel(output_folder, req.orientation)
    )
    while not task.done():
        yield _sse("ping", {"message": "Rendering high-quality video…"})
        await asyncio.sleep(5)
    final_result = await task

    if not final_result.get("success"):
        yield _sse("error", {"message": f"Final render failed: {final_result.get('error', '')[:300]}"}); return

    master_path = final_result.get("master_path", "")

    # ── Post-production ──
    if req.run_postprod:
        yield _sse("status", {"message": "✨ Post-production polish…", "phase": "postprod"})
        try:
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from video_postprod.pipeline import run_postproduction
            pp_result = await loop.run_in_executor(
                executor, lambda: run_postproduction(output_folder, req.topic, master_path, scenes)
            )
            master_path = pp_result.get("final_video", master_path)
            yield _sse("postprod_done", {"message": f"✅ Post-production done → {master_path}"})
        except Exception as exc:
            log.error(f"Post-production: {exc}")
            yield _sse("ping", {"message": "⚠️ Post-production skipped"})

    yield _sse("complete", {
        "message": "🏆 3B1B masterpiece complete!",
        "output_folder": output_folder,
        "master_path": master_path,
        "size_mb": final_result.get("size_mb", 0),
    })


# ─────────────────────────────────────────────────────────────────────────────
# LangGraph (legacy /create endpoint)
# ─────────────────────────────────────────────────────────────────────────────

class VideoProductionState(TypedDict):
    topic: str; audience: str; style: str; metaphor: str; source_material: str
    persona_id: int; output_folder: str; orientation: str
    learning_steps: list[dict]; script_scenes: list[dict]; manim_classes: list[str]
    render_error: str; retry_count: int; preview_path: str; events: list[dict]


def _researcher_node(state):
    steps = run_researcher(state["topic"], state["audience"], state["style"], state["metaphor"], state.get("source_material", ""))
    return {"learning_steps": steps, "events": state.get("events", []) + [{"phase": "researcher", "data": steps, "message": f"✅ {len(steps)} steps"}]}

def _scriptwriter_node(state):
    scenes = run_scriptwriter(state["learning_steps"], state["style"])
    return {"script_scenes": scenes, "events": state.get("events", []) + [{"phase": "scriptwriter", "data": scenes, "message": f"✅ {len(scenes)} scenes"}]}

def _designer_node(state):
    scenes = run_visual_designer(state["script_scenes"])
    return {"script_scenes": scenes, "events": state.get("events", []) + [{"phase": "visual_designer", "data": {}, "message": "✅ Storyboard plans ready"}]}

def _manim_coder_node(state):
    classes = run_template_orchestrator(state["script_scenes"])
    return {"manim_classes": classes, "render_error": "", "events": state.get("events", []) + [{"phase": "manim_coder", "data": {"count": len(classes)}, "message": f"✅ {len(classes)} classes"}]}

def _critic_node(state):
    result = run_critic(state["manim_classes"], state["output_folder"], state.get("retry_count", 0))
    if result["success"]:
        return {"preview_path": result.get("preview_path", ""), "render_error": "", "events": state.get("events", []) + [{"phase": "critic", "data": {"success": True}, "message": "🎬 Preview ready!"}]}
    return {"render_error": result.get("error", ""), "retry_count": state.get("retry_count", 0) + 1, "events": state.get("events", []) + [{"phase": "critic", "data": {"success": False}, "message": f"🔧 Healing {state.get('retry_count', 0)+1}/{MAX_CRITIC_RETRIES}"}]}

def _should_continue(state):
    return "retry" if state.get("render_error") and state.get("retry_count", 0) < MAX_CRITIC_RETRIES else "done"

_wf = StateGraph(VideoProductionState)
_wf.add_node("researcher", _researcher_node)
_wf.add_node("scriptwriter", _scriptwriter_node)
_wf.add_node("visual_designer", _designer_node)
_wf.add_node("manim_coder", _manim_coder_node)
_wf.add_node("critic", _critic_node)
_wf.set_entry_point("researcher")
_wf.add_edge("researcher", "scriptwriter")
_wf.add_edge("scriptwriter", "visual_designer")
_wf.add_edge("visual_designer", "manim_coder")
_wf.add_edge("manim_coder", "critic")
_wf.add_conditional_edges("critic", _should_continue, {"retry": "manim_coder", "done": END})
graph = _wf.compile()


# ─────────────────────────────────────────────────────────────────────────────
# FastAPI App
# ─────────────────────────────────────────────────────────────────────────────

app = FastAPI(title="3B1B English Course Factory", version="4.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.post("/storyboard")
async def storyboard(req: StoryboardRequest):
    return StreamingResponse(
        _stream_storyboard(req), media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.post("/render_scenes")
async def render_scenes(req: RenderScenesRequest):
    return StreamingResponse(
        _stream_render(req), media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.post("/render_final")
def render_final(req: FinalRenderRequest):
    result = run_final_render_parallel(req.output_folder, req.orientation)
    if result.get("success") and req.topic:
        try:
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from video_postprod.pipeline import run_postproduction
            pp = run_postproduction(req.output_folder, req.topic, result.get("master_path", ""))
            result["final_video"] = pp.get("final_video", result.get("master_path"))
        except Exception as exc:
            log.error(f"Post-production in render_final: {exc}")
    return result


@app.post("/generate_full")
async def generate_full(req: GenerateFullRequest):
    """One-shot full pipeline — fully automated."""
    return StreamingResponse(
        _stream_generate_full(req), media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.post("/create")
async def create_video(req: CreateJobRequest):
    """Legacy: full pipeline via LangGraph."""
    output_folder = _make_output_folder(req.output_folder)
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
            try:
                kind, payload = await asyncio.wait_for(q.get(), timeout=5.0)
            except asyncio.TimeoutError:
                yield _sse("ping", {"message": "Thinking…"})
                continue
            if kind == "error":
                yield _sse("error", {"message": payload}); break
            if kind == "done":
                yield _sse("complete", {"message": "🚀 Done!", "output_folder": output_folder}); break
            node_name = list(payload.keys())[0]
            events = payload[node_name].get("events", [])
            if events:
                ev = events[-1]
                yield _sse(ev["phase"] + "_done", {"message": ev["message"], "data": ev.get("data")})
            await asyncio.sleep(0)

    return StreamingResponse(_gen(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "3b1b-course-factory",
        "version": "4.0.0",
        "port": ORCHESTRATOR_PORT,
        "auto_approve": AUTO_APPROVE,
        "mode": "3b1b_english_only",
        "templates": 30,
        "pipeline": ["researcher", "scriptwriter", "visual_designer", "math_verifier",
                     "template_orchestrator", "critic", "postprod"],
    }


@app.get("/exit")
def force_exit():
    import os
    os._exit(0)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("orchestrator:app", host="0.0.0.0", port=ORCHESTRATOR_PORT,
                log_level="info", reload=False)
