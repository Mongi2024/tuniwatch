"""
Module collector_ui.py - Fonctions d'interface pour la gestion des sources
Etape B - Session 2 (avec db_universal)
"""

from db_universal import get_connexion


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
        rows = curseur.fetchall()
        return [
            {
                "id": int(r["id"]),
                "nom": r["nom"],
                "categorie": r["categorie"],
                "langue": r["langue"],
                "url_site": r["url_site"],
                "url_rss": r["url_rss"],
                "actif": int(r["actif"]) if r["actif"] is not None else 0,
                "date_ajout": str(r["date_ajout"]) if r["date_ajout"] else None
            }
            for r in rows
        ]
    finally:
        curseur.close()
        conn.close()


def stats_sources():
    """Statistiques : nombre de sources par categorie."""
    conn = get_connexion()
    if conn is None:
        return {}

    curseur = conn.cursor(dictionary=True)
    try:
        curseur.execute("""
            SELECT categorie, COUNT(*) AS nb
            FROM sources
            GROUP BY categorie
            ORDER BY categorie
        """)
        rows = curseur.fetchall()
        return {r["categorie"]: int(r["nb"]) for r in rows}
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
        result = curseur.fetchone()
        if isinstance(result, dict):
            return int(list(result.values())[0])
        elif isinstance(result, (list, tuple)):
            return int(result[0])
        return int(result)
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
        rows = curseur.fetchall()
        return [
            {
                "source": r["source"],
                "nb_articles": int(r["nb_articles"]),
                "dernier_ajout": str(r["dernier_ajout"]) if r["dernier_ajout"] else None
            }
            for r in rows
        ]
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
        return False, "Base non accessible"

    curseur = conn.cursor()
    try:
        curseur.execute("""
            INSERT INTO sources (nom, categorie, langue, url_site, url_rss, actif)
            VALUES (%s, %s, %s, %s, %s, 1)
        """, (nom, categorie, langue, url_site, url_rss))
        conn.commit()
        return True, f"Source '{nom}' ajoutee"
    except Exception as e:
        return False, f"Erreur : {e}"
    finally:
        curseur.close()
        conn.close()


def modifier_source(source_id, url_rss=None, actif=None, url_site=None):
    """Modifie une source existante."""
    conn = get_connexion()
    if conn is None:
        return False, "Base non accessible"

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
    except Exception as e:
        return False, f"Erreur : {e}"
    finally:
        curseur.close()
        conn.close()


def supprimer_source(source_id, nom):
    """Supprime une source."""
    conn = get_connexion()
    if conn is None:
        return False, "Base non accessible"

    curseur = conn.cursor()
    try:
        curseur.execute("DELETE FROM sources WHERE id = %s", (source_id,))
        conn.commit()
        return True, f"Source '{nom}' supprimee"
    except Exception as e:
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

    print("1. Sources par categorie :")
    for cat, nb in sorted(stats_sources().items()):
        print(f"   - {cat:15} : {nb} sources")
    print()

    print(f"2. Sources avec RSS : {compter_avec_rss()}")
    print()

    print("3. Top 5 sources (par articles) :")
    stats = stats_articles_par_source()[:5]
    for s in stats:
        print(f"   - {s['source'][:30]:30} : {s['nb_articles']} articles")
    print()

    print("=" * 60)
    print("TEST TERMINE")
    print("=" * 60)