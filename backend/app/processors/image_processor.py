import pytesseract
from PIL import Image, ImageFilter, ImageEnhance
import os

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def preprocess_image(image):
    """Améliore l'image pour un meilleur OCR."""
    # Convertir en RGB
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Agrandir si trop petite
    w, h = image.size
    if w < 800:
        scale = 800 / w
        image = image.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    
    # Améliorer le contraste
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)
    
    # Convertir en niveaux de gris
    image = image.convert('L')
    
    return image

def extract_text_from_image(file_path: str) -> dict:
    try:
        image = Image.open(file_path)
        processed = preprocess_image(image)
        
        # Essayer plusieurs configurations OCR
        configs = [
            '--psm 6 --oem 3',   # Bloc de texte uniforme
            '--psm 11 --oem 3',  # Texte épars
            '--psm 3 --oem 3',   # Auto
        ]
        
        best_text = ""
        for config in configs:
            try:
                text = pytesseract.image_to_string(
                    processed,
                    lang='fra+eng',
                    config=config
                )
                if len(text.strip()) > len(best_text.strip()):
                    best_text = text
            except:
                continue
        
        text = best_text.strip()
        
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

def extract_text_from_uml(file_path: str) -> dict:
    try:
        image = Image.open(file_path)
        processed = preprocess_image(image)
        
        text = pytesseract.image_to_string(
            processed,
            lang='fra+eng',
            config='--psm 11 --oem 3'
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