"""
Page Analyse - Version compacte 2x3
Etape A3 Session 2 - Optimisee pour affichage sans scroll
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import numpy as np

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import auth
import style
style.appliquer_style()
# Protection
auth.require_login()

# Configuration de la page
st.set_page_config(
    page_title="Analyse - Monitoring",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Page Analyse")
st.caption("Vue compacte — tous les graphiques sur un seul écran")
st.markdown("---")

# ============================================================
# LIGNE 1 : Evolution (gauche) + Camembert (droite)
# ============================================================
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Évolution des mentions")
    donnees = pd.DataFrame({
        "Date": pd.date_range("2026-08-15", periods=30),
        "Twitter": [120, 145, 132, 167, 189, 210, 198, 220, 240, 265,
                    250, 270, 290, 310, 285, 300, 320, 340, 360, 350,
                    370, 390, 410, 395, 420, 440, 460, 480, 470, 500],
        "LinkedIn": [80, 85, 92, 88, 95, 102, 98, 105, 110, 115,
                     112, 120, 125, 130, 128, 135, 140, 145, 148, 145,
                     150, 155, 160, 158, 165, 170, 175, 172, 180, 185]
    })
    st.line_chart(donnees.set_index("Date"), height=280)

with col2:
    st.subheader("🥧 Répartition des sentiments")
    sentiments_df = pd.DataFrame({
        "Sentiment": ["Positif", "Neutre", "Négatif"],
        "Nombre": [850, 450, 242]
    })

    fig_camembert = px.pie(
        sentiments_df,
        values="Nombre",
        names="Sentiment",
        color="Sentiment",
        color_discrete_map={
            "Positif": "#2ecc71",
            "Neutre": "#f1c40f",
            "Négatif": "#e74c3c"
        },
        hole=0.4
    )
    fig_camembert.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>%{value} mentions<br>%{percent}<extra></extra>"
    )
    fig_camembert.update_layout(
        showlegend=False,
        height=280,
        margin=dict(l=10, r=10, t=10, b=10)
    )
    st.plotly_chart(fig_camembert, use_container_width=True)

# ============================================================
# LIGNE 2 : Bar chart (gauche) + WordCloud (droite)
# ============================================================
col1, col2 = st.columns(2)

mots_cles = pd.DataFrame({
    "Mot-clé": ["intelligence artificielle", "python", "monitoring",
                "données", "analyse", "réseaux sociaux", "dashboard",
                "temps réel", "API", "automatisation"],
    "Occurrences": [342, 298, 251, 220, 198, 187, 165, 142, 128, 112]
})

with col1:
    st.subheader("📊 Top 10 mots-clés")
    fig_barres = px.bar(
        mots_cles,
        x="Occurrences",
        y="Mot-clé",
        orientation="h",
        color="Occurrences",
        color_continuous_scale="Blues"
    )
    fig_barres.update_layout(
        height=280,
        yaxis=dict(autorange="reversed"),
        showlegend=False,
        coloraxis_showscale=False,
        margin=dict(l=10, r=10, t=10, b=10)
    )
    st.plotly_chart(fig_barres, use_container_width=True)

with col2:
    st.subheader("☁️ Nuage de mots-clés")
    frequences = dict(zip(mots_cles["Mot-clé"], mots_cles["Occurrences"]))
    wordcloud = WordCloud(
        width=800,
        height=300,
        background_color="white",
        colormap="viridis",
        prefer_horizontal=0.7,
        min_font_size=10,
        max_font_size=100
    ).generate_from_frequencies(frequences)

    fig_wc, ax = plt.subplots(figsize=(8, 3))
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")
    plt.tight_layout(pad=0)
    st.pyplot(fig_wc)

# ============================================================
# LIGNE 3 : Heatmap (large) + Résumé (petit)
# ============================================================
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🔥 Heatmap horaire")
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    heures = [f"{h:02d}h" for h in range(24)]

    base = np.array([
        [5, 3, 2, 1, 1, 2, 8, 25, 45, 62, 58, 50,
         42, 48, 65, 72, 68, 55, 40, 30, 22, 15, 10, 7]
    ])
    heatmap_data = np.vstack([base * (0.7 + 0.1 * i) for i in range(7)]).astype(int)

    fig_heatmap = go.Figure(data=go.Heatmap(
        z=heatmap_data,
        x=heures,
        y=jours,
        colorscale="YlOrRd",
        hovertemplate="<b>%{y} à %{x}</b><br>%{z} mentions<extra></extra>"
    ))
    fig_heatmap.update_layout(
        height=280,
        xaxis_title="Heure",
        yaxis_title="",
        margin=dict(l=10, r=10, t=10, b=10)
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

with col2:
    st.subheader("📋 Résumé")
    st.metric("Total mentions", "1 542", "+12%")
    st.metric("Positif", "55%", "+3%")
    st.metric("Négatif", "16%", "-2%")
    st.caption("💡 Pics d'activité : 9h et 15h")
    st.caption("📅 Meilleur jour : Mercredi")

st.markdown("---")
st.caption("Page Analyse — Version 0.3 (compacte 2x3)")
style.footer()