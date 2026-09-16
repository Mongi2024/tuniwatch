"""
Module db_universal.py - Connexion universelle MySQL/SQLite
Detecte automatiquement l'environnement (local vs cloud)
Etape K - Mise en ligne (version corrigee)
"""

import os
import re
import sqlite3


DB_FILE = "tuniwatch.db"


def est_en_production():
    """
    Detecte si on est sur Streamlit Cloud.
    On est en production UNIQUEMENT si on tourne sur le cloud Streamlit.
    """
    # Streamlit Cloud definit toujours /home/appuser
    if os.path.exists("/home/appuser"):
        return True
    # Detection alternative : variable d'environnement
    if os.getenv("STREAMLIT_SHARING_MODE") or os.getenv("IS_STREAMLIT_CLOUD"):
        return True
    return False


# Configuration MySQL (locale)
MYSQL_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "python_user",
    "password": "PythonUser2026!",
    "database": "monitoring",
    "charset": "utf8mb4"
}


class SQLiteCursorWrapper:
    """Wrapper pour cursor SQLite qui imite l'API MySQL."""

    def __init__(self, cursor, dictionary=False):
        self._cursor = cursor
        self._dictionary = dictionary

    def execute(self, sql, params=None):
        # 1. Traduire les placeholders %s en ?
        sql_traduit = sql.replace("%s", "?")

        # 2. Traduire les fonctions MySQL en SQLite
        # NOW() -> datetime('now')
        sql_traduit = re.sub(r"\bNOW\(\)", "datetime('now')", sql_traduit)

        # DATE_SUB(NOW(), INTERVAL X DAY) -> datetime('now', '-X days')
        sql_traduit = re.sub(
            r"DATE_SUB\(datetime\('now'\), INTERVAL (\d+) DAY\)",
            r"datetime('now', '-\1 days')",
            sql_traduit
        )
        sql_traduit = re.sub(
            r"DATE_SUB\(NOW\(\), INTERVAL (\d+) DAY\)",
            r"datetime('now', '-\1 days')",
            sql_traduit
        )
        sql_traduit = re.sub(
            r"DATE_SUB\(NOW\(\), INTERVAL (\d+) HOUR\)",
            r"datetime('now', '-\1 hours')",
            sql_traduit
        )

        # YEAR(x), MONTH(x), DAY(x) -> strftime
        sql_traduit = re.sub(r"\bYEAR\(([^)]+)\)", r"CAST(strftime('%Y', \1) AS INTEGER)", sql_traduit)
        sql_traduit = re.sub(r"\bMONTH\(([^)]+)\)", r"CAST(strftime('%m', \1) AS INTEGER)", sql_traduit)
        sql_traduit = re.sub(r"\bDAY\(([^)]+)\)", r"CAST(strftime('%d', \1) AS INTEGER)", sql_traduit)

        # 3. Executer
        if params is None:
            return self._cursor.execute(sql_traduit)
        return self._cursor.execute(sql_traduit, params)

    def fetchone(self):
        row = self._cursor.fetchone()
        if row is None:
            return None
        if self._dictionary:
            return dict(row)
        return tuple(row) if not isinstance(row, tuple) else row

    def fetchall(self):
        rows = self._cursor.fetchall()
        if self._dictionary:
            return [dict(r) for r in rows]
        return [tuple(r) if not isinstance(r, tuple) else r for r in rows]

    def close(self):
        return self._cursor.close()

    def __iter__(self):
        for row in self._cursor:
            if self._dictionary:
                yield dict(row)
            else:
                yield tuple(row) if not isinstance(row, tuple) else row

    @property
    def rowcount(self):
        return self._cursor.rowcount

    @property
    def lastrowid(self):
        return self._cursor.lastrowid


class SQLiteConnectionWrapper:
    """Wrapper pour connexion SQLite qui imite l'API MySQL."""

    def __init__(self, connection):
        self._conn = connection

    def cursor(self, dictionary=False, buffered=False):
        """Retourne un curseur. dictionary=True renvoie des dicts."""
        self._conn.row_factory = sqlite3.Row
        cur = self._conn.cursor()
        return SQLiteCursorWrapper(cur, dictionary=dictionary)

    def commit(self):
        return self._conn.commit()

    def rollback(self):
        return self._conn.rollback()

    def close(self):
        return self._conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def get_connexion():
    """
    Retourne une connexion a la base de donnees.
    - SQLite si on est sur Streamlit Cloud
    - MySQL en local
    """
    if est_en_production():
        if not os.path.exists(DB_FILE):
            raise FileNotFoundError(
                f"Fichier {DB_FILE} introuvable. "
                "Verifiez que le fichier est bien dans le repo GitHub."
            )
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        return SQLiteConnectionWrapper(conn)
    else:
        try:
            import mysql.connector
            return mysql.connector.connect(**MYSQL_CONFIG)
        except Exception as e:
            print(f"MySQL indisponible, fallback SQLite : {e}")
            conn = sqlite3.connect(DB_FILE, check_same_thread=False)
            return SQLiteConnectionWrapper(conn)


# Export pour compatibilite
DB_CONFIG = MYSQL_CONFIG


if __name__ == "__main__":
    print("=" * 60)
    print("TEST DU MODULE db_universal.py")
    print("=" * 60)
    print()

    print(f"En production ? {est_en_production()}")
    print()

    conn = get_connexion()
    print(f"Type de connexion : {type(conn).__name__}")
    print()

    # Test 1 : Requete simple
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) AS total FROM articles")
    result = cursor.fetchone()
    print(f"Test 1 - Articles en base : {result}")
    print()

    # Test 2 : Requete avec parametre
    cursor.execute("SELECT id, titre, source FROM articles LIMIT 3")
    articles = cursor.fetchall()
    print(f"Test 2 - 3 premiers articles :")
    for a in articles:
        titre = a.get("titre", "")[:50] if isinstance(a, dict) else str(a)
        print(f"   - {titre}")
    print()

    # Test 3 : Requete avec %s
    cursor.execute("SELECT COUNT(*) AS nb FROM articles WHERE source = %s", ("African Manager",))
    result = cursor.fetchone()
    print(f"Test 3 - Articles African Manager : {result}")
    print()

    cursor.close()
    conn.close()

    print("=" * 60)
    print("TEST TERMINE")
    print("=" * 60)