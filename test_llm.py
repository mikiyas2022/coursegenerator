import os
import sys

# Append agent_core path correctly for importing config
agent_core_path = os.path.join(os.path.dirname(__file__), "agent_core")
sys.path.insert(0, agent_core_path)

from config import get_llm, RESEARCHER_MODEL
from langchain_core.messages import HumanMessage

def test():
    print(f"Testing local Ollama model: {RESEARCHER_MODEL} via 11434")
    llm = get_llm(RESEARCHER_MODEL, temperature=0.1, max_tokens=100)
    try:
        response = llm.invoke([HumanMessage(content="Say 'Local AI is working!'")])
        print("Success! Output:", response.content)
    except Exception as e:
        print("Failed:", str(e))

if __name__ == "__main__":
    test()
