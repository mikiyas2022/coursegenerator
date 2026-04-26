"""
agents/researcher.py — Pedagogical Research Agent

Takes high-level topic inputs and produces a structured, logical
learning journey as a list of scene dicts. Each scene defines:
  - The concept to teach
  - The visual representation
  - The narrative hook for the audience
"""

import json
import re

from langchain_core.messages import HumanMessage, SystemMessage
from utils import safe_json_loads

# Use sys.path-safe absolute import when run as part of the package
import sys, os
os.environ["HF_HOME"] = "/tmp/huggingface_cache"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import get_llm, RESEARCHER_MODEL

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

SYSTEM_PROMPT = """You are an educational content designer. Break a STEM topic into 4-5 structured scene beats.
Output ONLY a valid JSON array, no markdown, no explanation.

JSON schema per scene:
{
  "scene_name": "Scene1_Intro",
  "concept": "Short concept name",
  "explanation": "What to teach in this scene, including key maths/physics steps",
  "visual": "Detailed Manim animation request: what shapes, graphs, vectors, or diagrams to draw and animate",
  "narrative_hook": "How to make this scene engaging",
  "latex_formulas": ["F = ma"]
}

Must include: one real-world analogy scene and one worked example scene with numbers."""

def filter_source_material(topic: str, source_material: str) -> str:
    """Uses FAISS local RAG to extract only the 4 most relevant chunks to the topic."""
    if not source_material or len(source_material.strip()) < 10:
        return ""

    # For short texts (<2000 chars), pass the full text directly — no need for RAG compression
    if len(source_material) < 2000:
        return source_material.strip()

    print(f"  [researcher] RAG: Compressing {len(source_material)} characters of source material...", flush=True)
    
    # We strictly enforce local file caching. MiniLM requires zero internet since it's already in /tmp.
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    splitter   = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks     = splitter.split_text(source_material)
    
    vectorstore = FAISS.from_texts(chunks, embeddings)
    best_docs   = vectorstore.similarity_search(topic, k=4)
    compressed  = "\n\n... ".join(doc.page_content for doc in best_docs)
    print(f"  [researcher] RAG: Compressed context to {len(compressed)} characters.", flush=True)
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
    """
    print("  [researcher] Prompting LLM...", flush=True)
    llm = get_llm(model_name=RESEARCHER_MODEL, temperature=0.2, max_tokens=1200)
    filtered_source = filter_source_material(topic, source_material)

    user_prompt = f"""Topic: {topic}
Audience Level: {audience}
Narrative Style: {style}
Visual Metaphor / Theme: {metaphor or "Abstract mathematical animations"}

{'--- SOURCE MATERIAL (MUST BE USED) ---' if filtered_source else ''}
{filtered_source if filtered_source else ''}
{'--- END SOURCE MATERIAL ---' if filtered_source else ''}

{'CRITICAL: Your scene concepts and explanations MUST be grounded in and derived from the SOURCE MATERIAL above.' if filtered_source else 'No source material provided — use your knowledge.'}
{'Do NOT invent facts that contradict or are absent from the source material.' if filtered_source else ''}

Break this topic into 4–6 structured scene beats. Output the JSON array."""

    try:
        response = llm.invoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ])
        
        scenes = safe_json_loads(response.content.strip())
        
        if not isinstance(scenes, list) or not scenes:
            raise ValueError("LLM returned empty or non-list JSON")

        print(f"  [researcher] {len(scenes)} scenes planned.", flush=True)
        return scenes

    except Exception as exc:
        error_msg = str(exc)
        print(f"  [researcher] LLM error: {error_msg}", flush=True)
        if "429" in error_msg or "Rate limit" in error_msg or "quota" in error_msg.lower():
            raise RuntimeError(f"OpenRouter API Rate Limit Exceeded: Please add credits. {error_msg[:120]}")
        raise RuntimeError(f"Researcher generation failed: {error_msg}")
