"""
Module politiques_stats.py - Analyse des personnalités politiques
Version 2.0 - Mentions par média + répartition H/F + variantes + langues
"""

from db_universal import get_connexion


# ============================================================
# VARIANTES DE NOMS
# ============================================================

def generer_variantes(nom_fr, nom_ar=None):
    """
    Génère toutes les variantes possibles d'un nom pour la recherche.
    Gère les accents français et les diacritiques arabes.
    """
    variantes = set()
    
    if nom_fr:
        variantes.add(nom_fr)
        # Variantes sans accents
        sans_accents = (nom_fr
            .replace('ï', 'i').replace('é', 'e').replace('è', 'e')
            .replace('ê', 'e').replace('à', 'a').replace('â', 'a')
            .replace('ô', 'o').replace('û', 'u').replace('ç', 'c')
        )
        variantes.add(sans_accents)
        # Variante avec/sans "e" final (Kaïs Saïed / Kaïs Saïd)
        if nom_fr.endswith('ed'):
            variantes.add(nom_fr[:-1])
        # Variante sans particule
        for particule in [' Ben ', ' El ', ' Al ', ' Caïd ']:
            if particule in nom_fr:
                variantes.add(nom_fr.replace(particule, ' '))
    
    if nom_ar:
        variantes.add(nom_ar)
        # Sans chadda
        variantes.add(nom_ar.replace('ّ', ''))
        # Sans alif hamza
        variantes.add(nom_ar.replace('أ', 'ا').replace('إ', 'ا'))
        # Sans ta marbouta finale
        if nom_ar.endswith('ة'):
            variantes.add(nom_ar[:-1])
    
    return [v for v in variantes if v and len(v) >= 3]


def _construire_clause_recherche(variantes, champs=('titre', 'description')):
    """
    Construit une clause SQL OR sur les variantes et les champs.
    Retourne (clause_sql, params).
    """
    conditions = []
    params = []
    for variante in variantes:
        for champ in champs:
            conditions.append(f"{champ} ILIKE %s")
            params.append(f"%{variante}%")
    return " OR ".join(conditions), params


# ============================================================
# FONCTIONS PRINCIPALES
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


def mentions_personnalite(nom_fr, nom_ar=None):
    """Compte les mentions d'une personnalité (avec variantes)."""
    conn = get_connexion()
    if conn is None:
        return 0
    curseur = conn.cursor()
    try:
        variantes = generer_variantes(nom_fr, nom_ar)
        clause, params = _construire_clause_recherche(variantes)
        curseur.execute(f"SELECT COUNT(*) FROM articles WHERE {clause}", params)
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
        variantes = generer_variantes(nom_fr, nom_ar)
        clause, params = _construire_clause_recherche(variantes)
        params.append(limite)
        curseur.execute(f"""
            SELECT source, COUNT(*) AS nb
            FROM articles
            WHERE {clause}
            GROUP BY source
            ORDER BY nb DESC
            LIMIT %s
        """, params)
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
    top = top_personnalites(1000)  # Tous

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
    """
    Compte les mentions H/F par média.
    Version optimisée : une seule requête par média (au lieu de N×M).
    """
    conn = get_connexion()
    if conn is None:
        return []
    curseur = conn.cursor(dictionary=True)
    try:
        # Récupérer toutes les personnalités
        curseur.execute("""
            SELECT nom_fr, nom_ar, genre
            FROM personnalites_politiques
            WHERE actif = 1
        """)
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
                variantes = generer_variantes(p["nom_fr"], p.get("nom_ar"))
                clause, params = _construire_clause_recherche(variantes)
                # Ajouter le filtre source
                params.insert(0, source)
                curseur.execute(f"""
                    SELECT COUNT(*) AS nb
                    FROM articles
                    WHERE source = %s AND ({clause})
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
    print("=" * 60)
    print("TEST DU MODULE politiques_stats.py v2.0")
    print("=" * 60)

    print("\n1. Liste des personnalités :")
    persos = liste_personnalites()
    print(f"   {len(persos)} personnalités")

    print("\n2. Top 10 personnalités :")
    top = top_personnalites(10)
    for i, p in enumerate(top, 1):
        emoji = "H" if p["genre"] == "homme" else "F"
        barre = "#" * min(p["mentions"], 30)
        print(f"   {i:2d}. [{emoji}] {p['nom_fr']:30s} {barre} {p['mentions']}")

    print("\n3. Répartition Hommes/Femmes :")
    rep = repartition_genre()
    print(f"   Hommes : {rep['hommes']:5d} mentions ({rep['pct_hommes']:.1f}%)")
    print(f"   Femmes : {rep['femmes']:5d} mentions ({rep['pct_femmes']:.1f}%)")
    print(f"   Total  : {rep['total']:5d} mentions")

    print("\n4. Mentions par média (top 5) :")
    par_media = mentions_par_genre_et_media(5)
    for m in par_media:
        print(f"   {m['source'][:40]:40s} : {m['hommes']:4d} H / {m['femmes']:4d} F")

    print("\n" + "=" * 60)
    print("Test terminé !")
    print("=" * 60)