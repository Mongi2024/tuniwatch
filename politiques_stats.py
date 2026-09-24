"""
Module politiques_stats.py - Analyse des personnalites politiques
Version 5.0 - Recherche stricte + Periodes + Partis + Comparaisons + Export
"""

from datetime import datetime, timedelta
from db_universal import get_connexion


# ============================================================
# VARIANTES DE NOMS
# ============================================================

def generer_variantes(nom_fr, nom_ar=None, stricte=False):
    """
    Genere les variantes d'un nom.
    - stricte=False : variantes souples (nom seul autorise)
    - stricte=True  : nom complet obligatoire
    """
    variantes = set()

    if nom_fr:
        variantes.add(nom_fr)
        # Sans accents
        sans_accents = (nom_fr
            .replace('ï', 'i').replace('é', 'e').replace('è', 'e')
            .replace('ê', 'e').replace('à', 'a').replace('â', 'a')
            .replace('ô', 'o').replace('û', 'u').replace('ç', 'c')
            .replace('î', 'i')
        )
        if sans_accents != nom_fr:
            variantes.add(sans_accents)

        # Variantes souples uniquement si NON stricte
        if not stricte:
            if nom_fr.endswith('ed'):
                variantes.add(nom_fr[:-1])
            for particule in [' Ben ', ' El ', ' Al ', ' Caid ', ' Caïd ']:
                if particule in nom_fr:
                    variantes.add(nom_fr.replace(particule, ' '))
            mots = nom_fr.split()
            if len(mots) >= 2 and len(mots[-1]) >= 4:
                variantes.add(mots[-1])

    if nom_ar:
        variantes.add(nom_ar)
        # Sans chadda
        v_sans_chadda = nom_ar.replace('ّ', '')
        if v_sans_chadda != nom_ar:
            variantes.add(v_sans_chadda)
        # Sans alif hamza
        v_sans_hamza = nom_ar.replace('أ', 'ا').replace('إ', 'ا')
        if v_sans_hamza != nom_ar:
            variantes.add(v_sans_hamza)
        # Sans "ال" (article défini)
        if nom_ar.startswith('ال'):
            variantes.add(nom_ar[2:])
        # Remplacement de "ال" par rien dans chaque mot
        mots_ar = nom_ar.split()
        if len(mots_ar) >= 2:
            sans_al = ' '.join(m[2:] if m.startswith('ال') and len(m) > 3 else m
                               for m in mots_ar)
            if sans_al != nom_ar:
                variantes.add(sans_al)

        if not stricte:
            if nom_ar.endswith('ة'):
                variantes.add(nom_ar[:-1])
            if len(mots_ar) >= 2 and len(mots_ar[-1]) >= 3:
                variantes.add(mots_ar[-1])

    return [v for v in variantes if v and len(v) >= 3]


def _construire_clause_recherche(variantes, champs=('titre', 'description')):
    """Construit une clause SQL OR sur les variantes."""
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
# LISTE PERSONNALITES
# ============================================================

def liste_personnalites():
    """Liste toutes les personnalites actives."""
    conn = get_connexion()
    if conn is None:
        return []
    curseur = conn.cursor(dictionary=True)
    try:
        curseur.execute("""
            SELECT id, nom_fr, nom_ar, genre, parti, fonction, recherche_stricte
            FROM personnalites_politiques
            WHERE actif = 1
            ORDER BY nom_fr
        """)
        return curseur.fetchall()
    finally:
        curseur.close()
        conn.close()


# ============================================================
# MENTIONS PAR PERSONNALITE
# ============================================================

def mentions_personnalite(nom_fr, nom_ar=None, stricte=False,
                          jours=None):
    """
    Compte les mentions d'une personnalite.
    - jours=None : toutes les dates
    - jours=7    : 7 derniers jours
    """
    conn = get_connexion()
    if conn is None:
        return 0
    curseur = conn.cursor()
    try:
        variantes = generer_variantes(nom_fr, nom_ar, stricte)
        clause, params = _construire_clause_recherche(variantes)

        if jours:
            date_limite = datetime.now() - timedelta(days=jours)
            clause = "(" + clause + ") AND date_publication >= %s"
            params.append(date_limite)

        curseur.execute("SELECT COUNT(*) FROM articles WHERE " + clause, params)
        result = curseur.fetchone()
        return int(result[0]) if result else 0
    finally:
        curseur.close()
        conn.close()


def mentions_par_langue(nom_fr, nom_ar=None, stricte=False, jours=None):
    """Compte les mentions par langue (FR / AR)."""
    conn = get_connexion()
    if conn is None:
        return {"fr": 0, "ar": 0, "total": 0}
    curseur = conn.cursor(dictionary=True)
    try:
        variantes = generer_variantes(nom_fr, nom_ar, stricte)
        clause, params = _construire_clause_recherche(variantes)

        if jours:
            date_limite = datetime.now() - timedelta(days=jours)
            clause = "(" + clause + ") AND date_publication >= %s"
            params.append(date_limite)

        curseur.execute("SELECT titre, description FROM articles WHERE " + clause, params)
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


def articles_personnalite(nom_fr, nom_ar=None, stricte=False,
                          limite=20, jours=None):
    """Retourne les articles mentionnant une personnalite."""
    conn = get_connexion()
    if conn is None:
        return []
    curseur = conn.cursor(dictionary=True)
    try:
        variantes = generer_variantes(nom_fr, nom_ar, stricte)
        clause, params = _construire_clause_recherche(variantes)

        if jours:
            date_limite = datetime.now() - timedelta(days=jours)
            clause = "(" + clause + ") AND date_publication >= %s"
            params.append(date_limite)

        params.append(limite)
        curseur.execute("""
            SELECT id, titre, source, date_publication, url
            FROM articles
            WHERE """ + clause + """
            ORDER BY date_publication DESC NULLS LAST
            LIMIT %s
        """, params)
        return curseur.fetchall()
    finally:
        curseur.close()
        conn.close()


# ============================================================
# TOP PERSONNALITES
# ============================================================

def top_personnalites(limite=10, jours=None):
    """
    Retourne les personnalites les plus mentionnees.
    - jours=None : toutes les dates
    - jours=7    : 7 derniers jours
    """
    personnalites = liste_personnalites()
    resultats = []

    for p in personnalites:
        stricte = bool(p.get("recherche_stricte", 0))
        nb = mentions_personnalite(p["nom_fr"], p.get("nom_ar"), stricte, jours)
        if nb > 0:
            langues = mentions_par_langue(p["nom_fr"], p.get("nom_ar"),
                                          stricte, jours)
            resultats.append({
                "nom_fr": p["nom_fr"],
                "nom_ar": p["nom_ar"],
                "genre": p["genre"],
                "parti": p["parti"],
                "fonction": p["fonction"],
                "mentions": nb,
                "mentions_fr": langues.get("fr", 0),
                "mentions_ar": langues.get("ar", 0),
                "recherche_stricte": stricte,
            })

    resultats.sort(key=lambda x: x["mentions"], reverse=True)

    total = sum(r["mentions"] for r in resultats)
    for r in resultats:
        r["pourcentage"] = round((r["mentions"] / total * 100), 1) if total > 0 else 0

    return resultats[:limite], total


def repartition_genre(jours=None):
    """Retourne la repartition Hommes/Femmes avec pourcentages."""
    top, total = top_personnalites(1000, jours)

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


# ============================================================
# REPARTITION PAR MEDIA
# ============================================================

def mentions_par_genre_et_media(limite_medias=10, jours=None):
    """Compte les mentions H/F par media avec pourcentages."""
    conn = get_connexion()
    if conn is None:
        return []
    curseur = conn.cursor(dictionary=True)
    try:
        curseur.execute("""
            SELECT nom_fr, nom_ar, genre, recherche_stricte
            FROM personnalites_politiques
            WHERE actif = 1
        """)
        personnalites = curseur.fetchall()

        # Construire le filtre date
        filtre_date = ""
        params_date = []
        if jours:
            date_limite = datetime.now() - timedelta(days=jours)
            filtre_date = " AND date_publication >= %s"
            params_date = [date_limite]

        curseur.execute("""
            SELECT source, COUNT(*) AS nb
            FROM articles
            WHERE source IS NOT NULL AND source != '' AND source != 'Source inconnue'
            """ + filtre_date + """
            GROUP BY source
            ORDER BY nb DESC
            LIMIT %s
        """, params_date + [limite_medias])
        medias = curseur.fetchall()

        resultats = []
        for media in medias:
            source = media["source"]
            nb_h = 0
            nb_f = 0

            for p in personnalites:
                stricte = bool(p.get("recherche_stricte", 0))
                variantes = generer_variantes(p["nom_fr"], p.get("nom_ar"), stricte)
                clause, params = _construire_clause_recherche(variantes)
                params.insert(0, source)

                req = """
                    SELECT COUNT(*) AS nb
                    FROM articles
                    WHERE source = %s AND (""" + clause + """)""" + filtre_date

                if jours:
                    params.append(datetime.now() - timedelta(days=jours))

                curseur.execute(req, params)
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
# REPARTITION PAR PARTI
# ============================================================

def mentions_par_parti(jours=None):
    """Regroupe les mentions par parti politique."""
    top, total = top_personnalites(1000, jours)
    partis = {}

    for p in top:
        parti = p.get("parti") or "Indépendant"
        if parti not in partis:
            partis[parti] = {
                "parti": parti,
                "hommes": 0,
                "femmes": 0,
                "total": 0,
                "nb_personnalites": 0,
            }
        if p["genre"] == "homme":
            partis[parti]["hommes"] += p["mentions"]
        else:
            partis[parti]["femmes"] += p["mentions"]
        partis[parti]["total"] += p["mentions"]
        partis[parti]["nb_personnalites"] += 1

    resultats = list(partis.values())
    resultats.sort(key=lambda x: x["total"], reverse=True)

    for r in resultats:
        r["pourcentage"] = round(r["total"] / total * 100, 1) if total > 0 else 0

    return resultats


# ============================================================
# COMPARAISON ENTRE PERSONNALITES
# ============================================================

def comparer_personnalites(noms_fr, jours=None):
    """
    Compare plusieurs personnalites.
    noms_fr : liste de noms (ex: ['Kaïs Saïed', 'Abir Moussi'])
    """
    conn = get_connexion()
    if conn is None:
        return []
    curseur = conn.cursor(dictionary=True)
    try:
        resultats = []
        for nom in noms_fr:
            curseur.execute("""
                SELECT nom_fr, nom_ar, genre, parti, fonction, recherche_stricte
                FROM personnalites_politiques
                WHERE nom_fr = %s AND actif = 1
            """, (nom,))
            p = curseur.fetchone()
            if not p:
                continue

            stricte = bool(p.get("recherche_stricte", 0))
            nb = mentions_personnalite(p["nom_fr"], p.get("nom_ar"), stricte, jours)
            langues = mentions_par_langue(p["nom_fr"], p.get("nom_ar"),
                                          stricte, jours)

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

        total = sum(r["mentions"] for r in resultats)
        for r in resultats:
            r["pourcentage"] = round(r["mentions"] / total * 100, 1) if total > 0 else 0

        resultats.sort(key=lambda x: x["mentions"], reverse=True)
        return resultats
    finally:
        curseur.close()
        conn.close()


# ============================================================
# EVOLUTION TEMPORELLE
# ============================================================

def evolution_personnalite(nom_fr, nom_ar=None, stricte=False, jours=30):
    """
    Retourne l'evolution jour par jour des mentions.
    Retourne une liste de dict {date, mentions}.
    """
    conn = get_connexion()
    if conn is None:
        return []
    curseur = conn.cursor(dictionary=True)
    try:
        variantes = generer_variantes(nom_fr, nom_ar, stricte)
        clause, params = _construire_clause_recherche(variantes)
        date_limite = datetime.now() - timedelta(days=jours)
        params.append(date_limite)

        curseur.execute("""
            SELECT DATE(date_publication) AS jour, COUNT(*) AS nb
            FROM articles
            WHERE (""" + clause + """) AND date_publication >= %s
            GROUP BY DATE(date_publication)
            ORDER BY jour
        """, params)
        return curseur.fetchall()
    finally:
        curseur.close()
        conn.close()


# ============================================================
# STATISTIQUES GLOBALES
# ============================================================

def stats_globales():
    """Retourne les statistiques globales du systeme."""
    conn = get_connexion()
    if conn is None:
        return {}
    curseur = conn.cursor(dictionary=True)
    try:
        curseur.execute("SELECT COUNT(*) AS nb FROM articles")
        total_articles = curseur.fetchone()["nb"]

        curseur.execute("SELECT COUNT(*) AS nb FROM personnalites_politiques WHERE actif = 1")
        total_persos = curseur.fetchone()["nb"]

        curseur.execute("SELECT COUNT(*) AS nb FROM personnalites_politiques WHERE recherche_stricte = 1")
        total_strict = curseur.fetchone()["nb"]

        return {
            "total_articles": total_articles,
            "total_personnalites": total_persos,
            "total_strict": total_strict,
        }
    finally:
        curseur.close()
        conn.close()


# ============================================================
# TEST
# ============================================================
if __name__ == "__main__":
    print("=" * 70)
    print("TEST politiques_stats.py v5.0")
    print("=" * 70)

    stats = stats_globales()
    print("\n0. Stats globales :")
    print("   Articles en base : " + str(stats.get("total_articles", 0)))
    print("   Personnalites : " + str(stats.get("total_personnalites", 0)))
    print("   En strict : " + str(stats.get("total_strict", 0)))

    print("\n1. Top 10 personnalites (toutes periodes) :")
    top, total = top_personnalites(10)
    print("   Total mentions : " + str(total))
    print()
    for i, p in enumerate(top, 1):
        emoji = "H" if p["genre"] == "homme" else "F"
        strict = " [STRICT]" if p.get("recherche_stricte") else ""
        barre = "#" * min(int(p["pourcentage"]), 30)
        print("   {:2d}. [{}] {:30s} {:3d} ({:.1f}%) FR:{} AR:{}{}".format(
            i, emoji, p["nom_fr"][:30], p["mentions"], p["pourcentage"],
            p["mentions_fr"], p["mentions_ar"], strict))
        print("       {}".format(barre))

    print("\n2. Top 5 sur 7 derniers jours :")
    top7, total7 = top_personnalites(5, jours=7)
    if not top7:
        print("   Aucune mention sur 7 jours.")
    else:
        for i, p in enumerate(top7, 1):
            emoji = "H" if p["genre"] == "homme" else "F"
            print("   {:2d}. [{}] {:30s} {:3d} mentions".format(
                i, emoji, p["nom_fr"][:30], p["mentions"]))

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

    print("\n5. Repartition par parti :")
    par_parti = mentions_par_parti()
    for r in par_parti[:5]:
        print("   {:30s} : {:3d} mentions ({:.1f}%) - {} persos".format(
            r["parti"][:30], r["total"], r["pourcentage"], r["nb_personnalites"]))

    print("\n6. Comparaison Kaïs Saïed vs Abir Moussi :")
    comp = comparer_personnalites(["Kaïs Saïed", "Abir Moussi"])
    for c in comp:
        print("   {} : {} mentions ({}%)".format(
            c["nom_fr"], c["mentions"], c["pourcentage"]))

    print("\n" + "=" * 70)
    print("Test termine !")
    print("=" * 70)