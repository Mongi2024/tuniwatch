"""
Page Analyse - Exploration des données TuniWatch
Version 3.0 - Graphiques premium (inspiré dashboards modernes)
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
# PALETTE PREMIUM (inspirée des dashboards modernes)
# ============================================================
COULEUR_PRIMAIRE = "#e70013"
COULEUR_TEAL = "#14b8a6"
COULEUR_JAUNE = "#f59e0b"
COULEUR_VIOLET = "#8b5cf6"
COULEUR_BLEU = "#3b82f6"
COULEUR_VERT = "#10b981"
COULEUR_ROUGE = "#ef4444"
COULEUR_GRIS = "#64748b"

COULEURS_SENTIMENT = {
    "positif": COULEUR_VERT,
    "neutre": COULEUR_JAUNE,
    "negatif": COULEUR_ROUGE
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
# CSS ADDITIONNEL POUR LES GRAPHIQUES
# ============================================================
st.markdown("""
<style>
    /* Conteneur des graphiques avec ombre douce */
    div[data-testid="stPlotlyChart"] {
        background: #ffffff;
        border-radius: 16px;
        padding: 16px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(0, 0, 0, 0.03);
    }
    
    /* Titres des sous-sections */
    div[data-testid="stMarkdownContainer"] h5 {
        color: #1a1a1a;
        font-weight: 700;
        font-size: 1rem;
        margin-bottom: 12px;
        letter-spacing: 0.3px;
    }
</style>
""", unsafe_allow_html=True)

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
        evolution = cockpit_stats.evolution_mentions(30)
    donnees_ok = True
except Exception as e:
    donnees_ok = False
    erreur_msg = str(e)

if not donnees_ok:
    st.error(f"⚠️ Impossible de charger les données : {erreur_msg}")
    st.stop()

# ============================================================
# SECTION 1 : KPIs avec sparklines
# ============================================================
style.section_title("📊", "Contexte", "Chiffres clés pour situer l'analyse")

col1, col2, col3, col4 = st.columns(4)

# Préparer les données de sparkline (30 derniers jours)
if evolution:
    spark_data = [item["nb"] for item in evolution]
else:
    spark_data = [0] * 10

def make_sparkline(data, color):
    """Crée une mini-courbe pour les KPIs."""
    if not data or len(data) < 2:
        return None
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=data,
        mode="lines",
        line=dict(color=color, width=2, shape="spline"),
        fill="tozeroy",
        fillcolor=f"rgba{tuple(list(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + [0.1])}",
        hoverinfo="skip"
    ))
    fig.update_layout(
        height=40,
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
    )
    return fig

# --- KPI 1 : Articles ---
with col1:
    style.kpi_card(
        "📰", "Articles analysés",
        f"{kpis['total_articles']:,}".replace(",", " "),
        couleur=COULEUR_PRIMAIRE
    )

# --- KPI 2 : Thèmes ---
with col2:
    style.kpi_card(
        "🎯", "Thèmes détectés",
        kpis["themes_actifs"],
        couleur=COULEUR_JAUNE
    )

# --- KPI 3 : Sentiments ---
with col3:
    style.kpi_card(
        "💭", "Analyses sentiments",
        kpis["total_analyses_sentiment"],
        couleur=COULEUR_TEAL
    )

# --- KPI 4 : Score ---
with col4:
    score = kpis.get("score_moyen", 0)
    style.kpi_card(
        "⭐", "Score moyen",
        f"{score:.2f}" if score else "0.00",
        couleur=COULEUR_VIOLET
    )

# ============================================================
# SECTION 2 : EVOLUTION + SENTIMENT GLOBAL (premium)
# ============================================================
style.section_title("📈", "Évolution et sentiment", "Tendances sur 30 jours")

col1, col2 = st.columns([2, 1])

# --- Courbe d'évolution premium ---
with col1:
    st.markdown("##### 📈 Évolution des mentions")

    if evolution:
        df_evol = pd.DataFrame(evolution)

        fig_evol = go.Figure()

        # Gradient sous la courbe
        fig_evol.add_trace(go.Scatter(
            x=df_evol["jour"],
            y=df_evol["nb"],
            mode="lines",
            line=dict(color=COULEUR_PRIMAIRE, width=3, shape="spline"),
            fill="tozeroy",
            fillcolor="rgba(231, 0, 19, 0.08)",
            name="Mentions",
            hovertemplate="<b>%{x}</b><br>📊 %{y} articles<extra></extra>"
        ))

        # Points visibles sur les pics
        fig_evol.add_trace(go.Scatter(
            x=df_evol["jour"],
            y=df_evol["nb"],
            mode="markers",
            marker=dict(size=8, color=COULEUR_PRIMAIRE,
                        line=dict(width=2, color="white")),
            hoverinfo="skip",
            showlegend=False
        ))

        fig_evol.update_layout(
            height=340,
            margin=dict(l=10, r=10, t=20, b=10),
            showlegend=False,
            hovermode="x unified",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(
                showgrid=False,
                showline=False,
                tickfont=dict(size=11, color="#888")
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor="rgba(0,0,0,0.04)",
                showline=False,
                tickfont=dict(size=11, color="#888")
            ),
            font=dict(family="Inter, sans-serif", color="#1a1a1a"),
        )
        st.plotly_chart(fig_evol, use_container_width=True)
    else:
        st.info("Aucune donnée d'évolution disponible.")

# --- Donut sentiment avec valeur centrale ---
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
            hole=0.68,
            marker=dict(
                colors=[COULEUR_VERT, COULEUR_JAUNE, COULEUR_ROUGE],
                line=dict(color="white", width=3)
            ),
            textinfo="percent",
            textposition="outside",
            textfont=dict(size=12, color="#1a1a1a", family="Inter"),
            hovertemplate="<b>%{label}</b><br>%{value} (%{percent})<extra></extra>",
            sort=False
        )])

        # Valeur centrale
        fig_sent.update_layout(
            showlegend=True,
            height=340,
            margin=dict(l=10, r=10, t=10, b=10),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif", color="#1a1a1a"),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.15,
                xanchor="center",
                x=0.5,
                font=dict(size=11)
            ),
            annotations=[dict(
                text=f"<b style='font-size:22px; color:#1a1a1a'>{total_sent:,}</b><br>"
                     f"<span style='font-size:11px; color:#888'>analyses</span>".replace(",", " "),
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(family="Inter")
            )]
        )
        st.plotly_chart(fig_sent, use_container_width=True)
    else:
        st.info("Aucune donnée de sentiment.")

# ============================================================
# SECTION 3 : TOP SOURCES + REPARTITION THEMES (premium)
# ============================================================
style.section_title("📊", "Sources et thèmes", "Répartition des articles collectés")

col1, col2 = st.columns([1, 1])

# --- Top sources avec barres arrondies ---
with col1:
    st.markdown("##### 📡 Top sources")

    top_src = cockpit_stats.top_sources(8)

    if top_src:
        df_src = pd.DataFrame(top_src)
        df_src["source_court"] = df_src["source"].apply(lambda s: s[:28])

        # Créer un dégradé de couleurs du rouge foncé au rouge clair
        couleurs = ["#7f1d1d", "#991b1b", "#b91c1c", "#dc2626",
                    "#e70013", "#ef4444", "#f87171", "#fca5a5"]

        fig_src = go.Figure()
        fig_src.add_trace(go.Bar(
            x=df_src.sort_values("nb_articles")["nb_articles"],
            y=df_src.sort_values("nb_articles")["source_court"],
            orientation="h",
            marker=dict(
                color=couleurs[:len(df_src)],
                line=dict(width=0)
            ),
            text=df_src.sort_values("nb_articles")["nb_articles"],
            textposition="outside",
            textfont=dict(size=12, color="#1a1a1a", family="Inter"),
            hovertemplate="<b>%{y}</b><br>📰 %{x} articles<extra></extra>"
        ))
        fig_src.update_layout(
            height=360,
            xaxis_title="",
            yaxis_title="",
            showlegend=False,
            margin=dict(l=10, r=40, t=10, b=10),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif", color="#1a1a1a"),
            xaxis=dict(
                showgrid=True,
                gridcolor="rgba(0,0,0,0.04)",
                showline=False,
                tickfont=dict(size=11, color="#888")
            ),
            yaxis=dict(
                showgrid=False,
                tickfont=dict(size=12, color="#1a1a1a")
            ),
            bargap=0.35
        )
        st.plotly_chart(fig_src, use_container_width=True)
    else:
        st.info("Aucune source.")

# --- Donut thèmes premium ---
with col2:
    st.markdown("##### 🎯 Répartition par thème")

    stats_themes = cockpit_stats.stats_themes_rapide()

    if stats_themes:
        df_themes = pd.DataFrame(stats_themes)
        df_themes["label"] = df_themes["theme"].apply(
            lambda t: f"{EMOJIS_THEMES.get(t, '🌐')} {t}"
        )

        fig_pie = go.Figure(data=[go.Pie(
            labels=df_themes["label"],
            values=df_themes["nb_articles"],
            hole=0.6,
            marker=dict(
                colors=[COULEURS_THEMES.get(t, "#95a5a6") for t in df_themes["theme"]],
                line=dict(color="white", width=3)
            ),
            textinfo="percent",
            textposition="outside",
            textfont=dict(size=12, color="#1a1a1a", family="Inter"),
            hovertemplate="<b>%{label}</b><br>%{value} articles<br>%{percent}<extra></extra>",
            sort=False
        )])

        total_themes = int(df_themes["nb_articles"].sum())

        fig_pie.update_layout(
            showlegend=True,
            height=360,
            margin=dict(l=10, r=10, t=10, b=10),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif", color="#1a1a1a"),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.18,
                xanchor="center",
                x=0.5,
                font=dict(size=10)
            ),
            annotations=[dict(
                text=f"<b style='font-size:20px; color:#1a1a1a'>{total_themes}</b><br>"
                     f"<span style='font-size:11px; color:#888'>articles</span>",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(family="Inter")
            )]
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("Aucun thème détecté.")

# ============================================================
# SECTION 4 : SENTIMENT PAR SOURCE (barres arrondies)
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
        labels={"source_court": "", "nb": "Articles", "sentiment": "Sentiment"},
        category_orders={"sentiment": ["positif", "neutre", "negatif"]}
    )

    fig_sent_src.update_traces(
        marker=dict(line=dict(width=0)),
        hovertemplate="<b>%{x}</b><br>%{fullData.name}: %{y}<extra></extra>"
    )

    fig_sent_src.update_layout(
        height=400,
        xaxis_tickangle=-30,
        xaxis_title="",
        yaxis_title="",
        margin=dict(l=10, r=10, t=10, b=80),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#1a1a1a"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11)
        ),
        xaxis=dict(
            showgrid=False,
            tickfont=dict(size=11, color="#1a1a1a")
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(0,0,0,0.04)",
            tickfont=dict(size=11, color="#888")
        ),
        bargap=0.25
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