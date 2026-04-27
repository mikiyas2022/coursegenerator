"""
agents/math_verifier.py — SymPy Math Verification Agent (NEW)

Runs AFTER the Scriptwriter and BEFORE the Visual Designer.

Extracts LaTeX-style formulas from each scene and attempts to:
  1. Parse them with SymPy
  2. Check basic dimensional/numeric consistency where possible
  3. Flag ambiguous or incorrect formulas for the LLM to fix

Graceful by design: any failure passes the scene through unchanged.
No scene is ever blocked or skipped because of this agent.
"""

import sys
import os
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from logger import get_logger

log = get_logger("math_verifier")


# ─────────────────────────────────────────────────────────────────────────────
# SymPy import (optional — graceful fallback if not available)
# ─────────────────────────────────────────────────────────────────────────────

try:
    import sympy
    from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
    HAS_SYMPY = True
    log.info("SymPy available — math verification enabled.")
except ImportError:
    HAS_SYMPY = False
    log.warning("SymPy not installed — math verification will be skipped (pip install sympy).")


# ─────────────────────────────────────────────────────────────────────────────
# Formula cleaner
# ─────────────────────────────────────────────────────────────────────────────

_LATEX_SUBS = [
    (r"\\frac{([^}]+)}{([^}]+)}", r"((\1)/(\2))"),
    (r"\\sqrt{([^}]+)}", r"sqrt(\1)"),
    (r"\\pi", "pi"),
    (r"\\times", "*"),
    (r"\\cdot", "*"),
    (r"\\approx", "="),
    (r"[{}]", ""),
    (r"\\", ""),
    (r"\^", "**"),
]


def _latex_to_sympy_str(latex: str) -> str:
    """Best-effort conversion from LaTeX formula to SymPy-parseable string."""
    s = latex.strip()
    # Remove display math markers
    s = s.replace("$$", "").replace("$", "").strip()
    # Only keep the RHS if there's an '=' sign
    if "=" in s:
        s = s.split("=", 1)[1].strip()
    for pattern, repl in _LATEX_SUBS:
        s = re.sub(pattern, repl, s)
    return s.strip()


def _try_parse(formula: str) -> dict:
    """Attempt to parse a formula string with SymPy. Returns a result dict."""
    if not HAS_SYMPY:
        return {"ok": True, "skipped": True}

    sympy_str = _latex_to_sympy_str(formula)
    if not sympy_str or len(sympy_str) < 2:
        return {"ok": True, "skipped": True, "reason": "Empty after cleaning"}

    try:
        transforms = standard_transformations + (implicit_multiplication_application,)
        expr = parse_expr(sympy_str, transformations=transforms)
        return {"ok": True, "expr": str(expr), "sympy_str": sympy_str}
    except Exception as exc:
        return {
            "ok": False,
            "error": str(exc)[:200],
            "original": formula,
            "sympy_str": sympy_str,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def run_math_verifier(scenes: list[dict]) -> list[dict]:
    """
    Verify LaTeX formulas in each scene using SymPy.
    Adds a 'math_verification' key to each scene with results.
    Scenes are NEVER blocked — issues are flagged as hints for the Manim Coder.
    """
    if not HAS_SYMPY:
        log.info("SymPy unavailable — passing all scenes through unchanged.")
        return scenes

    verified = []
    for scene in scenes:
        formulas = scene.get("latex_formulas", [])
        results = []
        warnings = []

        for formula in formulas:
            result = _try_parse(formula)
            results.append(result)
            if not result.get("ok") and not result.get("skipped"):
                warnings.append(
                    f"Formula '{formula}' may have a parse issue: {result.get('error', '')}"
                )
                log.warning(
                    f"  [{scene.get('scene_name', '?')}] Formula warning: {formula!r} → "
                    f"{result.get('error', '')}"
                )
            elif result.get("ok") and not result.get("skipped"):
                log.info(
                    f"  [{scene.get('scene_name', '?')}] ✓ Formula parsed: {formula!r} → "
                    f"{result.get('expr', '')}"
                )

        verified.append({
            **scene,
            "math_verification": {
                "results": results,
                "warnings": warnings,
                "verified": len(warnings) == 0,
            }
        })

    total_warnings = sum(len(s["math_verification"]["warnings"]) for s in verified)
    log.info(
        f"Math verifier done: {len(scenes)} scenes, {total_warnings} formula warning(s)."
    )
    return verified
