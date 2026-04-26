import os
import sys
import json
agent_core_path = os.path.join(os.path.dirname(__file__), "agent_core")
sys.path.insert(0, agent_core_path)

from config import get_llm, SCRIPTWRITER_MODEL
from agents.scriptwriter import SYSTEM_PROMPT
from langchain_core.messages import SystemMessage, HumanMessage

def test():
    llm = get_llm(SCRIPTWRITER_MODEL)
    print(f"Testing {SCRIPTWRITER_MODEL} on scriptwriter prompt...")
    user_prompt = "Topic: Vector Addition. Concept: Tip-to-tail method."
    resp = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_prompt)
    ]).content
    print("RAW OUTPUT:")
    print(resp)

test()
