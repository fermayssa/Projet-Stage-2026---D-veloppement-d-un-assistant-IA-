from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.services.form_service import suggest_form_fields, generate_form

router = APIRouter()

class SuggestRequest(BaseModel):
    file_id: str

class FormField(BaseModel):
    id: str
    label: str
    type: str
    placeholder: Optional[str] = ""
    valeur_extraite: Optional[str] = ""
    obligatoire: Optional[bool] = False
    options: Optional[List[str]] = None

class GenerateRequest(BaseModel):
    file_id: str
    selected_fields: List[dict]

@router.post("/forms/suggest")
async def suggest_fields(request: SuggestRequest):
    """Analyse le document et propose des champs de formulaire."""
    if not request.file_id:
        raise HTTPException(status_code=400, detail="file_id requis")

    result = suggest_form_fields(request.file_id)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result

@router.post("/forms/generate")
async def generate(request: GenerateRequest):
    """Génère le formulaire final avec les champs sélectionnés."""
    if not request.file_id or not request.selected_fields:
        raise HTTPException(
            status_code=400,
            detail="file_id et selected_fields requis"
        )

    result = generate_form(request.file_id, request.selected_fields)
    return result