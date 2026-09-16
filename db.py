"""
Module db.py - Connexion et operations MySQL
Etape C - Session 6
"""

import mysql.connector
from mysql.connector import Error
from datetime import datetime

# ============================================================
# CONFIGURATION DE LA CONNEXION
# ============================================================
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "python_user",
    "password": "PythonUser2026!",
    "database": "monitoring",
    "charset": "utf8mb4",
    "use_unicode": True
}


def get_connexion():
    """
    Ouvre une connexion a MySQL.
    Retourne un objet connexion ou None si erreur.
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Erreur connexion MySQL : {e}")
        return None


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

    Args:
        articles : liste de dictionnaires

    Returns:
        Nombre d'articles reellement inseres
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

            # Convertir la date au format MySQL
            date_pub = None
            if date_pub_str:
                try:
                    # Format ISO : 2026-09-14T15:30:00Z
                    date_pub = datetime.strptime(
                        date_pub_str[:19], "%Y-%m-%dT%H:%M:%S"
                    )
                except ValueError:
                    date_pub = None

            # Insertion (ignorer si URL existe deja)
            try:
                curseur.execute("""
                    INSERT INTO articles
                        (titre, source, auteur, date_publication,
                         url, description, mot_cle)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (titre, source, auteur, date_pub,
                      url, description, mot_cle))
                inseres += 1
            except mysql.connector.IntegrityError:
                # URL en double → ignore
                ignores += 1

        conn.commit()
        print(f"OK - {inseres} articles inseres, {ignores} doublons ignores")
        return inseres

    except Error as e:
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
        return curseur.fetchone()[0]
    except Error:
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
        return curseur.fetchall()
    except Error as e:
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
    except Error:
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
        print("   OK - MySQL accessible")
    else:
        print("   ECHEC - Verifier MySQL")
        exit()

    print()

    # Test 2 : comptage
    print("2. Nombre d'articles en base...")
    nb = compter_articles()
    print(f"   {nb} articles")

    print()

    # Test 3 : insertion d'un article test
    print("3. Insertion d'un article test...")
    article_test = [{
        "titre": "Article de test depuis db.py",
        "source": "Test",
        "auteur": "Khadraoui Mongi",
        "date": "2026-09-15T10:00:00Z",
        "url": f"https://test.example.com/article-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "description": "Ceci est un article de test pour valider la connexion MySQL.",
        "mot_cle": "test"
    }]
    inseres = sauvegarder_articles(article_test)
    print(f"   {inseres} article(s) insere(s)")

    print()

    # Test 4 : nouveau comptage
    print("4. Nouveau comptage...")
    nb = compter_articles()
    print(f"   {nb} articles maintenant")

    print()
    print("=" * 60)
    print("TEST TERMINE")
    print("=" * 60)