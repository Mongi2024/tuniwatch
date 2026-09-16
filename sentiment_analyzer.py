"""
Module sentiment_analyzer.py - Analyse de sentiment par regles
Version SANS IA - Fonctionne sur Python 3.14
Etape F - Session 1
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

# Cache des dictionnaires (charge une seule fois)
_dict_positif = None
_dict_negatif = None


def get_connexion():
    """Ouvre une connexion MySQL."""
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        print(f"Erreur connexion : {e}")
        return None


def normaliser_texte(texte):
    """Normalise pour la recherche (avec suppression du prefixe ال arabe)."""
    if not texte:
        return ""
    texte = texte.lower()
    texte = unicodedata.normalize("NFKD", texte)
    texte = "".join(c for c in texte if not unicodedata.combining(c))
    texte = re.sub(r"[^\w\s]", " ", texte, flags=re.UNICODE)
    texte = re.sub(r"\s+", " ", texte).strip()
    return texte


def normaliser_mot_arabe(mot):
    """
    Normalise un mot arabe en supprimant les prefixes courants.
    Ex: البطالة -> بطالة, والفقر -> فقر
    """
    if not mot:
        return mot

    # Supprimer le "و" (et) au debut
    if mot.startswith("و") and len(mot) > 2:
        mot = mot[1:]

    # Supprimer "ال" (article defini) au debut
    if mot.startswith("ال") and len(mot) > 3:
        mot = mot[2:]

    # Supprimer "ب" "ل" "ك" "ف" (prefixes prepositionnels)
    if len(mot) > 3 and mot[0] in "بلكف":
        mot = mot[1:]

    return mot


def charger_dictionnaires():
    """Charge les mots positifs et negatifs depuis MySQL."""
    global _dict_positif, _dict_negatif

    if _dict_positif is not None and _dict_negatif is not None:
        return

    conn = get_connexion()
    if conn is None:
        print("Impossible de charger les dictionnaires.")
        _dict_positif = {}
        _dict_negatif = {}
        return

    curseur = conn.cursor(dictionary=True)
    try:
        curseur.execute("""
            SELECT mot, polarite, intensite
            FROM mots_sentiment
            WHERE actif = 1
        """)

        _dict_positif = {}
        _dict_negatif = {}

        for row in curseur.fetchall():
            mot_norm = normaliser_texte(row["mot"])
            if not mot_norm:
                continue
            if row["polarite"] == "positif":
                _dict_positif[mot_norm] = row["intensite"]
            else:
                _dict_negatif[mot_norm] = row["intensite"]

        print(f"   Dictionnaires charges : {len(_dict_positif)} positifs, {len(_dict_negatif)} negatifs")

    finally:
        curseur.close()
        conn.close()


def detecter_langue(texte):
    """Detection simple de la langue dominante."""
    if not texte:
        return "inconnu"
    arabes = len(re.findall(r"[\u0600-\u06FF]", texte))
    latins = len(re.findall(r"[a-zA-Z]", texte))
    if arabes > latins:
        return "ar"
    elif latins > 0:
        return "fr"
    return "inconnu"


def analyser_article(titre, description):
    """
    Analyse le sentiment d'un article par regles de mots.
    """
    charger_dictionnaires()

    texte = normaliser_texte(f"{titre} {description}")

    if not texte or len(texte) < 10:
        return None

    score_positif = 0.0
    score_negatif = 0.0
    nb_positifs = 0
    nb_negatifs = 0

    mots = texte.split()

    # Chercher dans les dictionnaires
        # Chercher dans les dictionnaires
    for mot in mots:
        # Version normale
        if mot in _dict_positif:
            score_positif += _dict_positif[mot]
            nb_positifs += 1
        if mot in _dict_negatif:
            score_negatif += _dict_negatif[mot]
            nb_negatifs += 1

        # Version avec prefixe arabe supprime (si different)
        mot_sans_prefixe = normaliser_mot_arabe(mot)
        if mot_sans_prefixe != mot:
            if mot_sans_prefixe in _dict_positif:
                score_positif += _dict_positif[mot_sans_prefixe]
                nb_positifs += 1
            if mot_sans_prefixe in _dict_negatif:
                score_negatif += _dict_negatif[mot_sans_prefixe]
                nb_negatifs += 1

    # Calcul du score final (-1 a +1)
    total = score_positif + score_negatif

    if total == 0:
        # Aucun mot detecte -> neutre
        return {
            "sentiment": "neutre",
            "score": 0.0,
            "confiance": 0.0,
            "emotion": None,
            "langue": detecter_langue(texte)
        }

    # Score normalise : -1 (tres negatif) a +1 (tres positif)
    score_final = (score_positif - score_negatif) / total

    # Confiance : basee sur le nombre de mots trouves
    confiance = min(1.0, (nb_positifs + nb_negatifs) / 5.0)

    # Categorie
    if score_final > 0.2:
        sentiment = "positif"
    elif score_final < -0.2:
        sentiment = "negatif"
    else:
        sentiment = "neutre"

    return {
        "sentiment": sentiment,
        "score": round(score_final, 2),
        "confiance": round(confiance, 2),
        "emotion": None,
        "langue": detecter_langue(texte)
    }


def analyser_articles_en_base(limite=None, reanalyser=False):
    """Analyse tous les articles."""
    from datetime import datetime
    debut = datetime.now()

    conn = get_connexion()
    if conn is None:
        return None

    curseur = conn.cursor(dictionary=True)

    try:
        if reanalyser:
            requete = "SELECT id, titre, description FROM articles"
        else:
            requete = """
                SELECT a.id, a.titre, a.description
                FROM articles a
                LEFT JOIN articles_sentiment s ON s.article_id = a.id
                WHERE s.id IS NULL
            """

        if limite:
            requete += f" LIMIT {limite}"

        curseur.execute(requete)
        articles = curseur.fetchall()

        print(f"Articles a analyser : {len(articles)}")
        print()

        if not articles:
            print("Tous les articles ont deja ete analyses.")
            return {"analyses": 0, "articles_traites": 0, "duree": 0}

        # Charger les dictionnaires
        charger_dictionnaires()
        print()

        curseur2 = conn.cursor()
        total_analyses = 0

        for i, art in enumerate(articles, 1):
            if i % 50 == 0 or i == 1:
                print(f"   Analyse : {i}/{len(articles)}...")

            resultat = analyser_article(
                art["titre"] or "",
                art["description"] or ""
            )

            if resultat:
                try:
                    curseur2.execute("""
                        INSERT INTO articles_sentiment
                            (article_id, sentiment, score, confiance,
                             emotion, langue_detectee)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                            sentiment = VALUES(sentiment),
                            score = VALUES(score),
                            confiance = VALUES(confiance),
                            langue_detectee = VALUES(langue_detectee),
                            date_analyse = CURRENT_TIMESTAMP
                    """, (
                        art["id"],
                        resultat["sentiment"],
                        resultat["score"],
                        resultat["confiance"],
                        resultat["emotion"],
                        resultat["langue"]
                    ))
                    total_analyses += 1
                except Error as e:
                    print(f"   Erreur insertion : {e}")

        conn.commit()
        duree = (datetime.now() - debut).total_seconds()

        print()
        print(f"Analyse terminee en {duree:.1f} secondes")
        print(f"   Articles analyses : {total_analyses}")

        return {
            "analyses": total_analyses,
            "articles_traites": len(articles),
            "duree": duree
        }

    except Error as e:
        print(f"Erreur : {e}")
        return None
    finally:
        curseur.close()
        conn.close()


def stats_sentiment():
    """Statistiques par sentiment."""
    conn = get_connexion()
    if conn is None:
        return []

    curseur = conn.cursor(dictionary=True)
    try:
        curseur.execute("""
            SELECT 
                sentiment,
                COUNT(*) AS nb,
                ROUND(AVG(score), 2) AS score_moyen,
                ROUND(AVG(confiance), 2) AS confiance_moyenne
            FROM articles_sentiment
            GROUP BY sentiment
            ORDER BY nb DESC
        """)
        return curseur.fetchall()
    finally:
        curseur.close()
        conn.close()


def compter_analyses():
    """Compte les analyses de sentiment."""
    conn = get_connexion()
    if conn is None:
        return 0
    curseur = conn.cursor()
    try:
        curseur.execute("SELECT COUNT(*) FROM articles_sentiment")
        return curseur.fetchone()[0]
    finally:
        curseur.close()
        conn.close()


# ============================================================
# TEST
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("TEST DU MODULE sentiment_analyzer.py (par regles)")
    print("=" * 60)
    print()

    print("1. Test article positif :")
    r = analyser_article(
        "Excellente nouvelle pour la Tunisie",
        "Le pays enregistre une croissance record et un succes remarquable."
    )
    print(f"   Resultat : {r}")
    print()

    print("2. Test article negatif :")
    r = analyser_article(
        "Violence grave a Tunis",
        "Une agression violente et une crise qui inquiete les Tunisiens."
    )
    print(f"   Resultat : {r}")
    print()

    print("3. Test article en arabe :")
    r = analyser_article(
        "أخبار سيئة للاقتصاد التونسي",
        "تراجع كبير في نسبة النمو وارتفاع البطالة والفقر."
    )
    print(f"   Resultat : {r}")
    print()

    print("4. Statistiques actuelles :")
    print(f"   Analyses en base : {compter_analyses()}")
    for s in stats_sentiment():
        print(f"      - {s['sentiment']} : {s['nb']} articles")
    print()

    print("=" * 60)
    print("TEST TERMINE")
    print("=" * 60)