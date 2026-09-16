"""
Dashboard Cockpit TuniWatch - Page d'accueil
Etape G - Session 1 (avec sidebar automatique)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os
from datetime import datetime

# Ajout du dossier
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import auth
import style
import cockpit_stats

# Configuration
st.set_page_config(
    page_title="TuniWatch - Cockpit",
    page_icon="🇹🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style + Sidebar automatique (logo, user, navigation, deconnexion)
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
col1, col2 = st.columns([3, 1])

with col1:
    st.title("🏠 Cockpit TuniWatch")
    st.caption(f"Vue d'ensemble — {datetime.now().strftime('%A %d %B %Y à %H:%M')}")

with col2:
    if st.button("🔄 Actualiser", use_container_width=True, key="cockpit_refresh"):
        st.cache_data.clear()
        st.rerun()

st.markdown("---")

# ============================================================
# CHARGEMENT DES DONNEES
# ============================================================
with st.spinner("Chargement des données..."):
    kpis = cockpit_stats.kpis_globaux()
    sentiment = cockpit_stats.stats_sentiment()

# ============================================================
# SECTION 1 : KPIs PRINCIPAUX
# ============================================================
st.subheader("📊 Vue globale")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="📰 Articles collectés",
        value=f"{kpis['total_articles']:,}".replace(",", " "),
        delta=f"+{kpis['total_articles'] - 411}" if kpis['total_articles'] > 411 else None
    )

with col2:
    st.metric(
        label="📡 Sources actives",
        value=kpis["total_sources"]
    )

with col3:
    st.metric(
        label="🎯 Analyses thèmes",
        value=kpis["total_analyses_themes"]
    )

with col4:
    st.metric(
        label="💭 Analyses sentiments",
        value=kpis["total_analyses_sentiment"]
    )

# ============================================================
# SECTION 2 : SENTIMENT GLOBAL
# ============================================================
st.markdown("---")
st.subheader("😊 Sentiment global")

col1, col2, col3, col4 = st.columns(4)

total = (sentiment.get("positifs", 0) or 0) + (sentiment.get("neutres", 0) or 0) + (sentiment.get("negatifs", 0) or 0)

with col1:
    st.metric(
        label="🟢 Positifs",
        value=sentiment.get("positifs", 0) or 0,
        delta=f"{((sentiment.get('positifs', 0) or 0) / total * 100):.0f}%" if total > 0 else None
    )

with col2:
    st.metric(
        label="🟡 Neutres",
        value=sentiment.get("neutres", 0) or 0,
        delta=f"{((sentiment.get('neutres', 0) or 0) / total * 100):.0f}%" if total > 0 else None
    )

with col3:
    st.metric(
        label="🔴 Négatifs",
        value=sentiment.get("negatifs", 0) or 0,
        delta=f"{((sentiment.get('negatifs', 0) or 0) / total * 100):.0f}%" if total > 0 else None
    )

with col4:
    st.metric(
        label="📊 Score moyen",
        value=f"{kpis['score_moyen']:.2f}" if kpis['score_moyen'] else "0.00"
    )

# ============================================================
# SECTION 3 : EVOLUTION + TOP SOURCES
# ============================================================
st.markdown("---")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📈 Évolution des mentions (30 jours)")

    evolution = cockpit_stats.evolution_mentions(30)

    if evolution:
        df_evol = pd.DataFrame(evolution)

        fig_evol = px.area(
            df_evol,
            x="jour",
            y="nb",
            labels={"jour": "", "nb": "Articles"},
            color_discrete_sequence=["#e70013"]
        )
        fig_evol.update_traces(
            line=dict(width=2, color="#e70013"),
            fillcolor="rgba(231, 0, 19, 0.1)"
        )
        fig_evol.update_layout(
            height=300,
            margin=dict(l=10, r=10, t=10, b=10),
            showlegend=False,
            hovermode="x unified"
        )
        st.plotly_chart(fig_evol, use_container_width=True)
    else:
        st.info("Aucune donnée d'évolution disponible.")

with col2:
    st.subheader("📡 Top sources")

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
            margin=dict(l=10, r=10, t=10, b=10)
        )
        st.plotly_chart(fig_src, use_container_width=True)
    else:
        st.info("Aucune source.")

# ============================================================
# SECTION 4 : THEMES
# ============================================================
st.markdown("---")
st.subheader("🎯 Répartition par thème")

stats_themes = cockpit_stats.stats_themes_rapide()

if stats_themes:
    df_themes = pd.DataFrame(stats_themes)
    df_themes["emoji"] = df_themes["theme"].apply(lambda t: EMOJIS_THEMES.get(t, "🌐"))
    df_themes["label"] = df_themes["emoji"] + " " + df_themes["theme"]
    df_themes["couleur"] = df_themes["theme"].apply(lambda t: COULEURS_THEMES.get(t, "#95a5a6"))

    col1, col2 = st.columns([1, 1])

    with col1:
        fig_pie = px.pie(
            df_themes,
            values="nb_articles",
            names="theme",
            color="theme",
            color_discrete_map=COULEURS_THEMES,
            hole=0.4
        )
        fig_pie.update_traces(
            textposition="inside",
            textinfo="percent+label",
            hovertemplate="<b>%{label}</b><br>%{value} articles<br>%{percent}<extra></extra>"
        )
        fig_pie.update_layout(
            showlegend=False,
            height=300,
            margin=dict(l=10, r=10, t=10, b=10)
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
            height=300,
            xaxis_title="Articles",
            yaxis_title="",
            showlegend=False,
            coloraxis_showscale=False,
            margin=dict(l=10, r=10, t=10, b=10)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

# ============================================================
# SECTION 5 : TOP ARTICLES + DERNIERS ARTICLES
# ============================================================
st.markdown("---")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🏆 Top articles pertinents")

    top_arts = cockpit_stats.top_articles_pertinents(5)

    if top_arts:
        for i, art in enumerate(top_arts, 1):
            emoji = EMOJIS_THEMES.get(art["theme"], "🌐")
            with st.container():
                if art["url"]:
                    st.markdown(f"**{i}.** {emoji} [{art['titre'][:75]}...]({art['url']})")
                else:
                    st.markdown(f"**{i}.** {emoji} {art['titre'][:75]}...")
                st.caption(f"📰 {art['source']} • Score : **{art['score']:.2f}** • Thème : `{art['theme']}`")
    else:
        st.info("Aucun article.")

with col2:
    st.subheader("🆕 Derniers articles")

    derniers = cockpit_stats.derniers_articles(5)

    if derniers:
        for art in derniers:
            with st.container():
                if art["url"]:
                    st.markdown(f"• [{art['titre'][:75]}...]({art['url']})")
                else:
                    st.markdown(f"• {art['titre'][:75]}...")
                st.caption(f"📰 {art['source']}")
    else:
        st.info("Aucun article.")

# ============================================================
# SECTION 6 : SENTIMENT PAR SOURCE
# ============================================================
st.markdown("---")
st.subheader("📊 Sentiment par source")

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
        height=350,
        xaxis_tickangle=-30,
        xaxis_title="",
        yaxis_title="Articles",
        margin=dict(l=10, r=10, t=10, b=80)
    )
    st.plotly_chart(fig_sent_src, use_container_width=True)

# ============================================================
# FOOTER
# ============================================================
style.footer()