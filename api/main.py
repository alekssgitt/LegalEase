import uvicorn
import logging
import os
from fastapi import FastAPI, UploadFile, File, HTTPException, Body, Form, Request
from fastapi.params import Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
from core.llm_manager import LLMManager
from services.document_processor import DocumentProcessor
from langchain_community.llms import Ollama as OllamaRaw
from api.agent import Agent

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

ollama_base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
qa_llm = OllamaRaw(model="llama3.2", base_url=ollama_base_url)

agent = Agent()

@app.post("/analyze")
async def analyze_document(
    file: UploadFile = File(...),
    profile_type: str = Form(...),
    experience_level: str = Form("beginner")
):
    req_dict = {
        "file": file,
        "profile_type": profile_type,
        "experience_level": experience_level
    }
    response = agent.route(req_dict)
    return response

@app.post("/legal_qa")
async def legal_qa(
    question: str = Form(...),
    file: UploadFile = File(None)
):
    req_dict = {
        "question": question,
        "file": file
    }
    response = agent.route(req_dict)
    return response

@app.post("/process_input")
async def process_input(request: Request):
    req_json = await request.json()
    response = agent.route(req_json)
    return response


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)