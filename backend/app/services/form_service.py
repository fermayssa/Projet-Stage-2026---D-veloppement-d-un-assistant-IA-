from llama_index.llms.groq import Groq
import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import os
import json
from dotenv import load_dotenv

load_dotenv()

CHROMA_DIR = "chroma_db"

def setup_llm():
    return Groq(
        model="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY")
    )

def get_document_text(file_id: str) -> str:
    """Récupère le texte d'un document depuis ChromaDB."""
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_or_create_collection("documents")

    results = collection.get(
        where={"file_id": file_id},
        include=["documents", "metadatas"]
    )

    if not results["documents"]:
        return ""

    return "\n".join(results["documents"])

def suggest_form_fields(file_id: str) -> dict:
    """
    Analyse le document et propose des champs de formulaire.
    Retourne une liste de champs suggérés avec type et nom.
    """
    text = get_document_text(file_id)

    if not text.strip():
        return {"error": "Aucun texte trouvé dans ce document"}

    llm = setup_llm()

    prompt = f"""Analyse ce document et identifie les données structurées qu'il contient.
Propose une liste de champs de formulaire pertinents pour capturer ces données.

Document :
{text[:3000]}

Réponds UNIQUEMENT avec un JSON valide, sans texte avant ou après, avec cette structure exacte :
{{
  "titre_formulaire": "Titre suggéré pour le formulaire",
  "description": "Courte description du formulaire",
  "champs": [
    {{
      "id": "champ_1",
      "label": "Nom du champ",
      "type": "text",
      "placeholder": "Exemple de valeur",
      "valeur_extraite": "Valeur trouvée dans le document ou vide",
      "obligatoire": true
    }}
  ]
}}

Types disponibles : text, number, date, email, textarea, select
Pour les champs select, ajoute une clé "options" avec la liste des choix possibles.
Propose entre 4 et 10 champs pertinents."""

    response = llm.complete(prompt)
    response_text = str(response).strip()

    # Nettoyer la réponse
    if "```json" in response_text:
        response_text = response_text.split("```json")[1].split("```")[0].strip()
    elif "```" in response_text:
        response_text = response_text.split("```")[1].split("```")[0].strip()

    try:
        form_data = json.loads(response_text)
        return form_data
    except json.JSONDecodeError:
        return {
            "titre_formulaire": "Formulaire extrait",
            "description": "Formulaire généré depuis le document",
            "champs": [
                {
                    "id": "champ_1",
                    "label": "Contenu extrait",
                    "type": "textarea",
                    "placeholder": "Contenu du document",
                    "valeur_extraite": text[:500],
                    "obligatoire": False
                }
            ]
        }

def generate_form(file_id: str, selected_fields: list) -> dict:
    """
    Génère le formulaire final avec les champs sélectionnés par l'utilisateur.
    """
    text = get_document_text(file_id)
    llm = setup_llm()

    fields_str = json.dumps(selected_fields, ensure_ascii=False)

    prompt = f"""Tu as ces champs de formulaire à remplir :
{fields_str}

Voici le contenu du document source :
{text[:3000]}

Remplis les valeurs de chaque champ en extrayant les informations pertinentes du document.
Réponds UNIQUEMENT avec un JSON valide avec la même structure que les champs fournis,
mais avec les "valeur_extraite" remplis avec les données trouvées dans le document."""

    response = llm.complete(prompt)
    response_text = str(response).strip()

    if "```json" in response_text:
        response_text = response_text.split("```json")[1].split("```")[0].strip()
    elif "```" in response_text:
        response_text = response_text.split("```")[1].split("```")[0].strip()

    try:
        filled_fields = json.loads(response_text)
        if isinstance(filled_fields, list):
            return {"champs": filled_fields}
        return filled_fields
    except:
        return {"champs": selected_fields}