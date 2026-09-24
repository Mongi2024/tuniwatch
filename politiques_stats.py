"""
Module politiques_stats.py - Analyse des personnalites politiques
Version 3.0 - Variantes arabes + Pourcentages + Langues
"""

from db_universal import get_connexion


# ============================================================
# VARIANTES DE NOMS
# ============================================================

def generer_variantes(nom_fr, nom_ar=None):
    """Genere toutes les variantes possibles d'un nom."""
    variantes = set()

    if nom_fr:
        variantes.add(nom_fr)
        # Sans accents
        sans_accents = (nom_fr
            .replace('ï', 'i').replace('é', 'e').replace('è', 'e')
            .replace('ê', 'e').replace('à', 'a').replace('â', 'a')
            .replace('ô', 'o').replace('û', 'u').replace('ç', 'c')
            .replace('î', 'i').replace('ô', 'o')
        )
        variantes.add(sans_accents)
        # Sans "ed" final
        if nom_fr.endswith('ed'):
            variantes.add(nom_fr[:-1])
        # Sans particule
        for particule in [' Ben ', ' El ', ' Al ', ' Caid ', ' Caïd ']:
            if particule in nom_fr:
                variantes.add(nom_fr.replace(particule, ' '))
        # Nom de famille seul (dernier mot)
        mots = nom_fr.split()
        if len(mots) >= 2 and len(mots[-1]) >= 4:
            variantes.add(mots[-1])

    if nom_ar:
        variantes.add(nom_ar)
        # Sans chadda
        variantes.add(nom_ar.replace('ّ', ''))
        # Sans alif hamza
        variantes.add(nom_ar.replace('أ', 'ا').replace('إ', 'ا'))
        # Sans ta marbouta
        if nom_ar.endswith('ة'):
            variantes.add(nom_ar[:-1])
        # Dernier mot arabe seul (nom de famille)
        mots_ar = nom_ar.split()
        if len(mots_ar) >= 2 and len(mots_ar[-1]) >= 3:
            variantes.add(mots_ar[-1])

    return [v for v in variantes if v and len(v) >= 3]


def _construire_clause_recherche(variantes, champs=('titre', 'description')):
    """Construit une clause SQL OR sur les variantes et les champs."""
    conditions = []
    params = []
    for variante in variantes:
        for champ in champs:
            conditions.append(champ + " ILIKE %s")
            params.append("%" + variante + "%")
    return " OR ".join(conditions), params


def _detecter_langue(texte):
    """Retourne 'ar' si le texte contient de l'arabe, sinon 'fr'."""
    if not texte:
        return 'fr'
    for c in texte:
        if '\u0600' <= c <= '\u06FF':
            return 'ar'
    return 'fr'


# ============================================================
# FONCTIONS PRINCIPALES
# ============================================================

def liste_personnalites():
    """Liste toutes les personnalites actives."""
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
    """Compte les mentions d'une personnalite (avec variantes)."""
    conn = get_connexion()
    if conn is None:
        return 0
    curseur = conn.cursor()
    try:
        variantes = generer_variantes(nom_fr, nom_ar)
        clause, params = _construire_clause_recherche(variantes)
        curseur.execute("SELECT COUNT(*) FROM articles WHERE " + clause, params)
        result = curseur.fetchone()
        return int(result[0]) if result else 0
    finally:
        curseur.close()
        conn.close()


def mentions_par_langue(nom_fr, nom_ar=None):
    """Compte les mentions par langue (FR / AR)."""
    conn = get_connexion()
    if conn is None:
        return {"fr": 0, "ar": 0}
    curseur = conn.cursor(dictionary=True)
    try:
        variantes = generer_variantes(nom_fr, nom_ar)
        clause, params = _construire_clause_recherche(variantes)
        curseur.execute("""
            SELECT titre, description FROM articles WHERE """ + clause, params)
        rows = curseur.fetchall()
        fr = 0
        ar = 0
        for r in rows:
            texte = (r.get("titre") or "") + " " + (r.get("description") or "")
            if _detecter_langue(texte) == "ar":
                ar += 1
            else:
                fr += 1
        return {"fr": fr, "ar": ar, "total": fr + ar}
    finally:
        curseur.close()
        conn.close()


def mentions_par_media(nom_fr, nom_ar=None, limite=10):
    """Compte les mentions d'une personnalite par media."""
    conn = get_connexion()
    if conn is None:
        return []
    curseur = conn.cursor(dictionary=True)
    try:
        variantes = generer_variantes(nom_fr, nom_ar)
        clause, params = _construire_clause_recherche(variantes)
        params.append(limite)
        curseur.execute("""
            SELECT source, COUNT(*) AS nb
            FROM articles
            WHERE """ + clause + """
            GROUP BY source
            ORDER BY nb DESC
            LIMIT %s
        """, params)
        return curseur.fetchall()
    finally:
        curseur.close()
        conn.close()


def top_personnalites(limite=10):
    """Retourne les personnalites les plus mentionnees avec pourcentages."""
    personnalites = liste_personnalites()
    resultats = []

    for p in personnalites:
        nb = mentions_personnalite(p["nom_fr"], p.get("nom_ar"))
        if nb > 0:
            langues = mentions_par_langue(p["nom_fr"], p.get("nom_ar"))
            resultats.append({
                "nom_fr": p["nom_fr"],
                "nom_ar": p["nom_ar"],
                "genre": p["genre"],
                "parti": p["parti"],
                "fonction": p["fonction"],
                "mentions": nb,
                "mentions_fr": langues.get("fr", 0),
                "mentions_ar": langues.get("ar", 0),
            })

    resultats.sort(key=lambda x: x["mentions"], reverse=True)

    # Calculer les pourcentages
    total = sum(r["mentions"] for r in resultats)
    for r in resultats:
        r["pourcentage"] = (r["mentions"] / total * 100) if total > 0 else 0

    return resultats[:limite], total


def repartition_genre():
    """Retourne la repartition Hommes/Femmes avec pourcentages."""
    top, total = top_personnalites(1000)

    total_h = sum(p["mentions"] for p in top if p["genre"] == "homme")
    total_f = sum(p["mentions"] for p in top if p["genre"] == "femme")
    total_gen = total_h + total_f

    return {
        "hommes": total_h,
        "femmes": total_f,
        "total": total_gen,
        "pct_hommes": round(total_h / total_gen * 100, 1) if total_gen > 0 else 0,
        "pct_femmes": round(total_f / total_gen * 100, 1) if total_gen > 0 else 0,
        "nb_hommes": sum(1 for p in top if p["genre"] == "homme"),
        "nb_femmes": sum(1 for p in top if p["genre"] == "femme"),
    }


def mentions_par_genre_et_media(limite_medias=10):
    """Compte les mentions H/F par media avec pourcentages."""
    conn = get_connexion()
    if conn is None:
        return []
    curseur = conn.cursor(dictionary=True)
    try:
        curseur.execute("""
            SELECT nom_fr, nom_ar, genre
            FROM personnalites_politiques
            WHERE actif = 1
        """)
        personnalites = curseur.fetchall()

        curseur.execute("""
            SELECT source, COUNT(*) AS nb
            FROM articles
            WHERE source IS NOT NULL AND source != '' AND source != 'Source inconnue'
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
                params.insert(0, source)
                curseur.execute("""
                    SELECT COUNT(*) AS nb
                    FROM articles
                    WHERE source = %s AND (""" + clause + """)
                """, params)
                row = curseur.fetchone()
                nb = int(row["nb"]) if row and row.get("nb") else 0

                if p["genre"] == "homme":
                    nb_h += nb
                else:
                    nb_f += nb

            total = nb_h + nb_f
            resultats.append({
                "source": source,
                "hommes": nb_h,
                "femmes": nb_f,
                "total": total,
                "pct_hommes": round(nb_h / total * 100, 1) if total > 0 else 0,
                "pct_femmes": round(nb_f / total * 100, 1) if total > 0 else 0,
            })

        return resultats
    finally:
        curseur.close()
        conn.close()


# ============================================================
# TEST
# ============================================================
if __name__ == "__main__":
    print("=" * 70)
    print("TEST politiques_stats.py v3.0")
    print("=" * 70)

    print("\n1. Liste des personnalites :")
    persos = liste_personnalites()
    print("   " + str(len(persos)) + " personnalites")

    print("\n2. Top 10 personnalites (avec % et langues) :")
    top, total = top_personnalites(10)
    print("   Total mentions : " + str(total))
    print()
    for i, p in enumerate(top, 1):
        emoji = "H" if p["genre"] == "homme" else "F"
        barre = "#" * min(int(p["pourcentage"]), 30)
        print("   {:2d}. [{}] {:30s} {:3d} ({:.1f}%) FR:{} AR:{}".format(
            i, emoji, p["nom_fr"][:30], p["mentions"], p["pourcentage"],
            p["mentions_fr"], p["mentions_ar"]))
        print("       {}".format(barre))

    print("\n3. Repartition Hommes/Femmes :")
    rep = repartition_genre()
    print("   Hommes : {:3d} mentions ({:.1f}%) - {} personnalites".format(
        rep["hommes"], rep["pct_hommes"], rep["nb_hommes"]))
    print("   Femmes : {:3d} mentions ({:.1f}%) - {} personnalites".format(
        rep["femmes"], rep["pct_femmes"], rep["nb_femmes"]))
    print("   Total  : {:3d} mentions".format(rep["total"]))

    print("\n4. Mentions par media (top 5) :")
    par_media = mentions_par_genre_et_media(5)
    for m in par_media:
        print("   {:40s} : {:3d} H ({:.0f}%) / {:3d} F ({:.0f}%)".format(
            m["source"][:40], m["hommes"], m["pct_hommes"],
            m["femmes"], m["pct_femmes"]))

    print("\n" + "=" * 70)
    print("Test termine !")
    print("=" * 70)