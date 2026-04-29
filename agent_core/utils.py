import re
import json

def clean_json_response(raw: str) -> str:
    """
    Robustly extract and clean JSON from LLM output.
    Handles markdown fences, unescaped newlines, and trailing characters.
    """
    # 1. Strip markdown fences
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)
    if match:
        raw = match.group(1).strip()
    else:
        # Try to find anything between the first { or [ and last } or ]
        start_obj = raw.find("{")
        start_arr = raw.find("[")
        
        # Decide if it starts as an object or array
        start = start_obj if start_obj != -1 else start_arr
        if start_obj != -1 and start_arr != -1:
            start = min(start_obj, start_arr)
            
        end_obj = raw.rfind("}")
        end_arr = raw.rfind("]")
        
        end = end_obj if end_obj != -1 else end_arr
        if end_obj != -1 and end_arr != -1:
            end = max(end_obj, end_arr)
            
        if start != -1 and end != -1 and end > start:
            raw = raw[start:end+1]
        else:
            raw = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()

    # 2. Fix common JSON syntax hallucinations
    # Escape raw newlines and tabs inside strings
    def _escape_controls(m):
        return m.group(0).replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t")
    
    cleaned = re.sub(r'"[^"]*"', _escape_controls, raw)
    
    # Remove problematic trailing commas before closing braces
    cleaned = re.sub(r',\s*\}', '}', cleaned)
    cleaned = re.sub(r',\s*\]', ']', cleaned)
    
    return cleaned

def safe_json_loads(raw: str):
    """Attempt to parse JSON with multiple fallback cleaning steps."""
    try:
        return json.loads(raw)
    except Exception:
        try:
            cleaned = clean_json_response(raw)
            return json.loads(cleaned)
        except Exception as e:
            # Last ditch effort: simple replacement of common errors
            try:
                second_pass = raw.replace('\\', '\\\\').replace('\\\\"', '\\"')
                return json.loads(second_pass)
            except:
                raise e
