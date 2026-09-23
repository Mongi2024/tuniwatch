"""
Page Profil - Changement de mot de passe
Version 2.0 - Connectée à PostgreSQL
"""

import streamlit as st
import sys
import os
import bcrypt

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import auth
import style
from db_universal import get_connexion

style.appliquer_style()

st.set_page_config(
    page_title="Profil - TuniWatch",
    page_icon="🔑",
    layout="wide"
)

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
# FONCTION : CHANGER LE MOT DE PASSE
# ============================================================
def changer_mot_de_passe(user_id, ancien_mdp, nouveau_mdp):
    """Change le mot de passe d'un utilisateur."""
    conn = get_connexion()
    if conn is None:
        return False, "Connexion impossible"

    curseur = conn.cursor(dictionary=True)
    try:
        # Récupérer le hash actuel
        curseur.execute(
            "SELECT mot_de_passe FROM utilisateurs WHERE id = %s",
            (user_id,)
        )
        row = curseur.fetchone()
        if not row:
            return False, "Utilisateur non trouvé."

        hash_actuel = row["mot_de_passe"]

        # Vérifier l'ancien mot de passe
        if not bcrypt.checkpw(ancien_mdp.encode("utf-8"), hash_actuel.encode("utf-8")):
            return False, "Le mot de passe actuel est incorrect."

        # Générer le nouveau hash
        nouveau_hash = bcrypt.hashpw(
            nouveau_mdp.encode("utf-8"),
            bcrypt.gensalt(rounds=12)
        ).decode("utf-8")

        # Mettre à jour
        curseur.execute(
            "UPDATE utilisateurs SET mot_de_passe = %s WHERE id = %s",
            (nouveau_hash, user_id)
        )
        conn.commit()
        return True, "Mot de passe changé avec succès."

    except Exception as e:
        return False, f"Erreur : {e}"
    finally:
        curseur.close()
        conn.close()


# ============================================================
# SECTION 1 : Informations
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
        if not ancien_mdp or not nouveau_mdp or not confirmation:
            st.error("⚠️ Veuillez remplir tous les champs.")
        elif len(nouveau_mdp) < 8:
            st.error("⚠️ Le nouveau mot de passe doit contenir au moins 8 caractères.")
        elif nouveau_mdp != confirmation:
            st.error("⚠️ Les deux mots de passe ne correspondent pas.")
        elif ancien_mdp == nouveau_mdp:
            st.error("⚠️ Le nouveau mot de passe doit être différent de l'ancien.")
        else:
            with st.spinner("Vérification..."):
                ok, msg = changer_mot_de_passe(user['id'], ancien_mdp, nouveau_mdp)
            if ok:
                st.success(f"✅ {msg}")
                st.info("💡 Utilisez votre nouveau mot de passe à la prochaine connexion.")
            else:
                st.error(f"❌ {msg}")

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
st.caption("Page Profil — Version 2.0")
style.footer()