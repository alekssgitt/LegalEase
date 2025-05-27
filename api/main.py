import uvicorn
import logging
from fastapi import FastAPI, UploadFile, File, HTTPException, Body, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, Optional 
from api.agent import LLMRouterAgent
from api.Models import DocumentAnalysisResponse, LegalQAResponse
from api.chains import analyzeChain, ragChain
from core.llm_manager import llm_manager_qa

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI(title="LegalEase API")

agent = LLMRouterAgent(llm=llm_manager_qa.llm)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/process_input")
async def processInput(
    question: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    profile_type: str = Form("student"),
    experience_level: str = Form("beginner")
):
    if not question and not file:
        raise HTTPException(status_code=400, detail="Either a question or a file must be provided for processing.")

    try:
        response_data = await agent.route(
            question=question,
            file=file,
            profile_type=profile_type,
            experience_level=experience_level
        )

        return response_data
    except Exception as e:
        logger.error(f"Error in /process_input: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze", response_model=DocumentAnalysisResponse)
async def analyze(
    file: UploadFile = File(...),
    profile_type: str = Form(...),
    experience_level: str = Form("beginner")
):
    logger.info(f"Received file: {file.filename} for analysis with profile: {profile_type}, experience: {experience_level}")
    request_data = {
        "file": file,
        "profile_type": profile_type,
        "experience_level": experience_level,
        "question": "Analyze this document."
    }
    try:
        return analyzeChain(request_data) # Corrected call
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/legal_qa", response_model=LegalQAResponse) 
async def qa(
    question: str = Form(...),
    file: Optional[UploadFile] = File(None),
    profile_type: str = Form(...),
    experience_level: str = Form("beginner")
):
    logger.info(f"Received question: {question} for legal_qa")
    request_data = {
        "question": question,
        "file": file,
        "profile_type": "general_user",
        "experience_level": "beginner"
    }
    try:
        return ragChain(request_data)
    except Exception as e:
        logger.error(f"Error in /legal_qa endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)