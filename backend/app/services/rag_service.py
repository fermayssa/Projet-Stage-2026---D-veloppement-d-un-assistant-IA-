from llama_index.core import Document, VectorStoreIndex, Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.llms.anthropic import Anthropic
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext
import os

# Dossier où ChromaDB stocke ses données sur le disque
CHROMA_DIR = "chroma_db"

def get_chroma_collection():
    """Connexion à ChromaDB — crée la base si elle n'existe pas."""
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_or_create_collection("documents")
    return client, collection

def get_vector_store():
    """Prépare le vector store LlamaIndex connecté à ChromaDB."""
    client, collection = get_chroma_collection()
    vector_store = ChromaVectorStore(chroma_collection=collection)
    return vector_store, client

def setup_settings():
    """Configure LlamaIndex pour utiliser un modèle d'embedding local gratuit."""
    Settings.embed_model = HuggingFaceEmbedding(
        model_name="BAAI/bge-small-en-v1.5"
    )
    # On ne configure pas le LLM ici, on le fera à l'étape suivante
    Settings.llm = None

def index_document(file_id: str, filename: str, full_text: str) -> dict:
    """
    Prend le texte extrait d'un document et l'indexe dans ChromaDB.
    C'est le cœur du pipeline RAG — étape d'ingestion.
    """
    setup_settings()

    # Étape 1 : Créer un Document LlamaIndex
    document = Document(
        text=full_text,
        metadata={
            "file_id": file_id,
            "filename": filename,
            "source": filename
        }
    )

    # Étape 2 : Découper en chunks
    # chunk_size=512 = ~512 tokens par morceau
    # chunk_overlap=50 = 50 tokens de chevauchement entre chunks
    splitter = SentenceSplitter(chunk_size=512, chunk_overlap=50)
    nodes = splitter.get_nodes_from_documents([document])

    # Étape 3 : Stocker dans ChromaDB avec embeddings
    vector_store, _ = get_vector_store()
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    index = VectorStoreIndex(
        nodes,
        storage_context=storage_context,
        show_progress=True
    )

    return {
        "file_id": file_id,
        "chunks_created": len(nodes),
        "indexed": True
    }