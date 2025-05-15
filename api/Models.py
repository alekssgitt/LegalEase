from pydantic import BaseModel
from typing import List, Optional

class UserProfile(BaseModel):
    type: str
    experience_level: str = "beginner"

class DocumentAnalysisRequest(BaseModel):
    file: bytes
    profile_type: str
    experience_level: str

class DocumentAnalysisResponse(BaseModel):
    summary: str
    key_points: List[str]
    risks: List[str]
    recommendations: List[str]

class LegalQARequest(BaseModel):
    question: str
    file: Optional[bytes] = None

class LegalQAResponse(BaseModel):
    answer: str
