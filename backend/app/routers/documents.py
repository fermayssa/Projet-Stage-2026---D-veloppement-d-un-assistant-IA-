from fastapi import APIRouter, UploadFile, File, HTTPException
from app.processors.pdf_processor import extract_text_from_pdf
from app.processors.image_processor import extract_text_from_image, extract_text_from_uml
from app.services.rag_service import index_document
import shutil, os, uuid

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_TYPES = {
    "application/pdf": "pdf",
    "image/png": "image",
    "image/jpeg": "image",
    "image/jpg": "image"
}

documents_store = {}

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):

    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Type non supporté : {file.content_type}. Acceptés : PDF, PNG, JPG"
        )

    # Sauvegarder le fichier
    file_id = str(uuid.uuid4())
    extension = file.filename.split(".")[-1].lower()
    file_path = f"{UPLOAD_DIR}/{file_id}.{extension}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    extracted_text = ""
    pages_count = 0
    chunks_count = 0
    doc_type = ALLOWED_TYPES[file.content_type]

    # Traitement selon le type de fichier
    if file.content_type == "application/pdf":
        result = extract_text_from_pdf(file_path)
        extracted_text = result["full_text"]
        pages_count = result["total_pages"]

    elif file.content_type in ["image/png", "image/jpeg", "image/jpg"]:
        # Détecter si c'est un diagramme UML par le nom du fichier
        filename_lower = file.filename.lower()
        is_uml = any(word in filename_lower for word in ["uml", "diagram", "diagramme", "class", "sequence"])

        if is_uml:
            result = extract_text_from_uml(file_path)
        else:
            result = extract_text_from_image(file_path)

        extracted_text = result["text"]

    # Indexer si du texte a été extrait
    if extracted_text.strip():
        index_result = index_document(
            file_id=file_id,
            filename=file.filename,
            full_text=extracted_text
        )
        chunks_count = index_result["chunks_created"]

    documents_store[file_id] = {
        "file_id": file_id,
        "filename": file.filename,
        "type": doc_type,
        "content_type": file.content_type,
        "path": file_path,
        "pages": pages_count,
        "chunks": chunks_count,
        "indexed": chunks_count > 0
    }

    return {
        "message": "Fichier importé et traité avec succès",
        "file_id": file_id,
        "filename": file.filename,
        "document_type": doc_type,
        "pages": pages_count,
        "chars_extracted": len(extracted_text),
        "chunks_created": chunks_count,
        "indexed": chunks_count > 0
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

@router.delete("/documents/{file_id}")
async def delete_document(file_id: str):
    if file_id not in documents_store:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    
    # Supprimer le fichier physique
    doc = documents_store[file_id]
    if os.path.exists(doc["path"]):
        os.remove(doc["path"])
    
    # Supprimer de la mémoire
    del documents_store[file_id]
    
    return {"message": "Document supprimé", "file_id": file_id}
@router.get("/documents/{file_id}/preview")
async def preview_document(file_id: str):
    """Retourne un aperçu du contenu d'un document depuis ChromaDB."""
    import chromadb
    
    CHROMA_DIR = "chroma_db"
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_or_create_collection("documents")
    
    results = collection.get(
        where={"file_id": file_id},
        include=["documents", "metadatas"]
    )
    
    if not results["documents"]:
        raise HTTPException(status_code=404, detail="Document non trouvé dans la base vectorielle")
    
    chunks = []
    for i, (doc, meta) in enumerate(zip(results["documents"], results["metadatas"])):
        chunks.append({
            "index": i + 1,
            "text": doc[:300],
            "metadata": meta
        })
    
    return {
        "file_id": file_id,
        "filename": results["metadatas"][0].get("filename", "inconnu") if results["metadatas"] else "inconnu",
        "total_chunks": len(chunks),
        "chunks": chunks[:5]  # Afficher max 5 premiers chunks
    }