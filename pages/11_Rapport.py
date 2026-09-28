"""
Page Rapport - Generation d'un rapport imprimable en PDF
Version 2.0 - Ajout section Personnalités politiques
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
import analyzer
import sentiment_analyzer
from politiques_stats import (
    top_personnalites,
    repartition_genre,
    mentions_par_genre_et_media,
)

# Configuration
st.set_page_config(
    page_title="Rapport - TuniWatch",
    page_icon="📄",
    layout="wide"
)

# Style
style.appliquer_style()

# Protection
auth.require_login()
from status import afficher_status

# Indicateur de connexion
col_st1, col_st2, col_st3 = st.columns([4, 1, 1])
with col_st2:
    afficher_status()
with col_st3:
    if st.button("🔄 Rafraîchir"):
        st.cache_data.clear()
        st.rerun()

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

COULEUR_HOMME = "#1D3557"
COULEUR_FEMME = "#EF476F"

# ============================================================
# CSS SPECIAL POUR IMPRESSION PDF
# ============================================================
st.markdown("""
<style>
    @media print {
        [data-testid="stSidebar"],
        [data-testid="stToolbar"],
        header,
        footer,
        .stButton,
        button,
        [data-testid="stHeader"],
        .stDeployButton {
            display: none !important;
        }
        .main {
            padding: 0 !important;
            max-width: 100% !important;
        }
        .report-section {
            page-break-inside: avoid;
            margin-bottom: 20px;
        }
        h1 { font-size: 22pt !important; page-break-before: avoid; }
        h2 { font-size: 16pt !important; page-break-after: avoid; }
        @page { margin: 1.5cm; size: A4; }
    }

    .report-header {
        text-align: center;
        padding: 20px 0;
        border-bottom: 3px solid #e70013;
        margin-bottom: 30px;
    }
    .report-section {
        margin-bottom: 40px;
        padding: 20px;
        background: #f8f9fa;
        border-left: 4px solid #e70013;
        border-radius: 5px;
    }
    .report-kpi {
        background: white;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        border: 1px solid #e0e0e0;
    }
    .report-kpi-value {
        font-size: 2rem;
        font-weight: 700;
        color: #e70013;
    }
    .report-kpi-label {
        font-size: 0.85rem;
        color: #666;
    }
    .report-footer {
        text-align: center;
        padding: 20px;
        border-top: 2px solid #e70013;
        margin-top: 30px;
        color: #666;
        font-size: 0.85rem;
    }
    .comment {
        background: #fff8e1;
        padding: 12px 16px;
        border-left: 4px solid #f39c12;
        border-radius: 5px;
        margin: 15px 0;
        font-style: italic;
        color: #555;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# CHARGEMENT DES DONNEES
# ============================================================
kpis = cockpit_stats.kpis_globaux()
sentiment = cockpit_stats.stats_sentiment()
stats_themes = cockpit_stats.stats_themes_rapide()
top_sources = cockpit_stats.top_sources(8)
top_articles = cockpit_stats.top_articles_pertinents(5)

# Personnalités politiques (avec cache)
@st.cache_data(ttl=600, show_spinner=False)
def charger_personnalites():
    top, total = top_personnalites(10)
    rep = repartition_genre()
    media = mentions_par_genre_et_media(10)
    return top, total, rep, media

top_persos, total_mentions, rep_genre, par_media = charger_personnalites()

# ============================================================
# EN-TETE DU RAPPORT
# ============================================================
st.markdown(f"""
<div class="report-header">
    <div style="font-size: 3rem;">🇹🇳</div>
    <h1 style="margin: 10px 0; color: #1a1a1a;">TuniWatch</h1>
    <p style="font-size: 1.2rem; color: #666; margin: 5px 0;">
        Observatoire des médias tunisiens
    </p>
    <p style="font-size: 1rem; color: #888; margin: 10px 0;">
        <b>Rapport d'analyse médiatique</b><br>
        Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}
    </p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# BOUTON D'IMPRESSION
# ============================================================
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("""
    <div style="text-align: center; padding: 15px; background: #fff3cd;
                border-radius: 8px; margin-bottom: 30px;">
        <p style="margin: 0; font-size: 0.95rem; color: #856404;">
            💡 <b>Pour générer le PDF</b> : utilisez
            <b>Ctrl + P</b> (Windows) ou <b>Cmd + P</b> (Mac),
            puis choisissez <b>"Enregistrer au format PDF"</b>.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# SECTION 1 : RESUME EXECUTIF
# ============================================================
st.markdown("""
<div class="report-section">
    <h2>📊 1. Résumé exécutif</h2>
</div>
""", unsafe_allow_html=True)

total_sent = (sentiment.get("positifs", 0) or 0) + (sentiment.get("neutres", 0) or 0) + (sentiment.get("negatifs", 0) or 0)
pct_pos = ((sentiment.get("positifs", 0) or 0) / total_sent * 100) if total_sent > 0 else 0
pct_neu = ((sentiment.get("neutres", 0) or 0) / total_sent * 100) if total_sent > 0 else 0
pct_neg = ((sentiment.get("negatifs", 0) or 0) / total_sent * 100) if total_sent > 0 else 0

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="report-kpi">
        <div class="report-kpi-value">{kpis['total_articles']:,}</div>
        <div class="report-kpi-label">📰 Articles collectés</div>
    </div>
    """.replace(",", " "), unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="report-kpi">
        <div class="report-kpi-value">{kpis['total_sources']}</div>
        <div class="report-kpi-label">📡 Sources actives</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="report-kpi">
        <div class="report-kpi-value">{kpis['total_analyses_themes']}</div>
        <div class="report-kpi-label">🎯 Analyses de thèmes</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="report-kpi">
        <div class="report-kpi-value">{kpis['total_analyses_sentiment']}</div>
        <div class="report-kpi-label">💭 Analyses de sentiment</div>
    </div>
    """, unsafe_allow_html=True)

if kpis['total_articles'] > 0:
    st.markdown(f"""
    <div class="comment">
        📌 <b>Constat</b> : L'observatoire TuniWatch a collecté
        <b>{kpis['total_articles']} articles</b> provenant de
        <b>{kpis['total_sources']} sources tunisiennes</b> (presse, radios, TV).
        {kpis['total_analyses_themes']} analyses thématiques et
        {kpis['total_analyses_sentiment']} analyses de sentiment ont été réalisées.
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================
# SECTION 2 : ANALYSE DE SENTIMENT
# ============================================================
st.markdown("""
<div class="report-section">
    <h2>💭 2. Analyse de sentiment</h2>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])

with col1:
    df_sentiment = pd.DataFrame({
        "Sentiment": ["Positif", "Neutre", "Négatif"],
        "Nombre": [
            sentiment.get("positifs", 0) or 0,
            sentiment.get("neutres", 0) or 0,
            sentiment.get("negatifs", 0) or 0
        ]
    })

    fig_pie = px.pie(
        df_sentiment,
        values="Nombre",
        names="Sentiment",
        color="Sentiment",
        color_discrete_map={
            "Positif": COULEURS_SENTIMENT["positif"],
            "Neutre": COULEURS_SENTIMENT["neutre"],
            "Négatif": COULEURS_SENTIMENT["negatif"]
        },
        hole=0.4
    )
    fig_pie.update_traces(
        textposition="inside",
        textinfo="percent+label+value"
    )
    fig_pie.update_layout(
        showlegend=False,
        height=350,
        margin=dict(l=10, r=10, t=30, b=10)
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    st.markdown(f"""
    <div style="padding: 20px; background: white; border-radius: 8px; height: 100%;">
        <h3 style="color: #1a1a1a;">Répartition détaillée</h3>
        <table style="width: 100%; font-size: 1.1rem; margin-top: 20px;">
            <tr>
                <td style="padding: 8px;">🟢 <b>Positifs</b></td>
                <td style="text-align: right; color: #27ae60; font-weight: 700;">
                    {sentiment.get('positifs', 0) or 0} ({pct_pos:.1f}%)
                </td>
            </tr>
            <tr>
                <td style="padding: 8px;">🟡 <b>Neutres</b></td>
                <td style="text-align: right; color: #f39c12; font-weight: 700;">
                    {sentiment.get('neutres', 0) or 0} ({pct_neu:.1f}%)
                </td>
            </tr>
            <tr>
                <td style="padding: 8px;">🔴 <b>Négatifs</b></td>
                <td style="text-align: right; color: #e74c3c; font-weight: 700;">
                    {sentiment.get('negatifs', 0) or 0} ({pct_neg:.1f}%)
                </td>
            </tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

st.markdown(f"""
<div class="comment">
    📌 <b>Interprétation</b> : Sur les {total_sent} articles analysés,
    <b>{pct_neu:.1f}%</b> ont un ton neutre (factuel),
    <b>{pct_pos:.1f}%</b> sont positifs et
    <b>{pct_neg:.1f}%</b> sont négatifs.
    Le score moyen global est de <b>{kpis['score_moyen'] if kpis['score_moyen'] else 0:.2f}</b>.
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================
# SECTION 3 : REPARTITION PAR THEME
# ============================================================
st.markdown("""
<div class="report-section">
    <h2>🎯 3. Répartition par thème</h2>
</div>
""", unsafe_allow_html=True)

if stats_themes:
    df_themes = pd.DataFrame(stats_themes)
    df_themes["emoji"] = df_themes["theme"].apply(lambda t: EMOJIS_THEMES.get(t, "🌐"))
    df_themes["label"] = df_themes["emoji"] + " " + df_themes["theme"]

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
        height=350,
        xaxis_title="Nombre d'articles",
        yaxis_title="",
        showlegend=False,
        coloraxis_showscale=False,
        margin=dict(l=10, r=10, t=20, b=10)
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("#### Tableau détaillé")
    df_table = df_themes[["emoji", "theme", "nb_articles"]].copy()
    df_table.columns = ["", "Thème", "Articles"]
    df_table = df_table.sort_values("Articles", ascending=False)
    st.dataframe(df_table, use_container_width=True, hide_index=True)

    total_themes = df_themes["nb_articles"].sum()
    top_theme = df_themes.iloc[0]

    st.markdown(f"""
    <div class="comment">
        📌 <b>Constat</b> : Le thème le plus couvert est
        <b>{EMOJIS_THEMES.get(top_theme['theme'], '🌐')} {top_theme['theme']}</b>
        avec <b>{top_theme['nb_articles']} articles</b>
        ({top_theme['nb_articles']/total_themes*100:.1f}% du total).
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================
# SECTION 4 : TOP SOURCES
# ============================================================
st.markdown("""
<div class="report-section">
    <h2>📡 4. Sources les plus actives</h2>
</div>
""", unsafe_allow_html=True)

if top_sources:
    df_sources = pd.DataFrame(top_sources)
    df_sources["source_court"] = df_sources["source"].apply(lambda s: s[:30])

    fig_src = px.bar(
        df_sources.sort_values("nb_articles"),
        x="nb_articles",
        y="source_court",
        orientation="h",
        text="nb_articles",
        color="nb_articles",
        color_continuous_scale="Blues"
    )
    fig_src.update_traces(textposition="outside")
    fig_src.update_layout(
        height=350,
        xaxis_title="Articles",
        yaxis_title="",
        showlegend=False,
        coloraxis_showscale=False,
        margin=dict(l=10, r=10, t=20, b=10)
    )
    st.plotly_chart(fig_src, use_container_width=True)

    top_source = df_sources.iloc[0]
    st.markdown(f"""
    <div class="comment">
        📌 <b>Source la plus active</b> :
        <b>{top_source['source']}</b> avec <b>{top_source['nb_articles']} articles</b>.
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================
# SECTION 5 : PERSONNALITÉS POLITIQUES ⭐ NOUVEAU
# ============================================================
st.markdown("""
<div class="report-section">
    <h2>🏛️ 5. Personnalités politiques / الشخصيات السياسية</h2>
</div>
""", unsafe_allow_html=True)

if total_mentions > 0:
    # ---------- 5.1 — KPI ----------
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="report-kpi">
            <div class="report-kpi-value">{total_mentions}</div>
            <div class="report-kpi-label">📰 Mentions totales</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="report-kpi">
            <div class="report-kpi-value">{rep_genre['nb_hommes']}</div>
            <div class="report-kpi-label">👨 Hommes</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="report-kpi">
            <div class="report-kpi-value">{rep_genre['nb_femmes']}</div>
            <div class="report-kpi-label">👩 Femmes</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="report-kpi">
            <div class="report-kpi-value">{rep_genre['pct_femmes']}%</div>
            <div class="report-kpi-label">♀ Part des femmes</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ---------- 5.2 — Donut H/F + Top 10 ----------
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("#### ⚖️ Répartition Hommes / Femmes")
        fig_hf = go.Figure(data=[go.Pie(
            labels=["Hommes", "Femmes"],
            values=[rep_genre["hommes"], rep_genre["femmes"]],
            hole=0.55,
            marker=dict(colors=[COULEUR_HOMME, COULEUR_FEMME],
                        line=dict(color="white", width=3)),
            textinfo="label+percent",
            textfont=dict(size=13, color="white"),
        )])
        fig_hf.update_layout(
            height=350, showlegend=False,
            margin=dict(l=10, r=10, t=20, b=10),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            annotations=[dict(
                text=f"<b>{total_mentions}</b><br>mentions",
                x=0.5, y=0.5, font_size=16, showarrow=False,
                font=dict(family="Inter")
            )]
        )
        st.plotly_chart(fig_hf, use_container_width=True)

    with col2:
        st.markdown("#### 🏆 Top 10 des personnalités")
        if top_persos:
            df_top = pd.DataFrame(top_persos)
            df_top["couleur"] = df_top["genre"].apply(
                lambda g: COULEUR_HOMME if g == "homme" else COULEUR_FEMME
            )
            df_top = df_top.sort_values("pourcentage")

            fig_top = go.Figure()
            for _, row in df_top.iterrows():
                fig_top.add_trace(go.Bar(
                    y=[row["nom_fr"]],
                    x=[row["pourcentage"]],
                    orientation="h",
                    marker=dict(color=row["couleur"]),
                    text=f"{row['pourcentage']:.1f}%",
                    textposition="outside",
                    textfont=dict(size=12, color="#0f172a"),
                    showlegend=False,
                    hovertemplate=(
                        f"<b>{row['nom_fr']}</b><br>"
                        f"Part: {row['pourcentage']:.1f}%<br>"
                        f"Mentions: {row['mentions']}<br>"
                        f"AR: {row['mentions_ar']} | FR: {row['mentions_fr']}"
                        "<extra></extra>"
                    ),
                ))
            fig_top.update_layout(
                height=350,
                margin=dict(l=10, r=60, t=20, b=10),
                xaxis_title="Part des mentions (%)",
                xaxis=dict(range=[0, max(df_top["pourcentage"]) * 1.25],
                           showgrid=True, gridcolor="rgba(15,23,42,0.04)"),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter, sans-serif"),
            )
            st.plotly_chart(fig_top, use_container_width=True)

    # ---------- 5.3 — Tableau Top 10 ----------
    st.markdown("#### 📋 Tableau des personnalités")
    if top_persos:
        df_full = pd.DataFrame(top_persos)
        df_full = df_full[["nom_fr", "nom_ar", "genre", "parti",
                            "mentions", "mentions_ar", "mentions_fr", "pourcentage"]]
        df_full.columns = ["Nom (FR)", "Nom (AR)", "Genre", "Parti",
                           "Mentions", "AR", "FR", "%"]
        st.dataframe(df_full, use_container_width=True, hide_index=True)

    # ---------- 5.4 — Mentions par média ----------
    st.markdown("#### 📺 Mentions par média (Hommes / Femmes)")
    if par_media:
        df_media = pd.DataFrame(par_media).sort_values("total", ascending=True)

        fig_media = go.Figure()
        fig_media.add_trace(go.Bar(
            y=df_media["source"], x=df_media["pct_hommes"],
            name="Hommes", orientation="h",
            marker=dict(color=COULEUR_HOMME),
            text=df_media["pct_hommes"].apply(lambda v: f"{v:.0f}%"),
            textposition="inside",
            textfont=dict(size=11, color="white"),
        ))
        fig_media.add_trace(go.Bar(
            y=df_media["source"], x=df_media["pct_femmes"],
            name="Femmes", orientation="h",
            marker=dict(color=COULEUR_FEMME),
            text=df_media["pct_femmes"].apply(lambda v: f"{v:.0f}%"),
            textposition="inside",
            textfont=dict(size=11, color="white"),
        ))
        fig_media.update_layout(
            barmode="stack",
            height=max(300, len(df_media) * 35),
            margin=dict(l=10, r=10, t=20, b=10),
            xaxis_title="Répartition (%)",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02,
                        xanchor="right", x=1, font=dict(size=11)),
        )
        st.plotly_chart(fig_media, use_container_width=True)

    # ---------- 5.5 — Commentaire automatique ----------
    top_3 = top_persos[:3] if len(top_persos) >= 3 else top_persos
    noms_top = ", ".join([f"<b>{p['nom_fr']}</b> ({p['mentions']})" for p in top_3])

    st.markdown(f"""
    <div class="comment">
        📌 <b>Constat</b> : Sur <b>{total_mentions} mentions</b> de personnalités politiques
        dans les médias tunisiens, <b>{rep_genre['pct_hommes']}%</b> concernent des hommes
        et <b>{rep_genre['pct_femmes']}%</b> des femmes.
        Les 3 personnalités les plus citées sont : {noms_top}.
        La présence médiatique est <b>{"équilibrée" if abs(rep_genre['pct_hommes'] - rep_genre['pct_femmes']) < 10 else ("majoritairement masculine" if rep_genre['pct_hommes'] > rep_genre['pct_femmes'] else "majoritairement féminine")}</b>.
    </div>
    """, unsafe_allow_html=True)

else:
    st.info("Aucune mention de personnalité politique dans la période analysée.")

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================
# SECTION 6 : TOP ARTICLES
# ============================================================
st.markdown("""
<div class="report-section">
    <h2>🏆 6. Articles les plus pertinents</h2>
</div>
""", unsafe_allow_html=True)

if top_articles:
    for i, art in enumerate(top_articles, 1):
        emoji = EMOJIS_THEMES.get(art["theme"], "🌐")
        st.markdown(f"""
        <div style="padding: 12px; background: white; border-radius: 6px;
                    margin-bottom: 10px; border-left: 3px solid #e70013;">
            <div style="font-size: 0.75rem; color: #666;">
                {emoji} <b>{art['theme']}</b> • Score : <b>{art['score']:.2f}</b>
            </div>
            <div style="font-size: 1rem; margin-top: 5px; font-weight: 500;">
                {i}. {art['titre'][:120]}
            </div>
            <div style="font-size: 0.8rem; color: #888; margin-top: 5px;">
                📰 {art['source']}
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================
# SECTION 7 : METHODOLOGIE
# ============================================================
st.markdown("""
<div class="report-section">
    <h2>🔬 7. Méthodologie</h2>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background: white; padding: 20px; border-radius: 8px;">
<h3 style="color: #1a1a1a;">📡 Collecte des données</h3>
<p>Les articles sont collectés automatiquement via des flux RSS de <b>32 sources tunisiennes</b> (presse écrite, radios nationales et régionales).</p>

<h3 style="color: #1a1a1a; margin-top: 20px;">🎯 Analyse thématique</h3>
<p>Chaque article est analysé pour détecter <b>7 thèmes sociétaux</b> :</p>
<ul>
<li>⚖️ Violence contre les femmes</li>
<li>🚨 Discours de haine</li>
<li>👩 Présence des femmes</li>
<li>👥 Présence des handicapés</li>
<li>🧑 Présence des jeunes</li>
<li>🏛️ Équilibre politique</li>
<li>🗺️ Équilibre régional</li>
</ul>

<h3 style="color: #1a1a1a; margin-top: 20px;">🏛️ Analyse des personnalités politiques</h3>
<p><b>40 personnalités politiques tunisiennes</b> sont suivies (25 hommes, 15 femmes). L'analyse détecte leurs mentions dans les articles via :</p>
<ul>
<li>Recherche en <b>français</b> (avec variantes d'accents)</li>
<li>Recherche en <b>arabe</b> (variantes chadda, alif hamza, ta marbouta)</li>
<li><b>Recherche stricte</b> pour éviter les faux positifs (noms courts)</li>
<li>Répartition par <b>genre</b>, <b>média</b> et <b>parti politique</b></li>
</ul>

<h3 style="color: #1a1a1a; margin-top: 20px;">🌍 Multilinguisme</h3>
<p>L'analyse est effectuée en <b>4 langues</b> : Français, Arabe standard (فصحى), Arabe tunisien (دارجة), Arabizi. Un dictionnaire de <b>600+ mots-clés</b> est utilisé pour la détection.</p>

<h3 style="color: #1a1a1a; margin-top: 20px;">💭 Analyse de sentiment</h3>
<p>Le sentiment (positif / neutre / négatif) est calculé via une méthode à base de <b>dictionnaires pondérés</b> de mots positifs et négatifs, adaptée au contexte tunisien.</p>

<h3 style="color: #1a1a1a; margin-top: 20px;">⚠️ Limites</h3>
<p>Les analyses reflètent <b>uniquement</b> les sources collectées. Les scores sont <b>indicatifs</b> et non des vérités absolues. La détection automatique peut générer des <b>faux positifs</b>. Le contexte humain reste indispensable pour interpréter les résultats.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# ============================================================
# PIED DE PAGE DU RAPPORT
# ============================================================
st.markdown(f"""
<div class="report-footer">
    <b>🇹🇳 TuniWatch</b> — Observatoire des médias tunisiens<br>
    Rapport généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}<br>
    © 2026 Khadraoui Mongi — Tous droits réservés
</div>
""", unsafe_allow_html=True)

# ============================================================
# BOUTON IMPRIMER (EN BAS)
# ============================================================
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("""
    <div style="text-align: center; padding: 20px; background: #e70013;
                border-radius: 8px; color: white; margin-top: 30px;">
        <h3 style="margin: 0; color: white;">📄 Prêt à imprimer ?</h3>
        <p style="margin: 10px 0 0 0; font-size: 1.1rem;">
            Appuyez sur <b>Ctrl + P</b> pour générer le PDF
        </p>
    </div>
    """, unsafe_allow_html=True)