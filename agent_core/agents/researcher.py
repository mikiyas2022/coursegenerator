"""
agents/researcher.py — 3B1B Pedagogical Research Agent (v3)

Produces 6–10 distinct scene beats for a full 3B1B episode:
  HOOK → ANALOGY → CONCEPT_BUILD → WORKED_EXAMPLE → VISUAL_INSIGHT →
  DEEPER_DIVE → SECOND_EXAMPLE → CONNECTIONS → SUMMARY
"""

import json
import re

from langchain_core.messages import HumanMessage, SystemMessage
from utils import safe_json_loads

import sys, os
os.environ["HF_HOME"] = "/tmp/huggingface_cache"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import get_llm, RESEARCHER_MODEL

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

SYSTEM_PROMPT = """You are a 3Blue1Brown-style educational content architect.
Design a 6–8 scene visual learning journey that feels like a real Grant Sanderson episode.

EPISODE STRUCTURE (follow this arc — every episode needs ALL these types):
1. HOOK: Surprising question or counterintuitive fact that grabs attention
2. ANALOGY: A vivid, animatable everyday analogy (water flow, falling objects, etc.)
3. CONCEPT_BUILD: Core definition built from first principles with visual intuition
4. WORKED_EXAMPLE: Complete step-by-step calculation with SPECIFIC real numbers
5. VISUAL_INSIGHT: Graph, diagram, or animation revealing the "aha!" moment
6. DEEPER_DIVE: A subtle follow-up question that deepens understanding
7. SECOND_EXAMPLE: Second worked example with different numbers/context
8. SUMMARY: Connect everything — the big picture insight + what to explore next

Output ONLY a valid JSON array, no markdown, no explanation.

JSON schema per scene:
{
  "scene_name": "Scene1_Hook",
  "scene_type": "HOOK",
  "concept": "Short concept name (e.g., 'Why Gravity Feels Like Acceleration')",
  "explanation": "DETAILED: step-by-step math, specific formulas, concrete calculations with real numbers",
  "visual": "EXACT Manim animation description: objects, coordinates, how they move",
  "narrative_hook": "The surprising question or fact that opens this scene",
  "latex_formulas": ["F = mg", "a = g = 9.8 m/s²"],
  "worked_example": "Brief description: 'A 2kg ball dropped from 10m — calculates fall time as 1.43s'",
  "key_insight": "The one-line conceptual takeaway of this scene"
}

RULES:
- Each scene teaches something DISTINCT (no redundancy across scenes)
- The 'visual' field must describe EXACT shapes, coordinates, colors, animations
- The 'explanation' field must include REAL NUMBERS and step-by-step math
- WORKED_EXAMPLE scenes MUST have two different numerical examples
- Total scenes: minimum 6, maximum 10
- Scene names must be Python-valid identifiers (no spaces, start with letter)"""


def filter_source_material(topic: str, source_material: str) -> str:
    """Uses FAISS local RAG to extract only the 4 most relevant chunks to the topic."""
    if not source_material or len(source_material.strip()) < 10:
        return ""

    if len(source_material) < 2000:
        return source_material.strip()

    print(f"  [researcher] RAG: Compressing {len(source_material)} chars of source material...", flush=True)

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    splitter   = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks     = splitter.split_text(source_material)

    vectorstore = FAISS.from_texts(chunks, embeddings)
    best_docs   = vectorstore.similarity_search(topic, k=4)
    compressed  = "\n\n... ".join(doc.page_content for doc in best_docs)
    print(f"  [researcher] RAG: Compressed to {len(compressed)} chars.", flush=True)
    return compressed


def run_researcher(
    topic: str,
    audience: str,
    style: str,
    metaphor: str,
    source_material: str,
) -> list[dict]:
    """
    Invoke the Researcher Agent.
    Returns 6–10 structured scene beats for a full 3B1B episode.
    """
    print("  [researcher] Prompting LLM...", flush=True)
    llm = get_llm(model_name=RESEARCHER_MODEL, temperature=0.25, max_tokens=2000)
    filtered_source = filter_source_material(topic, source_material)

    user_prompt = f"""Topic: {topic}
Audience Level: {audience}
Narrative Style: {style}
Visual Metaphor / Theme: {metaphor or "Abstract 3B1B mathematical animations"}

{'--- SOURCE MATERIAL (MUST BE USED) ---' if filtered_source else ''}
{filtered_source if filtered_source else ''}
{'--- END SOURCE MATERIAL ---' if filtered_source else ''}

{'CRITICAL: Ground all explanations in the SOURCE MATERIAL above.' if filtered_source else 'No source material — use your knowledge.'}

Design a complete 6–8 scene 3B1B-style episode. Include: HOOK, ANALOGY, CONCEPT_BUILD, WORKED_EXAMPLE, VISUAL_INSIGHT, DEEPER_DIVE, SECOND_EXAMPLE, SUMMARY.
Each scene must have a distinct concept and unique visual approach.
Output the JSON array of 6–8 scenes."""

    try:
        response = llm.invoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ])

        scenes = safe_json_loads(response.content.strip())

        if not isinstance(scenes, list) or not scenes:
            raise ValueError("LLM returned empty or non-list JSON")

        # Ensure minimum 6 scenes
        if len(scenes) < 6:
            print(f"  [researcher] Only {len(scenes)} scenes — padding to 6", flush=True)
            while len(scenes) < 6:
                scenes.append(_fallback_scene(topic, len(scenes) + 1))

        print(f"  [researcher] {len(scenes)} scenes planned for '{topic}'.", flush=True)
        return scenes

    except Exception as exc:
        error_msg = str(exc)
        print(f"  [researcher] LLM error: {error_msg}", flush=True)
        if "429" in error_msg or "Rate limit" in error_msg or "quota" in error_msg.lower():
            raise RuntimeError(f"OpenRouter API Rate Limit Exceeded: {error_msg[:120]}")
        raise RuntimeError(f"Researcher generation failed: {error_msg}")


def _fallback_scene(topic: str, n: int) -> dict:
    """Generate a fallback scene when the LLM returns too few."""
    scene_types = ["HOOK", "ANALOGY", "CONCEPT_BUILD", "WORKED_EXAMPLE", "VISUAL_INSIGHT", "SUMMARY"]
    st = scene_types[(n - 1) % len(scene_types)]
    return {
        "scene_name": f"Scene{n}_{st.capitalize()}",
        "scene_type": st,
        "concept": topic,
        "explanation": f"Exploring {topic} from a {st.lower()} perspective with real examples.",
        "visual": "Show branded axes, formula box, and animated vectors demonstrating the concept.",
        "narrative_hook": f"What if I told you {topic} works in a surprising way?",
        "latex_formulas": ["F = ma"],
        "worked_example": "With m=5 kg and a=4 m/s², F = 20 N",
        "key_insight": f"The core insight of {topic} is elegant simplicity.",
    }
