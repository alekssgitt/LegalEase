from typing import Any, Dict
from .chains import rag_chain, analyze_chain

class Agent:
    def __init__(self):
        pass

    def classify_intent(self, request: Dict[str, Any]) -> str:
        if 'question' in request:
            return "legal_qa"
        elif 'file' in request and 'profile_type' in request:
            return "analyze"
        else:
            return "unknown"

    def route(self, request: Dict[str, Any]):
        intent = self.classify_intent(request)
        if intent == "legal_qa":
            return rag_chain(request)
        elif intent == "analyze":
            return analyze_chain(request)
        else:
            return {"error": "Unknown intent"}
