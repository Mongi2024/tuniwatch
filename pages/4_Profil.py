"""
Page Profil - Changement de mot de passe
Etape D - Session 6
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
    page_title="Profil - Monitoring",
    page_icon="🔑",
    layout="wide"
)

# Protection
auth.require_login()

# ============================================================
# TITRE
# ============================================================
st.title("🔑 Mon Profil")

user = auth.get_user()

st.markdown(f"### Connecté en tant que **{user['login']}**")
st.caption(f"Rôle : **{user['role'].capitalize()}**")

st.markdown("---")

# ============================================================
# SECTION 1 : Informations personnelles
# ============================================================
st.subheader("👤 Informations")

col1, col2, col3 = st.columns(3)
col1.metric("Login", user['login'])
col2.metric("Rôle", user['role'].capitalize())
col3.metric("ID", user['id'])

st.markdown("---")

# ============================================================
# SECTION 2 : Changement de mot de passe
# ============================================================
st.subheader("🔐 Changer mon mot de passe")
st.write("Pour des raisons de sécurité, vous devez saisir votre mot de passe actuel.")

with st.form("form_changement_mdp"):
    ancien_mdp = st.text_input(
        "🔑 Mot de passe actuel",
        type="password",
        key="profil_ancien"
    )

    nouveau_mdp = st.text_input(
        "🆕 Nouveau mot de passe",
        type="password",
        key="profil_nouveau"
    )

    confirmation = st.text_input(
        "✅ Confirmation du nouveau mot de passe",
        type="password",
        key="profil_confirm"
    )

    submit = st.form_submit_button(
        "Changer le mot de passe",
        use_container_width=True,
        type="primary"
    )

    if submit:
        # Verifications
        if not ancien_mdp or not nouveau_mdp or not confirmation:
            st.error("⚠️ Veuillez remplir tous les champs.")
        elif len(nouveau_mdp) < 8:
            st.error("⚠️ Le nouveau mot de passe doit contenir au moins 8 caractères.")
        elif nouveau_mdp != confirmation:
            st.error("⚠️ Les deux mots de passe ne correspondent pas.")
        elif ancien_mdp == nouveau_mdp:
            st.error("⚠️ Le nouveau mot de passe doit être différent de l'ancien.")
        else:
            # Verifier l'ancien mot de passe
            with st.spinner("Vérification..."):
                if not auth.verifier_identifiants(user['login'], ancien_mdp):
                    st.error("❌ Le mot de passe actuel est incorrect.")
                else:
                    # Changer le mot de passe
                    try:
                        conn = mysql.connector.connect(**auth.DB_CONFIG)
                        curseur = conn.cursor()

                        nouveau_hash = bcrypt.hashpw(
                            nouveau_mdp.encode("utf-8"),
                            bcrypt.gensalt(rounds=12)
                        ).decode("utf-8")

                        curseur.execute(
                            "UPDATE utilisateurs SET mot_de_passe = %s WHERE id = %s",
                            (nouveau_hash, user['id'])
                        )
                        conn.commit()
                        curseur.close()
                        conn.close()

                        st.success("✅ Mot de passe changé avec succès !")
                        st.info("💡 Utilisez votre nouveau mot de passe à la prochaine connexion.")

                    except Error as e:
                        st.error(f"❌ Erreur MySQL : {e}")

st.markdown("---")

# ============================================================
# SECTION 3 : Déconnexion
# ============================================================
st.subheader("🚪 Déconnexion")
st.write("Quitter votre session actuelle.")

if st.button("Se déconnecter", use_container_width=False, type="secondary", key="profil_logout"):
    auth.deconnecter()
    st.rerun()

st.markdown("---")
st.caption("Page Profil — Version 0.1")
style.footer()