"""
Page Accueil - Vitrine TuniWatch
Version 2.0 - Dashboard de monitoring
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os
from datetime import datetime

# Ajout du dossier parent
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import auth
import style
import cockpit_stats

# Configuration
st.set_page_config(
    page_title="Accueil - TuniWatch",
    page_icon="🇹🇳",
    layout="wide"
)

# Style
style.appliquer_style()

# Protection
auth.require_login()

# ============================================================
# COULEURS
# ============================================================
COULEURS_SENTIMENT = {
    "positif": "#27ae60",
    "neutre": "#f39c12",
    "negatif": "#e74c3c"
}

COULEURS_THEMES = {
    "violence_femmes": "#e74c3c",
    "discours_haine": "#c0392b",
    "presence_femmes": "#9b59b6",
    "presence_handicapes": "#3498db",
    "presence_jeunes": "#f39c12",
    "equilibre_politique": "#2c3e50",
    "equilibre_regional": "#27ae60"
}

EMOJIS_THEMES = {
    "violence_femmes": "⚖️",
    "discours_haine": "🚨",
    "presence_femmes": "👩",
    "presence_handicapes": "👥",
    "presence_jeunes": "🧑",
    "equilibre_politique": "🏛️",
    "equilibre_regional": "🗺️"
}

# ============================================================
# EN-TETE
# ============================================================
style.page_header(
    titre="TuniWatch",
    icone="🇹🇳",
    description="Observatoire des médias tunisiens — Suivi en temps réel des médias et réseaux sociaux",
    badge="EN DIRECT"
)

# ============================================================
# CHARGEMENT DES DONNEES
# ============================================================
try:
    with st.spinner("Chargement des données..."):
        kpis = cockpit_stats.kpis_globaux()
        sentiment = cockpit_stats.stats_sentiment()
        erreur_chargement = False
except Exception as e:
    erreur_chargement = True
    erreur_msg = str(e)

if erreur_chargement:
    st.error(f"⚠️ Impossible de charger les données : {erreur_msg}")
    st.stop()

# ============================================================
# SECTION 1 : KPIs PRINCIPAUX (VRAIS CHIFFRES)
# ============================================================
style.section_title("📊", "Vue globale", "Chiffres clés du monitoring en temps réel")

col1, col2, col3, col4 = st.columns(4)

with col1:
    trend = f"+{kpis['total_articles'] - 411}" if kpis['total_articles'] > 411 else None
    style.kpi_card(
        "📰", "Articles collectés",
        f"{kpis['total_articles']:,}".replace(",", " "),
        tendance=trend,
        couleur="#e70013"
    )

with col2:
    style.kpi_card(
        "📡", "Sources actives",
        kpis["total_sources"],
        couleur="#3498db"
    )

with col3:
    style.kpi_card(
        "🎯", "Analyses thèmes",
        kpis["total_analyses_themes"],
        couleur="#f39c12"
    )

with col4:
    style.kpi_card(
        "💭", "Analyses sentiments",
        kpis["total_analyses_sentiment"],
        couleur="#27ae60"
    )

# ============================================================
# SECTION 2 : COURBE D'EVOLUTION
# ============================================================
style.section_title("📈", "Évolution des mentions", "30 derniers jours")

evolution = cockpit_stats.evolution_mentions(30)

if evolution:
    df_evol = pd.DataFrame(evolution)

    fig_evol = go.Figure()
    fig_evol.add_trace(go.Scatter(
        x=df_evol["jour"],
        y=df_evol["nb"],
        mode="lines",
        line=dict(color="#e70013", width=3, shape="spline"),
        fill="tozeroy",
        fillcolor="rgba(231, 0, 19, 0.08)",
        hovertemplate="<b>%{x}</b><br>%{y} articles<extra></extra>"
    ))
    fig_evol.update_layout(
        height=320,
        margin=dict(l=10, r=10, t=20, b=10),
        showlegend=False,
        hovermode="x unified",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, showline=True, linecolor="#e0e0e0"),
        yaxis=dict(showgrid=True, gridcolor="#f0f0f0", showline=False),
        font=dict(family="Inter, sans-serif", color="#1a1a1a"),
    )
    st.plotly_chart(fig_evol, use_container_width=True)
else:
    st.info("Aucune donnée d'évolution disponible.")

# ============================================================
# SECTION 3 : SENTIMENT + TOP SOURCES
# ============================================================
style.section_title("📊", "Répartition", "Sentiments et sources principales")

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("##### 😊 Sentiment global")

    total_sent = (sentiment.get("positifs", 0) or 0) + (sentiment.get("neutres", 0) or 0) + (sentiment.get("negatifs", 0) or 0)

    if total_sent > 0:
        fig_sent = go.Figure(data=[go.Pie(
            labels=["Positifs", "Neutres", "Négatifs"],
            values=[
                sentiment.get("positifs", 0) or 0,
                sentiment.get("neutres", 0) or 0,
                sentiment.get("negatifs", 0) or 0
            ],
            hole=0.55,
            marker=dict(colors=["#27ae60", "#f39c12", "#e74c3c"]),
            textinfo="percent",
            textposition="outside",
            hovertemplate="<b>%{label}</b><br>%{value} (%{percent})<extra></extra>"
        )])
        fig_sent.update_layout(
            showlegend=True,
            height=320,
            margin=dict(l=10, r=10, t=10, b=10),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif", color="#1a1a1a"),
            legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_sent, use_container_width=True)
    else:
        st.info("Aucune donnée de sentiment.")

with col2:
    st.markdown("##### 📡 Top sources")

    top_src = cockpit_stats.top_sources(8)

    if top_src:
        df_src = pd.DataFrame(top_src)
        df_src["source_court"] = df_src["source"].apply(lambda s: s[:25])

        fig_src = px.bar(
            df_src.sort_values("nb_articles"),
            x="nb_articles",
            y="source_court",
            orientation="h",
            text="nb_articles",
            color="nb_articles",
            color_continuous_scale="Reds"
        )
        fig_src.update_traces(textposition="outside")
        fig_src.update_layout(
            height=320,
            xaxis_title="",
            yaxis_title="",
            showlegend=False,
            coloraxis_showscale=False,
            margin=dict(l=10, r=10, t=10, b=10),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif", color="#1a1a1a"),
        )
        st.plotly_chart(fig_src, use_container_width=True)
    else:
        st.info("Aucune source.")

# ============================================================
# SECTION 4 : THEMES
# ============================================================
style.section_title("🎯", "Répartition par thème", "Focus éditorial du monitoring")

stats_themes = cockpit_stats.stats_themes_rapide()

if stats_themes:
    df_themes = pd.DataFrame(stats_themes)
    df_themes["emoji"] = df_themes["theme"].apply(lambda t: EMOJIS_THEMES.get(t, "🌐"))
    df_themes["label"] = df_themes["emoji"] + " " + df_themes["theme"]

    col1, col2 = st.columns([1, 1])

    with col1:
        fig_pie = px.pie(
            df_themes,
            values="nb_articles",
            names="theme",
            color="theme",
            color_discrete_map=COULEURS_THEMES,
            hole=0.55
        )
        fig_pie.update_traces(
            textposition="outside",
            textinfo="percent",
            hovertemplate="<b>%{label}</b><br>%{value} articles<br>%{percent}<extra></extra>"
        )
        fig_pie.update_layout(
            showlegend=True,
            height=340,
            margin=dict(l=10, r=10, t=10, b=10),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif", color="#1a1a1a"),
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        fig_bar = px.bar(
            df_themes.sort_values("nb_articles"),
            x="nb_articles",
            y="label",
            orientation="h",
            text="nb_articles",
            color="nb_articles",
            color_continuous_scale="Reds"
        )
        fig_bar.update_traces(textposition="outside")
        fig_bar.update_layout(
            height=340,
            xaxis_title="Articles",
            yaxis_title="",
            showlegend=False,
            coloraxis_showscale=False,
            margin=dict(l=10, r=10, t=10, b=10),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif", color="#1a1a1a"),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

# ============================================================
# SECTION 5 : DERNIERS ARTICLES
# ============================================================
style.section_title("🆕", "Derniers articles", "Dernières publications collectées")

derniers = cockpit_stats.derniers_articles(5)

if derniers:
    col1, col2 = st.columns([1, 1])
    for i, art in enumerate(derniers):
        titre_court = (art['titre'][:85] + "...") if len(art['titre']) > 85 else art['titre']
        with (col1 if i % 2 == 0 else col2):
            style.article_card(
                titre=titre_court,
                source=art["source"],
                url=art["url"]
            )
else:
    st.info("Aucun article.")

# ============================================================
# SECTION 6 : A PROPOS (repliable)
# ============================================================
with st.expander("ℹ️ À propos de TuniWatch — Méthodologie et éthique"):
    st.markdown(
        """
        ### 🎯 Notre mission

        **TuniWatch** est un observatoire automatique qui analyse en continu 
        les contenus des médias tunisiens (presse, radios, TV) et des réseaux sociaux.

        ### 🔬 Méthodologie

        1. **Collecte automatique** — Articles récupérés via RSS (presse, radios, TV)
        2. **Analyse multilingue** — Français, Arabe standard, Arabe tunisien, Arabizi
        3. **Classification** — 456 mots-clés répartis sur 7 thèmes
        4. **Visualisation** — Statistiques exploitables et comparaisons

        ### ⚠️ Limites

        - Les analyses reflètent **uniquement** les sources collectées
        - Les scores sont **indicatifs** et non des vérités absolues
        - La détection automatique peut générer des **faux positifs**

        ### ⚖️ Éthique

        - **Aucune donnée personnelle** n'est collectée
        - Tous les articles sont **publics**
        - L'observatoire **respecte les CGU** des sources
        - Les résultats sont **transparents** et **vérifiables**

        ### 👤 Contact

        **Développé par** : Khadraoui Mongi — **Année** : 2026 — **Version** : 1.0
        """
    )

# Footer
style.footer()