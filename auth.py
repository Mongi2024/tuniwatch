"""
Module auth.py - Authentification et sessions
Etape D - Session 2 (avec db_universal)
"""

import bcrypt
import streamlit as st
from db_universal import get_connexion


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
            return None

        # Verifier le mot de passe
        hash_stocke = user["mot_de_passe"]
        if bcrypt.checkpw(
            mot_de_passe.encode("utf-8"),
            hash_stocke.encode("utf-8")
        ):
            return {
                "id": user["id"],
                "login": user["login"],
                "role": user["role"]
            }

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
    """Efface la session utilisateur."""
    if "user" in st.session_state:
        del st.session_state["user"]


# ============================================================
# PAGE DE LOGIN
# ============================================================
def afficher_page_login():
    """Affiche la page de connexion et gere la soumission."""

    # Centrer le formulaire
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <h1>🇹🇳 TuniWatch</h1>
            <p style="color: #666;">Observatoire des médias tunisiens</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # Formulaire
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
    """
    if not est_connecte():
        afficher_page_login()
        st.stop()


def require_admin():
    """
    A appeler au debut des pages admin.
    Bloque l'acces si l'utilisateur n'est pas admin.
    """
    require_login()
    if not est_admin():
        st.error("🚫 Accès refusé — Cette page est réservée aux administrateurs.")
        st.info(
            f"Vous êtes connecté en tant que **{get_user()['login']}** "
            f"avec le rôle **{get_user()['role']}**."
        )
        st.stop()


def require_super_admin():
    """
    A appeler sur les pages sensibles (Admin, Utilisateurs).
    Bloque l'acces si l'utilisateur n'est pas super_admin.
    """
    require_login()
    if not est_super_admin():
        st.error("🚫 Accès refusé — Cette page est réservée au SUPER ADMINISTRATEUR.")
        st.info(
            f"Vous êtes connecté en tant que **{get_user()['login']}** "
            f"avec le rôle **{get_user()['role']}**."
        )
        st.stop()


# ============================================================
# TEST DU MODULE (execution directe)
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("TEST DU MODULE auth.py")
    print("=" * 60)
    print()

    # Test 1 : bons identifiants (super_admin)
    resultat = verifier_identifiants("superadmin", "SuperAdmin2026!")
    if resultat:
        print(f"OK - Connexion super_admin : {resultat}")
    else:
        print("ECHEC - superadmin non trouve")

    print()

    # Test 2 : bons identifiants (admin)
    resultat = verifier_identifiants("admin", "Admin2026!")
    if resultat:
        print(f"OK - Connexion admin : {resultat}")
    else:
        print("Note - admin avec ancien mot de passe (peut avoir change)")

    print()

    # Test 3 : mauvais mot de passe
    resultat = verifier_identifiants("admin", "mauvais")
    print(f"Test mauvais mdp : {resultat} (doit etre None)")

    print()

    # Test 4 : utilisateur inexistant
    resultat = verifier_identifiants("inconnu", "peu importe")
    print(f"Test utilisateur inexistant : {resultat} (doit etre None)")

    print()
    print("=" * 60)
    print("TEST TERMINE")
    print("=" * 60)