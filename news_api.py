"""
Module news_api - Fonctions reutilisables pour NewsAPI
Etape B - Session 2 (avec support Streamlit Secrets)
"""

import os
import requests
from datetime import datetime, timedelta

# ============================================================
# CHARGEMENT DE LA CLE API (Streamlit Secrets OU .env)
# ============================================================
API_KEY = None

# 1. Essayer Streamlit Secrets (cloud Streamlit)
try:
    import streamlit as st
    API_KEY = st.secrets.get("NEWSAPI_KEY")
except Exception:
    pass

# 2. Si pas trouve, essayer le fichier .env (local)
if not API_KEY:
    try:
        from dotenv import load_dotenv
        load_dotenv()
        API_KEY = os.getenv("NEWSAPI_KEY")
    except Exception:
        pass

# 3. Afficher un avertissement si rien n'est trouve
if not API_KEY:
    print("ATTENTION : NEWSAPI_KEY non trouvee (ni Streamlit Secrets, ni .env)")

API_URL = "https://newsapi.org/v2/everything"


# ============================================================
# FONCTIONS
# ============================================================
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


# ============================================================
# TEST
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("TEST DU MODULE news_api.py")
    print("=" * 60)
    print()

    if est_configure():
        print("Cle API chargee : OK")
        print(f"   Debut : {API_KEY[:8]}...")
        print()

        print("Test de recuperation (5 articles sur 'Tunisie')...")
        articles = recuperer_news("Tunisie", nb_articles=5, jours=7)

        if articles:
            print(f"OK - {len(articles)} articles recuperes")
            for i, a in enumerate(articles[:3], 1):
                print(f"   {i}. {a['titre'][:70]}...")
        else:
            print("Aucun article recupere")
    else:
        print("ATTENTION : Cle API non configuree")
        print("   - En local : ajoutez NEWSAPI_KEY dans .env")
        print("   - Sur Streamlit Cloud : ajoutez dans Settings > Secrets")

    print()
    print("=" * 60)
    print("TEST TERMINE")
    print("=" * 60)