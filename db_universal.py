"""
Module db_universal.py - Connexion universelle (SQLite / PostgreSQL)
Detecte automatiquement l'environnement
Etape K - Version finale PostgreSQL + Streamlit Secrets
"""

import os
import re
import sqlite3

# Fichier SQLite (local)
DB_FILE = "tuniwatch.db"


# ============================================================
# CONFIGURATION POSTGRESQL (VPS)
# ============================================================
def get_postgres_config():
    """
    Recupere la config PostgreSQL depuis Streamlit Secrets (cloud)
    ou utilise les valeurs par defaut (local).
    """
    # Valeurs par defaut
    config = {
        "host": "92.113.26.224",
        "port": 5432,
        "database": "tuniwatch",
        "user": "tuniwatch_user",
        "password": "TuniWatchSecure2026",
        "connect_timeout": 10
    }

    # Essayer de lire depuis Streamlit Secrets (cloud)
    try:
        import streamlit as st
        if "DB_HOST" in st.secrets:
            config["host"] = st.secrets["DB_HOST"]
            config["port"] = int(st.secrets.get("DB_PORT", 5432))
            config["database"] = st.secrets["DB_NAME"]
            config["user"] = st.secrets["DB_USER"]
            config["password"] = st.secrets["DB_PASSWORD"]
    except Exception:
        pass  # Pas de Streamlit disponible (local)

    return config


# Configuration PostgreSQL (lue au chargement)
POSTGRES_CONFIG = get_postgres_config()


def est_en_production():
    """
    Detecte si on est en production (Streamlit Cloud).
    """
    # Streamlit Cloud definit toujours /home/appuser
    if os.path.exists("/home/appuser"):
        return True
    # Variable d'environnement
    if os.getenv("STREAMLIT_SHARING_MODE") or os.getenv("IS_STREAMLIT_CLOUD"):
        return True
    return False


def get_connexion():
    """
    Retourne une connexion a la base de donnees.
    - PostgreSQL si on est en production (Streamlit Cloud)
    - MySQL en local si dispo, sinon SQLite local
    """
    if est_en_production():
        # ============================================================
        # PRODUCTION : PostgreSQL sur VPS
        # ============================================================
        try:
            import psycopg2
            conn = psycopg2.connect(**POSTGRES_CONFIG)
            return PostgresConnectionWrapper(conn)
        except Exception as e:
            print(f"Erreur PostgreSQL : {e}")
            # Fallback SQLite si erreur
            if os.path.exists(DB_FILE):
                conn = sqlite3.connect(DB_FILE, check_same_thread=False)
                return SQLiteConnectionWrapper(conn)
            raise
    else:
        # ============================================================
        # LOCAL : MySQL puis SQLite en fallback
        # ============================================================
        try:
            import mysql.connector
            return mysql.connector.connect(
                host="localhost",
                port=3306,
                user="python_user",
                password="PythonUser2026!",
                database="monitoring",
                charset="utf8mb4"
            )
        except Exception:
            # Fallback sur SQLite local
            if os.path.exists(DB_FILE):
                conn = sqlite3.connect(DB_FILE, check_same_thread=False)
                return SQLiteConnectionWrapper(conn)
            raise


# ============================================================
# WRAPPER POSTGRESQL (imite l'API MySQL)
# ============================================================
class PostgresCursorWrapper:
    """Wrapper pour cursor PostgreSQL qui imite l'API MySQL."""

    def __init__(self, cursor, dictionary=False):
        self._cursor = cursor
        self._dictionary = dictionary

    def execute(self, sql, params=None):
        # PostgreSQL utilise %s comme MySQL
        if params is None:
            return self._cursor.execute(sql)
        return self._cursor.execute(sql, params)

    def fetchone(self):
        row = self._cursor.fetchone()
        if row is None:
            return None
        if self._dictionary and hasattr(self._cursor, "description") and self._cursor.description:
            cols = [d[0] for d in self._cursor.description]
            return dict(zip(cols, row))
        return row

    def fetchall(self):
        rows = self._cursor.fetchall()
        if self._dictionary and hasattr(self._cursor, "description") and self._cursor.description:
            cols = [d[0] for d in self._cursor.description]
            return [dict(zip(cols, r)) for r in rows]
        return rows

    def close(self):
        return self._cursor.close()

    def __iter__(self):
        rows = self._cursor.fetchall()
        if self._dictionary and hasattr(self._cursor, "description") and self._cursor.description:
            cols = [d[0] for d in self._cursor.description]
            for r in rows:
                yield dict(zip(cols, r))
        else:
            for r in rows:
                yield r

    @property
    def rowcount(self):
        return self._cursor.rowcount

    @property
    def lastrowid(self):
        return getattr(self._cursor, "lastrowid", None)


class PostgresConnectionWrapper:
    """Wrapper pour connexion PostgreSQL."""

    def __init__(self, connection):
        self._conn = connection

    def cursor(self, dictionary=False, buffered=False):
        cur = self._conn.cursor()
        return PostgresCursorWrapper(cur, dictionary=dictionary)

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


# ============================================================
# WRAPPER SQLITE (imite l'API MySQL)
# ============================================================
class SQLiteCursorWrapper:
    """Wrapper pour cursor SQLite qui imite l'API MySQL."""

    def __init__(self, cursor, dictionary=False):
        self._cursor = cursor
        self._dictionary = dictionary

    def execute(self, sql, params=None):
        sql_traduit = sql.replace("%s", "?")

        # Traduire les fonctions MySQL en SQLite
        sql_traduit = re.sub(r"\bNOW\(\)", "datetime('now')", sql_traduit)
        sql_traduit = re.sub(
            r"DATE_SUB\(datetime\('now'\), INTERVAL (\d+) DAY\)",
            r"datetime('now', '-\1 days')", sql_traduit
        )
        sql_traduit = re.sub(
            r"DATE_SUB\(NOW\(\), INTERVAL (\d+) DAY\)",
            r"datetime('now', '-\1 days')", sql_traduit
        )

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
    """Wrapper pour connexion SQLite."""

    def __init__(self, connection):
        self._conn = connection

    def cursor(self, dictionary=False, buffered=False):
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


# ============================================================
# TEST
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("TEST DU MODULE db_universal.py")
    print("=" * 60)
    print()

    print(f"En production ? {est_en_production()}")
    print()
    print(f"Config PostgreSQL : {POSTGRES_CONFIG['host']}:{POSTGRES_CONFIG['port']}")
    print()

    conn = get_connexion()
    print(f"Type de connexion : {type(conn).__name__}")
    print()

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) AS total FROM articles")
    result = cursor.fetchone()
    print(f"Articles en base : {result}")
    print()

    cursor.execute("SELECT id, titre, source FROM articles LIMIT 3")
    articles = cursor.fetchall()
    print(f"3 premiers articles :")
    for a in articles:
        titre = a.get("titre", "")[:50] if isinstance(a, dict) else str(a)
        print(f"   - {titre}")
    print()

    cursor.close()
    conn.close()

    print("=" * 60)
    print("TEST TERMINE")
    print("=" * 60)