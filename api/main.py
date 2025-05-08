import uvicorn
import logging
from fastapi import FastAPI, UploadFile, File, HTTPException, Body, Form
from fastapi.params import Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any

from core.llm_manager import LLMManager
from services.document_processor import DocumentProcessor
from langchain_community.llms import Ollama as OllamaRaw

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI(title="LegalEase API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserProfile(BaseModel):
    type: str
    experience_level: str = "beginner"

class DocumentAnalysis(BaseModel):
    summary: str
    key_points: list[str]
    risks: list[str]
    recommendations: list[str]

class LegalQARequest(BaseModel):
    question: str
    file: UploadFile | None = None

llm_manager = LLMManager()
document_processor = DocumentProcessor()

qa_llm = OllamaRaw(model="llama3.2", base_url="http://localhost:11434")

@app.post("/analyze", response_model=DocumentAnalysis)
async def analyze_document(
    file: UploadFile = File(...),
    profile_type: str = Form(...),
    experience_level: str = Form(default="beginner")
) -> Dict[str, Any]:
    try:
        logger.debug(f"Received file: {file.filename}")
        logger.debug(f"Profile type: {profile_type}")
        logger.debug(f"Experience level: {experience_level}")
        
        if file.content_type not in ["application/pdf", "text/plain"]:
            raise HTTPException(
                status_code=400,
                detail="Only PDF and text files are supported"
            )
        
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Empty file provided")

        try:
            text = document_processor.extract_text(content, file.content_type)
            logger.debug(f"Extracted text length: {len(text)}")
        except Exception as e:
            logger.error(f"Error extracting text: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Error processing document: {str(e)}")

        vector_store = document_processor.create_vector_store(text)
        
        analysis = llm_manager.analyze_document(text, {
            "type": profile_type,
            "experience_level": experience_level
        })
        
        logger.debug(f"Analysis generated: {analysis[:100]}...")
        
        response_lines = analysis.split("\n")
        result = {
            "summary": "",
            "key_points": [],
            "risks": [],
            "recommendations": []
        }

        current_section = "summary"
        for line in response_lines:
            line = line.strip()
            if not line:
                continue

            if any(x in line.lower() for x in ["key points", "obligations"]):
                current_section = "key_points"
                continue
            elif any(x in line.lower() for x in ["risks", "hidden clauses"]):
                current_section = "risks"
                continue
            elif any(x in line.lower() for x in ["recommended", "recommendations", "actions"]):
                current_section = "recommendations"
                continue

            line = line.lstrip("1234567890.-) ")

            if current_section == "summary":
                if not line.startswith(("Key Points", "Risks", "Recommendations")):
                    result["summary"] += line + " "
            elif current_section in ["key_points", "risks", "recommendations"]:
                if line and not line.lower().startswith(("key points", "risks", "recommendations")):
                    result[current_section].append(line)

        result["summary"] = result["summary"].replace("**Summary**", "").strip()
        
        for section in ["key_points", "risks", "recommendations"]:
            result[section] = list(filter(None, dict.fromkeys(result[section])))
        
        logger.debug(f"Returning result with {len(result['key_points'])} key points, " +
                    f"{len(result['risks'])} risks, and {len(result['recommendations'])} recommendations")
        
        return DocumentAnalysis(**result)

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/legal-qa")
async def legal_qa(
    question: str = Form(...),
    file: UploadFile = File(None)
):
    try:
        if file is not None:
            file_content = await file.read()
            text = document_processor.extract_text(file_content, file.content_type)
            vector_store = document_processor.create_vector_store(text)

            context_chunks = document_processor.retrieve_relevant_context(vector_store, question, k=3)
            context = "\n".join(context_chunks)

            prompt = f"You are a legal assistant. Use the following document context to answer the user's question.\n\nContext:\n{context}\n\nQuestion: {question}\nAnswer:"
            answer = qa_llm.invoke(prompt)
            return {"answer": answer}
        else:
            prompt = f"You are a legal expert. Answer the following question clearly and concisely.\n\nQuestion: {question}\nAnswer:"
            answer = qa_llm.invoke(prompt)
            return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
