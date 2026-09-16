"""
Page Utilisateurs - Gestion des comptes (admin uniquement)
Etape D - Session 7
"""

import streamlit as st
import sys
import os
import bcrypt
import mysql.connector
from mysql.connector import Error

# Ajout du dossier parent
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import auth
import style
style.appliquer_style()
# Configuration
st.set_page_config(
    page_title="Utilisateurs - Monitoring",
    page_icon="👥",
    layout="wide"
)

# Protection ADMIN uniquement
auth.require_super_admin()
# ============================================================
# TITRE
# ============================================================
st.title("👥 Gestion des utilisateurs")
st.caption("Page réservée aux administrateurs")

st.markdown("---")


# ============================================================
# FONCTIONS UTILITAIRES
# ============================================================
def lister_utilisateurs():
    """Retourne la liste des utilisateurs."""
    conn = auth.get_connexion()
    if conn is None:
        return []
    curseur = conn.cursor(dictionary=True)
    try:
        curseur.execute("""
            SELECT id, login, role, date_creation
            FROM utilisateurs
            ORDER BY id
        """)
        return curseur.fetchall()
    finally:
        curseur.close()
        conn.close()


def creer_utilisateur(login, mot_de_passe, role):
    """Cree un nouvel utilisateur. Retourne (succes, message)."""
    conn = auth.get_connexion()
    if conn is None:
        return False, "MySQL non accessible"

    curseur = conn.cursor()
    try:
        # Verifier si existe deja
        curseur.execute(
            "SELECT id FROM utilisateurs WHERE login = %s",
            (login,)
        )
        if curseur.fetchone():
            return False, f"Le login '{login}' existe déjà."

        # Creer
        hash_ = bcrypt.hashpw(
            mot_de_passe.encode("utf-8"),
            bcrypt.gensalt(rounds=12)
        ).decode("utf-8")

        curseur.execute("""
            INSERT INTO utilisateurs (login, mot_de_passe, role)
            VALUES (%s, %s, %s)
        """, (login, hash_, role))
        conn.commit()
        return True, f"Utilisateur '{login}' créé avec succès."

    except Error as e:
        return False, f"Erreur : {e}"
    finally:
        curseur.close()
        conn.close()


def supprimer_utilisateur(user_id, user_login):
    """Supprime un utilisateur (sauf admin connecte)."""
    conn = auth.get_connexion()
    if conn is None:
        return False, "MySQL non accessible"

    curseur = conn.cursor()
    try:
        curseur.execute("DELETE FROM utilisateurs WHERE id = %s", (user_id,))
        conn.commit()
        return True, f"Utilisateur '{user_login}' supprimé."
    except Error as e:
        return False, f"Erreur : {e}"
    finally:
        curseur.close()
        conn.close()


def changer_role(user_id, nouveau_role):
    """Change le role d'un utilisateur."""
    conn = auth.get_connexion()
    if conn is None:
        return False, "MySQL non accessible"

    curseur = conn.cursor()
    try:
        curseur.execute(
            "UPDATE utilisateurs SET role = %s WHERE id = %s",
            (nouveau_role, user_id)
        )
        conn.commit()
        return True, f"Rôle changé en '{nouveau_role}'."
    except Error as e:
        return False, f"Erreur : {e}"
    finally:
        curseur.close()
        conn.close()


def reinitialiser_mdp(user_id, nouveau_mdp):
    """Reinitialise le mot de passe d'un utilisateur."""
    conn = auth.get_connexion()
    if conn is None:
        return False, "MySQL non accessible"

    curseur = conn.cursor()
    try:
        hash_ = bcrypt.hashpw(
            nouveau_mdp.encode("utf-8"),
            bcrypt.gensalt(rounds=12)
        ).decode("utf-8")

        curseur.execute(
            "UPDATE utilisateurs SET mot_de_passe = %s WHERE id = %s",
            (hash_, user_id)
        )
        conn.commit()
        return True, "Mot de passe réinitialisé."
    except Error as e:
        return False, f"Erreur : {e}"
    finally:
        curseur.close()
        conn.close()


# ============================================================
# RECUPERER L'UTILISATEUR CONNECTE
# ============================================================
current_user = auth.get_user()

# ============================================================
# SECTION 1 : LISTE DES UTILISATEURS
# ============================================================
st.subheader("📋 Utilisateurs existants")

users = lister_utilisateurs()

if not users:
    st.warning("Aucun utilisateur trouvé.")
else:
    st.caption(f"**{len(users)}** utilisateur(s) dans la base")

    for u in users:
        col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 3, 2])

        with col1:
            badge = "👑" if u["role"] == "admin" else "👤"
            st.write(f"{badge} **{u['login']}**")

        with col2:
            st.write(f"Rôle : **{u['role']}**")

        with col3:
            st.caption(f"ID : {u['id']}")

        with col4:
            st.caption(f"Créé le {u['date_creation']}")

        with col5:
            # Ne pas permettre de supprimer son propre compte
            if u["id"] == current_user["id"]:
                st.caption("(vous)")
            else:
                if st.button("🗑️", key=f"del_{u['id']}", help="Supprimer"):
                    ok, msg = supprimer_utilisateur(u["id"], u["login"])
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

        st.markdown("---")

# ============================================================
# SECTION 2 : CREER UN UTILISATEUR
# ============================================================
st.subheader("➕ Créer un nouvel utilisateur")

with st.form("form_create_user"):
    col1, col2 = st.columns(2)

    with col1:
        nouveau_login = st.text_input(
            "👤 Login",
            placeholder="Ex: marie",
            key="new_user_login"
        )

        nouveau_role = st.selectbox(
            "👑 Rôle",
            ["viewer", "admin"],
            key="new_user_role"
        )

    with col2:
        nouveau_mdp = st.text_input(
            "🔑 Mot de passe",
            type="password",
            placeholder="Min 8 caractères",
            key="new_user_pwd"
        )

        confirmation = st.text_input(
            "✅ Confirmation",
            type="password",
            key="new_user_pwd_confirm"
        )

    submit = st.form_submit_button(
        "Créer l'utilisateur",
        use_container_width=True,
        type="primary"
    )

    if submit:
        if not nouveau_login or not nouveau_mdp or not confirmation:
            st.error("⚠️ Veuillez remplir tous les champs.")
        elif len(nouveau_login) < 3:
            st.error("⚠️ Le login doit contenir au moins 3 caractères.")
        elif len(nouveau_mdp) < 8:
            st.error("⚠️ Le mot de passe doit contenir au moins 8 caractères.")
        elif nouveau_mdp != confirmation:
            st.error("⚠️ Les mots de passe ne correspondent pas.")
        else:
            ok, msg = creer_utilisateur(nouveau_login, nouveau_mdp, nouveau_role)
            if ok:
                st.success(f"✅ {msg}")
                st.rerun()
            else:
                st.error(f"❌ {msg}")

st.markdown("---")

# ============================================================
# SECTION 3 : ACTIONS AVANCEES
# ============================================================
st.subheader("🔧 Actions avancées")

with st.expander("🔄 Changer le rôle d'un utilisateur"):
    user_a_modifier = st.selectbox(
        "Utilisateur",
        [u["login"] for u in users if u["id"] != current_user["id"]],
        key="role_user_select"
    )

    nouveau_role = st.selectbox(
        "Nouveau rôle",
        ["viewer", "admin"],
        key="role_nouveau"
    )

    if st.button("Appliquer le changement de rôle", key="btn_role_change"):
        # Trouver l'id
        user_target = next((u for u in users if u["login"] == user_a_modifier), None)
        if user_target:
            ok, msg = changer_role(user_target["id"], nouveau_role)
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

with st.expander("🔑 Réinitialiser un mot de passe"):
    user_mdp = st.selectbox(
        "Utilisateur",
        [u["login"] for u in users],
        key="mdp_user_select"
    )

    nouveau_mdp_admin = st.text_input(
        "Nouveau mot de passe",
        type="password",
        key="mdp_admin_new"
    )

    if st.button("Réinitialiser le mot de passe", key="btn_mdp_reset"):
        if len(nouveau_mdp_admin) < 8:
            st.error("⚠️ Le mot de passe doit contenir au moins 8 caractères.")
        else:
            user_target = next((u for u in users if u["login"] == user_mdp), None)
            if user_target:
                ok, msg = reinitialiser_mdp(user_target["id"], nouveau_mdp_admin)
                if ok:
                    st.success(f"✅ {msg} (utilisateur : {user_mdp})")
                else:
                    st.error(msg)

st.markdown("---")
st.caption(f"Page Utilisateurs — Version 0.1 | Connecté en tant que {current_user['login']}")
style.footer()