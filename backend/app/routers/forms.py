from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional
from app.services.form_service import suggest_form_fields, generate_form, fill_template
from app.services.templates import get_all_templates, get_template_by_id
import json

router = APIRouter()


class SuggestRequest(BaseModel):
    file_id: str


class GenerateRequest(BaseModel):
    file_id: str
    selected_fields: List[dict]


class FillTemplateRequest(BaseModel):
    file_id: str
    template_id: Optional[str] = None
    custom_template: Optional[dict] = None


@router.get("/forms/templates")
async def list_templates():
    """Retourne la liste des templates disponibles."""
    return {"templates": get_all_templates()}


@router.get("/forms/templates/{template_id}")
async def get_template(template_id: str):
    """Retourne un template complet par son ID."""
    template = get_template_by_id(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template non trouvé")
    return template


@router.post("/forms/fill-template")
async def fill_template_endpoint(request: FillTemplateRequest):
    """
    Remplit un template avec les données extraites du document source.
    Accepte un template_id (prédéfini) ou un custom_template (JSON uploadé).
    """
    if not request.file_id:
        raise HTTPException(status_code=400, detail="file_id requis")
    if not request.template_id and not request.custom_template:
        raise HTTPException(
            status_code=400,
            detail="template_id ou custom_template requis"
        )

    result = fill_template(
        file_id=request.file_id,
        template_id=request.template_id or "",
        custom_template=request.custom_template
    )

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result


@router.post("/forms/suggest")
async def suggest_fields(request: SuggestRequest):
    if not request.file_id:
        raise HTTPException(status_code=400, detail="file_id requis")
    result = suggest_form_fields(request.file_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.post("/forms/generate")
async def generate(request: GenerateRequest):
    if not request.file_id or not request.selected_fields:
        raise HTTPException(
            status_code=400,
            detail="file_id et selected_fields requis"
        )
    result = generate_form(request.file_id, request.selected_fields)
    return result