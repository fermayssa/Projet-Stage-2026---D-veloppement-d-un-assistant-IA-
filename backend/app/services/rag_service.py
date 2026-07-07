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

    # Récupérer les chunks pertinents
    retriever = index.as_retriever(similarity_top_k=5)
    nodes = retriever.retrieve(question)

    # Filtrer les chunks avec score > 0.55
    relevant_nodes = [n for n in nodes if (n.score or 0) >= 0.55]

    if not relevant_nodes:
        return {
            "question": question,
            "answer": "Je ne trouve pas cette information dans les documents indexés.",
            "sources": []
        }

    # Construire le contexte depuis les chunks
    context_parts = []
    for node in relevant_nodes:
        filename = node.metadata.get("filename", "inconnu")
        context_parts.append(f"[{filename}]: {node.text}")

    context = "\n\n".join(context_parts)

    # Prompt très court et très direct pour llama3.2:1b
    qa_prompt = PromptTemplate(
        "Contexte:\n{context_str}\n\n"
        "Question: {query_str}\n\n"
        "Réponds en français en utilisant UNIQUEMENT le contexte. "
        "Si la réponse est dans le contexte, cite-la directement. "
        "Réponse:"
    )

    query_engine = index.as_query_engine(
        similarity_top_k=5,
        response_mode="compact",
        text_qa_template=qa_prompt
    )

    response = query_engine.query(question)
    answer = str(response).strip()

    # Si la réponse est trop générique, retourner directement le texte extrait
    mots_generiques = [
        "bibliothèque", "multimodale", "embedding", "vectoriel",
        "reconnaissance optique", "je suis désolé", "cannot", "I cannot"
    ]
    
    if any(mot in answer.lower() for mot in mots_generiques):
        # Retourner directement le contenu extrait des chunks
        direct_answer = "Voici le contenu extrait des documents :\n\n"
        for node in relevant_nodes:
            filename = node.metadata.get("filename", "inconnu")
            direct_answer += f"📄 {filename} :\n{node.text.strip()}\n\n"
        answer = direct_answer

    # Construire les sources
    sources = []
    for node in relevant_nodes:
        sources.append({
            "filename": node.metadata.get("filename", "inconnu"),
            "page": node.metadata.get("page", None),
            "score": round(node.score, 3) if node.score else None,
            "text_preview": node.text[:150]
        })

    return {
        "question": question,
        "answer": answer,
        "sources": sources
    }