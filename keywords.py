"""
Module keywords.py - Gestion des mots-cles de l'observatoire
Etape F - Session 1 (avec db_universal)
"""

from db_universal import get_connexion


# ============================================================
# LECTURE
# ============================================================
def charger_mots(theme=None, langue=None, actifs_seulement=True):
    """
    Charge les mots-cles selon les filtres.

    Args:
        theme : filtrer par theme (ex: 'violence_femmes')
        langue : filtrer par langue ('fr', 'ar', 'ar_tn', 'arabizi')
        actifs_seulement : ne prendre que les mots actifs

    Returns:
        Liste de dictionnaires {"id", "theme", "langue", "mot", "poids"}
    """
    conn = get_connexion()
    if conn is None:
        return []

    curseur = conn.cursor(dictionary=True)
    try:
        requete = "SELECT id, theme, langue, mot, poids FROM mots_cles WHERE 1=1"
        params = []

        if theme:
            requete += " AND theme = %s"
            params.append(theme)

        if langue:
            requete += " AND langue = %s"
            params.append(langue)

        if actifs_seulement:
            requete += " AND actif = 1"

        requete += " ORDER BY poids DESC, mot"

        curseur.execute(requete, params)
        rows = curseur.fetchall()
        return [
            {
                "id": int(r["id"]),
                "theme": r["theme"],
                "langue": r["langue"],
                "mot": r["mot"],
                "poids": float(r["poids"])
            }
            for r in rows
        ]
    except Exception as e:
        print(f"Erreur lecture : {e}")
        return []
    finally:
        curseur.close()
        conn.close()


def charger_mots_par_theme(theme):
    """
    Charge tous les mots d'un theme, groupes par langue.

    Returns:
        dict {"fr": [...], "ar": [...], "ar_tn": [...], "arabizi": [...]}
    """
    mots = charger_mots(theme=theme)
    groupes = {"fr": [], "ar": [], "ar_tn": [], "arabizi": []}

    for m in mots:
        if m["langue"] in groupes:
            groupes[m["langue"]].append(m["mot"])

    return groupes


def lister_themes():
    """Retourne la liste des themes existants."""
    conn = get_connexion()
    if conn is None:
        return []

    curseur = conn.cursor(dictionary=True)
    try:
        curseur.execute("""
            SELECT theme, COUNT(*) AS nb_mots
            FROM mots_cles
            WHERE actif = 1
            GROUP BY theme
            ORDER BY theme
        """)
        rows = curseur.fetchall()
        return [
            {"theme": r["theme"], "nb_mots": int(r["nb_mots"])}
            for r in rows
        ]
    except Exception as e:
        print(f"Erreur : {e}")
        return []
    finally:
        curseur.close()
        conn.close()


def stats_par_langue(theme):
    """Retourne le nombre de mots par langue pour un theme."""
    conn = get_connexion()
    if conn is None:
        return {}

    curseur = conn.cursor(dictionary=True)
    try:
        curseur.execute("""
            SELECT langue, COUNT(*) AS nb
            FROM mots_cles
            WHERE theme = %s AND actif = 1
            GROUP BY langue
        """, (theme,))
        rows = curseur.fetchall()
        return {r["langue"]: int(r["nb"]) for r in rows}
    except Exception:
        return {}
    finally:
        curseur.close()
        conn.close()


def compter_total():
    """Retourne le nombre total de mots actifs."""
    conn = get_connexion()
    if conn is None:
        return 0

    curseur = conn.cursor()
    try:
        curseur.execute("SELECT COUNT(*) FROM mots_cles WHERE actif = 1")
        result = curseur.fetchone()
        if isinstance(result, dict):
            return int(list(result.values())[0])
        elif isinstance(result, (list, tuple)):
            return int(result[0])
        return int(result)
    except Exception:
        return 0
    finally:
        curseur.close()
        conn.close()


# ============================================================
# AJOUT / MODIFICATION
# ============================================================
def ajouter_mot(theme, langue, mot, poids=1.0):
    """
    Ajoute un mot-cle. Retourne (succes, message).
    Si le mot existe deja, il est reactive et son poids mis a jour.
    """
    conn = get_connexion()
    if conn is None:
        return False, "Base non accessible"

    curseur = conn.cursor()
    try:
        # Verifier si le mot existe deja
        curseur.execute(
            "SELECT id FROM mots_cles WHERE theme = %s AND mot = %s",
            (theme, mot)
        )
        existe = curseur.fetchone()

        if existe:
            # Mettre a jour
            curseur.execute(
                "UPDATE mots_cles SET poids = %s, actif = 1 WHERE theme = %s AND mot = %s",
                (poids, theme, mot)
            )
            conn.commit()
            return True, f"Mot '{mot}' mis a jour"
        else:
            # Inserer
            curseur.execute("""
                INSERT INTO mots_cles (theme, langue, mot, poids, actif)
                VALUES (%s, %s, %s, %s, 1)
            """, (theme, langue, mot, poids))
            conn.commit()
            return True, f"Mot '{mot}' ajoute au theme '{theme}'"
    except Exception as e:
        return False, f"Erreur : {e}"
    finally:
        curseur.close()
        conn.close()


def modifier_poids(mot_id, nouveau_poids):
    """Modifie le poids d'un mot."""
    conn = get_connexion()
    if conn is None:
        return False, "Base non accessible"

    curseur = conn.cursor()
    try:
        curseur.execute(
            "UPDATE mots_cles SET poids = %s WHERE id = %s",
            (nouveau_poids, mot_id)
        )
        conn.commit()
        return True, "Poids modifie"
    except Exception as e:
        return False, f"Erreur : {e}"
    finally:
        curseur.close()
        conn.close()


def desactiver_mot(mot_id):
    """Desactive un mot (le rend inactif sans le supprimer)."""
    conn = get_connexion()
    if conn is None:
        return False, "Base non accessible"

    curseur = conn.cursor()
    try:
        curseur.execute(
            "UPDATE mots_cles SET actif = 0 WHERE id = %s",
            (mot_id,)
        )
        conn.commit()
        return True, "Mot desactive"
    except Exception as e:
        return False, f"Erreur : {e}"
    finally:
        curseur.close()
        conn.close()


def reactiver_mot(mot_id):
    """Reactive un mot."""
    conn = get_connexion()
    if conn is None:
        return False, "Base non accessible"

    curseur = conn.cursor()
    try:
        curseur.execute(
            "UPDATE mots_cles SET actif = 1 WHERE id = %s",
            (mot_id,)
        )
        conn.commit()
        return True, "Mot reactive"
    except Exception as e:
        return False, f"Erreur : {e}"
    finally:
        curseur.close()
        conn.close()


def supprimer_mot(mot_id):
    """Supprime definitivement un mot."""
    conn = get_connexion()
    if conn is None:
        return False, "Base non accessible"

    curseur = conn.cursor()
    try:
        curseur.execute("DELETE FROM mots_cles WHERE id = %s", (mot_id,))
        conn.commit()
        return True, "Mot supprime"
    except Exception as e:
        return False, f"Erreur : {e}"
    finally:
        curseur.close()
        conn.close()


# ============================================================
# TEST DU MODULE
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("TEST DU MODULE keywords.py")
    print("=" * 60)
    print()

    # Test 1 : Compter total
    total = compter_total()
    print(f"1. Total mots actifs : {total}")
    print()

    # Test 2 : Lister les themes
    print("2. Themes disponibles :")
    for t in lister_themes():
        print(f"   - {t['theme']} : {t['nb_mots']} mots")
    print()

    # Test 3 : Stats par langue pour violence_femmes
    print("3. Repartition par langue (violence_femmes) :")
    stats = stats_par_langue("violence_femmes")
    for langue, nb in sorted(stats.items()):
        print(f"   - {langue} : {nb} mots")
    print()

    # Test 4 : Charger les mots par theme
    print("4. Exemples de mots (violence_femmes) :")
    groupes = charger_mots_par_theme("violence_femmes")
    for langue, mots in groupes.items():
        if mots:
            print(f"   [{langue}] {', '.join(mots[:3])}...")
    print()

    print("=" * 60)
    print("TEST TERMINE")
    print("=" * 60)