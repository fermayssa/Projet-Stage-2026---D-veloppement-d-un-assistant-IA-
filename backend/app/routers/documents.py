from fastapi import APIRouter, UploadFile, File, HTTPException
from app.processors.pdf_processor import extract_text_from_pdf
import shutil, os, uuid, json

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_TYPES = ["application/pdf", "image/png", "image/jpeg"]

# Petit "stockage" en mémoire pour garder trace des documents
documents_store = {}

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):

    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Type non supporté : {file.content_type}"
        )

    # Sauvegarder le fichier
    file_id = str(uuid.uuid4())
    extension = file.filename.split(".")[-1]
    file_path = f"{UPLOAD_DIR}/{file_id}.{extension}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Si c'est un PDF, extraire le texte immédiatement
    extracted_text = None
    pages_count = 0

    if file.content_type == "application/pdf":
        result = extract_text_from_pdf(file_path)
        extracted_text = result["full_text"]
        pages_count = result["total_pages"]

    # Stocker les infos du document
    documents_store[file_id] = {
        "file_id": file_id,
        "filename": file.filename,
        "type": file.content_type,
        "path": file_path,
        "pages": pages_count,
        "text_extracted": extracted_text is not None,
        "text_preview": extracted_text[:200] if extracted_text else None
    }

    return {
        "message": "Fichier importé et traité avec succès",
        "file_id": file_id,
        "filename": file.filename,
        "pages": pages_count,
        "text_preview": extracted_text[:200] if extracted_text else "Pas de texte extrait",
        "chars_extracted": len(extracted_text) if extracted_text else 0
    }

@router.get("/documents")
async def list_documents():
    return {
        "documents": list(documents_store.values()),
        "count": len(documents_store)
    }

@router.get("/documents/{file_id}")
async def get_document(file_id: str):
    if file_id not in documents_store:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    return documents_store[file_id]