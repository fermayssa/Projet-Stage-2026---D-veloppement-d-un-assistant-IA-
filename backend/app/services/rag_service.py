from llama_index.core import VectorStoreIndex, Settings, PromptTemplate
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import Document, StorageContext
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb

CHROMA_DIR = "chroma_db"

def setup_settings():
    """Configure le modèle d'embedding et Ollama comme LLM."""
    Settings.embed_model = HuggingFaceEmbedding(
        model_name="BAAI/bge-small-en-v1.5"
    )
    Settings.llm = Ollama(
    model="llama3.2:1b",
    request_timeout=120.0,
    context_window=2048
)

def get_vector_store():
    """Connexion à ChromaDB."""
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_or_create_collection("documents")
    vector_store = ChromaVectorStore(chroma_collection=collection)
    return vector_store, client

def index_document(file_id: str, filename: str, full_text: str) -> dict:
    """Indexe un document dans ChromaDB."""
    setup_settings()

    document = Document(
        text=full_text,
        metadata={
            "file_id": file_id,
            "filename": filename,
            "source": filename
        }
    )

    splitter = SentenceSplitter(chunk_size=256, chunk_overlap=30)
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
    """Pose une question sur tous les documents indexés."""
    setup_settings()

    vector_store, _ = get_vector_store()
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        storage_context=storage_context
    )

    # Prompt strict — force à utiliser uniquement le contexte documentaire
    qa_prompt = PromptTemplate(
        "Tu es un assistant documentaire professionnel de Vermeg.\n"
        "Réponds UNIQUEMENT en te basant sur le contexte fourni ci-dessous.\n"
        "Si la réponse n'est pas dans le contexte, réponds exactement : "
        "'Cette information n'est pas disponible dans les documents fournis.'\n"
        "Réponds en français, de façon claire et structurée.\n\n"
        "Contexte extrait des documents :\n"
        "---------------------\n"
        "{context_str}\n"
        "---------------------\n\n"
        "Question : {query_str}\n\n"
        "Réponse :"
    )

    query_engine = index.as_query_engine(
        similarity_top_k=5,
        response_mode="compact",
        text_qa_template=qa_prompt
    )

    response = query_engine.query(question)

    sources = []
    if hasattr(response, 'source_nodes'):
        for node in response.source_nodes:
            sources.append({
                "filename": node.metadata.get("filename", "inconnu"),
                "page": node.metadata.get("page", None),
                "score": round(node.score, 3) if node.score else None,
                "text_preview": node.text[:150]
            })

    return {
        "question": question,
        "answer": str(response),
        "sources": sources
    }