from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.rag_service import query_documents

router = APIRouter()

class QuestionRequest(BaseModel):
    question: str

@router.post("/chat")
async def chat(request: QuestionRequest):
    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="La question ne peut pas être vide"
        )
    result = query_documents(request.question)
    return result