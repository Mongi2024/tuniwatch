"""
Module cockpit_stats.py - Requetes pour le dashboard Cockpit
Version 2.0 - Ajout fonctions analyse par média et par thème
"""

from db_universal import get_connexion
from datetime import datetime, timedelta


# ============================================================
# FONCTIONS EXISTANTES (inchangées)
# ============================================================

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
                (SELECT AVG(score) FROM articles_sentiment) AS score_moyen
        """)
        result = curseur.fetchone()
        if result:
            return {
                "total_articles": int(result.get("total_articles") or 0),
                "total_sources": int(result.get("total_sources") or 0),
                "total_analyses_themes": int(result.get("total_analyses_themes") or 0),
                "total_analyses_sentiment": int(result.get("total_analyses_sentiment") or 0),
                "articles_classes": int(result.get("articles_classes") or 0),
                "themes_actifs": int(result.get("themes_actifs") or 0),
                "score_moyen": round(float(result.get("score_moyen") or 0), 2)
            }
        return {}
    finally:
        curseur.close()
        conn.close()


def stats_sentiment():
    """Repartition par sentiment (avec conversion int)."""
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
        result = curseur.fetchone()
        if result:
            return {
                "positifs": int(result.get("positifs") or 0),
                "neutres": int(result.get("neutres") or 0),
                "negatifs": int(result.get("negatifs") or 0)
            }
        return {}
    finally:
        curseur.close()
        conn.close()


def evolution_mentions(jours=30):
    """Evolution du nombre d'articles par jour."""
    date_limite = (datetime.now() - timedelta(days=jours)).strftime("%Y-%m-%d %H:%M:%S")

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
            WHERE date_ajout >= %s
            GROUP BY DATE(date_ajout)
            ORDER BY jour
        """, (date_limite,))
        rows = curseur.fetchall()
        return [
            {"jour": str(r["jour"]), "nb": int(r["nb"])}
            for r in rows
        ]
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
        rows = curseur.fetchall()
        return [
            {"source": r["source"], "nb_articles": int(r["nb_articles"])}
            for r in rows
        ]
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
        rows = curseur.fetchall()
        return [
            {
                "id": int(r["id"]),
                "titre": r["titre"],
                "source": r["source"],
                "url": r["url"],
                "date_ajout": str(r["date_ajout"]) if r["date_ajout"] else None,
                "date_publication": str(r["date_publication"]) if r["date_publication"] else None
            }
            for r in rows
        ]
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
        rows = curseur.fetchall()
        return [
            {
                "id": int(r["id"]),
                "titre": r["titre"],
                "source": r["source"],
                "url": r["url"],
                "theme": r["theme"],
                "score": float(r["score"]),
                "mots_trouves": r["mots_trouves"]
            }
            for r in rows
        ]
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
        rows = curseur.fetchall()
        return [
            {"theme": r["theme"], "nb_articles": int(r["nb_articles"])}
            for r in rows
        ]
    finally:
        curseur.close()
        conn.close()


def sentiment_par_source(limite=8):
    """Sentiment par source (top sources)."""
    conn = get_connexion()
    if conn is None:
        return []

    curseur = conn.cursor(dictionary=True)
    try:
        curseur.execute("""
            SELECT source
            FROM articles
            WHERE source IS NOT NULL AND source != ''
            GROUP BY source
            ORDER BY COUNT(*) DESC
            LIMIT %s
        """, (limite,))

        rows = curseur.fetchall()
        top_sources_list = [row["source"] for row in rows]

        if not top_sources_list:
            return []

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

        rows = curseur.fetchall()
        return [
            {
                "source": r["source"],
                "sentiment": r["sentiment"],
                "nb": int(r["nb"])
            }
            for r in rows
        ]
    finally:
        curseur.close()
        conn.close()


# ============================================================
# NOUVELLES FONCTIONS - Analyse par média et par thème
# ============================================================

def liste_sources_actives():
    """Liste toutes les sources actives (pour les filtres)."""
    conn = get_connexion()
    if conn is None:
        return []
    curseur = conn.cursor(dictionary=True)
    try:
        curseur.execute("""
            SELECT DISTINCT source
            FROM articles
            WHERE source IS NOT NULL AND source != ''
            ORDER BY source
        """)
        rows = curseur.fetchall()
        return [row["source"] for row in rows]
    finally:
        curseur.close()
        conn.close()


def stats_par_source(source, jours=30):
    """
    Statistiques complètes pour un média donné.
    Retourne : dict avec nb_articles, nb_themes, score_moyen, sentiments.
    """
    conn = get_connexion()
    if conn is None:
        return {}

    curseur = conn.cursor(dictionary=True)
    try:
        # 1. Nombre d'articles
        curseur.execute("""
            SELECT COUNT(*) AS nb FROM articles WHERE source = %s
        """, (source,))
        nb_articles = int(curseur.fetchone()["nb"] or 0)

        # 2. Nombre de thèmes distincts détectés
        curseur.execute("""
            SELECT COUNT(DISTINCT at.theme) AS nb
            FROM articles_themes at
            JOIN articles a ON a.id = at.article_id
            WHERE a.source = %s
        """, (source,))
        nb_themes = int(curseur.fetchone()["nb"] or 0)

        # 3. Score moyen des thèmes
        curseur.execute("""
            SELECT AVG(at.score) AS moyenne
            FROM articles_themes at
            JOIN articles a ON a.id = at.article_id
            WHERE a.source = %s
        """, (source,))
        score_moyen = round(float(curseur.fetchone()["moyenne"] or 0), 2)

        # 4. Répartition des sentiments
        curseur.execute("""
            SELECT 
                SUM(CASE WHEN s.sentiment = 'positif' THEN 1 ELSE 0 END) AS positifs,
                SUM(CASE WHEN s.sentiment = 'neutre' THEN 1 ELSE 0 END) AS neutres,
                SUM(CASE WHEN s.sentiment = 'negatif' THEN 1 ELSE 0 END) AS negatifs
            FROM articles_sentiment s
            JOIN articles a ON a.id = s.article_id
            WHERE a.source = %s
        """, (source,))
        sent = curseur.fetchone()

        return {
            "source": source,
            "nb_articles": nb_articles,
            "nb_themes": nb_themes,
            "score_moyen": score_moyen,
            "positifs": int(sent.get("positifs") or 0),
            "neutres": int(sent.get("neutres") or 0),
            "negatifs": int(sent.get("negatifs") or 0)
        }
    finally:
        curseur.close()
        conn.close()


def themes_par_source(source, limite=10):
    """
    Répartition thématique pour un média donné.
    Retourne : [{theme, nb_articles, score_moyen}, ...]
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
                AVG(at.score) AS score_moyen
            FROM articles_themes at
            JOIN articles a ON a.id = at.article_id
            WHERE a.source = %s
            GROUP BY at.theme
            ORDER BY nb_articles DESC
            LIMIT %s
        """, (source, limite))
        rows = curseur.fetchall()
        return [
            {
                "theme": r["theme"],
                "nb_articles": int(r["nb_articles"]),
                "score_moyen": round(float(r["score_moyen"] or 0), 2)
            }
            for r in rows
        ]
    finally:
        curseur.close()
        conn.close()


def evolution_par_source(source, jours=30):
    """
    Évolution quotidienne d'un média donné.
    Retourne : [{jour, nb}, ...]
    """
    date_limite = (datetime.now() - timedelta(days=jours)).strftime("%Y-%m-%d %H:%M:%S")

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
            WHERE source = %s AND date_ajout >= %s
            GROUP BY DATE(date_ajout)
            ORDER BY jour
        """, (source, date_limite))
        rows = curseur.fetchall()
        return [
            {"jour": str(r["jour"]), "nb": int(r["nb"])}
            for r in rows
        ]
    finally:
        curseur.close()
        conn.close()


def articles_par_source(source, limite=10):
    """
    Derniers articles d'un média donné.
    Retourne : [{id, titre, url, date_ajout, theme, score}, ...]
    """
    conn = get_connexion()
    if conn is None:
        return []
    curseur = conn.cursor(dictionary=True)
    try:
        curseur.execute("""
            SELECT 
                a.id, a.titre, a.url, a.date_ajout,
                at.theme, at.score
            FROM articles a
            LEFT JOIN articles_themes at ON at.article_id = a.id
            WHERE a.source = %s
            ORDER BY a.id DESC
            LIMIT %s
        """, (source, limite))
        rows = curseur.fetchall()
        return [
            {
                "id": int(r["id"]),
                "titre": r["titre"],
                "url": r["url"],
                "date_ajout": str(r["date_ajout"]) if r["date_ajout"] else None,
                "theme": r["theme"],
                "score": float(r["score"]) if r["score"] else 0.0
            }
            for r in rows
        ]
    finally:
        curseur.close()
        conn.close()


def sentiment_par_theme(limite=10):
    """
    Répartition sentiment par thème (pour heatmap ou stacked bar).
    Retourne : [{theme, sentiment, nb}, ...]
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
                COUNT(*) AS nb
            FROM articles_themes at
            JOIN articles_sentiment s ON s.article_id = at.article_id
            GROUP BY at.theme, s.sentiment
            ORDER BY at.theme, s.sentiment
        """)
        rows = curseur.fetchall()
        return [
            {
                "theme": r["theme"],
                "sentiment": r["sentiment"],
                "nb": int(r["nb"])
            }
            for r in rows
        ][:limite * 3]
    finally:
        curseur.close()
        conn.close()


def comparaison_sources(sources_list, jours=30):
    """
    Compare plusieurs médias dans le temps (graphique multi-lignes).
    Retourne : [{jour, source, nb}, ...]
    """
    if not sources_list:
        return []

    date_limite = (datetime.now() - timedelta(days=jours)).strftime("%Y-%m-%d %H:%M:%S")

    conn = get_connexion()
    if conn is None:
        return []
    curseur = conn.cursor(dictionary=True)
    try:
        placeholders = ",".join(["%s"] * len(sources_list))
        curseur.execute(f"""
            SELECT 
                DATE(date_ajout) AS jour,
                source,
                COUNT(*) AS nb
            FROM articles
            WHERE source IN ({placeholders}) AND date_ajout >= %s
            GROUP BY DATE(date_ajout), source
            ORDER BY jour, source
        """, tuple(sources_list) + (date_limite,))
        rows = curseur.fetchall()
        return [
            {
                "jour": str(r["jour"]),
                "source": r["source"],
                "nb": int(r["nb"])
            }
            for r in rows
        ]
    finally:
        curseur.close()
        conn.close()


# ============================================================
# TEST DU MODULE
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("TEST DU MODULE cockpit_stats.py")
    print("=" * 60)
    print()

    print("1. KPIs globaux :")
    kpis = kpis_globaux()
    for k, v in kpis.items():
        print(f"   {k}: {v}")
    print()

    print("2. Sentiment global :")
    sentiment = stats_sentiment()
    print(f"   {sentiment}")
    print()

    print("3. Evolution mentions (30 jours) :")
    evolution = evolution_mentions(30)
    print(f"   {len(evolution)} jours avec donnees")
    print()

    print("4. Repartition par theme :")
    themes = stats_themes_rapide()
    for t in themes:
        print(f"   {t['theme']}: {t['nb_articles']} articles")
    print()

    print("5. Top 3 sources :")
    sources = top_sources(3)
    for s in sources:
        print(f"   {s['source']}: {s['nb_articles']} articles")
    print()

    print("6. Liste des sources actives :")
    liste = liste_sources_actives()
    print(f"   {len(liste)} sources : {liste[:3]}...")
    print()

    print("7. Stats par source (première source) :")
    if liste:
        stats = stats_par_source(liste[0])
        for k, v in stats.items():
            print(f"   {k}: {v}")
    print()

    print("=" * 60)
    print("TEST TERMINE")
    print("=" * 60)