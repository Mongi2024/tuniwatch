"""
Module alert_detector.py - Detection automatique d'anomalies
Etape H - Session 1 (avec fonction articles lies)
"""

import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta


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


# ============================================================
# DETECTION DES ANOMALIES
# ============================================================

def detecter_pics_mentions():
    """
    Detecte les pics d'articles sur un theme.
    Compare le nombre d'articles des 3 derniers jours vs les 7 jours precedents.
    """
    conn = get_connexion()
    if conn is None:
        return []

    curseur = conn.cursor(dictionary=True)
    alertes = []

    try:
        # Articles recents (3 derniers jours)
        curseur.execute("""
            SELECT at.theme, COUNT(DISTINCT at.article_id) AS nb_recents
            FROM articles_themes at
            JOIN articles a ON a.id = at.article_id
            WHERE a.date_ajout >= DATE_SUB(NOW(), INTERVAL 3 DAY)
            GROUP BY at.theme
        """)
        recents = {r["theme"]: r["nb_recents"] for r in curseur.fetchall()}

        # Articles precedents (7 jours avant)
        curseur.execute("""
            SELECT at.theme, COUNT(DISTINCT at.article_id) AS nb_anciens
            FROM articles_themes at
            JOIN articles a ON a.id = at.article_id
            WHERE a.date_ajout BETWEEN DATE_SUB(NOW(), INTERVAL 10 DAY)
                                    AND DATE_SUB(NOW(), INTERVAL 3 DAY)
            GROUP BY at.theme
        """)
        anciens = {r["theme"]: r["nb_anciens"] for r in curseur.fetchall()}

        # Comparer
        for theme, nb_recent in recents.items():
            nb_ancien = anciens.get(theme, 0)

            # Seuil : au moins 5 articles recents ET 2x plus que la periode precedente
            if nb_recent >= 5 and nb_ancien > 0:
                ratio = nb_recent / max(nb_ancien, 1)
                if ratio >= 2.0:
                    alertes.append({
                        "niveau": "attention",
                        "message": f"Pic d'activite sur '{theme}' : {nb_recent} articles recents (x{ratio:.1f} vs periode precedente)",
                        "mot_cle": theme
                    })

    except Error as e:
        print(f"Erreur pics : {e}")
    finally:
        curseur.close()
        conn.close()

    return alertes


def detecter_sentiment_negatif():
    """
    Detecte les themes avec un sentiment tres negatif.
    """
    conn = get_connexion()
    if conn is None:
        return []

    curseur = conn.cursor(dictionary=True)
    alertes = []

    try:
        curseur.execute("""
            SELECT 
                at.theme,
                COUNT(DISTINCT at.article_id) AS nb_articles,
                ROUND(AVG(s.score), 2) AS score_moyen,
                SUM(CASE WHEN s.sentiment = 'negatif' THEN 1 ELSE 0 END) AS nb_negatifs
            FROM articles_themes at
            JOIN articles_sentiment s ON s.article_id = at.article_id
            WHERE s.sentiment = 'negatif'
            GROUP BY at.theme
            HAVING score_moyen < -0.5 AND nb_articles >= 2
        """)

        for row in curseur.fetchall():
            alertes.append({
                "niveau": "critique",
                "message": f"Sentiment tres negatif sur '{row['theme']}' : "
                           f"score {row['score_moyen']:.2f} sur {row['nb_articles']} articles",
                "mot_cle": row["theme"]
            })

    except Error as e:
        print(f"Erreur sentiment : {e}")
    finally:
        curseur.close()
        conn.close()

    return alertes


def detecter_baisse_activite():
    """
    Detecte les themes qui ont une chute d'activite.
    """
    conn = get_connexion()
    if conn is None:
        return []

    curseur = conn.cursor(dictionary=True)
    alertes = []

    try:
        curseur.execute("""
            SELECT at.theme, COUNT(DISTINCT at.article_id) AS nb_recents
            FROM articles_themes at
            JOIN articles a ON a.id = at.article_id
            WHERE a.date_ajout >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            GROUP BY at.theme
        """)
        recents = {r["theme"]: r["nb_recents"] for r in curseur.fetchall()}

        curseur.execute("""
            SELECT at.theme, COUNT(DISTINCT at.article_id) AS nb_anciens
            FROM articles_themes at
            JOIN articles a ON a.id = at.article_id
            WHERE a.date_ajout BETWEEN DATE_SUB(NOW(), INTERVAL 14 DAY)
                                    AND DATE_SUB(NOW(), INTERVAL 7 DAY)
            GROUP BY at.theme
        """)
        anciens = {r["theme"]: r["nb_anciens"] for r in curseur.fetchall()}

        for theme, nb_ancien in anciens.items():
            if nb_ancien >= 5:
                nb_recent = recents.get(theme, 0)
                if nb_recent < nb_ancien * 0.5:
                    alertes.append({
                        "niveau": "attention",
                        "message": f"Baisse d'activite sur '{theme}' : "
                                   f"{nb_recent} articles cette semaine (vs {nb_ancien} semaine precedente)",
                        "mot_cle": theme
                    })

    except Error as e:
        print(f"Erreur baisse : {e}")
    finally:
        curseur.close()
        conn.close()

    return alertes


def detecter_volume_global():
    """
    Detecte un pic global de collecte.
    """
    conn = get_connexion()
    if conn is None:
        return []

    curseur = conn.cursor(dictionary=True)
    alertes = []

    try:
        curseur.execute("""
            SELECT DATE(date_ajout) AS jour, COUNT(*) AS nb
            FROM articles
            WHERE date_ajout >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            GROUP BY DATE(date_ajout)
            ORDER BY jour
        """)

        jours = curseur.fetchall()

        if len(jours) >= 2:
            for i in range(1, len(jours)):
                nb_avant = jours[i-1]["nb"]
                nb_apres = jours[i]["nb"]

                if nb_avant >= 20 and nb_apres >= nb_avant * 3:
                    alertes.append({
                        "niveau": "critique",
                        "message": f"Pic global de collecte le {jours[i]['jour']} : "
                                   f"{nb_apres} articles (vs {nb_avant} la veille)",
                        "mot_cle": "global"
                    })

    except Error as e:
        print(f"Erreur volume : {e}")
    finally:
        curseur.close()
        conn.close()

    return alertes


# ============================================================
# SAUVEGARDE ET GESTION DES ALERTES
# ============================================================

def sauvegarder_alerte(alerte):
    """Sauvegarde une alerte si elle n'existe pas deja (meme message dans les 24h)."""
    conn = get_connexion()
    if conn is None:
        return False

    curseur = conn.cursor()
    try:
        # Verifier si alerte similaire dans les 24h
        curseur.execute("""
            SELECT id FROM alertes
            WHERE message = %s
              AND date_creation >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
        """, (alerte["message"],))

        if curseur.fetchone():
            return False  # Deja existante

        curseur.execute("""
            INSERT INTO alertes (message, niveau, mot_cle, lue)
            VALUES (%s, %s, %s, 0)
        """, (alerte["message"], alerte["niveau"], alerte.get("mot_cle", "")))

        conn.commit()
        return True
    except Error as e:
        print(f"Erreur insertion : {e}")
        return False
    finally:
        curseur.close()
        conn.close()


def lancer_detection_complete():
    """Lance toutes les detections et sauvegarde les nouvelles alertes."""
    print("Lancement de la detection d'anomalies...")
    print()

    toutes_alertes = []

    # 1. Pics de mentions
    print("1. Detection des pics de mentions...")
    pics = detecter_pics_mentions()
    toutes_alertes.extend(pics)
    print(f"   {len(pics)} alerte(s) detectee(s)")

    # 2. Sentiment negatif
    print("2. Detection du sentiment negatif...")
    sentiments = detecter_sentiment_negatif()
    toutes_alertes.extend(sentiments)
    print(f"   {len(sentiments)} alerte(s) detectee(s)")

    # 3. Baisse d'activite
    print("3. Detection des baisses d'activite...")
    baisses = detecter_baisse_activite()
    toutes_alertes.extend(baisses)
    print(f"   {len(baisses)} alerte(s) detectee(s)")

    # 4. Volume global
    print("4. Detection du volume global...")
    volumes = detecter_volume_global()
    toutes_alertes.extend(volumes)
    print(f"   {len(volumes)} alerte(s) detectee(s)")

    print()
    print(f"TOTAL : {len(toutes_alertes)} alerte(s) detectee(s)")

    # Sauvegarder
    print()
    print("Sauvegarde en base...")
    nb_sauvees = 0
    for alerte in toutes_alertes:
        if sauvegarder_alerte(alerte):
            nb_sauvees += 1

    print(f"   {nb_sauvees} nouvelle(s) alerte(s) sauvegardee(s)")

    return {
        "detectees": len(toutes_alertes),
        "sauvees": nb_sauvees,
        "alertes": toutes_alertes
    }


# ============================================================
# LECTURE DES ALERTES
# ============================================================

def lister_alertes(lues=None, niveau=None, limite=100):
    """Liste les alertes avec filtres optionnels."""
    conn = get_connexion()
    if conn is None:
        return []

    curseur = conn.cursor(dictionary=True)
    try:
        requete = "SELECT * FROM alertes WHERE 1=1"
        params = []

        if lues is not None:
            requete += " AND lue = %s"
            params.append(int(lues))

        if niveau:
            requete += " AND niveau = %s"
            params.append(niveau)

        requete += " ORDER BY date_creation DESC LIMIT %s"
        params.append(limite)

        curseur.execute(requete, params)
        return curseur.fetchall()
    finally:
        curseur.close()
        conn.close()


def marquer_lue(alerte_id, lue=True):
    """Marque une alerte comme lue ou non lue."""
    conn = get_connexion()
    if conn is None:
        return False

    curseur = conn.cursor()
    try:
        curseur.execute(
            "UPDATE alertes SET lue = %s WHERE id = %s",
            (int(lue), alerte_id)
        )
        conn.commit()
        return True
    except Error as e:
        print(f"Erreur : {e}")
        return False
    finally:
        curseur.close()
        conn.close()


def supprimer_alerte(alerte_id):
    """Supprime une alerte."""
    conn = get_connexion()
    if conn is None:
        return False

    curseur = conn.cursor()
    try:
        curseur.execute("DELETE FROM alertes WHERE id = %s", (alerte_id,))
        conn.commit()
        return True
    except Error:
        return False
    finally:
        curseur.close()
        conn.close()


def supprimer_toutes_alertes():
    """Supprime toutes les alertes."""
    conn = get_connexion()
    if conn is None:
        return False

    curseur = conn.cursor()
    try:
        curseur.execute("DELETE FROM alertes")
        conn.commit()
        return True
    except Error:
        return False
    finally:
        curseur.close()
        conn.close()


def stats_alertes():
    """Statistiques des alertes."""
    conn = get_connexion()
    if conn is None:
        return {}

    curseur = conn.cursor(dictionary=True)
    try:
        curseur.execute("""
            SELECT 
                COUNT(*) AS total,
                SUM(CASE WHEN lue = 0 THEN 1 ELSE 0 END) AS non_lues,
                SUM(CASE WHEN niveau = 'critique' THEN 1 ELSE 0 END) AS critiques,
                SUM(CASE WHEN niveau = 'attention' THEN 1 ELSE 0 END) AS attention
            FROM alertes
        """)
        return curseur.fetchone()
    finally:
        curseur.close()
        conn.close()


# ============================================================
# NOUVEAU : ARTICLES LIES A UNE ALERTE
# ============================================================

def get_articles_lies_alerte(alerte):
    """
    Retourne les articles lies a une alerte.
    Pour les alertes de sentiment : articles du theme avec sentiment negatif.
    Pour les autres : articles recents du theme.
    """
    conn = get_connexion()
    if conn is None:
        return []

    curseur = conn.cursor(dictionary=True)
    try:
        mot_cle = alerte.get("mot_cle", "")
        message = alerte.get("message", "").lower()

        # Cas 1 : Alerte sur le sentiment (chercher articles negatifs du theme)
        if "sentiment" in message:
            curseur.execute("""
                SELECT DISTINCT
                    a.id,
                    a.titre,
                    a.source,
                    a.url,
                    a.date_publication,
                    s.sentiment,
                    s.score AS score_sentiment,
                    at.score AS score_theme
                FROM articles a
                JOIN articles_themes at ON at.article_id = a.id
                JOIN articles_sentiment s ON s.article_id = a.id
                WHERE at.theme = %s
                  AND s.sentiment = 'negatif'
                ORDER BY s.score ASC
                LIMIT 20
            """, (mot_cle,))
            return curseur.fetchall()

        # Cas 2 : Alerte sur un pic de mentions
        if "pic" in message:
            curseur.execute("""
                SELECT DISTINCT
                    a.id,
                    a.titre,
                    a.source,
                    a.url,
                    a.date_publication,
                    at.score AS score_theme
                FROM articles a
                JOIN articles_themes at ON at.article_id = a.id
                WHERE at.theme = %s
                  AND a.date_ajout >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                ORDER BY a.date_ajout DESC
                LIMIT 20
            """, (mot_cle,))
            return curseur.fetchall()

        # Cas 3 : Baisse d'activite
        if "baisse" in message:
            curseur.execute("""
                SELECT DISTINCT
                    a.id,
                    a.titre,
                    a.source,
                    a.url,
                    a.date_publication,
                    at.score AS score_theme
                FROM articles a
                JOIN articles_themes at ON at.article_id = a.id
                WHERE at.theme = %s
                ORDER BY a.date_ajout DESC
                LIMIT 20
            """, (mot_cle,))
            return curseur.fetchall()

        # Cas 4 : Alerte globale - derniers articles
        if mot_cle == "global":
            curseur.execute("""
                SELECT id, titre, source, url, date_publication
                FROM articles
                ORDER BY date_ajout DESC
                LIMIT 20
            """)
            return curseur.fetchall()

        # Cas par defaut : articles du theme
        curseur.execute("""
            SELECT DISTINCT
                a.id,
                a.titre,
                a.source,
                a.url,
                a.date_publication,
                at.score AS score_theme
            FROM articles a
            JOIN articles_themes at ON at.article_id = a.id
            WHERE at.theme = %s
            ORDER BY a.date_ajout DESC
            LIMIT 20
        """, (mot_cle,))
        return curseur.fetchall()

    except Error as e:
        print(f"Erreur get_articles_lies_alerte : {e}")
        return []
    finally:
        curseur.close()
        conn.close()


# ============================================================
# TEST
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("TEST DU MODULE alert_detector.py")
    print("=" * 60)
    print()

    # Lancer la detection
    resultat = lancer_detection_complete()

    print()
    print("=" * 60)
    print("STATISTIQUES DES ALERTES")
    print("=" * 60)
    print()

    stats = stats_alertes()
    print(f"   Total alertes    : {stats.get('total', 0)}")
    print(f"   Non lues         : {stats.get('non_lues', 0)}")
    print(f"   Critiques        : {stats.get('critiques', 0)}")
    print(f"   Attention        : {stats.get('attention', 0)}")
    print()

    # Test de la nouvelle fonction
    print("=" * 60)
    print("TEST DE get_articles_lies_alerte")
    print("=" * 60)
    print()

    alertes = lister_alertes(limite=2)
    for alerte in alertes:
        print(f"Alerte : {alerte['message'][:70]}")
        articles = get_articles_lies_alerte(alerte)
        print(f"   -> {len(articles)} article(s) lie(s)")
        for art in articles[:3]:
            print(f"      - {art.get('titre', '')[:60]}...")
        print()

    print("=" * 60)
    print("TEST TERMINE")
    print("=" * 60)