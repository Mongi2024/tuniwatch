"""
Module cockpit_stats.py - Requetes pour le dashboard Cockpit
Etape G - Session 1 (avec correction sentiment_par_source)
"""

import mysql.connector
from mysql.connector import Error


DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "python_user",
    "password": "PythonUser2026!",
    "database": "monitoring",
    "charset": "utf8mb4"
}


def get_connexion():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        print(f"Erreur : {e}")
        return None


def kpis_globaux():
    """KPIs principaux pour la page d'accueil."""
    conn = get_connexion()
    if conn is None:
        return {}

    curseur = conn.cursor(dictionary=True)
    try:
        curseur.execute("""
            SELECT 
                (SELECT COUNT(*) FROM articles) AS total_articles,
                (SELECT COUNT(*) FROM sources WHERE actif = 1) AS total_sources,
                (SELECT COUNT(*) FROM articles_themes) AS total_analyses_themes,
                (SELECT COUNT(*) FROM articles_sentiment) AS total_analyses_sentiment,
                (SELECT COUNT(DISTINCT article_id) FROM articles_themes) AS articles_classes,
                (SELECT COUNT(DISTINCT theme) FROM articles_themes) AS themes_actifs,
                (SELECT ROUND(AVG(score), 2) FROM articles_sentiment) AS score_moyen
        """)
        return curseur.fetchone()
    finally:
        curseur.close()
        conn.close()


def stats_sentiment():
    """Repartition par sentiment."""
    conn = get_connexion()
    if conn is None:
        return {}
    curseur = conn.cursor(dictionary=True)
    try:
        curseur.execute("""
            SELECT 
                SUM(CASE WHEN sentiment = 'positif' THEN 1 ELSE 0 END) AS positifs,
                SUM(CASE WHEN sentiment = 'neutre' THEN 1 ELSE 0 END) AS neutres,
                SUM(CASE WHEN sentiment = 'negatif' THEN 1 ELSE 0 END) AS negatifs
            FROM articles_sentiment
        """)
        return curseur.fetchone()
    finally:
        curseur.close()
        conn.close()


def evolution_mentions(jours=30):
    """Evolution du nombre d'articles par jour."""
    conn = get_connexion()
    if conn is None:
        return []
    curseur = conn.cursor(dictionary=True)
    try:
        curseur.execute("""
            SELECT 
                DATE(date_ajout) AS jour,
                COUNT(*) AS nb
            FROM articles
            WHERE date_ajout >= DATE_SUB(NOW(), INTERVAL %s DAY)
            GROUP BY DATE(date_ajout)
            ORDER BY jour
        """, (jours,))
        return curseur.fetchall()
    finally:
        curseur.close()
        conn.close()


def top_sources(limite=10):
    """Top sources par nombre d'articles."""
    conn = get_connexion()
    if conn is None:
        return []
    curseur = conn.cursor(dictionary=True)
    try:
        curseur.execute("""
            SELECT source, COUNT(*) AS nb_articles
            FROM articles
            WHERE source IS NOT NULL AND source != ''
            GROUP BY source
            ORDER BY nb_articles DESC
            LIMIT %s
        """, (limite,))
        return curseur.fetchall()
    finally:
        curseur.close()
        conn.close()


def derniers_articles(limite=5):
    """Derniers articles collectes."""
    conn = get_connexion()
    if conn is None:
        return []
    curseur = conn.cursor(dictionary=True)
    try:
        curseur.execute("""
            SELECT id, titre, source, url, date_ajout, date_publication
            FROM articles
            ORDER BY id DESC
            LIMIT %s
        """, (limite,))
        return curseur.fetchall()
    finally:
        curseur.close()
        conn.close()


def top_articles_pertinents(limite=5):
    """Articles les plus pertinents (score maximum)."""
    conn = get_connexion()
    if conn is None:
        return []
    curseur = conn.cursor(dictionary=True)
    try:
        curseur.execute("""
            SELECT 
                a.id, a.titre, a.source, a.url,
                at.theme, at.score, at.mots_trouves
            FROM articles_themes at
            JOIN articles a ON a.id = at.article_id
            ORDER BY at.score DESC
            LIMIT %s
        """, (limite,))
        return curseur.fetchall()
    finally:
        curseur.close()
        conn.close()


def stats_themes_rapide():
    """Nombre d'articles par theme."""
    conn = get_connexion()
    if conn is None:
        return []
    curseur = conn.cursor(dictionary=True)
    try:
        curseur.execute("""
            SELECT theme, COUNT(DISTINCT article_id) AS nb_articles
            FROM articles_themes
            GROUP BY theme
            ORDER BY nb_articles DESC
        """)
        return curseur.fetchall()
    finally:
        curseur.close()
        conn.close()


def sentiment_par_source(limite=8):
    """
    Sentiment par source (top sources).
    Version corrigee : 2 requetes separees (pas de subquery avec LIMIT).
    """
    conn = get_connexion()
    if conn is None:
        return []

    curseur = conn.cursor(dictionary=True)
    try:
        # 1. Recuperer d'abord les top sources
        curseur.execute("""
            SELECT source
            FROM articles
            WHERE source IS NOT NULL AND source != ''
            GROUP BY source
            ORDER BY COUNT(*) DESC
            LIMIT %s
        """, (limite,))

        top_sources_list = [row["source"] for row in curseur.fetchall()]

        if not top_sources_list:
            return []

        # 2. Construire la requete avec une liste de sources
        placeholders = ",".join(["%s"] * len(top_sources_list))

        curseur.execute(f"""
            SELECT 
                a.source,
                s.sentiment,
                COUNT(*) AS nb
            FROM articles a
            JOIN articles_sentiment s ON s.article_id = a.id
            WHERE a.source IN ({placeholders})
            GROUP BY a.source, s.sentiment
            ORDER BY a.source, s.sentiment
        """, tuple(top_sources_list))

        return curseur.fetchall()
    finally:
        curseur.close()
        conn.close()