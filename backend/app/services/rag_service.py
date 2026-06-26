from llama_index.core import VectorStoreIndex, Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import Document, StorageContext
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb

CHROMA_DIR = "chroma_db"

def setup_settings():
    """Configure le modèle d'embedding et Ollama comme LLM gratuit."""
    
    Settings.embed_model = HuggingFaceEmbedding(
        model_name="BAAI/bge-small-en-v1.5"
    )
    
    # Ollama tourne localement — aucune clé API nécessaire
    Settings.llm = Ollama(
        model="llama3.2:1b",
        request_timeout=120.0
    )

def get_vector_store():
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_or_create_collection("documents")
    vector_store = ChromaVectorStore(chroma_collection=collection)
    return vector_store, client

def index_document(file_id: str, filename: str, full_text: str) -> dict:
    setup_settings()

    document = Document(
        text=full_text,
        metadata={
            "file_id": file_id,
            "filename": filename,
            "source": filename
        }
    )

    splitter = SentenceSplitter(chunk_size=512, chunk_overlap=50)
    nodes = splitter.get_nodes_from_documents([document])

    vector_store, _ = get_vector_store()
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    VectorStoreIndex(
        nodes,
        storage_context=storage_context,
        show_progress=True
    )

    return {
        "file_id": file_id,
        "chunks_created": len(nodes),
        "indexed": True
    }

def query_documents(question: str) -> dict:
    setup_settings()

    vector_store, _ = get_vector_store()
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        storage_context=storage_context
    )

    query_engine = index.as_query_engine(
        similarity_top_k=3,
        response_mode="compact"
    )

    response = query_engine.query(question)

    sources = []
    if hasattr(response, 'source_nodes'):
        for node in response.source_nodes:
            sources.append({
                "filename": node.metadata.get("filename", "inconnu"),
                "score": round(node.score, 3) if node.score else None,
                "text_preview": node.text[:150]
            })

    return {
        "question": question,
        "answer": str(response),
        "sources": sources
    }