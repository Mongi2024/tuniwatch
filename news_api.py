"""
Module news_api - Fonctions reutilisables pour NewsAPI
Etape B - Session 2
"""

import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Charge la cle API depuis le fichier .env
load_dotenv()

API_KEY = os.getenv("NEWSAPI_KEY")
API_URL = "https://newsapi.org/v2/everything"


def est_configure():
    """Verifie que la cle API est bien chargee."""
    return API_KEY is not None and len(API_KEY) > 10


def recuperer_news(mot_cle, langue="fr", nb_articles=20, jours=7):
    """
    Recupere les articles correspondant a un mot-cle.

    Args:
        mot_cle : mot-cle de recherche
        langue  : code langue (fr, en, es...)
        nb_articles : nombre max d'articles (max 100 sur plan gratuit)
        jours   : nombre de jours en arriere (7 par defaut)

    Returns:
        Liste de dictionnaires (articles) ou liste vide si erreur
    """
    if not est_configure():
        return []

    # Date de debut (il y a X jours)
    date_debut = (datetime.now() - timedelta(days=jours)).strftime("%Y-%m-%d")

    parametres = {
        "q": mot_cle,
        "language": langue,
        "pageSize": min(nb_articles, 100),
        "sortBy": "publishedAt",
        "from": date_debut,
        "apiKey": API_KEY
    }

    try:
        reponse = requests.get(API_URL, params=parametres, timeout=15)
        reponse.raise_for_status()

        donnees = reponse.json()

        if donnees.get("status") != "ok":
            return []

        articles = []
        for a in donnees.get("articles", []):
            articles.append({
                "titre": a.get("title") or "",
                "source": a.get("source", {}).get("name") or "",
                "auteur": a.get("author") or "",
                "date": a.get("publishedAt") or "",
                "url": a.get("url") or "",
                "description": a.get("description") or "",
                "image": a.get("urlToImage") or ""
            })

        return articles

    except Exception as e:
        print(f"Erreur : {e}")
        return []


def recuperer_news_multi(mots_cles, langue="fr", nb_par_mot=10, jours=7):
    """
    Recupere les news pour plusieurs mots-cles.
    Fusionne et deduplique par titre.
    """
    tous = []
    titres_vus = set()

    for mot in mots_cles:
        articles = recuperer_news(mot, langue=langue, nb_articles=nb_par_mot, jours=jours)
        for a in articles:
            if a["titre"] and a["titre"] not in titres_vus:
                a["mot_cle"] = mot  # Garde la trace du mot-cle de recherche
                tous.append(a)
                titres_vus.add(a["titre"])

    # Tri par date decroissante
    tous.sort(key=lambda x: x["date"], reverse=True)
    return tous