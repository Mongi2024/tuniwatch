# ============================================================
# TuniWatch - Dashboard Cockpit (Page d'accueil)
# Fichier : dashboard.py
# Version : 2.0 - Visuel premium
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os
from datetime import datetime

# Ajout du dossier au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Imports locaux
import auth
import style
import cockpit_stats

# ============================================================
# CONFIGURATION DE LA PAGE
# ============================================================
st.set_page_config(
    page_title="TuniWatch - Cockpit",
    page_icon="🇹🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# APPLICATION DU STYLE + SIDEBAR
# ============================================================
style.apply_style()

# Protection : connexion obligatoire
auth.require_login()

# ============================================================
# COULEURS
# ============================================================
COULEURS_SENTIMENT = {
    "positif": "#06D6A0",
    "neutre": "#FFD166",
    "negatif": "#EF476F"
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
# EN-TÊTE
# ============================================================
col1, col2 = st.columns([3, 1])

with col1:
    st.title("🏠 Cockpit TuniWatch")
    st.caption(f"Vue d'ensemble — {datetime.now().strftime('%A %d %B %Y à %H:%M')}")

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Actualiser", use_container_width=True, key="cockpit_refresh"):
        st.cache_data.clear()
        st.rerun()

st.markdown("---")

# ============================================================
# CHARGEMENT DES DONNÉES
# ============================================================
with st.spinner("Chargement des données..."):
    kpis = cockpit_stats.kpis_globaux()
    sentiment = cockpit_stats.stats_sentiment()

# ============================================================
# SECTION 1 : KPIs PRINCIPAUX
# ============================================================
st.markdown("## 📊 Vue globale")
st.caption("Chiffres clés du monitoring")
st.markdown("")

col1, col2, col3, col4 = st.columns(4)

with col1:
    trend = f"+{kpis['total_articles'] - 411}" if kpis['total_articles'] > 411 else None
    style.kpi_card(
        "📰",
        "Articles collectés",
        f"{kpis['total_articles']:,}".replace(",", " "),
        trend=trend,
        trend_type="positive"
    )

with col2:
    style.kpi_card(
        "📡",
        "Sources actives",
        str(kpis["total_sources"]),
        trend_type="neutral"
    )

with col3:
    style.kpi_card(
        "🎯",
        "Analyses thèmes",
        str(kpis["total_analyses_themes"]),
        trend_type="neutral"
    )

with col4:
    style.kpi_card(
        "💭",
        "Analyses sentiments",
        str(kpis["total_analyses_sentiment"]),
        trend_type="neutral"
    )

st.markdown("---")

# ============================================================
# SECTION 2 : SENTIMENT GLOBAL
# ============================================================
st.markdown("## 😊 Sentiment global")
st.caption("Répartition des analyses")
st.markdown("")

col1, col2, col3, col4 = st.columns(4)

total = (
    (sentiment.get("positifs", 0) or 0)
    + (sentiment.get("neutres", 0) or 0)
    + (sentiment.get("negatifs", 0) or 0)
)

with col1:
    pos = sentiment.get("positifs", 0) or 0
    pct = f"{pos / total * 100:.0f}%" if total > 0 else None
    style.kpi_card("🟢", "Positifs", str(pos), trend=pct, trend_type="positive")

with col2:
    neu = sentiment.get("neutres", 0) or 0
    pct = f"{neu / total * 100:.0f}%" if total > 0 else None
    style.kpi_card("🟡", "Neutres", str(neu), trend=pct, trend_type="neutral")

with col3:
    neg = sentiment.get("negatifs", 0) or 0
    pct = f"{neg / total * 100:.0f}%" if total > 0 else None
    style.kpi_card("🔴", "Négatifs", str(neg), trend=pct, trend_type="negative")

with col4:
    score = f"{kpis['score_moyen']:.2f}" if kpis.get('score_moyen') else "0.00"
    style.kpi_card("📊", "Score moyen", score, trend_type="neutral")

st.markdown("---")

# ============================================================
# SECTION 3 : ÉVOLUTION + TOP SOURCES
# ============================================================
st.markdown("## 📈 Tendances")
st.caption("Évolution et sources principales")
st.markdown("")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("##### 📈 Évolution des mentions (30 jours)")

    evolution = cockpit_stats.evolution_mentions(30)

    if evolution:
        df_evol = pd.DataFrame(evolution)

        fig_evol = go.Figure()
        fig_evol.add_trace(go.Scatter(
            x=df_evol["jour"],
            y=df_evol["nb"],
            mode="lines",
            line=dict(color="#E63946", width=3, shape="spline"),
            fill="tozeroy",
            fillcolor="rgba(230, 57, 70, 0.08)",
            hovertemplate="<b>%{x}</b><br>%{y} articles<extra></extra>"
        ))
        fig_evol.update_layout(
            height=300,
            margin=dict(l=10, r=10, t=20, b=10),
            showlegend=False,
            hovermode="x unified",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False, showline=True, linecolor="#E9ECEF"),
            yaxis=dict(showgrid=True, gridcolor="#F1F3F5", showline=False),
            font=dict(family="Inter, sans-serif", color="#1D3557"),
        )
        st.plotly_chart(fig_evol, use_container_width=True)
    else:
        st.info("Aucune donnée d'évolution disponible.")

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
            height=300,
            xaxis_title="",
            yaxis_title="",
            showlegend=False,
            coloraxis_showscale=False,
            margin=dict(l=10, r=10, t=10, b=10),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif", color="#1D3557"),
        )
        st.plotly_chart(fig_src, use_container_width=True)
    else:
        st.info("Aucune source.")

st.markdown("---")

# ============================================================
# SECTION 4 : THÈMES
# ============================================================
st.markdown("## 🎯 Répartition par thème")
st.caption("Focus éditorial")
st.markdown("")

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
            height=320,
            margin=dict(l=10, r=10, t=10, b=10),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif", color="#1D3557"),
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
            height=320,
            xaxis_title="Articles",
            yaxis_title="",
            showlegend=False,
            coloraxis_showscale=False,
            margin=dict(l=10, r=10, t=10, b=10),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif", color="#1D3557"),
        )
        st.plotly_chart(fig_bar, use_container_width=True)
else:
    st.info("Aucune donnée de thème disponible.")

st.markdown("---")

# ============================================================
# SECTION 5 : TOP ARTICLES + DERNIERS ARTICLES
# ============================================================
# ============================================================
# SECTION 5 : TOP ARTICLES + DERNIERS ARTICLES
# ============================================================
st.markdown("## 📰 Articles")
st.caption("Top pertinents et dernières publications")
st.markdown("")

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("##### 🏆 Top articles pertinents")

    top_arts = cockpit_stats.top_articles_pertinents(5)

    if top_arts:
        for i, art in enumerate(top_arts, 1):
            titre_complet = art.get("titre", "") or ""
            titre_avec_num = f"{i}. {titre_complet[:85]}" + ("..." if len(titre_complet) > 85 else "")

            # Détecter le sentiment si dispo
            sentiment_art = None
            if art.get("sentiment"):
                s = str(art["sentiment"]).lower()
                if "pos" in s:
                    sentiment_art = "positif"
                elif "neg" in s:
                    sentiment_art = "negatif"
                else:
                    sentiment_art = "neutre"

            style.article_card(
                titre=titre_avec_num,
                source=art.get("source", ""),
                date=str(art.get("date_publication", ""))[:10] if art.get("date_publication") else "",
                sentiment=sentiment_art,
                url=art.get("url", "")
            )
    else:
        st.info("Aucun article.")

with col2:
    st.markdown("##### 🆕 Derniers articles")

    derniers = cockpit_stats.derniers_articles(5)

    if derniers:
        for art in derniers:
            titre_complet = art.get("titre", "") or ""
            titre_court = titre_complet[:85] + ("..." if len(titre_complet) > 85 else "")

            style.article_card(
                titre=titre_court,
                source=art.get("source", ""),
                date=str(art.get("date_publication", ""))[:10] if art.get("date_publication") else "",
                url=art.get("url", "")
            )
    else:
        st.info("Aucun article.")

st.markdown("---")

# ============================================================
# SECTION 6 : SENTIMENT PAR SOURCE
# ============================================================
st.markdown("## 📊 Sentiment par source")
st.caption("Répartition par média")
st.markdown("")

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
        font=dict(family="Inter, sans-serif", color="#1D3557"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_sent_src, use_container_width=True)
else:
    st.info("Aucune donnée de sentiment par source.")

# ============================================================
# PIED DE PAGE
# ============================================================
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#6C757D; font-size:0.8rem; padding:1rem;'>"
    "🇹🇳 <b>TuniWatch</b> © 2026 — Observatoire des médias en Tunisie"
    "</div>",
    unsafe_allow_html=True
)