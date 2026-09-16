"""
Module config_prod.py - Configuration pour production
Detecte automatiquement si on est en local ou en production
"""

import os


def est_en_production():
    """
    Detecte si on est en production.
    En production, la variable d'environnement TUNIWATCH_PROD sera definie.
    """
    return os.getenv("TUNIWATCH_PROD") == "1"


def get_db_config():
    """
    Retourne la config MySQL selon l'environnement.
    """
    if est_en_production():
        # Configuration INFOMANIAK (production)
        return {
            "host": os.getenv("DB_HOST", "localhost"),
            "port": int(os.getenv("DB_PORT", "3306")),
            "user": os.getenv("DB_USER", "tuniwatch"),
            "password": os.getenv("DB_PASSWORD", ""),
            "database": os.getenv("DB_NAME", "tuniwatch_db"),
            "charset": "utf8mb4"
        }
    else:
        # Configuration LOCALE
        return {
            "host": "localhost",
            "port": 3306,
            "user": "python_user",
            "password": "PythonUser2026!",
            "database": "monitoring",
            "charset": "utf8mb4"
        }


# Export pour utilisation dans les modules
DB_CONFIG = get_db_config()