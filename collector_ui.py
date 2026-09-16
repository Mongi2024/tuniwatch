"""
Module collector_ui.py - Fonctions d'interface pour la gestion des sources
Etape B - Session 2
"""

import mysql.connector
from mysql.connector import Error


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


# ============================================================
# LECTURE DES SOURCES
# ============================================================
def lister_sources(categorie=None, actives_seulement=False):
    """Liste toutes les sources (avec filtres optionnels)."""
    conn = get_connexion()
    if conn is None:
        return []

    curseur = conn.cursor(dictionary=True)
    try:
        requete = """
            SELECT id, nom, categorie, langue, url_site, url_rss, actif,
                   date_ajout
            FROM sources
            WHERE 1=1
        """
        params = []

        if categorie:
            requete += " AND categorie = %s"
            params.append(categorie)

        if actives_seulement:
            requete += " AND actif = 1"

        requete += " ORDER BY categorie, nom"

        curseur.execute(requete, params)
        return curseur.fetchall()
    finally:
        curseur.close()
        conn.close()


def stats_sources():
    """Statistiques : nombre de sources par categorie."""
    conn = get_connexion()
    if conn is None:
        return {}

    curseur = conn.cursor()
    try:
        curseur.execute("""
            SELECT categorie, COUNT(*) AS nb
            FROM sources
            GROUP BY categorie
            ORDER BY categorie
        """)
        return {cat: nb for cat, nb in curseur.fetchall()}
    finally:
        curseur.close()
        conn.close()


def compter_avec_rss():
    """Nombre de sources avec un flux RSS."""
    conn = get_connexion()
    if conn is None:
        return 0

    curseur = conn.cursor()
    try:
        curseur.execute("""
            SELECT COUNT(*) FROM sources
            WHERE actif = 1 AND url_rss IS NOT NULL AND url_rss != ''
        """)
        return curseur.fetchone()[0]
    finally:
        curseur.close()
        conn.close()


def stats_articles_par_source():
    """Nombre d'articles collectes par source."""
    conn = get_connexion()
    if conn is None:
        return []

    curseur = conn.cursor(dictionary=True)
    try:
        curseur.execute("""
            SELECT source, COUNT(*) AS nb_articles,
                   MAX(date_ajout) AS dernier_ajout
            FROM articles
            GROUP BY source
            ORDER BY nb_articles DESC
        """)
        return curseur.fetchall()
    finally:
        curseur.close()
        conn.close()


# ============================================================
# AJOUT / MODIFICATION
# ============================================================
def ajouter_source(nom, categorie, langue, url_site, url_rss):
    """Ajoute une nouvelle source. Retourne (succes, message)."""
    conn = get_connexion()
    if conn is None:
        return False, "MySQL non accessible"

    curseur = conn.cursor()
    try:
        curseur.execute("""
            INSERT INTO sources (nom, categorie, langue, url_site, url_rss, actif)
            VALUES (%s, %s, %s, %s, %s, 1)
        """, (nom, categorie, langue, url_site, url_rss))
        conn.commit()
        return True, f"Source '{nom}' ajoutee"
    except Error as e:
        return False, f"Erreur : {e}"
    finally:
        curseur.close()
        conn.close()


def modifier_source(source_id, url_rss=None, actif=None, url_site=None):
    """Modifie une source existante."""
    conn = get_connexion()
    if conn is None:
        return False, "MySQL non accessible"

    curseur = conn.cursor()
    try:
        champs = []
        params = []

        if url_rss is not None:
            champs.append("url_rss = %s")
            params.append(url_rss)

        if url_site is not None:
            champs.append("url_site = %s")
            params.append(url_site)

        if actif is not None:
            champs.append("actif = %s")
            params.append(int(actif))

        if not champs:
            return False, "Aucun champ a modifier"

        params.append(source_id)

        requete = f"UPDATE sources SET {', '.join(champs)} WHERE id = %s"
        curseur.execute(requete, params)
        conn.commit()
        return True, "Source mise a jour"
    except Error as e:
        return False, f"Erreur : {e}"
    finally:
        curseur.close()
        conn.close()


def supprimer_source(source_id, nom):
    """Supprime une source."""
    conn = get_connexion()
    if conn is None:
        return False, "MySQL non accessible"

    curseur = conn.cursor()
    try:
        curseur.execute("DELETE FROM sources WHERE id = %s", (source_id,))
        conn.commit()
        return True, f"Source '{nom}' supprimee"
    except Error as e:
        return False, f"Erreur : {e}"
    finally:
        curseur.close()
        conn.close()


def basculer_actif(source_id, actif_actuel):
    """Active ou desactive une source."""
    nouveau = 0 if actif_actuel else 1
    return modifier_source(source_id, actif=nouveau)


# ============================================================
# TEST
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("TEST DU MODULE collector_ui.py")
    print("=" * 60)
    print()

    # Stats par categorie
    print("1. Sources par categorie :")
    for cat, nb in sorted(stats_sources().items()):
        print(f"   - {cat:15} : {nb} sources")
    print()

    # Sources avec RSS
    print(f"2. Sources avec RSS : {compter_avec_rss()}")
    print()

    # Articles par source (top 10)
    print("3. Top 10 sources (par articles) :")
    stats = stats_articles_par_source()[:10]
    for s in stats:
        print(f"   - {s['source'][:30]:30} : {s['nb_articles']} articles")
    print()

    print("=" * 60)
    print("TEST TERMINE")
    print("=" * 60)