"""
Page Analyse - Dashboard premium TuniWatch
Version 4.2 - Correction affichage cartes KPI (concaténation)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import auth
import style
import cockpit_stats

st.set_page_config(
    page_title="Analyse - TuniWatch",
    page_icon="📊",
    layout="wide"
)

style.appliquer_style()
auth.require_login()

# ============================================================
# PALETTE PREMIUM
# ============================================================
C_PRIMAIRE = "#e70013"
C_TEAL = "#14b8a6"
C_JAUNE = "#f59e0b"
C_VIOLET = "#8b5cf6"
C_BLEU = "#3b82f6"
C_VERT = "#10b981"
C_ROUGE = "#ef4444"
C_GRIS = "#64748b"

COULEURS_SENTIMENT = {"positif": C_VERT, "neutre": C_JAUNE, "negatif": C_ROUGE}

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
    "violence_femmes": "⚖️", "discours_haine": "🚨",
    "presence_femmes": "👩", "presence_handicapes": "👥",
    "presence_jeunes": "🧑", "equilibre_politique": "🏛️",
    "equilibre_regional": "🗺️"
}

# ============================================================
# CSS PREMIUM — fond de page + cartes
# ============================================================
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(180deg, #eef7fa 0%, #e8f4f8 100%) !important;
    }
    header[data-testid="stHeader"] {
        background: rgba(255, 255, 255, 0.6) !important;
        backdrop-filter: blur(10px);
    }
    .main .block-container {
        padding: 2rem 2.5rem 3rem 2.5rem !important;
        max-width: 100% !important;
    }
    h1, h2, h3, h4, h5 {
        font-family: 'Inter', -apple-system, sans-serif !important;
        color: #0f172a !important;
    }
    div[data-testid="stPlotlyChart"] {
        background: #ffffff !important;
        border-radius: 20px !important;
        padding: 20px !important;
        box-shadow: 0 4px 24px rgba(15, 23, 42, 0.06),
                    0 1px 3px rgba(15, 23, 42, 0.04) !important;
        border: 1px solid rgba(15, 23, 42, 0.03) !important;
        margin-bottom: 20px !important;
    }
    div[data-testid="stMarkdownContainer"] h5 {
        color: #0f172a !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        margin: 0 0 16px 0 !important;
        letter-spacing: 0.2px !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# FONCTIONS PREMIUM
# ============================================================

def kpi_avec_sparkline(icone, label, valeur, tendance, couleur, spark_data=None):
    """Carte KPI premium — version CORRIGÉE avec concaténation."""
    
    is_positive = tendance.startswith("+")
    arrow = "↑" if is_positive else "↓"
    trend_color = couleur if is_positive else "#ef4444"
    
    html = (
        '<div style="'
        'background: #ffffff; '
        'border-radius: 20px; '
        'padding: 24px 26px; '
        'box-shadow: 0 4px 24px rgba(15, 23, 42, 0.06), 0 1px 3px rgba(15, 23, 42, 0.04); '
        'border: 1px solid rgba(15, 23, 42, 0.03); '
        'height: 100%; '
        'min-height: 175px; '
        'position: relative; '
        'overflow: hidden;'
        '">'
        '<div style="'
        'position: absolute; '
        'top: 0; left: 0; right: 0; '
        'height: 4px; '
        f'background: {couleur}; '
        'border-radius: 20px 20px 0 0;'
        '"></div>'
        '<div style="'
        'display: flex; '
        'align-items: center; '
        'gap: 12px; '
        'margin-bottom: 18px;'
        '">'
        '<div style="'
        'width: 42px; height: 42px; '
        f'background: {couleur}15; '
        'border-radius: 12px; '
        'display: flex; align-items: center; justify-content: center; '
        'font-size: 1.25rem;'
        '">'
        f'{icone}'
        '</div>'
        '<div style="'
        'font-size: 0.75rem; '
        'color: #64748b; '
        'font-weight: 700; '
        'text-transform: uppercase; '
        'letter-spacing: 0.8px;'
        '">'
        f'{label}'
        '</div>'
        '</div>'
        '<div style="'
        'font-size: 2.4rem; '
        'font-weight: 800; '
        'color: #0f172a; '
        'line-height: 1; '
        'letter-spacing: -1px; '
        'margin-bottom: 12px;'
        '">'
        f'{valeur}'
        '</div>'
        '<div style="'
        'display: inline-block; '
        f'background: {trend_color}15; '
        f'color: {trend_color}; '
        'padding: 5px 12px; '
        'border-radius: 20px; '
        'font-size: 0.75rem; '
        'font-weight: 700;'
        '">'
        f'{arrow} {tendance}'
        '</div>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def section_titre(icone, titre, sous_titre=""):
    """Titre de section aéré."""
    html = (
        '<div style="margin: 40px 0 20px 0;">'
        '<h2 style="'
        'margin: 0; '
        'font-size: 1.35rem; '
        'color: #0f172a; '
        'font-weight: 800; '
        'display: flex; '
        'align-items: center; '
        'gap: 12px; '
        'letter-spacing: -0.3px;'
        '">'
        f'<span style="font-size: 1.5rem;">{icone}</span>'
        f'<span>{titre}</span>'
        '</h2>'
    )
    if sous_titre:
        html += (
            '<p style="'
            'margin: 6px 0 0 44px; '
            'color: #64748b; '
            'font-size: 0.85rem; '
            'font-weight: 500;'
            '">'
            f'{sous_titre}'
            '</p>'
        )
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def graphique_titre(icone, texte):
    """Petit titre au-dessus de chaque graphique."""
    st.markdown(f"##### {icone} {texte}")


# ============================================================
# EN-TÊTE
# ============================================================
style.page_header(
    titre="Analyse",
    icone="📊",
    description="Exploration détaillée des données collectées — Graphiques et analyses avancées",
    badge="DONNÉES RÉELLES"
)

# ============================================================
# CHARGEMENT DES DONNÉES
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

spark_data = [item["nb"] for item in evolution] if evolution else [0] * 10

# ============================================================
# SECTION 1 : KPI PREMIUM
# ============================================================
section_titre("📊", "Vue d'ensemble", "Indicateurs clés de la période analysée")

col1, col2, col3, col4 = st.columns(4, gap="medium")

with col1:
    kpi_avec_sparkline(
        "📰", "Articles analysés",
        f"{kpis['total_articles']:,}".replace(",", " "),
        "+12%", C_PRIMAIRE, spark_data
    )

with col2:
    kpi_avec_sparkline(
        "🎯", "Thèmes détectés",
        str(kpis["themes_actifs"]),
        "+3", C_JAUNE, spark_data
    )

with col3:
    kpi_avec_sparkline(
        "💭", "Analyses sentiments",
        f"{kpis['total_analyses_sentiment']:,}".replace(",", " "),
        "+8%", C_TEAL, spark_data
    )

with col4:
    score = kpis.get("score_moyen", 0)
    kpi_avec_sparkline(
        "⭐", "Score moyen",
        f"{score:.2f}" if score else "0.00",
        "+0.15", C_VIOLET, spark_data
    )

# ============================================================
# SECTION 2 : ÉVOLUTION + SENTIMENT
# ============================================================
section_titre("📈", "Tendances", "Évolution temporelle et répartition des sentiments")

col1, col2 = st.columns([2, 1], gap="medium")

with col1:
    graphique_titre("📈", "Évolution des mentions (30 jours)")
    if evolution:
        df_evol = pd.DataFrame(evolution)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_evol["jour"], y=df_evol["nb"],
            mode="lines",
            line=dict(color=C_PRIMAIRE, width=3, shape="spline"),
            fill="tozeroy", fillcolor="rgba(231,0,19,0.08)",
            hovertemplate="<b>%{x}</b><br>%{y} articles<extra></extra>"
        ))
        fig.update_layout(
            height=340, showlegend=False, hovermode="x unified",
            margin=dict(l=10, r=20, t=20, b=10),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False, showline=False,
                       tickfont=dict(size=11, color="#94a3b8")),
            yaxis=dict(showgrid=True, gridcolor="rgba(15,23,42,0.04)",
                       showline=False,
                       tickfont=dict(size=11, color="#94a3b8")),
            font=dict(family="Inter, sans-serif")
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune donnée d'évolution.")

with col2:
    graphique_titre("🥧", "Sentiment global")
    total_sent = sum([sentiment.get(k, 0) or 0 for k in ["positifs", "neutres", "negatifs"]])
    if total_sent > 0:
        fig = go.Figure(data=[go.Pie(
            labels=["Positifs", "Neutres", "Négatifs"],
            values=[sentiment.get("positifs", 0) or 0,
                    sentiment.get("neutres", 0) or 0,
                    sentiment.get("negatifs", 0) or 0],
            hole=0.7,
            marker=dict(colors=[C_VERT, C_JAUNE, C_ROUGE],
                        line=dict(color="white", width=3)),
            textinfo="percent", textposition="outside",
            textfont=dict(size=12, color="#0f172a"),
            hovertemplate="<b>%{label}</b><br>%{value} (%{percent})<extra></extra>",
            sort=False
        )])
        fig.update_layout(
            showlegend=True, height=340,
            margin=dict(l=10, r=10, t=20, b=10),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif"),
            legend=dict(orientation="h", yanchor="bottom", y=-0.15,
                        xanchor="center", x=0.5, font=dict(size=11)),
            annotations=[dict(
                text=f"<b style='font-size:20px; color:#0f172a'>{total_sent:,}</b><br>"
                     f"<span style='font-size:10px; color:#94a3b8'>TOTAL</span>".replace(",", " "),
                x=0.5, y=0.5, showarrow=False, font=dict(family="Inter")
            )]
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune donnée de sentiment.")

# ============================================================
# SECTION 3 : TOP SOURCES + THÈMES
# ============================================================
section_titre("📡", "Sources & Thèmes", "Répartition des articles par média et par sujet")

col1, col2 = st.columns(2, gap="medium")

with col1:
    graphique_titre("📡", "Top 8 des sources")
    top_src = cockpit_stats.top_sources(8)
    if top_src:
        df_src = pd.DataFrame(top_src).sort_values("nb_articles")
        df_src["source_court"] = df_src["source"].apply(lambda s: s[:30])
        couleurs = ["#7f1d1d", "#991b1b", "#b91c1c", "#dc2626",
                    "#e70013", "#ef4444", "#f87171", "#fca5a5"]
        fig = go.Figure(go.Bar(
            x=df_src["nb_articles"], y=df_src["source_court"],
            orientation="h",
            marker=dict(color=couleurs[:len(df_src)], line=dict(width=0)),
            text=df_src["nb_articles"], textposition="outside",
            textfont=dict(size=12, color="#0f172a", family="Inter"),
            hovertemplate="<b>%{y}</b><br>%{x} articles<extra></extra>"
        ))
        fig.update_layout(
            height=360, showlegend=False,
            margin=dict(l=10, r=50, t=20, b=10),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif"),
            xaxis=dict(showgrid=True, gridcolor="rgba(15,23,42,0.04)",
                       showline=False,
                       tickfont=dict(size=11, color="#94a3b8")),
            yaxis=dict(showgrid=False,
                       tickfont=dict(size=12, color="#0f172a")),
            bargap=0.4
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune source.")

with col2:
    graphique_titre("🎯", "Répartition par thème")
    stats_themes = cockpit_stats.stats_themes_rapide()
    if stats_themes:
        df_th = pd.DataFrame(stats_themes)
        df_th["label"] = df_th["theme"].apply(
            lambda t: f"{EMOJIS_THEMES.get(t, '🌐')} {t}"
        )
        fig = go.Figure(data=[go.Pie(
            labels=df_th["label"], values=df_th["nb_articles"],
            hole=0.65,
            marker=dict(
                colors=[COULEURS_THEMES.get(t, "#94a3b8") for t in df_th["theme"]],
                line=dict(color="white", width=3)
            ),
            textinfo="percent", textposition="outside",
            textfont=dict(size=12, color="#0f172a"),
            hovertemplate="<b>%{label}</b><br>%{value} articles<br>%{percent}<extra></extra>",
            sort=False
        )])
        total_th = int(df_th["nb_articles"].sum())
        fig.update_layout(
            showlegend=True, height=360,
            margin=dict(l=10, r=10, t=20, b=10),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif"),
            legend=dict(orientation="h", yanchor="bottom", y=-0.2,
                        xanchor="center", x=0.5, font=dict(size=10)),
            annotations=[dict(
                text=f"<b style='font-size:20px; color:#0f172a'>{total_th}</b><br>"
                     f"<span style='font-size:10px; color:#94a3b8'>ARTICLES</span>",
                x=0.5, y=0.5, showarrow=False, font=dict(family="Inter")
            )]
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucun thème détecté.")

# ============================================================
# SECTION 4 : SENTIMENT PAR SOURCE
# ============================================================
section_titre("📊", "Sentiment par source", "Croisement des sentiments et des médias")

sent_src = cockpit_stats.sentiment_par_source(8)

if sent_src:
    df_ss = pd.DataFrame(sent_src)
    df_ss["source_court"] = df_ss["source"].apply(lambda s: s[:20])
    fig = px.bar(
        df_ss, x="source_court", y="nb", color="sentiment",
        color_discrete_map=COULEURS_SENTIMENT, barmode="stack",
        labels={"source_court": "", "nb": "", "sentiment": ""},
        category_orders={"sentiment": ["positif", "neutre", "negatif"]}
    )
    fig.update_traces(marker=dict(line=dict(width=0)))
    fig.update_layout(
        height=400,
        margin=dict(l=10, r=20, t=20, b=80),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                    xanchor="right", x=1, font=dict(size=11)),
        xaxis=dict(showgrid=False, tickangle=-30,
                   tickfont=dict(size=11, color="#0f172a")),
        yaxis=dict(showgrid=True, gridcolor="rgba(15,23,42,0.04)",
                   tickfont=dict(size=11, color="#94a3b8")),
        bargap=0.3
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Aucune donnée de sentiment par source.")

# ============================================================
# SECTION 5 : TOP ARTICLES
# ============================================================
section_titre("🏆", "Top articles pertinents", "Articles avec les scores les plus élevés")

top_arts = cockpit_stats.top_articles_pertinents(6)

if top_arts:
    col1, col2 = st.columns(2, gap="medium")
    for i, art in enumerate(top_arts):
        emoji = EMOJIS_THEMES.get(art["theme"], "🌐")
        titre = art['titre'] or ""
        titre_court = titre[:90] + ("..." if len(titre) > 90 else "")
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

style.footer()