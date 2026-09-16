"""
Module cockpit_stats.py - Requetes pour le dashboard Cockpit
Etape G - Session 1 (avec db_universal)
"""

from db_universal import get_connexion


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
        result = curseur.fetchone()
        if result:
            # Convertir les Decimal en int/float pour compatibilite SQLite
            return {
                "total_articles": int(result.get("total_articles") or 0),
                "total_sources": int(result.get("total_sources") or 0),
                "total_analyses_themes": int(result.get("total_analyses_themes") or 0),
                "total_analyses_sentiment": int(result.get("total_analyses_sentiment") or 0),
                "articles_classes": int(result.get("articles_classes") or 0),
                "themes_actifs": int(result.get("themes_actifs") or 0),
                "score_moyen": float(result.get("score_moyen") or 0)
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
        rows = curseur.fetchall()
        # Convertir les Decimal en int
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
    """
    Sentiment par source (top sources).
    Version 2 requetes separees (compatible MySQL et SQLite).
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

        rows = curseur.fetchall()
        top_sources_list = [row["source"] for row in rows]

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
# TEST DU MODULE
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("TEST DU MODULE cockpit_stats.py")
    print("=" * 60)
    print()

    # Test 1 : KPIs globaux
    print("1. KPIs globaux :")
    kpis = kpis_globaux()
    for k, v in kpis.items():
        print(f"   {k}: {v}")
    print()

    # Test 2 : Sentiment
    print("2. Sentiment global :")
    sentiment = stats_sentiment()
    print(f"   {sentiment}")
    print()

    # Test 3 : Themes
    print("3. Repartition par theme :")
    themes = stats_themes_rapide()
    for t in themes:
        print(f"   {t['theme']}: {t['nb_articles']} articles")
    print()

    # Test 4 : Top sources
    print("4. Top 3 sources :")
    sources = top_sources(3)
    for s in sources:
        print(f"   {s['source']}: {s['nb_articles']} articles")
    print()

    # Test 5 : Derniers articles
    print("5. Derniers 2 articles :")
    derniers = derniers_articles(2)
    for d in derniers:
        print(f"   - {d['titre'][:60]}...")
    print()

    print("=" * 60)
    print("TEST TERMINE")
    print("=" * 60)