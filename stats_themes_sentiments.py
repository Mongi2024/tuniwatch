"""
Module stats_themes_sentiments.py - Statistiques croisees themes x sentiments
Etape F - Session 2
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
        print(f"Erreur connexion : {e}")
        return None


def stats_themes_avec_sentiment():
    """
    Statistiques croisees : nombre d'articles par theme ET par sentiment.
    Retourne une liste de dicts.
    """
    conn = get_connexion()
    if conn is None:
        return []

    curseur = conn.cursor(dictionary=True)
    try:
        curseur.execute("""
            SELECT 
                at.theme,
                s.sentiment,
                COUNT(DISTINCT at.article_id) AS nb
            FROM articles_themes at
            JOIN articles_sentiment s ON s.article_id = at.article_id
            GROUP BY at.theme, s.sentiment
            ORDER BY at.theme, s.sentiment
        """)
        return curseur.fetchall()
    finally:
        curseur.close()
        conn.close()


def stats_par_theme_detail():
    """
    Pour chaque theme : nb articles, score moyen sentiment, repartition.
    """
    conn = get_connexion()
    if conn is None:
        return []

    curseur = conn.cursor(dictionary=True)
    try:
        curseur.execute("""
            SELECT 
                at.theme,
                COUNT(DISTINCT at.article_id) AS nb_articles,
                ROUND(AVG(s.score), 2) AS score_moyen_sentiment,
                SUM(CASE WHEN s.sentiment = 'positif' THEN 1 ELSE 0 END) AS nb_positifs,
                SUM(CASE WHEN s.sentiment = 'neutre' THEN 1 ELSE 0 END) AS nb_neutres,
                SUM(CASE WHEN s.sentiment = 'negatif' THEN 1 ELSE 0 END) AS nb_negatifs
            FROM articles_themes at
            JOIN articles_sentiment s ON s.article_id = at.article_id
            GROUP BY at.theme
            ORDER BY nb_articles DESC
        """)
        return curseur.fetchall()
    finally:
        curseur.close()
        conn.close()


def stats_par_langue_theme():
    """Pour chaque theme : repartition par langue detectee."""
    conn = get_connexion()
    if conn is None:
        return []

    curseur = conn.cursor(dictionary=True)
    try:
        curseur.execute("""
            SELECT 
                at.theme,
                s.langue_detectee AS langue,
                COUNT(DISTINCT at.article_id) AS nb
            FROM articles_themes at
            JOIN articles_sentiment s ON s.article_id = at.article_id
            WHERE s.langue_detectee IS NOT NULL
            GROUP BY at.theme, s.langue_detectee
            ORDER BY at.theme, nb DESC
        """)
        return curseur.fetchall()
    finally:
        curseur.close()
        conn.close()


def evolution_sentiment_par_theme(theme):
    """Evolution temporelle du sentiment pour un theme."""
    conn = get_connexion()
    if conn is None:
        return []

    curseur = conn.cursor(dictionary=True)
    try:
        curseur.execute("""
            SELECT 
                DATE(a.date_ajout) AS jour,
                s.sentiment,
                COUNT(*) AS nb
            FROM articles_themes at
            JOIN articles a ON a.id = at.article_id
            JOIN articles_sentiment s ON s.article_id = at.article_id
            WHERE at.theme = %s AND a.date_ajout IS NOT NULL
            GROUP BY DATE(a.date_ajout), s.sentiment
            ORDER BY jour
        """, (theme,))
        return curseur.fetchall()
    finally:
        curseur.close()
        conn.close()


# ============================================================
# TEST
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("TEST DU MODULE stats_themes_sentiments.py")
    print("=" * 60)
    print()

    print("1. Stats croisees (theme x sentiment) :")
    stats = stats_themes_avec_sentiment()
    print(f"   {len(stats)} lignes")
    for s in stats[:5]:
        print(f"   - {s['theme']:25} | {s['sentiment']:10} | {s['nb']} articles")
    print()

    print("2. Stats detaillees par theme :")
    detail = stats_par_theme_detail()
    print(f"   {len(detail)} themes")
    for d in detail:
        print(f"   - {d['theme']:25} | {d['nb_articles']} art | "
              f"score={d['score_moyen_sentiment']:.2f} | "
              f"P:{d['nb_positifs']} N:{d['nb_neutres']} Neg:{d['nb_negatifs']}")
    print()

    print("3. Repartition par langue :")
    langue = stats_par_langue_theme()
    for l in langue[:5]:
        print(f"   - {l['theme']:25} | {l['langue']:5} | {l['nb']}")
    print()

    print("=" * 60)
    print("TEST TERMINE")
    print("=" * 60)