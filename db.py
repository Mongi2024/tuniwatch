"""
Module db.py - Connexion et operations (universel MySQL/PostgreSQL/SQLite)
Etape C - Session 6 (avec db_universal)
"""

from db_universal import get_connexion
from datetime import datetime


def tester_connexion():
    """Test rapide : la base est-elle accessible ?"""
    conn = get_connexion()
    if conn is None:
        return False
    conn.close()
    return True


# ============================================================
# INSERTION DES ARTICLES
# ============================================================
def sauvegarder_articles(articles):
    """
    Sauvegarde une liste d'articles dans la table 'articles'.
    Ignore les doublons (meme URL).
    """
    if not articles:
        return 0

    conn = get_connexion()
    if conn is None:
        return 0

    curseur = conn.cursor()
    inseres = 0
    ignores = 0

    try:
        for article in articles:
            # Extraire et nettoyer les donnees
            titre = (article.get("titre") or "")[:500]
            source = (article.get("source") or "")[:200]
            auteur = (article.get("auteur") or "")[:200]
            url = (article.get("url") or "")[:1000]
            description = article.get("description") or ""
            mot_cle = (article.get("mot_cle") or "")[:200]
            date_pub_str = article.get("date") or ""

            # Convertir la date
            date_pub = None
            if date_pub_str:
                try:
                    date_pub = datetime.strptime(
                        date_pub_str[:19], "%Y-%m-%dT%H:%M:%S"
                    )
                except ValueError:
                    date_pub = None

            # Verifier si URL existe deja
            try:
                curseur.execute(
                    "SELECT id FROM articles WHERE url = %s",
                    (url,)
                )
                if curseur.fetchone():
                    ignores += 1
                    continue
            except Exception:
                pass

            # Insertion
            try:
                curseur.execute("""
                    INSERT INTO articles
                        (titre, source, auteur, date_publication,
                         url, description, mot_cle)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (titre, source, auteur, date_pub,
                      url, description, mot_cle))
                inseres += 1
            except Exception:
                ignores += 1

        conn.commit()
        print(f"OK - {inseres} articles inseres, {ignores} doublons ignores")
        return inseres

    except Exception as e:
        conn.rollback()
        print(f"Erreur insertion : {e}")
        return 0
    finally:
        curseur.close()
        conn.close()


# ============================================================
# LECTURE DES ARTICLES
# ============================================================
def compter_articles():
    """Retourne le nombre total d'articles en base."""
    conn = get_connexion()
    if conn is None:
        return 0

    curseur = conn.cursor()
    try:
        curseur.execute("SELECT COUNT(*) FROM articles")
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


def recuperer_articles(limite=50):
    """
    Recupere les derniers articles stockes.
    Retourne une liste de dictionnaires.
    """
    conn = get_connexion()
    if conn is None:
        return []

    curseur = conn.cursor(dictionary=True)
    try:
        curseur.execute("""
            SELECT id, titre, source, auteur,
                   date_publication, url, description,
                   mot_cle, sentiment, date_ajout
            FROM articles
            ORDER BY date_ajout DESC
            LIMIT %s
        """, (limite,))
        rows = curseur.fetchall()
        return rows if rows else []
    except Exception as e:
        print(f"Erreur lecture : {e}")
        return []
    finally:
        curseur.close()
        conn.close()


def vider_articles():
    """Supprime TOUS les articles (utile pour tester)."""
    conn = get_connexion()
    if conn is None:
        return False

    curseur = conn.cursor()
    try:
        curseur.execute("DELETE FROM articles")
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        curseur.close()
        conn.close()


# ============================================================
# TEST DIRECT DU MODULE
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("TEST DU MODULE db.py")
    print("=" * 60)
    print()

    # Test 1 : connexion
    print("1. Test de connexion...")
    if tester_connexion():
        print("   OK - Base accessible")
    else:
        print("   ECHEC - Verifier la connexion")
        exit()

    print()

    # Test 2 : comptage
    print("2. Nombre d'articles en base...")
    nb = compter_articles()
    print(f"   {nb} articles")

    print()

    # Test 3 : recuperation
    print("3. Derniers articles...")
    articles = recuperer_articles(3)
    for a in articles:
        titre = a.get("titre", "")[:60] if isinstance(a, dict) else str(a)
        print(f"   - {titre}")

    print()
    print("=" * 60)
    print("TEST TERMINE")
    print("=" * 60)