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

# Use sys.path-safe absolute import when run as part of the package
import sys, os
os.environ["HF_HOME"] = "/tmp/huggingface_cache"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import get_llm

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

SYSTEM_PROMPT = """You are a world-class educational content designer and pedagogue.
Your task: break a topic into a structured learning journey for video lessons.

OUTPUT: Valid JSON array ONLY. No markdown, no explanation, no code fences.

Each element is ONE scene. Rules:
- 4 to 6 scenes maximum
- Each scene MUST build logically on the previous
- Visuals MUST be describable as Manim Community Edition animations
  (geometric shapes, arrows, coordinate planes, LaTeX formulas, graphs)
- Keep concepts appropriate for the specified audience level
- The last scene should include a summary / takeaway

JSON schema per scene:
{
  "scene_name": "Scene1_Intro",
  "concept": "One-line concept name",
  "explanation": "2-3 sentences of what to teach in this beat",
  "visual": "Specific Manim visual description (e.g. 'Draw a right triangle with labeled sides a, b, c on a coordinate grid')",
  "narrative_hook": "How to make this engaging for the audience",
  "latex_formulas": ["F = ma", "W = Fd"]
}"""

def filter_source_material(topic: str, source_material: str) -> str:
    """Uses FAISS local RAG to extract only the 4 most relevant chunks to the topic."""
    if not source_material or len(source_material) < 2000:
        return source_material

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
    llm = get_llm(temperature=0.2)
    filtered_source = filter_source_material(topic, source_material)

    user_prompt = f"""Topic: {topic}
Audience Level: {audience}
Narrative Style: {style}
Visual Metaphor / Theme: {metaphor or "Abstract mathematical animations"}
Source Material: {filtered_source if filtered_source else "None provided — use your knowledge."}

Break this topic into 4–6 structured scene beats. Output the JSON array."""

    try:
        response = llm.invoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ])
        raw = response.content.strip()

        # Strip markdown fences if the LLM added them
        raw = re.sub(r"```(?:json)?", "", raw).strip().rstrip("```").strip()

        scenes = json.loads(raw)
        if not isinstance(scenes, list) or not scenes:
            raise ValueError("LLM returned empty or non-list JSON")

        print(f"  [researcher] {len(scenes)} scenes planned.", flush=True)
        return scenes

    except Exception as exc:
        print(f"  [researcher] LLM error ({exc}). Using minimal fallback.", flush=True)
        # Graceful fallback so the pipeline doesn't crash
        return [
            {
                "scene_name": "Scene1_Intro",
                "concept": f"Introduction to {topic}",
                "explanation": f"We introduce the core idea of {topic} for {audience} students.",
                "visual": "Fade in title text centred on dark background",
                "narrative_hook": "Open with a thought-provoking question",
                "latex_formulas": ["F = ma", "E = mc^2"],
            },
            {
                "scene_name": "Scene2_Core",
                "concept": f"Core principles of {topic}",
                "explanation": "We explore the key mathematical or conceptual foundation.",
                "visual": "Draw labeled diagram or formula using Write() animation",
                "narrative_hook": "Show a real-world application",
                "latex_formulas": ["A^2 + B^2 = C^2"],
            },
            {
                "scene_name": "Scene3_Summary",
                "concept": "Summary and takeaway",
                "explanation": "We recap the key points and leave students with a clear mental model.",
                "visual": "Fade in a summary bullet list",
                "narrative_hook": "Challenge students to apply this to a new problem",
                "latex_formulas": ["\\sum_i F_i = 0"],
            },
        ]
