import fitz  # PyMuPDF
import os

def extract_text_from_pdf(file_path: str) -> dict:
    """
    Lit un PDF et extrait tout son texte page par page.
    Retourne un dictionnaire avec le texte et les métadonnées.
    """
    doc = fitz.open(file_path)
    
    pages_content = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()  # Extrait le texte de la page
        
        if text.strip():  # On ignore les pages vides
            pages_content.append({
                "page": page_num + 1,
                "text": text,
                "char_count": len(text)
            })
    
    doc.close()
    
    return {
        "total_pages": len(doc),
        "pages_with_text": len(pages_content),
        "content": pages_content,
        "full_text": "\n".join([p["text"] for p in pages_content])
    }