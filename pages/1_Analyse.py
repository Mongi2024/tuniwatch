"""
Page Analyse - Exploration des données TuniWatch
Version 2.0 - Données réelles + visuel premium
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
    page_title="Analyse - TuniWatch",
    page_icon="📊",
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
    titre="Analyse",
    icone="📊",
    description="Exploration détaillée des données collectées — Graphiques et analyses avancées",
    badge="DONNÉES RÉELLES"
)

# ============================================================
# CHARGEMENT DES DONNEES
# ============================================================
try:
    with st.spinner("Chargement des données..."):
        kpis = cockpit_stats.kpis_globaux()
        sentiment = cockpit_stats.stats_sentiment()
    donnees_ok = True
except Exception as e:
    donnees_ok = False
    erreur_msg = str(e)

if not donnees_ok:
    st.error(f"⚠️ Impossible de charger les données : {erreur_msg}")
    st.stop()

# ============================================================
# SECTION 1 : KPIs CONTEXTUELS
# ============================================================
style.section_title("📊", "Contexte", "Chiffres clés pour situer l'analyse")

col1, col2, col3, col4 = st.columns(4)

with col1:
    style.kpi_card(
        "📰", "Articles analysés",
        f"{kpis['total_articles']:,}".replace(",", " "),
        couleur="#e70013"
    )

with col2:
    style.kpi_card(
        "🎯", "Thèmes détectés",
        kpis["themes_actifs"],
        couleur="#f39c12"
    )

with col3:
    style.kpi_card(
        "💭", "Analyses sentiments",
        kpis["total_analyses_sentiment"],
        couleur="#27ae60"
    )

with col4:
    score = kpis.get("score_moyen", 0)
    style.kpi_card(
        "⭐", "Score moyen",
        f"{score:.2f}" if score else "0.00",
        couleur="#2c3e50"
    )

# ============================================================
# SECTION 2 : EVOLUTION + SENTIMENT GLOBAL
# ============================================================
style.section_title("📈", "Évolution et sentiment", "Tendances sur 30 jours")

col1, col2 = st.columns([2, 1])

# --- Courbe d'évolution ---
with col1:
    st.markdown("##### 📈 Évolution des mentions")

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

# --- Donut sentiment ---
with col2:
    st.markdown("##### 🥧 Sentiment global")

    total_sent = (
        (sentiment.get("positifs", 0) or 0)
        + (sentiment.get("neutres", 0) or 0)
        + (sentiment.get("negatifs", 0) or 0)
    )

    if total_sent > 0:
        fig_sent = go.Figure(data=[go.Pie(
            labels=["Positifs", "Neutres", "Négatifs"],
            values=[
                sentiment.get("positifs", 0) or 0,
                sentiment.get("neutres", 0) or 0,
                sentiment.get("negatifs", 0) or 0
            ],
            hole=0.6,
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
            legend=dict(orientation="h", yanchor="bottom", y=-0.15,
                        xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_sent, use_container_width=True)
    else:
        st.info("Aucune donnée de sentiment.")

# ============================================================
# SECTION 3 : TOP SOURCES + REPARTITION THEMES
# ============================================================
style.section_title("📊", "Sources et thèmes", "Répartition des articles collectés")

col1, col2 = st.columns([1, 1])

# --- Top sources ---
with col1:
    st.markdown("##### 📡 Top sources")

    top_src = cockpit_stats.top_sources(8)

    if top_src:
        df_src = pd.DataFrame(top_src)
        df_src["source_court"] = df_src["source"].apply(lambda s: s[:28])

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
            height=340,
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

# --- Donut thèmes ---
with col2:
    st.markdown("##### 🎯 Répartition par thème")

    stats_themes = cockpit_stats.stats_themes_rapide()

    if stats_themes:
        df_themes = pd.DataFrame(stats_themes)
        df_themes["label"] = df_themes["theme"].apply(
            lambda t: f"{EMOJIS_THEMES.get(t, '🌐')} {t}"
        )

        fig_pie = px.pie(
            df_themes,
            values="nb_articles",
            names="label",
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
            legend=dict(orientation="h", yanchor="bottom", y=-0.2,
                        xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("Aucun thème détecté.")

# ============================================================
# SECTION 4 : SENTIMENT PAR SOURCE
# ============================================================
style.section_title("📊", "Sentiment par source", "Répartition des sentiments selon les médias")

sent_src = cockpit_stats.sentiment_par_source(8)

if sent_src:
    df_sent_src = pd.DataFrame(sent_src)
    df_sent_src["source_court"] = df_sent_src["source"].apply(lambda s: s[:20])

    fig_sent_src = px.bar(
        df_sent_src,
        x="source_court",
        y="nb",
        color="sentiment",
        color_discrete_map=COULEURS_SENTIMENT,
        barmode="stack",
        labels={"source_court": "Source", "nb": "Articles", "sentiment": "Sentiment"}
    )
    fig_sent_src.update_layout(
        height=380,
        xaxis_tickangle=-30,
        xaxis_title="",
        yaxis_title="Articles",
        margin=dict(l=10, r=10, t=10, b=80),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#1a1a1a"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                    xanchor="right", x=1)
    )
    st.plotly_chart(fig_sent_src, use_container_width=True)
else:
    st.info("Aucune donnée de sentiment par source.")

# ============================================================
# SECTION 5 : TOP ARTICLES PERTINENTS
# ============================================================
style.section_title("🏆", "Top articles pertinents", "Articles avec les scores les plus élevés")

top_arts = cockpit_stats.top_articles_pertinents(6)

if top_arts:
    col1, col2 = st.columns(2)
    for i, art in enumerate(top_arts):
        emoji = EMOJIS_THEMES.get(art["theme"], "🌐")
        titre_complet = art['titre'] if art['titre'] else ""
        titre_court = titre_complet[:90] + ("..." if len(titre_complet) > 90 else "")
        with (col1 if i % 2 == 0 else col2):
            style.article_card(
                titre=titre_court,
                source=art["source"],
                url=art["url"],
                score=art["score"],
                theme=art["theme"],
                emoji_theme=emoji
            )
else:
    st.info("Aucun article pertinent.")

# ============================================================
# FOOTER
# ============================================================
style.footer()