import pytesseract
from PIL import Image, ImageEnhance
import os
import base64
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# ──────────────────────────────────────────────
# 1. Analyse sémantique avec Groq Vision (comme pour le PDF)
# ──────────────────────────────────────────────
def analyze_image_with_groq(image_bytes: bytes, prompt_type: str = "general") -> str:
    """Analyse une image (diagramme, tableau, capture, UML) avec Groq Vision."""
    image_b64 = base64.b64encode(image_bytes).decode('utf-8')

    prompts = {
        "general": """Analyse cette image en détail. Décris précisément :
1. Si c'est un diagramme UML : liste TOUTES les classes, acteurs, relations, labels, cardinalités
2. Si c'est un tableau ou graphique : extrait TOUTES les données avec leurs valeurs exactes
3. Si c'est une capture d'écran : décris TOUT le texte et les éléments d'interface visibles
4. Si c'est un formulaire : liste TOUS les champs, labels et valeurs
5. Si c'est du texte simple : retranscris-le fidèlement
Sois exhaustif et précis. N'invente aucune information non visible.""",

        "uml": """Analyse ce diagramme UML en détail et exhaustif :
- Liste toutes les classes/entités avec leurs attributs et méthodes
- Liste toutes les relations (héritage, association, agrégation, composition) avec leur cardinalité
- Liste tous les acteurs et cas d'utilisation si c'est un diagramme de cas d'utilisation
- Décris le flux si c'est un diagramme de séquence ou d'activité
Sois précis sur les noms exacts visibles dans l'image."""
    }

    try:
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{image_b64}"}
                    },
                    {
                        "type": "text",
                        "text": prompts.get(prompt_type, prompts["general"])
                    }
                ]
            }],
            max_tokens=1536,
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[Analyse Groq Vision échouée: {e}]"


# ──────────────────────────────────────────────
# 2. Prétraitement pour l'OCR (gardé en complément)
# ──────────────────────────────────────────────
def preprocess_image(image):
    """Améliore l'image pour un meilleur OCR."""
    if image.mode != 'RGB':
        image = image.convert('RGB')

    w, h = image.size
    if w < 800:
        scale = 800 / w
        image = image.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)

    image = image.convert('L')
    return image


def _run_tesseract(image_path: str) -> str:
    """OCR brut avec plusieurs configs, retourne le meilleur résultat."""
    try:
        image = Image.open(image_path)
        processed = preprocess_image(image)
    except Exception:
        return ""

    configs = ['--psm 6 --oem 3', '--psm 11 --oem 3', '--psm 3 --oem 3']
    best_text = ""
    for config in configs:
        try:
            text = pytesseract.image_to_string(processed, lang='fra+eng', config=config)
            if len(text.strip()) > len(best_text.strip()):
                best_text = text
        except Exception:
            continue
    return best_text.strip()


# ──────────────────────────────────────────────
# 3. Fonctions principales — combinent Groq Vision + OCR
# ──────────────────────────────────────────────
def extract_text_from_image(file_path: str) -> dict:
    """
    Extraction combinée :
    - Groq Vision pour la compréhension sémantique (tableaux, schémas, mise en page)
    - Tesseract en complément pour capter du texte que la vision aurait pu manquer
    """
    try:
        with open(file_path, "rb") as f:
            image_bytes = f.read()

        vision_description = analyze_image_with_groq(image_bytes, prompt_type="general")
        ocr_text = _run_tesseract(file_path)

        combined = f"[ANALYSE VISUELLE]\n{vision_description}"
        if ocr_text and len(ocr_text) > 5:
            combined += f"\n\n[TEXTE OCR BRUT COMPLÉMENTAIRE]\n{ocr_text}"

        return {
            "text": combined,
            "chars_extracted": len(combined),
            "success": len(vision_description.strip()) > 5 or len(ocr_text) > 5
        }

    except Exception as e:
        return {
            "text": "",
            "chars_extracted": 0,
            "success": False,
            "error": str(e)
        }


def extract_text_from_uml(file_path: str) -> dict:
    """Extraction spécialisée pour les diagrammes UML — priorité à Groq Vision."""
    try:
        with open(file_path, "rb") as f:
            image_bytes = f.read()

        vision_description = analyze_image_with_groq(image_bytes, prompt_type="uml")
        ocr_text = _run_tesseract(file_path)

        combined = f"[ANALYSE UML]\n{vision_description}"
        if ocr_text and len(ocr_text) > 5:
            combined += f"\n\n[TEXTE OCR BRUT COMPLÉMENTAIRE]\n{ocr_text}"

        return {
            "text": combined,
            "chars_extracted": len(combined),
            "success": len(vision_description.strip()) > 5 or len(ocr_text) > 5
        }

    except Exception as e:
        return {
            "text": "",
            "chars_extracted": 0,
            "success": False,
            "error": str(e)
        }