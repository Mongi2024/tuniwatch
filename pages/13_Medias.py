"""
Page Médias - Analyse détaillée par source
Version 1.0 - Comparaison et profils des médias
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
    page_title="Médias - TuniWatch",
    page_icon="📡",
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
# CSS PREMIUM
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
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# FONCTIONS PREMIUM (concaténation, pas de f-string multi-lignes)
# ============================================================

def kpi_card(icone, label, valeur, tendance=None, couleur=None):
    """Carte KPI premium — version concaténation."""
    if couleur is None:
        couleur = C_PRIMAIRE

    if tendance:
        trend_html = (
            '<div style="display: inline-block; '
            'background: rgba(39, 174, 96, 0.12); '
            'color: #27ae60; padding: 5px 12px; '
            'border-radius: 20px; '
            'font-size: 0.75rem; font-weight: 700;">'
            f'↑ {tendance}'
            '</div>'
        )
    else:
        trend_html = ""

    html = (
        '<div style="'
        'background: #ffffff; '
        'border-radius: 20px; '
        'padding: 22px 24px; '
        'box-shadow: 0 4px 24px rgba(15, 23, 42, 0.06), 0 1px 3px rgba(15, 23, 42, 0.04); '
        'border: 1px solid rgba(15, 23, 42, 0.03); '
        'height: 100%; '
        'min-height: 155px; '
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
        'margin-bottom: 16px;'
        '">'
        '<div style="'
        'width: 40px; height: 40px; '
        f'background: {couleur}15; '
        'border-radius: 12px; '
        'display: flex; align-items: center; justify-content: center; '
        'font-size: 1.2rem;'
        '">'
        f'{icone}'
        '</div>'
        '<div style="'
        'font-size: 0.72rem; '
        'color: #64748b; '
        'font-weight: 700; '
        'text-transform: uppercase; '
        'letter-spacing: 0.8px;'
        '">'
        f'{label}'
        '</div>'
        '</div>'
        '<div style="'
        'font-size: 2.2rem; '
        'font-weight: 800; '
        'color: #0f172a; '
        'line-height: 1; '
        'letter-spacing: -1px; '
        'margin-bottom: 12px;'
        '">'
        f'{valeur}'
        '</div>'
        f'{trend_html}'
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


# ============================================================
# EN-TÊTE
# ============================================================
style.page_header(
    titre="Médias",
    icone="📡",
    description="Analyse détaillée par source — Profils, thèmes et évolution des médias",
    badge="PAR MÉDIA"
)

# ============================================================
# CHARGEMENT DES SOURCES
# ============================================================
try:
    with st.spinner("Chargement des sources..."):
        sources_liste = cockpit_stats.liste_sources_actives()
    donnees_ok = True
except Exception as e:
    donnees_ok = False
    erreur_msg = str(e)

if not donnees_ok or not sources_liste:
    st.error(f"⚠️ Impossible de charger les sources : {erreur_msg if not donnees_ok else 'aucune source'}")
    st.stop()

# ============================================================
# SECTION 1 : FILTRES
# ============================================================
section_titre("🎛️", "Filtres", "Sélectionnez un ou plusieurs médias à analyser")

col1, col2 = st.columns([3, 1])

with col1:
    # Top 20 sources pour la liste
    top_sources = cockpit_stats.top_sources(20)
    liste_top = [s["source"] for s in top_sources]

    sources_selectionnees = st.multiselect(
        "📡 Médias à analyser",
        options=sources_liste,
        default=liste_top[:3] if len(liste_top) >= 3 else liste_top,
        help="Sélectionnez un ou plusieurs médias"
    )

with col2:
    jours = st.selectbox(
        "📅 Période",
        options=[7, 14, 30, 60, 90],
        index=2,
        format_func=lambda x: f"{x} jours"
    )

if not sources_selectionnees:
    st.warning("⚠️ Sélectionnez au moins un média pour voir les analyses.")
    st.stop()

# ============================================================
# SECTION 2 : COMPARAISON MULTI-SOURCES (si plusieurs médias)
# ============================================================
if len(sources_selectionnees) > 1:
    section_titre(
        "🔍",
        "Comparaison des médias sélectionnés",
        f"Analyse comparative sur {len(sources_selectionnees)} médias"
    )

    # --- Évolution comparée ---
    st.markdown("##### 📈 Évolution comparée")
    comp_data = cockpit_stats.comparaison_sources(sources_selectionnees, jours)

    if comp_data:
        df_comp = pd.DataFrame(comp_data)

        # Palette de couleurs pour les lignes
        palette = [C_PRIMAIRE, C_TEAL, C_JAUNE, C_VIOLET, C_BLEU,
                   C_VERT, C_ROUGE, "#8b5cf6", "#ec4899", "#06b6d4"]

        fig_comp = go.Figure()
        for idx, src in enumerate(sources_selectionnees):
            df_src = df_comp[df_comp["source"] == src]
            if not df_src.empty:
                fig_comp.add_trace(go.Scatter(
                    x=df_src["jour"],
                    y=df_src["nb"],
                    mode="lines+markers",
                    name=src[:25],
                    line=dict(color=palette[idx % len(palette)],
                              width=3, shape="spline"),
                    marker=dict(size=7, line=dict(width=2, color="white")),
                    hovertemplate=f"<b>{src}</b><br>%{{x}}<br>%{{y}} articles<extra></extra>"
                ))

        fig_comp.update_layout(
            height=380,
            hovermode="x unified",
            margin=dict(l=10, r=20, t=20, b=10),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02,
                        xanchor="right", x=1, font=dict(size=11)),
            xaxis=dict(showgrid=False, showline=False,
                       tickfont=dict(size=11, color="#94a3b8")),
            yaxis=dict(showgrid=True, gridcolor="rgba(15,23,42,0.04)",
                       tickfont=dict(size=11, color="#94a3b8"))
        )
        st.plotly_chart(fig_comp, use_container_width=True)
    else:
        st.info("Aucune donnée de comparaison.")

# ============================================================
# SECTION 3 : ANALYSE MÉDIA PAR MÉDIA
# ============================================================
for source in sources_selectionnees:
    section_titre("📡", source, f"Détail du média sur {jours} jours")

    # --- Stats de ce média ---
    stats = cockpit_stats.stats_par_source(source, jours)

    if not stats:
        st.warning(f"Aucune donnée pour {source}")
        continue

    # --- KPI du média ---
    col1, col2, col3, col4 = st.columns(4, gap="medium")

    with col1:
        kpi_card("📰", "Articles",
                 f"{stats['nb_articles']:,}".replace(",", " "),
                 couleur=C_PRIMAIRE)

    with col2:
        kpi_card("🎯", "Thèmes couverts",
                 str(stats['nb_themes']),
                 couleur=C_JAUNE)

    with col3:
        kpi_card("⭐", "Score moyen",
                 f"{stats['score_moyen']:.2f}",
                 couleur=C_VIOLET)

    with col4:
        total_sent = stats['positifs'] + stats['neutres'] + stats['negatifs']
        pct_positif = (stats['positifs'] / total_sent * 100) if total_sent > 0 else 0
        kpi_card("😊", "Positif",
                 f"{pct_positif:.0f}%",
                 couleur=C_VERT)

    # --- Graphiques côte à côte ---
    col1, col2 = st.columns(2, gap="medium")

    # --- Thèmes du média ---
    with col1:
        st.markdown("##### 🎯 Répartition thématique")
        themes_src = cockpit_stats.themes_par_source(source, limite=10)

        if themes_src:
            df_th = pd.DataFrame(themes_src)
            df_th["label"] = df_th["theme"].apply(
                lambda t: f"{EMOJIS_THEMES.get(t, '🌐')} {t}"
            )
            df_th = df_th.sort_values("nb_articles")

            fig_th = go.Figure(go.Bar(
                x=df_th["nb_articles"],
                y=df_th["label"],
                orientation="h",
                marker=dict(
                    color=[COULEURS_THEMES.get(t, C_GRIS) for t in df_th["theme"]],
                    line=dict(width=0)
                ),
                text=df_th["nb_articles"],
                textposition="outside",
                textfont=dict(size=12, color="#0f172a", family="Inter"),
                hovertemplate="<b>%{y}</b><br>%{x} articles<extra></extra>"
            ))
            fig_th.update_layout(
                height=340, showlegend=False,
                margin=dict(l=10, r=40, t=20, b=10),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter, sans-serif"),
                xaxis=dict(showgrid=True, gridcolor="rgba(15,23,42,0.04)",
                           showline=False,
                           tickfont=dict(size=11, color="#94a3b8")),
                yaxis=dict(showgrid=False,
                           tickfont=dict(size=12, color="#0f172a")),
                bargap=0.35
            )
            st.plotly_chart(fig_th, use_container_width=True)
        else:
            st.info("Aucun thème détecté pour ce média.")

    # --- Sentiment du média ---
    with col2:
        st.markdown("##### 🥧 Sentiment du média")
        total_s = stats['positifs'] + stats['neutres'] + stats['negatifs']

        if total_s > 0:
            fig_s = go.Figure(data=[go.Pie(
                labels=["Positifs", "Neutres", "Négatifs"],
                values=[stats['positifs'], stats['neutres'], stats['negatifs']],
                hole=0.68,
                marker=dict(colors=[C_VERT, C_JAUNE, C_ROUGE],
                            line=dict(color="white", width=3)),
                textinfo="percent",
                textposition="outside",
                textfont=dict(size=12, color="#0f172a"),
                hovertemplate="<b>%{label}</b><br>%{value} articles<br>%{percent}<extra></extra>",
                sort=False
            )])
            fig_s.update_layout(
                showlegend=True, height=340,
                margin=dict(l=10, r=10, t=20, b=10),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter, sans-serif"),
                legend=dict(orientation="h", yanchor="bottom", y=-0.15,
                            xanchor="center", x=0.5, font=dict(size=11)),
                annotations=[dict(
                    text=f"<b style='font-size:20px; color:#0f172a'>{total_s:,}</b><br>"
                         f"<span style='font-size:10px; color:#94a3b8'>ANALYSES</span>".replace(",", " "),
                    x=0.5, y=0.5, showarrow=False, font=dict(family="Inter")
                )]
            )
            st.plotly_chart(fig_s, use_container_width=True)
        else:
            st.info("Aucune analyse de sentiment.")

    # --- Évolution de ce média ---
    st.markdown(f"##### 📈 Évolution de {source[:40]} sur {jours} jours")
    evolution_src = cockpit_stats.evolution_par_source(source, jours)

    if evolution_src:
        df_evo = pd.DataFrame(evolution_src)
        fig_evo = go.Figure()
        fig_evo.add_trace(go.Scatter(
            x=df_evo["jour"],
            y=df_evo["nb"],
            mode="lines+markers",
            line=dict(color=C_PRIMAIRE, width=3, shape="spline"),
            fill="tozeroy",
            fillcolor="rgba(231,0,19,0.08)",
            marker=dict(size=7, line=dict(width=2, color="white")),
            hovertemplate="<b>%{x}</b><br>%{y} articles<extra></extra>"
        ))
        fig_evo.update_layout(
            height=300, showlegend=False, hovermode="x unified",
            margin=dict(l=10, r=20, t=20, b=10),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif"),
            xaxis=dict(showgrid=False, showline=False,
                       tickfont=dict(size=11, color="#94a3b8")),
            yaxis=dict(showgrid=True, gridcolor="rgba(15,23,42,0.04)",
                       tickfont=dict(size=11, color="#94a3b8"))
        )
        st.plotly_chart(fig_evo, use_container_width=True)
    else:
        st.info("Aucune donnée d'évolution.")

    # --- Derniers articles du média ---
    st.markdown(f"##### 📰 Derniers articles de {source[:40]}")
    articles_src = cockpit_stats.articles_par_source(source, limite=6)

    if articles_src:
        col1, col2 = st.columns(2, gap="medium")
        for i, art in enumerate(articles_src):
            theme = art.get("theme", "")
            emoji = EMOJIS_THEMES.get(theme, "🌐")
            titre = art.get("titre") or ""
            titre_court = titre[:90] + ("..." if len(titre) > 90 else "")
            with (col1 if i % 2 == 0 else col2):
                style.article_card(
                    titre=titre_court,
                    source=source,
                    url=art.get("url"),
                    score=art.get("score") if art.get("score") else None,
                    theme=theme if theme else None,
                    emoji_theme=emoji
                )
    else:
        st.info("Aucun article pour ce média.")

    st.markdown("---")

# ============================================================
# FOOTER
# ============================================================
style.footer()