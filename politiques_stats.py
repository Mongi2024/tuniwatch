"""
Module politiques_stats.py - Analyse des personnalités politiques
Version 2.0 - Avec variantes de noms + mentions par média
"""

from db_universal import get_connexion


# ============================================================
# FONCTIONS DE BASE
# ============================================================
def liste_personnalites():
    """Liste toutes les personnalités actives."""
    conn = get_connexion()
    if conn is None:
        return []
    curseur = conn.cursor(dictionary=True)
    try:
        curseur.execute("""
            SELECT id, nom_fr, nom_ar, genre, parti, fonction
            FROM personnalites_politiques
            WHERE actif = 1
            ORDER BY nom_fr
        """)
        return curseur.fetchall()
    finally:
        curseur.close()
        conn.close()


def _generer_variantes(nom_fr, nom_ar=None):
    """Génère des variantes d'orthographe pour un nom."""
    variantes = set()
    
    if nom_fr:
        variantes.add(nom_fr)
        # Sans tréma
        v = nom_fr.replace('ï', 'i').replace('é', 'e').replace('è', 'e')
        variantes.add(v)
        # Sans accent
        v2 = nom_fr.replace('é', 'e').replace('è', 'e').replace('ê', 'e')
        variantes.add(v2)
    
    if nom_ar:
        variantes.add(nom_ar)
        # Sans chadda
        if 'ّ' in nom_ar:
            variantes.add(nom_ar.replace('ّ', ''))
    
    return list(variantes)


def mentions_personnalite(nom_fr, nom_ar=None):
    """Compte les mentions d'une personnalité (avec variantes)."""
    conn = get_connexion()
    if conn is None:
        return 0
    curseur = conn.cursor()
    try:
        variantes = _generer_variantes(nom_fr, nom_ar)
        
        conditions = []
        params = []
        for v in variantes:
            conditions.append("titre ILIKE %s")
            conditions.append("description ILIKE %s")
            params.append(f"%{v}%")
            params.append(f"%{v}%")
        
        requete = f"SELECT COUNT(*) FROM articles WHERE {' OR '.join(conditions)}"
        curseur.execute(requete, params)
        result = curseur.fetchone()
        return int(result[0]) if result else 0
    finally:
        curseur.close()
        conn.close()


def mentions_par_media(nom_fr, nom_ar=None, limite=10):
    """Compte les mentions d'une personnalité par média."""
    conn = get_connexion()
    if conn is None:
        return []
    curseur = conn.cursor(dictionary=True)
    try:
        variantes = _generer_variantes(nom_fr, nom_ar)
        
        conditions = []
        params = []
        for v in variantes:
            conditions.append("(titre ILIKE %s OR description ILIKE %s)")
            params.append(f"%{v}%")
            params.append(f"%{v}%")
        
        requete = f"""
            SELECT source, COUNT(*) AS nb
            FROM articles
            WHERE {' OR '.join(conditions)}
            GROUP BY source
            ORDER BY nb DESC
            LIMIT %s
        """
        params.append(limite)
        curseur.execute(requete, params)
        return curseur.fetchall()
    finally:
        curseur.close()
        conn.close()


def top_personnalites(limite=10):
    """Retourne les personnalités les plus mentionnées."""
    personnalites = liste_personnalites()
    resultats = []

    for p in personnalites:
        nb = mentions_personnalite(p["nom_fr"], p.get("nom_ar"))
        if nb > 0:
            resultats.append({
                "nom_fr": p["nom_fr"],
                "nom_ar": p["nom_ar"],
                "genre": p["genre"],
                "parti": p["parti"],
                "fonction": p["fonction"],
                "mentions": nb,
            })

    resultats.sort(key=lambda x: x["mentions"], reverse=True)
    return resultats[:limite]


def repartition_genre():
    """Retourne la répartition Hommes/Femmes."""
    top = top_personnalites(100)

    total_h = sum(p["mentions"] for p in top if p["genre"] == "homme")
    total_f = sum(p["mentions"] for p in top if p["genre"] == "femme")
    total = total_h + total_f

    return {
        "hommes": total_h,
        "femmes": total_f,
        "total": total,
        "pct_hommes": (total_h / total * 100) if total > 0 else 0,
        "pct_femmes": (total_f / total * 100) if total > 0 else 0,
    }


def mentions_par_genre_et_media(limite_medias=10):
    """Compte les mentions H/F par média."""
    conn = get_connexion()
    if conn is None:
        return []
    curseur = conn.cursor(dictionary=True)
    try:
        # Récupérer toutes les personnalités
        curseur.execute(
            "SELECT nom_fr, nom_ar, genre FROM personnalites_politiques WHERE actif = 1"
        )
        personnalites = curseur.fetchall()

        # Récupérer les top médias
        curseur.execute("""
            SELECT source, COUNT(*) AS nb
            FROM articles
            WHERE source IS NOT NULL AND source != ''
            GROUP BY source
            ORDER BY nb DESC
            LIMIT %s
        """, (limite_medias,))
        medias = curseur.fetchall()

        resultats = []
        for media in medias:
            source = media["source"]
            nb_h = 0
            nb_f = 0

            for p in personnalites:
                # Générer les variantes
                variantes = _generer_variantes(p["nom_fr"], p.get("nom_ar"))
                
                conditions = ["source = %s"]
                params = [source]
                
                for v in variantes:
                    conditions.append("(titre ILIKE %s OR description ILIKE %s)")
                    params.append(f"%{v}%")
                    params.append(f"%{v}%")

                # Exécuter UNE SEULE FOIS
                curseur.execute(f"""
                    SELECT COUNT(*) AS nb FROM articles
                    WHERE {' AND '.join(conditions)}
                """, params)
                row = curseur.fetchone()
                nb = int(row["nb"]) if row and row.get("nb") else 0

                if p["genre"] == "homme":
                    nb_h += nb
                else:
                    nb_f += nb

            resultats.append({
                "source": source,
                "hommes": nb_h,
                "femmes": nb_f,
                "total": nb_h + nb_f,
            })

        return resultats
    finally:
        curseur.close()
        conn.close()


# ============================================================
# TEST
# ============================================================
if __name__ == "__main__":
    print("Test du module politiques_stats.py")
    print()

    print("1. Liste des personnalités :")
    persos = liste_personnalites()
    print(f"   {len(persos)} personnalités")
    print()

    print("2. Top 10 personnalités :")
    top = top_personnalites(10)
    if top:
        for i, p in enumerate(top, 1):
            emoji = "H" if p["genre"] == "homme" else "F"
            print(f"   {i}. [{emoji}] {p['nom_fr']} : {p['mentions']} mentions")
    else:
        print("   Aucune mention trouvée")
    print()

    print("3. Répartition Hommes/Femmes :")
    rep = repartition_genre()
    print(f"   Hommes : {rep['hommes']} mentions ({rep['pct_hommes']:.1f}%)")
    print(f"   Femmes : {rep['femmes']} mentions ({rep['pct_femmes']:.1f}%)")
    print(f"   Total  : {rep['total']} mentions")
    print()

    print("4. Mentions par média (top 5) :")
    par_media = mentions_par_genre_et_media(5)
    if par_media:
        for m in par_media:
            print(f"   {m['source'][:40]} : {m['hommes']} H / {m['femmes']} F")
    else:
        print("   Aucune donnée")
    print()
    print("Test terminé !")