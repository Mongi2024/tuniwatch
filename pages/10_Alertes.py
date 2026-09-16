"""
Page Alertes - Detection et gestion des anomalies
Etape H - Session 1
"""

import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime

# Ajout du dossier parent
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import auth
import style
import alert_detector

# Configuration
st.set_page_config(
    page_title="Alertes - TuniWatch",
    page_icon="🚨",
    layout="wide"
)

# Style
style.appliquer_style()

# Protection
auth.require_login()

# ============================================================
# COULEURS DES NIVEAUX
# ============================================================
COULEURS_NIVEAU = {
    "critique": "#e74c3c",
    "attention": "#f39c12",
    "info": "#3498db"
}

EMOJIS_NIVEAU = {
    "critique": "🚨",
    "attention": "⚠️",
    "info": "ℹ️"
}

# ============================================================
# EN-TETE
# ============================================================
col1, col2 = st.columns([3, 1])

with col1:
    st.title("🚨 Centre d'alertes")
    st.caption("Détection automatique des anomalies médiatiques")

with col2:
    if st.button("🔄 Détecter maintenant", use_container_width=True, key="btn_detect"):
        with st.spinner("Détection en cours..."):
            resultat = alert_detector.lancer_detection_complete()
            if resultat["sauvees"] > 0:
                st.success(f"✅ {resultat['sauvees']} nouvelle(s) alerte(s) !")
                st.rerun()
            else:
                st.info(f"Aucune nouvelle alerte (sur {resultat['detectees']} détectées).")

st.markdown("---")

# ============================================================
# STATISTIQUES
# ============================================================
stats = alert_detector.stats_alertes()

col1, col2, col3, col4 = st.columns(4)

col1.metric("📊 Total alertes", stats.get("total", 0))
col2.metric("🔔 Non lues", stats.get("non_lues", 0))
col3.metric("🚨 Critiques", stats.get("critiques", 0))
col4.metric("⚠️ Attention", stats.get("attention", 0))

st.markdown("---")

# ============================================================
# FILTRES
# ============================================================
st.subheader("🎛️ Filtres")

col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    filtre_lues = st.selectbox(
        "Statut",
        ["Toutes", "Non lues", "Lues"],
        key="alertes_statut"
    )

with col2:
    filtre_niveau = st.selectbox(
        "Niveau",
        ["Tous", "critique", "attention", "info"],
        key="alertes_niveau"
    )

with col3:
    if st.button("🗑️ Supprimer TOUTES les alertes", key="btn_delete_all"):
        if alert_detector.supprimer_toutes_alertes():
            st.success("Toutes les alertes supprimées.")
            st.rerun()

# Application des filtres
lues_filter = None
if filtre_lues == "Non lues":
    lues_filter = False
elif filtre_lues == "Lues":
    lues_filter = True

niveau_filter = None if filtre_niveau == "Tous" else filtre_niveau

alertes = alert_detector.lister_alertes(
    lues=lues_filter,
    niveau=niveau_filter,
    limite=200
)

st.caption(f"**{len(alertes)}** alerte(s) affichée(s)")

st.markdown("---")

# ============================================================
# LISTE DES ALERTES
# ============================================================
st.subheader("📋 Liste des alertes")

if not alertes:
    st.info("Aucune alerte à afficher.")
else:
    for alerte in alertes:
        niveau = alerte.get("niveau", "info")
        couleur = COULEURS_NIVEAU.get(niveau, "#95a5a6")
        emoji = EMOJIS_NIVEAU.get(niveau, "ℹ️")
        lue = alerte.get("lue", 0)
        opacite = "0.5" if lue else "1"

        with st.container():
            col1, col2, col3 = st.columns([6, 1, 1])

            with col1:
                # Badge niveau + message
                statut = "✅ Lue" if lue else "🔵 Non lue"
                st.markdown(
                    f"""
                    <div style="border-left: 4px solid {couleur}; padding: 8px 12px; 
                                background: #f8f9fa; border-radius: 5px; opacity: {opacite};">
                        <div style="font-size: 0.75rem; color: #666;">
                            {emoji} <b>{niveau.upper()}</b> • {statut} • 
                            {alerte['date_creation']}
                        </div>
                        <div style="margin-top: 5px; font-size: 1rem;">
                            {alerte['message']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with col2:
                if lue:
                    if st.button("↩️ Non lue", key=f"unread_{alerte['id']}", use_container_width=True):
                        alert_detector.marquer_lue(alerte["id"], False)
                        st.rerun()
                else:
                    if st.button("✅ Lue", key=f"read_{alerte['id']}", use_container_width=True):
                        alert_detector.marquer_lue(alerte["id"], True)
                        st.rerun()

            with col3:
                if st.button("🗑️", key=f"del_{alerte['id']}", use_container_width=True, help="Supprimer"):
                    alert_detector.supprimer_alerte(alerte["id"])
                    st.rerun()

            # --- Articles lies a cette alerte ---
            with st.expander("📋 Voir les articles concernés"):
                articles_lies = alert_detector.get_articles_lies_alerte(alerte)

                if not articles_lies:
                    st.info("Aucun article lié trouvé.")
                else:
                    st.caption(f"**{len(articles_lies)}** article(s) lié(s) à cette alerte")

                    for i, art in enumerate(articles_lies, 1):
                        titre = art.get("titre", "Sans titre")
                        source = art.get("source", "")
                        url = art.get("url", "")
                        sentiment = art.get("sentiment")
                        score_s = art.get("score_sentiment")
                        score_t = art.get("score_theme")

                        info = f"📰 {source}"
                        if sentiment:
                            emoji_s = {"positif": "🟢", "neutre": "🟡", "negatif": "🔴"}.get(sentiment, "⚪")
                            info += f" • {emoji_s} {sentiment} ({score_s:+.2f})"
                        if score_t:
                            info += f" • Score thème : {score_t:.2f}"

                        if url:
                            st.markdown(f"**{i}.** [{titre[:120]}]({url})")
                        else:
                            st.markdown(f"**{i}.** {titre[:120]}")
                        st.caption(info)

                        if i < len(articles_lies):
                            st.markdown("")

            st.markdown("")

st.markdown("---")

# ============================================================
# INFORMATIONS SUR LES TYPES D'ALERTES
# ============================================================
st.subheader("ℹ️ Types d'alertes détectées")

with st.expander("📖 Comprendre les alertes"):
    st.markdown("""
    ### 🚨 Types d'alertes
    
    | Type | Niveau | Déclencheur |
    | :--- | :--- | :--- |
    | **Pic de mentions** | ⚠️ Attention | +200% d'articles sur un thème (3j vs 7j) |
    | **Sentiment négatif** | 🚨 Critique | Score moyen < -0.5 sur un thème |
    | **Baisse d'activité** | ⚠️ Attention | -50% d'articles sur un thème |
    | **Pic global** | 🚨 Critique | x3 d'articles en 1 jour |
    
    ### 🎯 Comment réagir
    
    - **🚨 Critique** : à examiner immédiatement
    - **⚠️ Attention** : à surveiller dans les 24h
    - **ℹ️ Info** : pour information
    """)

st.markdown("---")

# Footer
style.footer()