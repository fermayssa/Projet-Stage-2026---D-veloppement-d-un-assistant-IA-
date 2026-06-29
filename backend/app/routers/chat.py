from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.rag_service import query_documents
import asyncio

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
    # ✅ Exécute la fonction bloquante dans un thread séparé
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None, query_documents, request.question
    )
    return result