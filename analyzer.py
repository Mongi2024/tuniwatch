"""
Module analyzer.py - Analyse automatique des articles
Detecte les themes dans chaque article via les mots-cles
Version 0.3 - Avec filtre intelligent et clubs sportifs
Etape F - Session 2
"""

import mysql.connector
from mysql.connector import Error
import re
import unicodedata


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

# Seuil de pertinence (score minimum pour classer un article)
SEUIL_MINIMUM = 1.0


def get_connexion():
    """Ouvre une connexion MySQL."""
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        print(f"Erreur connexion : {e}")
        return None


# ============================================================
# NORMALISATION DU TEXTE
# ============================================================
def normaliser_texte(texte):
    """
    Normalise un texte pour la recherche :
    - Minuscules
    - Suppression des accents (pour le francais)
    - Suppression des diacritiques arabes
    - Conservation des caracteres arabes
    """
    if not texte:
        return ""

    # Minuscules
    texte = texte.lower()

    # Supprimer les diacritiques (accents francais, tashkeel arabe)
    texte = unicodedata.normalize("NFKD", texte)

    # Retirer les marques de combinaison (accents)
    texte = "".join(c for c in texte if not unicodedata.combining(c))

    # Remplacer la ponctuation par des espaces
    texte = re.sub(r"[^\w\s]", " ", texte, flags=re.UNICODE)

    # Espaces multiples
    texte = re.sub(r"\s+", " ", texte).strip()

    return texte


# ============================================================
# DETECTION DE CONTEXTE TUNISIEN
# ============================================================
# Mots qui indiquent que l'article parle de la Tunisie
MOTS_TUNISIE = [
    # Pays et adjectifs
    "tunisie", "tunisien", "tunisienne", "tunisiens", "tunisiennes",

    # Villes et regions
    "tunis", "sfax", "sousse", "kairouan", "bizerte", "gabes",
    "ariana", "gafsa", "monastir", "nabeul", "kasserine",
    "medenine", "tataouine", "kebili", "tozeur", "siliana",
    "zaghouan", "beja", "jendouba", "mahdia", "kef", "sidi bouzid",
    "ben arous", "manouba", "ben guerdane", "djerba",

    # Clubs sportifs tunisiens
    "jsk", "est", "ca", "css", "ess", "cab", "usm", "asg",
    "esperance", "club africain", "etoile du sahel", "cs sfaxien",
    "esperance sportive", "etoile sportive", "es tunis",
    "stade tunisien", "stade tunisienne", "js kairouan",

    # Institutions et lieux
    "kasbah", "bardo", "carthage", "la marsa", "la goulette",
    "hammamet", "zarzis",

    # Medias et chaines tunisiennes
    "mosaique", "shems", "jawhara", "express fm", "watania",
    "tunisia tv", "nessma", "hannibal", "el hiwar",

    # Arabe - Pays et adjectifs
    "تونس", "تونسي", "تونسية", "التونسي", "التونسية",

    # Arabe - Villes et regions
    "صفاقس", "سوسة", "القيروان", "بنزرت", "قابس",
    "أريانة", "قفصة", "المنستير", "نابل", "القصرين",
    "مدنين", "تطاوين", "قبلي", "توزر", "سليانة",
    "زغوان", "باجة", "جندوبة", "المهدية", "الكاف",
    "سيدي بوزيد", "بن عروس", "منوبة", "جربة",

    # Arabizi
    "tounes", "tounsi", "tounsiya"
]


def est_article_tunisien(texte_normalise):
    """
    Verifie si l'article mentionne la Tunisie ou une ville tunisienne.
    """
    for mot in MOTS_TUNISIE:
        mot_norm = normaliser_texte(mot)
        if not mot_norm:
            continue
        pattern = r"\b" + re.escape(mot_norm) + r"s?\b"
        if re.search(pattern, texte_normalise):
            return True
    return False


def contient_mot_theme_fort(texte_normalise, themes_mots):
    """
    Verifie si l'article contient un mot-cle de POIDS FORT (>= 1.5).
    Si oui, on considere qu'il est pertinent meme sans mention tunisienne.
    """
    for theme, mots in themes_mots.items():
        for mot_info in mots:
            if mot_info["poids"] >= 1.5 and len(mot_info["mot"]) >= 4:
                mot_norm = mot_info["mot"]
                pattern = r"\b" + re.escape(mot_norm) + r"s?\b"
                if re.search(pattern, texte_normalise):
                    return True
    return False


# ============================================================
# CHARGEMENT DES MOTS-CLES
# ============================================================
def charger_mots_par_theme():
    """
    Charge tous les mots-cles actifs, groupes par theme.
    """
    conn = get_connexion()
    if conn is None:
        return {}

    curseur = conn.cursor(dictionary=True)
    try:
        curseur.execute("""
            SELECT theme, langue, mot, poids
            FROM mots_cles
            WHERE actif = 1
            ORDER BY theme, poids DESC
        """)

        themes = {}
        for row in curseur.fetchall():
            theme = row["theme"]
            if theme not in themes:
                themes[theme] = []
            themes[theme].append({
                "mot": normaliser_texte(row["mot"]),
                "mot_original": row["mot"],
                "poids": row["poids"],
                "langue": row["langue"]
            })

        return themes
    finally:
        curseur.close()
        conn.close()


# ============================================================
# ANALYSE D'UN ARTICLE
# ============================================================
def analyser_article(titre, description, themes_mots):
    """
    Analyse un article et retourne les themes detectes.

    Args:
        titre : titre de l'article
        description : description/texte
        themes_mots : dict {theme: [mots]}

    Returns:
        dict {theme: {"score": X, "nb_mots": Y, "mots": [...]}}
    """
    # Texte complet normalise
    texte_complet = normaliser_texte(f"{titre} {description}")

    if not texte_complet:
        return {}

    # FILTRE INTELLIGENT : accepter si :
    # 1. Article tunisien
    # 2. OU article tres pertinent (contient un mot fort >= 1.5)
    est_tunisien = est_article_tunisien(texte_complet)

    if not est_tunisien:
        if not contient_mot_theme_fort(texte_complet, themes_mots):
            return {}

    resultats = {}

    for theme, mots in themes_mots.items():
        score = 0.0
        nb_mots_trouves = 0
        mots_matches = []

        for mot_info in mots:
            mot_normalise = mot_info["mot"]
            if not mot_normalise:
                continue

            # Recherche avec gestion des pluriels (s? optionnel)
            pattern = r"\b" + re.escape(mot_normalise) + r"s?\b"

            if re.search(pattern, texte_complet):
                score += mot_info["poids"]
                nb_mots_trouves += 1
                mots_matches.append(mot_info["mot_original"])

        # Uniquement si le score depasse le seuil
        if nb_mots_trouves > 0 and score >= SEUIL_MINIMUM:
            resultats[theme] = {
                "score": round(score, 2),
                "nb_mots": nb_mots_trouves,
                "mots": mots_matches
            }

    return resultats


# ============================================================
# ANALYSE DE TOUS LES ARTICLES
# ============================================================
def analyser_articles_en_base(limite=None, reanalyser=False):
    """
    Analyse tous les articles en base.
    """
    from datetime import datetime
    debut = datetime.now()

    conn = get_connexion()
    if conn is None:
        return None

    curseur = conn.cursor(dictionary=True)

    try:
        # 1. Charger les mots-cles
        print("Chargement des mots-cles...")
        themes_mots = charger_mots_par_theme()
        print(f"   {len(themes_mots)} themes charges")
        print()

        # 2. Recuperer les articles
        if reanalyser:
            requete = "SELECT id, titre, description FROM articles"
        else:
            requete = """
                SELECT id, titre, description
                FROM articles
                WHERE id NOT IN (SELECT DISTINCT article_id FROM articles_themes)
            """

        if limite:
            requete += f" LIMIT {limite}"

        curseur.execute(requete)
        articles = curseur.fetchall()

        print(f"Articles a analyser : {len(articles)}")
        print()

        if not articles:
            print("Aucun article a analyser.")
            return {"analyses": 0, "articles_traites": 0}

        # 3. Analyser chaque article
        curseur2 = conn.cursor()
        total_analyses = 0
        total_articles = 0

        for i, art in enumerate(articles, 1):
            if i % 50 == 0:
                print(f"   Traitement : {i}/{len(articles)}...")

            resultats = analyser_article(
                art["titre"] or "",
                art["description"] or "",
                themes_mots
            )

            if resultats:
                total_articles += 1

                for theme, data in resultats.items():
                    try:
                        curseur2.execute("""
                            INSERT INTO articles_themes
                                (article_id, theme, score, nb_mots_trouves, mots_trouves)
                            VALUES (%s, %s, %s, %s, %s)
                            ON DUPLICATE KEY UPDATE
                                score = VALUES(score),
                                nb_mots_trouves = VALUES(nb_mots_trouves),
                                mots_trouves = VALUES(mots_trouves),
                                date_analyse = CURRENT_TIMESTAMP
                        """, (
                            art["id"],
                            theme,
                            data["score"],
                            data["nb_mots"],
                            ", ".join(data["mots"][:20])
                        ))
                        total_analyses += 1
                    except Error as e:
                        print(f"   Erreur insertion : {e}")

        conn.commit()

        duree = (datetime.now() - debut).total_seconds()

        print()
        print(f"Analyse terminee en {duree:.1f} secondes")
        print(f"   Articles analyses : {total_articles}")
        print(f"   Analyses creees   : {total_analyses}")

        return {
            "analyses": total_analyses,
            "articles_traites": total_articles,
            "duree": duree
        }

    except Error as e:
        print(f"Erreur : {e}")
        return None
    finally:
        curseur.close()
        conn.close()


# ============================================================
# STATISTIQUES
# ============================================================
def stats_themes():
    """Retourne les statistiques par theme."""
    conn = get_connexion()
    if conn is None:
        return []

    curseur = conn.cursor(dictionary=True)
    try:
        curseur.execute("""
            SELECT 
                theme,
                COUNT(DISTINCT article_id) AS nb_articles,
                AVG(score) AS score_moyen,
                SUM(nb_mots_trouves) AS total_mots
            FROM articles_themes
            GROUP BY theme
            ORDER BY nb_articles DESC
        """)
        return curseur.fetchall()
    finally:
        curseur.close()
        conn.close()


def compter_analyses():
    """Compte le nombre total d'analyses."""
    conn = get_connexion()
    if conn is None:
        return 0

    curseur = conn.cursor()
    try:
        curseur.execute("SELECT COUNT(*) FROM articles_themes")
        return curseur.fetchone()[0]
    finally:
        curseur.close()
        conn.close()


# ============================================================
# TEST
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("TEST DU MODULE analyzer.py")
    print("=" * 60)
    print()

    # Test 1 : Charger les mots-cles
    print("1. Chargement des mots-cles...")
    themes = charger_mots_par_theme()
    print(f"   {len(themes)} themes :")
    for t, mots in themes.items():
        print(f"      - {t} : {len(mots)} mots")
    print()

    # Test 2 : Article tunisien classique
    print("2. Test article tunisien :")
    titre_test = "Violence conjugale : une femme agressée à Tunis"
    desc_test = "Un homme a été arrêté après avoir frappé son épouse."

    resultats = analyser_article(titre_test, desc_test, themes)
    print(f"   Titre : {titre_test}")
    print(f"   Themes detectes :")
    for theme, data in resultats.items():
        print(f"      - {theme} : score={data['score']}, mots={data['nb_mots']}")
    print()

    # Test 3 : Article sportif tunisien (avec club)
    print("3. Test article sportif :")
    titre_test2 = "Violences à la salle Aziz Miled : 4 matches à huis clos contre la JSK"
    resultats2 = analyser_article(titre_test2, "", themes)
    print(f"   Titre : {titre_test2}")
    print(f"   Themes detectes :")
    for theme, data in resultats2.items():
        print(f"      - {theme} : score={data['score']}")
    print()

    # Test 4 : Article etranger (doit etre rejete)
    print("4. Test article NON-tunisien :")
    titre_test3 = "L'extrême droite perd du terrain en Suède"
    resultats3 = analyser_article(titre_test3, "", themes)
    if resultats3:
        print(f"   PROBLEME : article etranger classifie")
    else:
        print(f"   OK : article etranger rejete")
    print()

    # Test 5 : Stats actuelles
    print("5. Statistiques actuelles :")
    print(f"   Analyses en base : {compter_analyses()}")
    print()

    print("=" * 60)
    print("TEST TERMINE")
    print("=" * 60)