import fitz  # PyMuPDF
import pdfplumber
import base64
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def analyze_image_with_groq(image_bytes: bytes, page_num: int, img_idx: int) -> str:
    """Analyse une image extraite du PDF avec Groq Vision."""
    image_b64 = base64.b64encode(image_bytes).decode('utf-8')
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
                        "text": """Analyse cette image extraite d'un PDF. Décris précisément :
1. Si c'est un diagramme UML : liste TOUTES les classes, acteurs, relations, labels
2. Si c'est un tableau ou graphique : extrait TOUTES les données avec leurs valeurs
3. Si c'est une capture d'écran : décris TOUT le texte et contenu visible
4. Si c'est un formulaire : liste TOUS les champs et leurs labels
Sois exhaustif. Extrais chaque information visible."""
                    }
                ]
            }],
            max_tokens=1024
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[Image page {page_num} index {img_idx} — analyse échouée: {e}]"


def extract_tables_with_pdfplumber(file_path: str) -> dict:
    """Extrait les tableaux du PDF page par page avec pdfplumber."""
    tables_by_page = {}
    try:
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                tables = page.extract_tables()
                if tables:
                    tables_by_page[page_num + 1] = []
                    for t_idx, table in enumerate(tables):
                        table_text = f"\n[TABLEAU {t_idx + 1} — page {page_num + 1}]\n"
                        for row in table:
                            cleaned = [str(cell) if cell is not None else "" for cell in row]
                            table_text += " | ".join(cleaned) + "\n"
                        tables_by_page[page_num + 1].append(table_text)
    except Exception as e:
        print(f"Erreur extraction tableaux pdfplumber: {e}")
    return tables_by_page


def extract_text_from_pdf(file_path: str) -> dict:
    """
    Extraction complète d'un PDF — garde la structure dict de ton code original.
    Ajoute : tableaux (pdfplumber) + images/figures (Groq Vision).
    """
    pages_content = []

    # Cache pour éviter de réanalyser les images à chaque upload
    cache_dir = file_path + "_images_cache"
    os.makedirs(cache_dir, exist_ok=True)

    print("Extraction des tableaux avec pdfplumber...")
    tables_by_page = extract_tables_with_pdfplumber(file_path)

    doc = fitz.open(file_path)
    total_pages = len(doc)
    print(f"Extraction du PDF — {total_pages} pages")

    for page_num in range(total_pages):
        page = doc.load_page(page_num)
        page_text = ""

        # 1. Texte brut (comme avant)
        text = page.get_text()
        if text.strip():
            page_text += text
            print(f"Page {page_num+1} : {len(text)} caractères extraits")
            print(f"Aperçu : {text[:200]}")
            print("---")

        # 2. Tableaux de cette page
        if (page_num + 1) in tables_by_page:
            for table_text in tables_by_page[page_num + 1]:
                page_text += table_text
            print(f"Page {page_num+1} — {len(tables_by_page[page_num+1])} tableau(x) ajouté(s)")

        # 3. Images embarquées analysées par Groq Vision
        image_list = page.get_images(full=True)
        for img_idx, img in enumerate(image_list):
            xref = img[0]
            cache_path = os.path.join(
                cache_dir, f"page{page_num+1}_img{img_idx}.txt"
            )

            if os.path.exists(cache_path):
                with open(cache_path, "r", encoding="utf-8") as f:
                    description = f.read()
                print(f"Image {img_idx+1} page {page_num+1} — depuis cache")
            else:
                print(f"Analyse image {img_idx+1} page {page_num+1} avec Groq Vision...")
                try:
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    description = analyze_image_with_groq(
                        image_bytes, page_num + 1, img_idx
                    )
                    with open(cache_path, "w", encoding="utf-8") as f:
                        f.write(description)
                    print(f"Image {img_idx+1} — analysée et mise en cache")
                except Exception as e:
                    description = f"[Erreur extraction image: {e}]"

            page_text += f"\n[IMAGE page {page_num+1} — {img_idx+1}]\n{description}\n"

        # Ajouter la page seulement si elle contient du contenu
        if page_text.strip():
            pages_content.append({
                "page": page_num + 1,
                "text": page_text
            })

    doc.close()

    full_text = "\n".join([p["text"] for p in pages_content])
    print(f"Extraction terminée — {len(full_text)} caractères au total")

    return {
        "total_pages": total_pages,
        "pages_extracted": len(pages_content),
        "content": pages_content,
        "full_text": full_text
    }