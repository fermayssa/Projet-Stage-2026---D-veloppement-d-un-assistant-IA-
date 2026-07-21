# 🤖 Vermeg Document Assistant

> **Multimodal RAG Platform for Technical Documents**  
> Assistant documentaire intelligent basé sur une architecture RAG multimodale

[![Angular](https://img.shields.io/badge/Angular-18-red?logo=angular)](https://angular.dev)
[![FastAPI](https://img.shields.io/badge/FastAPI-Python_3.11-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![LlamaIndex](https://img.shields.io/badge/LlamaIndex-0.14-blue)](https://llamaindex.ai)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vectorielle-purple)](https://chromadb.com)
[![Groq](https://img.shields.io/badge/Groq-llama--3.3--70b-orange)](https://console.groq.com)

---

## 📋 Description

**Vermeg Document Assistant** est un prototype d'assistant intelligent développé dans le cadre d'un stage d'été chez **Vermeg** (Tunisie, 2026).

Il permet d'interroger simultanément plusieurs types de documents techniques en langage naturel, et de générer automatiquement des formulaires structurés à partir de leur contenu.

### Fonctionnalités principales

- 📄 **Upload multimodal** — PDF, images PNG/JPG, captures d'écran, diagrammes UML
- 🔍 **Recherche sémantique** — via embeddings et base vectorielle ChromaDB
- 💬 **Chat RAG** — réponses contextualisées avec sources et scores de pertinence
- 🎯 **Filtrage par document** — sélection de sources spécifiques pour la recherche
- ▤ **Module Studio** — génération automatique de formulaires depuis les documents
- 📋 **Templates prédéfinis** — CIN → Fiche personnelle, Facture → Bon de commande, CV → Fiche RH
- ⬇️ **Export** — formulaires téléchargeables en PDF et JSON

---

## 🏗️ Architecture

```
Utilisateur
    │
    ▼
Angular 18 (Frontend)          ← localhost:4200
    │  HTTP REST
    ▼
FastAPI (Backend Python)        ← localhost:8000
    │
    ├── Processeurs
    │   ├── PyMuPDF + pdfplumber  (PDF texte + tableaux)
    │   ├── Groq Vision           (figures et images dans PDF)
    │   └── Tesseract OCR         (images PNG/JPG)
    │
    ├── LlamaIndex
    │   ├── SentenceSplitter      (chunks 256 tokens)
    │   ├── HuggingFace BGE-small (embeddings 384 dims)
    │   └── ChromaDB              (stockage vectoriel persistant)
    │
    └── Groq API
        └── llama-3.3-70b-versatile  (génération réponses)
```

---

## 🛠️ Stack technologique

| Couche | Technologie | Version |
|---|---|---|
| Frontend | Angular | 18 |
| Backend | FastAPI (Python) | 3.11 |
| Orchestration RAG | LlamaIndex | 0.14 |
| Base vectorielle | ChromaDB | Persistante |
| Embeddings | HuggingFace BGE-small-en-v1.5 | - |
| LLM | Groq (llama-3.3-70b-versatile) | API gratuite |
| OCR | Tesseract | 5.x |
| Extraction PDF | PyMuPDF + pdfplumber | - |
| Vision IA | Groq Vision (llama-4-scout) | API |
| Versions | Git + GitHub | - |

---

## 📁 Structure du projet

```
rag-assistant/
├── backend/
│   ├── app/
│   │   ├── main.py                  # Point d'entrée FastAPI
│   │   ├── routers/
│   │   │   ├── documents.py         # Upload, liste, suppression, preview
│   │   │   ├── chat.py              # Endpoint RAG conversationnel
│   │   │   └── forms.py             # Génération et remplissage formulaires
│   │   ├── services/
│   │   │   ├── rag_service.py       # Pipeline LlamaIndex + ChromaDB + Groq
│   │   │   ├── form_service.py      # Logique génération formulaires
│   │   │   └── templates.py         # Templates CIN / Facture / CV
│   │   └── processors/
│   │       ├── pdf_processor.py     # PyMuPDF + pdfplumber + Groq Vision
│   │       └── image_processor.py   # Tesseract OCR
│   ├── uploads/                     # Fichiers uploadés (non versionné)
│   ├── chroma_db/                   # Base vectorielle (non versionnée)
│   ├── requirements.txt
│   └── .env                         # Clés API (non versionnée)
│
├── frontend/
│   └── src/app/
│       ├── components/
│       │   ├── upload/              # Zone drag & drop + liste documents
│       │   ├── chat/                # Interface de conversation RAG
│       │   ├── studio/              # Panneau Studio (génération formulaires)
│       │   └── form-viewer/         # Visualisation et export formulaires
│       ├── services/
│       │   └── api.service.ts       # Communication avec le backend
│       └── models/
│           └── interfaces.ts        # Types TypeScript
│
├── .gitignore
└── README.md
```

---

## 🚀 Installation et lancement

### Prérequis

- Python 3.11+
- Node.js 20+ et npm
- Git
- Tesseract OCR ([télécharger](https://github.com/UB-Mannheim/tesseract/wiki))
- Compte Groq ([console.groq.com](https://console.groq.com)) pour la clé API gratuite

### 1. Cloner le dépôt

```bash
git clone https://github.com/fermayssa/Projet-Stage-2026---D-veloppement-d-un-assistant-IA-.git
cd Projet-Stage-2026---D-veloppement-d-un-assistant-IA-
```

### 2. Backend Python

```bash
# Créer et activer l'environnement virtuel
python -m venv venv

# Windows
venv\Scripts\activate
# Linux / Mac
source venv/bin/activate

# Installer les dépendances
pip install -r backend/requirements.txt

# Créer le fichier de configuration
# Créer backend/.env avec le contenu suivant :
# GROQ_API_KEY=gsk_votre_clé_ici

# Lancer le backend
cd backend
uvicorn app.main:app --reload
```

Le backend est disponible sur `http://localhost:8000`  
Documentation Swagger : `http://localhost:8000/docs`

### 3. Frontend Angular

```bash
# Dans un nouveau terminal
cd frontend
npm install
ng serve
```

L'application est disponible sur `http://localhost:4200`

---

## 🔑 Configuration

Créer le fichier `backend/.env` :

```env
GROQ_API_KEY=gsk_votre_clé_api_groq_ici
```

> ⚠️ Ne jamais committer ce fichier — il est déjà dans `.gitignore`

### Obtenir une clé Groq gratuite

1. Aller sur [console.groq.com](https://console.groq.com)
2. Créer un compte
3. API Keys → Create API Key
4. Copier la clé dans `backend/.env`

---

## 📖 Utilisation

### Importer un document

1. Glisser-déposer un fichier PDF, PNG ou JPG dans la zone d'upload (sidebar gauche)
2. Le système extrait automatiquement le texte, les tableaux et analyse les images
3. Le document est découpé en chunks et indexé dans ChromaDB

### Poser une question

1. Taper une question dans la zone de saisie en bas de la zone centrale
2. Optionnel : cliquer sur ▤ pour filtrer la recherche sur des documents spécifiques
3. La réponse s'affiche avec les sources utilisées et leurs scores de pertinence

### Générer un formulaire (Studio)

**Mode libre :**
1. Cliquer sur "▤ Générer un formulaire libre" dans le Studio (sidebar droite)
2. Choisir un document source
3. Le LLM propose des champs — sélectionner, désélectionner ou en ajouter manuellement
4. Cliquer "Générer"

**Mode template :**
1. Cliquer sur "◈ Remplir un template"
2. Choisir un template prédéfini (CIN, Facture ou CV)
3. Choisir le document source
4. Le formulaire est rempli automatiquement

**Export :**
- Bouton **⬇ PDF** — tableau imprimable
- Bouton **⬇ JSON** — données structurées

---

## 🧪 Tests

### Tester l'API (Swagger)

```
http://localhost:8000/docs
```

### Scénarios de test recommandés

| Question | Document recommandé |
|---|---|
| "Quelles sont les technologies utilisées ?" | Cahier des charges PDF |
| "Que fait la fonction query_documents ?" | Fichier de code Python |
| "Quel type de document prend le plus de temps selon la Figure 2 ?" | PDF avec figures |
| "Quel est le budget du projet ?" | N'importe quel doc (test question sans réponse) |

---

## 📡 API Reference

| Méthode | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check |
| `POST` | `/api/upload` | Upload et indexation |
| `GET` | `/api/documents` | Liste des documents |
| `DELETE` | `/api/documents/{id}` | Suppression |
| `GET` | `/api/documents/{id}/preview` | Aperçu des chunks |
| `POST` | `/api/chat` | Question RAG |
| `GET` | `/api/forms/templates` | Templates disponibles |
| `POST` | `/api/forms/suggest` | Suggestion de champs |
| `POST` | `/api/forms/generate` | Génération formulaire libre |
| `POST` | `/api/forms/fill-template` | Remplissage template |

---

## ⚠️ Limitations connues

- Les images avec texte stylisé ou logos donnent parfois peu de caractères OCR
- Le LLM nécessite une connexion internet (Groq API)
- ChromaDB est en mode local — pas de synchronisation multi-instance
- Les sections Corpus, Conversations et Historique sont des placeholders visuels

---

## 🔮 Perspectives

- [ ] Conteneurisation Docker complète
- [ ] Authentification utilisateurs (JWT)
- [ ] Persistance de l'historique des conversations
- [ ] Support du streaming de réponses
- [ ] Déploiement en production

---

## 👩‍💻 Auteure

**Ferjani Mayssa**  
Stage d'été — Vermeg, Tunisie  
Juin – Juillet 2026

---

## 📄 Licence

Projet de stage — Usage interne Vermeg uniquement.
