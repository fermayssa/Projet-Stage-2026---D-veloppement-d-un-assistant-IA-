TEMPLATES = {
    "cin_fiche_personnelle": {
        "nom": "Fiche personnelle depuis CIN",
        "description": "Extrait les informations d'une carte d'identité nationale",
        "icone": "▤",
        "champs": [
            {"id": "nom", "label": "Nom", "type": "text",
             "placeholder": "Nom de famille", "valeur_extraite": "", "obligatoire": True},
            {"id": "prenom", "label": "Prénom", "type": "text",
             "placeholder": "Prénom", "valeur_extraite": "", "obligatoire": True},
            {"id": "numero_cin", "label": "N° CIN", "type": "text",
             "placeholder": "Ex: 12345678", "valeur_extraite": "", "obligatoire": True},
            {"id": "date_naissance", "label": "Date de naissance", "type": "date",
             "placeholder": "", "valeur_extraite": "", "obligatoire": True},
            {"id": "lieu_naissance", "label": "Lieu de naissance", "type": "text",
             "placeholder": "Ville de naissance", "valeur_extraite": "", "obligatoire": False},
            {"id": "adresse", "label": "Adresse", "type": "textarea",
             "placeholder": "Adresse complète", "valeur_extraite": "", "obligatoire": False},
            {"id": "sexe", "label": "Sexe", "type": "select",
             "placeholder": "", "options": ["Masculin", "Féminin"],
             "valeur_extraite": "", "obligatoire": False},
            {"id": "date_expiration", "label": "Date d'expiration", "type": "date",
             "placeholder": "", "valeur_extraite": "", "obligatoire": False}
        ]
    },
    "facture_bon_commande": {
        "nom": "Bon de commande depuis facture",
        "description": "Extrait les données d'une facture fournisseur scannée",
        "icone": "▦",
        "champs": [
            {"id": "fournisseur", "label": "Fournisseur", "type": "text",
             "placeholder": "Nom du fournisseur", "valeur_extraite": "", "obligatoire": True},
            {"id": "numero_facture", "label": "N° Facture", "type": "text",
             "placeholder": "Ex: FAC-2026-001", "valeur_extraite": "", "obligatoire": True},
            {"id": "date_facture", "label": "Date de la facture", "type": "date",
             "placeholder": "", "valeur_extraite": "", "obligatoire": True},
            {"id": "articles", "label": "Lignes articles", "type": "textarea",
             "placeholder": "Liste des articles", "valeur_extraite": "", "obligatoire": False},
            {"id": "total_ht", "label": "Total HT", "type": "number",
             "placeholder": "0.00", "valeur_extraite": "", "obligatoire": False},
            {"id": "tva", "label": "TVA (%)", "type": "number",
             "placeholder": "19", "valeur_extraite": "", "obligatoire": False},
            {"id": "total_ttc", "label": "Total TTC", "type": "number",
             "placeholder": "0.00", "valeur_extraite": "", "obligatoire": False}
        ]
    },
    "cv_fiche_rh": {
        "nom": "Fiche candidat RH depuis CV",
        "description": "Extrait les informations d'un CV pour la fiche RH",
        "icone": "◈",
        "champs": [
            {"id": "nom_complet", "label": "Nom complet", "type": "text",
             "placeholder": "Nom et prénom", "valeur_extraite": "", "obligatoire": True},
            {"id": "email", "label": "Email", "type": "email",
             "placeholder": "email@exemple.com", "valeur_extraite": "", "obligatoire": True},
            {"id": "telephone", "label": "Téléphone", "type": "text",
             "placeholder": "+216 XX XXX XXX", "valeur_extraite": "", "obligatoire": False},
            {"id": "poste_vise", "label": "Poste visé", "type": "text",
             "placeholder": "Intitulé du poste", "valeur_extraite": "", "obligatoire": True},
            {"id": "experiences", "label": "Expériences professionnelles", "type": "textarea",
             "placeholder": "Liste des expériences", "valeur_extraite": "", "obligatoire": False},
            {"id": "formations", "label": "Formations", "type": "textarea",
             "placeholder": "Diplômes et formations", "valeur_extraite": "", "obligatoire": False},
            {"id": "competences", "label": "Compétences", "type": "textarea",
             "placeholder": "Compétences techniques et soft skills",
             "valeur_extraite": "", "obligatoire": False}
        ]
    }
}


def get_all_templates() -> list:
    """Retourne la liste des templates disponibles (sans les champs détaillés)."""
    return [
        {
            "id": key,
            "nom": val["nom"],
            "description": val["description"],
            "icone": val["icone"],
            "nb_champs": len(val["champs"])
        }
        for key, val in TEMPLATES.items()
    ]


def get_template_by_id(template_id: str) -> dict:
    """Retourne un template complet par son ID."""
    if template_id not in TEMPLATES:
        return None
    return TEMPLATES[template_id]