import pytesseract
from PIL import Image
import os

# Chemin vers Tesseract sur Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_image(file_path: str) -> dict:
    """
    Extrait le texte d'une image ou capture d'écran via OCR.
    Fonctionne pour : PNG, JPG, JPEG, captures d'écran, diagrammes UML.
    """
    try:
        # Ouvrir l'image
        image = Image.open(file_path)
        
        # Convertir en RGB si nécessaire (certains PNG ont un canal alpha)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # OCR en français et anglais
        text = pytesseract.image_to_string(
            image,
            lang='fra+eng',
            config='--psm 6'  # psm 6 = bloc de texte uniforme
        )
        
        # Nettoyer le texte
        text = text.strip()
        
        return {
            "text": text,
            "chars_extracted": len(text),
            "success": len(text) > 10
        }
        
    except Exception as e:
        return {
            "text": "",
            "chars_extracted": 0,
            "success": False,
            "error": str(e)
        }

def extract_text_from_uml(file_path: str) -> dict:
    """
    Pour les diagrammes UML (images PNG/JPG).
    Même traitement que les images normales mais avec config OCR optimisée.
    """
    try:
        image = Image.open(file_path)
        
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # psm 11 = texte épars, mieux pour les diagrammes
        text = pytesseract.image_to_string(
            image,
            lang='fra+eng',
            config='--psm 11'
        )
        
        text = text.strip()
        
        return {
            "text": text,
            "chars_extracted": len(text),
            "success": len(text) > 5
        }
        
    except Exception as e:
        return {
            "text": "",
            "chars_extracted": 0,
            "success": False,
            "error": str(e)
        }