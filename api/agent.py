from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableSequence
from langchain_core.language_models.llms import LLM
from typing import Dict, Any, Optional
import logging
from api.chains import analyzeChain, ragChain
from fastapi import UploadFile

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert routing assistant. Your task is to determine if the user's request is for document analysis or for a legal question & answer session.
Based on the user's request summary, output ONLY one of the following keywords:
- 'analyze': Choose this if the user's question is EXACTLY "Analyze this document." and a file is provided. Also choose this if the request implies a general, comprehensive analysis of a document (e.g., asking for summary, key points, risks, recommendations of the whole document).
- 'qa': Choose this if the user asks a specific question AND a document is provided as context to find the answer to that specific question. For example, "Question: 'What does clause 5 of this contract say about termination?' File: 'contract.pdf' provided." should be 'qa'. "Question: 'What are the main cases in this file?' File: 'doc.pdf' provided." should also be 'qa'. If no file is provided and there's only a question, it's 'qa'.

User request summary:
{request_summary}
"""

class LLMRouterAgent:
    def __init__(self, llm: LLM):
        self.llm = llm

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", "User request summary: {request_summary}")
        ])

        self.decision_chain = RunnableSequence(
            prompt_template, 
            self.llm, 
            StrOutputParser()
        )

    def summarizeRequest(self, question: Optional[str], file: Optional[UploadFile]) -> str:
        summary_parts = []
        if question:
            summary_parts.append(f"Question: '{question}'")
        if file:
            summary_parts.append(f"File: '{file.filename}' provided.")
        
        summary = " ".join(summary_parts)
        if not summary:
            summary = "No specific input provided."
        logger.info(f"Routing based on summary: {summary}") 
        return summary

    async def route(self, question: Optional[str] = None, file: Optional[UploadFile] = None, profile_type: Optional[str] = None, experience_level: Optional[str] = None) -> Dict[str, Any]:
        request_summary = self.summarizeRequest(question, file)
        try:
            decision = self.decision_chain.invoke({"request_summary": request_summary}).strip().lower()
            logger.info(f"LLM decision: {decision}")

            if "analyze" in decision:
                logger.info("Routing to analyzeChain.")
                return analyzeChain({"question": question, "file": file, "profile_type": profile_type, "experience_level": experience_level})
            elif "qa" in decision:
                logger.info("Routing to ragChain.")
                return ragChain({"question": question, "file": file, "profile_type": profile_type, "experience_level": experience_level})
            else:
                logger.warning(f"Unknown LLM decision: '{decision}'. Defaulting to RAG chain.")
                return ragChain({"question": question, "file": file, "profile_type": profile_type, "experience_level": experience_level}) # Fallback to RAG for unclear cases
        except Exception as e:
            logger.error(f"Error during routing: {e}", exc_info=True)
            logger.warning("Error in decision process. Defaulting to RAG chain.")
            return ragChain({"question": question, "file": file, "profile_type": profile_type, "experience_level": experience_level})
