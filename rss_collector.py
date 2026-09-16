"""
Module rss_collector.py - Collecte des articles via flux RSS
Etape B - Session 1
"""

import feedparser
import mysql.connector
from mysql.connector import Error
from datetime import datetime
from time import mktime
import re
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# ============================================================
# CONFIGURATION
# ============================================================
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "python_user",
    "password": "PythonUser2026!",
    "database": "monitoring",
    "charset": "utf8mb4"
}


def get_connexion():
    """Ouvre une connexion MySQL."""
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        print(f"Erreur connexion : {e}")
        return None


def nettoyer_texte(texte, max_len=1000):
    """Nettoie un texte (retire HTML, espaces multiples, limite longueur)."""
    if not texte:
        return ""

    # Retirer les balises HTML
    texte = re.sub(r'<[^>]+>', '', texte)

    # Decoder les entites HTML basiques
    texte = texte.replace("&nbsp;", " ").replace("&amp;", "&")
    texte = texte.replace("&lt;", "<").replace("&gt;", ">")
    texte = texte.replace("&quot;", '"').replace("&#39;", "'")

    # Espaces multiples
    texte = re.sub(r'\s+', ' ', texte).strip()

    # Limiter la longueur
    return texte[:max_len]


def parser_date(entry):
    """Essaie d'extraire une date d'une entree RSS."""
    try:
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            return datetime.fromtimestamp(mktime(entry.published_parsed))
        if hasattr(entry, "updated_parsed") and entry.updated_parsed:
            return datetime.fromtimestamp(mktime(entry.updated_parsed))
    except Exception:
        pass
    return None


# ============================================================
# LISTER LES SOURCES RSS
# ============================================================
def lister_sources_avec_rss():
    """Retourne la liste des sources ayant un flux RSS renseigne."""
    conn = get_connexion()
    if conn is None:
        return []

    curseur = conn.cursor(dictionary=True)
    try:
        curseur.execute("""
            SELECT id, nom, categorie, langue, url_rss
            FROM sources
            WHERE actif = 1 AND url_rss IS NOT NULL AND url_rss != ''
            ORDER BY categorie, nom
        """)
        return curseur.fetchall()
    finally:
        curseur.close()
        conn.close()


# ============================================================
# COLLECTE D'UN FLUX RSS
# ============================================================
def collecter_flux(url_rss, nom_source, max_articles=50):
    """
    Recupere les articles d'un flux RSS (avec SSL tolerant).
    Utilise requests pour gerer les certificats expires des radios tunisiennes.
    """
    import requests

    print(f"   Collecte : {nom_source}...")

    try:
        # Recuperer le contenu avec requests (SSL tolerant)
        headers = {
            "User-Agent": "Mozilla/5.0 (Monitoring Observatoire TN)"
        }
        reponse = requests.get(
            url_rss,
            headers=headers,
            timeout=15,
            verify=False  # Tolerant SSL pour radios tunisiennes
        )
        reponse.raise_for_status()

        # Parser le contenu avec feedparser
        flux = feedparser.parse(reponse.content)

        if flux.bozo and not flux.entries:
            print(f"      Erreur parsing : {flux.bozo_exception}")
            return []

        articles = []
        for entry in flux.entries[:max_articles]:
            titre = nettoyer_texte(getattr(entry, "title", ""), 500)
            lien = getattr(entry, "link", "")
            auteur = nettoyer_texte(getattr(entry, "author", ""), 200)

            description = ""
            for field in ["summary", "description", "content"]:
                if hasattr(entry, field):
                    val = getattr(entry, field)
                    if isinstance(val, list) and val:
                        val = val[0].get("value", "")
                    if val:
                        description = nettoyer_texte(str(val), 1000)
                        break

            date_pub = parser_date(entry)

            if not titre or not lien:
                continue

            articles.append({
                "titre": titre,
                "source": nom_source,
                "auteur": auteur,
                "date": date_pub,
                "url": lien[:1000],
                "description": description,
                "mot_cle": "rss_collect"
            })

        print(f"      OK : {len(articles)} articles")
        return articles

    except Exception as e:
        print(f"      Erreur : {e}")
        return []


# ============================================================
# SAUVEGARDE EN BASE
# ============================================================
def sauvegarder_articles(articles):
    """Insere les articles dans la table articles (ignore les doublons)."""
    if not articles:
        return 0

    conn = get_connexion()
    if conn is None:
        return 0

    curseur = conn.cursor()
    inseres = 0
    ignores = 0

    try:
        for a in articles:
            try:
                curseur.execute("""
                    INSERT INTO articles
                        (titre, source, auteur, date_publication,
                         url, description, mot_cle)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    a["titre"][:500],
                    a["source"][:200],
                    a["auteur"][:200],
                    a["date"],
                    a["url"][:1000],
                    a["description"],
                    a["mot_cle"][:200]
                ))
                inseres += 1
            except mysql.connector.IntegrityError:
                ignores += 1

        conn.commit()
        print(f"      --> {inseres} inseres, {ignores} doublons ignores")
        return inseres

    except Error as e:
        conn.rollback()
        print(f"      Erreur insertion : {e}")
        return 0
    finally:
        curseur.close()
        conn.close()


# ============================================================
# COLLECTE COMPLETE
# ============================================================
def collecter_tout(max_par_source=30):
    """Collecte tous les flux RSS actifs."""
    sources = lister_sources_avec_rss()

    if not sources:
        print("Aucune source RSS disponible.")
        return {"sources": 0, "articles": 0}

    print(f"Collecte sur {len(sources)} source(s)...")
    print()

    total_articles = 0

    for src in sources:
        articles = collecter_flux(src["url_rss"], src["nom"], max_par_source)
        if articles:
            nb = sauvegarder_articles(articles)
            total_articles += nb

    print()
    print(f"Total : {total_articles} articles inseres")

    return {"sources": len(sources), "articles": total_articles}


def compter_articles():
    """Compte les articles en base."""
    conn = get_connexion()
    if conn is None:
        return 0
    curseur = conn.cursor()
    try:
        curseur.execute("SELECT COUNT(*) FROM articles")
        return curseur.fetchone()[0]
    finally:
        curseur.close()
        conn.close()


# ============================================================
# TEST DIRECT
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("TEST DU MODULE rss_collector.py")
    print("=" * 60)
    print()

    # Test 1 : Lister les sources RSS
    sources = lister_sources_avec_rss()
    print(f"1. Sources RSS disponibles : {len(sources)}")
    for s in sources[:5]:
        print(f"   - [{s['categorie']}] {s['nom']}")
    if len(sources) > 5:
        print(f"   ... et {len(sources) - 5} autres")
    print()

    # Test 2 : Compter les articles AVANT
    nb_avant = compter_articles()
    print(f"2. Articles en base AVANT : {nb_avant}")
    print()

    # Test 3 : Collecte sur UN flux (le premier)
    if sources:
        print("3. Test de collecte sur le premier flux :")
        premiere = sources[0]
        print(f"   Source : {premiere['nom']}")
        articles = collecter_flux(premiere["url_rss"], premiere["nom"], max_articles=5)
        print()

        if articles:
            for i, a in enumerate(articles[:3], 1):
                print(f"   {i}. {a['titre'][:70]}...")
            print()

            # Sauvegarder
            print("4. Sauvegarde en base :")
            nb_inseres = sauvegarder_articles(articles)
            print()

    # Test 4 : Compter APRES
    nb_apres = compter_articles()
    print(f"5. Articles en base APRES : {nb_apres}")
    print(f"   Augmentation : +{nb_apres - nb_avant}")
    print()

    print("=" * 60)
    print("TEST TERMINE")
    print("=" * 60)