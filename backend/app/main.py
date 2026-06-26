from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import documents

app = FastAPI(title="RAG Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enregistrer le router documents
app.include_router(documents.router, prefix="/api", tags=["documents"])
app.include_router(chat.router, prefix="/api", tags=["chat"])

@app.get("/")
def health_check():
    return {"status": "ok", "message": "RAG Assistant is running"}