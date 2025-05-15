from typing import Dict, Any
from core.llm_manager import LLMManager
from services.document_processor import DocumentProcessor
import logging

logger = logging.getLogger(__name__)

llm_manager_analysis = LLMManager(model_name="LegalAI")
llm_manager_qa = LLMManager(model_name="llama3.2")
document_processor = DocumentProcessor()


def parse_analysis_output(text: str):
    sections = {"summary": "", "key_points": [], "risks": [], "recommendations": []}
    current = "summary"
    for line in text.splitlines():
        l = line.strip()
        if not l:
            continue
        if l.lower().startswith("**key points") or "key points" in l.lower():
            current = "key_points"
            continue
        if l.lower().startswith("**potential risks") or "risk" in l.lower():
            current = "risks"
            continue
        if l.lower().startswith("**recommended") or "recommendation" in l.lower():
            current = "recommendations"
            continue
        if current == "summary":
            sections["summary"] += l + " "
        else:
            sections[current].append(l)
    sections["summary"] = sections["summary"].strip()
    return sections


def analyze_chain(request: Dict[str, Any]) -> Dict[str, Any]:
    file = request['file']
    profile_type = request.get('profile_type', 'user')
    experience_level = request.get('experience_level', 'beginner')
    
    if hasattr(file, 'file'):
        file_content = file.file.read()
        content_type = file.content_type
    else:
        file_content = file.file if hasattr(file, 'file') else file
        content_type = "application/pdf" if getattr(file, 'filename', '').lower().endswith('.pdf') else "text/plain"
    
    text = document_processor.extract_text(file_content, content_type)
    result = llm_manager_analysis.analyze_document(
        text,
        {"type": profile_type, "experience_level": experience_level}
    )
    if isinstance(result, dict) and "response" in result:
        result_text = result["response"]
    else:
        result_text = result
    return parse_analysis_output(result_text)


def rag_chain(request: Dict[str, Any]) -> Dict[str, Any]:
    question = request['question']
    file = request.get('file', None)
    try:
        if file:
            if hasattr(file, 'file'):
                file_content = file.file.read()
                content_type = file.content_type
            else:
                file_content = file.file if hasattr(file, 'file') else file
                content_type = "application/pdf" if getattr(file, 'filename', '').lower().endswith('.pdf') else "text/plain"
            
            text = document_processor.extract_text(file_content, content_type)
            vector_store = document_processor.create_vector_store(text)
            context_chunks = document_processor.retrieve_relevant_context(vector_store, question, k=5)
            context = "\n".join(context_chunks)
            prompt = (
                "You are a legal assistant. Only answer the user's question based strictly on the provided context below. "
                "Do NOT provide a summary, key points, risks, or recommendations unless the question specifically asks for them. "
                "If the answer is not in the context, say you do not know.\n\n"
                f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
            )
            logger.info(f"Processing question: {question}")
            answer = llm_manager_qa.llm(prompt)
            return {"answer": answer}
        else:
            logger.info(f"Processing question without context: {question}")
            answer = llm_manager_qa.llm(question)
            return {"answer": answer}
    except Exception as e:
        logger.error(f"Error in rag_chain: {str(e)}")
        return {"answer": "I'm sorry, I encountered an error processing your question."}
