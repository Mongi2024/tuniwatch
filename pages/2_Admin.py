"""
Page Admin - Gestion des sources et parametres
"""

import streamlit as st

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import auth
import style
style.appliquer_style()
# Protection admin (bloque si pas admin)
auth.require_super_admin()
# Configuration
st.set_page_config(
    page_title="Admin - Monitoring",
    page_icon="⚙️",
    layout="wide"
)

# Titre
st.title("⚙️ Espace Administrateur")
st.write("Gestion des sources, des alertes et des paramètres.")

st.markdown("---")

# --- Section 1 : Sources suivies ---
st.subheader("🌐 Sources suivies")

sources = [
    {"nom": "Twitter / X", "statut": "🟢 Actif", "mentions_jour": 342},
    {"nom": "LinkedIn", "statut": "🟢 Actif", "mentions_jour": 187},
    {"nom": "Instagram", "statut": "🟢 Actif", "mentions_jour": 96},
    {"nom": "Facebook", "statut": "🟡 En pause", "mentions_jour": 0},
    {"nom": "TikTok", "statut": "🔴 Erreur", "mentions_jour": 0}
]

for source in sources:
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.write(f"**{source['nom']}**")
    with col2:
        st.write(source["statut"])
    with col3:
        st.write(f"{source['mentions_jour']} mentions/jour")

st.markdown("---")

# --- Section 2 : Ajouter une source (interface) ---
st.subheader("➕ Ajouter une nouvelle source")

with st.form("form_ajout_source"):
    nom_source = st.text_input("Nom de la source", placeholder="Ex: Reddit")
    api_key = st.text_input("Clé API", type="password")
    actif = st.checkbox("Activer immédiatement", value=True)
    
    submitted = st.form_submit_button("Ajouter la source")
    
    if submitted:
        if nom_source:
            st.success(f"✅ Source **{nom_source}** ajoutée ! (simulation)")
        else:
            st.error("❌ Veuillez saisir un nom de source.")

st.markdown("---")

# --- Section 3 : Parametres d'alerte ---
st.subheader("🚨 Paramètres des alertes")

col1, col2 = st.columns(2)

with col1:
    seuil_negatif = st.slider(
        "Seuil de sentiment négatif",
        min_value=-1.0,
        max_value=0.0,
        value=-0.3,
        step=0.05
    )
    st.caption(f"Une alerte est déclenchée si le sentiment est < {seuil_negatif}")

with col2:
    seuil_mentions = st.number_input(
        "Nombre de mentions pour alerte",
        min_value=100,
        max_value=10000,
        value=1000,
        step=100
    )
    st.caption(f"Alerte si plus de {seuil_mentions} mentions en 1h")

st.markdown("---")

# --- Section 4 : Actions systeme ---
st.subheader("🛠️ Actions système")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔄 Rafraîchir les données"):
        st.success("Données rafraîchies ! (simulation)")

with col2:
    if st.button("📥 Exporter en CSV"):
        st.info("Export CSV en préparation... (simulation)")

with col3:
    if st.button("🗑️ Vider le cache"):
        st.warning("Cache vidé ! (simulation)")

st.markdown("---")
st.caption("Page Admin — Version 0.1")
style.footer()