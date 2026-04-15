# agent_core/__init__.py
# Package marker — do not define get_llm() here.
# All agents import directly from agent_core.config:
#   from config import get_llm, get_vl_llm, VENV_MANIM, ...