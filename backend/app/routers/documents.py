from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
import os
import uuid

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_TYPES = ["application/pdf", "image/png", "image/jpeg"]

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    
    # Vérifier le type de fichier
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Type de fichier non supporté : {file.content_type}"
        )
    
    # Générer un nom unique pour éviter les conflits
    file_id = str(uuid.uuid4())
    extension = file.filename.split(".")[-1]
    file_path = f"{UPLOAD_DIR}/{file_id}.{extension}"
    
    # Sauvegarder le fichier sur le disque
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {
        "message": "Fichier importé avec succès",
        "file_id": file_id,
        "filename": file.filename,
        "type": file.content_type,
        "path": file_path
    }

@router.get("/documents")
async def list_documents():
    files = os.listdir(UPLOAD_DIR)
    return {"documents": files, "count": len(files)}