"""
Module auth.py - Authentification et sessions
Version 3.0 - Avec logs d'activité
"""

import bcrypt
import streamlit as st
from db_universal import get_connexion

# Import des fonctions de log
try:
    from activity_logger import log_login, log_logout, log_login_failed
    LOGS_ACTIFS = True
except ImportError:
    LOGS_ACTIFS = False
    def log_login(user): pass
    def log_logout(user): pass
    def log_login_failed(user): pass


# ============================================================
# VERIFICATION DES IDENTIFIANTS
# ============================================================
def verifier_identifiants(login, mot_de_passe):
    """
    Verifie si le couple login/mot de passe est valide.
    Retourne un dict {"id", "login", "role"} si OK, None sinon.
    """
    conn = get_connexion()
    if conn is None:
        return None

    curseur = conn.cursor(dictionary=True)
    try:
        curseur.execute("""
            SELECT id, login, mot_de_passe, role
            FROM utilisateurs
            WHERE login = %s
        """, (login,))

        user = curseur.fetchone()

        if not user:
            # Log : utilisateur inexistant
            if LOGS_ACTIFS:
                log_login_failed(login)
            return None

        # Verifier le mot de passe
        hash_stocke = user["mot_de_passe"]
        if bcrypt.checkpw(
            mot_de_passe.encode("utf-8"),
            hash_stocke.encode("utf-8")
        ):
            # Log : connexion réussie
            if LOGS_ACTIFS:
                log_login(user["login"])
            return {
                "id": user["id"],
                "login": user["login"],
                "role": user["role"]
            }

        # Log : mauvais mot de passe
        if LOGS_ACTIFS:
            log_login_failed(login)
        return None

    except Exception as e:
        print(f"Erreur auth : {e}")
        return None
    finally:
        curseur.close()
        conn.close()


# ============================================================
# GESTION DE LA SESSION
# ============================================================
def est_connecte():
    """Retourne True si un utilisateur est connecte."""
    return st.session_state.get("user") is not None


def get_user():
    """Retourne les infos de l'utilisateur connecte (ou None)."""
    return st.session_state.get("user")


def est_admin():
    """Retourne True si l'utilisateur est admin ou super_admin."""
    user = get_user()
    return user is not None and user.get("role") in ("admin", "super_admin")


def est_super_admin():
    """Retourne True si l'utilisateur est super_admin."""
    user = get_user()
    return user is not None and user.get("role") == "super_admin"


def connecter(user_info):
    """Enregistre l'utilisateur dans la session."""
    st.session_state["user"] = user_info


def deconnecter():
    """Efface la session utilisateur et log la déconnexion."""
    if "user" in st.session_state:
        user = st.session_state.get("user")
        if user and LOGS_ACTIFS:
            try:
                log_logout(user.get("login", "unknown"))
            except Exception:
                pass
        del st.session_state["user"]


# ============================================================
# PAGE DE LOGIN
# ============================================================
def afficher_page_login():
    """Affiche la page de connexion et gere la soumission."""

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <h1>🇹🇳 TuniWatch</h1>
            <p style="color: #666;">Observatoire des médias tunisiens</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        with st.form("form_login"):
            st.subheader("🔐 Connexion")
            st.write("Entrez vos identifiants pour accéder au dashboard.")

            login = st.text_input(
                "👤 Identifiant",
                placeholder="Votre login",
                key="login_input"
            )

            mot_de_passe = st.text_input(
                "🔑 Mot de passe",
                type="password",
                placeholder="Votre mot de passe",
                key="pwd_input"
            )

            submit = st.form_submit_button(
                "Se connecter",
                use_container_width=True,
                type="primary"
            )

            if submit:
                if not login or not mot_de_passe:
                    st.error("⚠️ Veuillez remplir les deux champs.")
                else:
                    with st.spinner("Vérification..."):
                        user_info = verifier_identifiants(login, mot_de_passe)

                    if user_info:
                        connecter(user_info)
                        st.success(f"✅ Bienvenue {user_info['login']} !")
                        st.rerun()
                    else:
                        st.error("❌ Identifiant ou mot de passe incorrect.")

        st.markdown("---")
        st.caption("© 2026 Khadraoui Mongi — Tous droits réservés")


# ============================================================
# PROTECTION DES PAGES
# ============================================================
def require_login():
    """
    A appeler au debut de chaque page protegee.
    Si non connecte, affiche le login et arrete l'execution.
    Si connecte, affiche le bloc utilisateur dans la sidebar.
    """
    if not est_connecte():
        afficher_page_login()
        st.stop()

    # Afficher le bloc utilisateur + bouton déconnexion
    try:
        import style
        style.sidebar_user()
        style.sidebar_logout()
    except Exception as e:
        print(f"Erreur sidebar : {e}")


def require_admin():
    """Bloque l'acces si l'utilisateur n'est pas admin."""
    require_login()
    if not est_admin():
        st.error("🚫 Accès refusé — Cette page est réservée aux administrateurs.")
        st.info(
            f"Vous êtes connecté en tant que **{get_user()['login']}** "
            f"avec le rôle **{get_user()['role']}**."
        )
        st.stop()


def require_super_admin():
    """Bloque l'acces si l'utilisateur n'est pas super_admin."""
    require_login()
    if not est_super_admin():
        st.error("🚫 Accès refusé — Cette page est réservée au SUPER ADMINISTRATEUR.")
        st.info(
            f"Vous êtes connecté en tant que **{get_user()['login']}** "
            f"avec le rôle **{get_user()['role']}**."
        )
        st.stop()