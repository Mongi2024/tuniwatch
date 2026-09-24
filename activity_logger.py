"""
Module activity_logger.py - Enregistre les activités de l'application
Version 1.1 - Correction du bug ip=local
"""

import os
from datetime import datetime

LOG_FILE = "/root/tuniwatch/logs/activity.log"


def log_activity(user, action, details=""):
    """
    Enregistre une activité dans le fichier de log.
    
    Args:
        user: Nom d'utilisateur (ou 'system' pour les tâches auto)
        action: Action effectuée (login, logout, create_user, etc.)
        details: Détails supplémentaires (optionnel)
    """
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Construire la ligne de log (sans IP pour éviter les doublons)
        line = f"[{timestamp}] user={user} action={action}"
        if details:
            line += f" {details}"
        line += "\n"
        
        # Écrire dans le fichier
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line)
        
        return True
    except Exception as e:
        print(f"Erreur log_activity: {e}")
        return False


def log_login(user):
    """Log une connexion réussie."""
    return log_activity(user, "login")


def log_logout(user):
    """Log une déconnexion."""
    return log_activity(user, "logout")


def log_login_failed(username):
    """Log un échec de connexion."""
    return log_activity(username, "login_failed")


def log_create_user(admin, target):
    """Log la création d'un utilisateur."""
    return log_activity(admin, "create_user", f"target={target}")


def log_delete_user(admin, target):
    """Log la suppression d'un utilisateur."""
    return log_activity(admin, "delete_user", f"target={target}")


def log_change_role(admin, target, new_role):
    """Log le changement de rôle."""
    return log_activity(admin, "change_role", f"target={target} new_role={new_role}")


def log_run_analysis(articles_count, duration):
    """Log une analyse."""
    return log_activity("system", "run_analysis", f"articles={articles_count} duration={duration:.1f}s")


def log_backup(size):
    """Log un backup."""
    return log_activity("system", "backup", f"size={size}")


def log_error(user, error_message):
    """Log une erreur."""
    return log_activity(user, "error", f"message={error_message[:200]}")


def log_source_update(admin, source_name):
    """Log la modification d'une source."""
    return log_activity(admin, "update_source", f"source={source_name}")


def get_recent_activities(limit=50):
    """Retourne les dernières activités."""
    try:
        if not os.path.exists(LOG_FILE):
            return []
        
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        # Prendre les N dernières lignes (plus récent en premier)
        return lines[-limit:][::-1]
    except Exception as e:
        print(f"Erreur get_recent_activities: {e}")
        return []


def count_activities():
    """Compte le nombre d'activités."""
    try:
        if not os.path.exists(LOG_FILE):
            return 0
        
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return sum(1 for _ in f)
    except Exception:
        return 0


def get_stats_by_action():
    """Retourne le nombre d'activités par type d'action."""
    try:
        if not os.path.exists(LOG_FILE):
            return {}
        
        stats = {}
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                # Extraire action=xxx
                if "action=" in line:
                    action = line.split("action=")[1].split()[0].strip()
                    stats[action] = stats.get(action, 0) + 1
        
        return stats
    except Exception:
        return {}


# ============================================================
# TEST
# ============================================================
if __name__ == "__main__":
    print("Test du module activity_logger.py")
    print()
    
    # Tester les fonctions
    log_login("test_user")
    log_logout("test_user")
    log_login_failed("unknown_user")
    log_create_user("superadmin", "marie")
    log_run_analysis(100, 22.5)
    log_backup("426KB")
    log_source_update("admin", "JDD Tunisie")
    
    print("Activités enregistrées.")
    print()
    print("Dernières activités :")
    for line in get_recent_activities(10):
        print(f"  {line.strip()}")
    print()
    print(f"Total : {count_activities()} activités")
    print()
    print("Statistiques par action :")
    for action, count in get_stats_by_action().items():
        print(f"  {action} : {count}")