import fitz  # PyMuPDF

def extract_text_from_pdf(file_path: str) -> dict:
    doc = fitz.open(file_path)
    pages_content = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        # AJOUT TEMPORAIRE POUR TEST
        print(f"Page {page_num+1} : {len(text)} caractères extraits")
        print(f"Aperçu : {text[:200]}")
        print("---")
        if text.strip():
            pages_content.append({
                "page": page_num + 1,
                "text": text
            })

    total_pages = len(doc)
    doc.close()

    return {
        "total_pages": total_pages,
        "pages_extracted": len(pages_content),
        "content": pages_content,
        "full_text": "\n".join([p["text"] for p in pages_content])
    }