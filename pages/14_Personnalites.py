"""
Page 14_Personnalites.py - Analyse des personnalités politiques
Version 3.0 - Pourcentages + Cache + Priorité arabe
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from politiques_stats import (
    top_personnalites,
    repartition_genre,
    mentions_par_genre_et_media,
    mentions_par_parti,
    comparer_personnalites,
    liste_personnalites,
    stats_globales,
)

st.set_page_config(
    page_title="Personnalités politiques - TuniWatch",
    page_icon="🏛️",
    layout="wide",
)

COULEUR_HOMME = "#1D3557"
COULEUR_FEMME = "#EF476F"


# ============================================================
# FONCTIONS AVEC CACHE
# ============================================================
@st.cache_data(ttl=300, show_spinner=False)
def cached_top(limite, jours):
    return top_personnalites(limite, jours=jours)


@st.cache_data(ttl=300, show_spinner=False)
def cached_repartition(jours):
    return repartition_genre(jours=jours)


@st.cache_data(ttl=300, show_spinner=False)
def cached_media(limite, jours):
    return mentions_par_genre_et_media(limite, jours=jours)


@st.cache_data(ttl=300, show_spinner=False)
def cached_parti(jours):
    return mentions_par_parti(jours=jours)


@st.cache_data(ttl=300, show_spinner=False)
def cached_stats():
    return stats_globales()


@st.cache_data(ttl=300, show_spinner=False)
def cached_personnalites():
    return liste_personnalites()


@st.cache_data(ttl=300, show_spinner=False)
def cached_comparaison(noms_tuple, jours):
    return comparer_personnalites(list(noms_tuple), jours=jours)


# ============================================================
# EN-TÊTE
# ============================================================
st.title("🏛️ Personnalités politiques / الشخصيات السياسية")
st.markdown("""
<div style="background: linear-gradient(90deg, #E63946 0%, #1D3557 100%);
            padding: 15px; border-radius: 8px; color: white; margin-bottom: 20px;">
    <h4 style="margin: 0; color: white;">📊 Présence des personnalités politiques dans les médias tunisiens</h4>
    <p style="margin: 5px 0 0 0; font-size: 0.95rem;">
        Comparaison Hommes / Femmes — par média — par langue — par parti
    </p>
</div>
""", unsafe_allow_html=True)


# ============================================================
# FILTRES
# ============================================================
col_f1, col_f2, col_f3 = st.columns([1, 1, 2])

with col_f1:
    periode = st.selectbox(
        "📅 Période",
        options=[None, 7, 30, 90],
        format_func=lambda x: "Toutes les dates" if x is None else f"{x} derniers jours",
        index=0,
    )

with col_f2:
    limite_medias = st.selectbox(
        "📺 Nb médias",
        options=[5, 10, 15, 20],
        index=1,
    )

with col_f3:
    st.write("")


# ============================================================
# CHARGEMENT AVEC CACHE
# ============================================================
with st.spinner("Chargement des données (première fois ~15 sec)..."):
    top, total_mentions = cached_top(10, periode)
    rep = cached_repartition(periode)
    par_media = cached_media(limite_medias, periode)
    par_parti = cached_parti(periode)
    stats = cached_stats()


# ============================================================
# KPI
# ============================================================
st.markdown("---")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("📰 Total mentions", total_mentions)
with col2:
    st.metric("👨 Hommes", f"{rep['hommes']} ({rep['pct_hommes']}%)",
              f"{rep['nb_hommes']} personnalités", delta_color="off")
with col3:
    st.metric("👩 Femmes", f"{rep['femmes']} ({rep['pct_femmes']}%)",
              f"{rep['nb_femmes']} personnalités", delta_color="off")
with col4:
    st.metric("🏛️ Actives", stats.get("total_personnalites", 0))
with col5:
    st.metric("📚 Articles base", stats.get("total_articles", 0))

st.markdown("---")


# ============================================================
# SECTION 1 — TOP 10 (UNIQUEMENT LES POURCENTAGES)
# ============================================================
st.subheader("les 10 premières personnalités politiques")

if not top:
    st.warning("Aucune mention de personnalité politique sur cette période.")
else:
    df_top = pd.DataFrame(top).sort_values("pourcentage", ascending=True)
    df_top["couleur"] = df_top["genre"].apply(
        lambda g: COULEUR_HOMME if g == "homme" else COULEUR_FEMME
    )

    fig_top = go.Figure()
    for _, row in df_top.iterrows():
        fig_top.add_trace(go.Bar(
            y=[row["nom_fr"]],
            x=[row["pourcentage"]],
            orientation="h",
            marker=dict(color=row["couleur"]),
            text="{}%".format(round(row["pourcentage"], 1)),
            textposition="outside",
            textfont=dict(size=14, color="#1D3557"),
            showlegend=False,
            hovertemplate=(
                f"<b>{row['nom_fr']}</b><br>"
                f"Genre: {'Homme' if row['genre'] == 'homme' else 'Femme'}<br>"
                f"Parti: {row.get('parti') or 'N/A'}<br>"
                f"Fonction: {row.get('fonction') or 'N/A'}<br>"
                f"<b>Part: {row['pourcentage']:.1f}%</b><br>"
                f"Mentions: {row['mentions']}<br>"
                f"🇸🇦 AR: {row['mentions_ar']} | 🇫🇷 FR: {row['mentions_fr']}"
                "<extra></extra>"
            ),
        ))
    fig_top.update_layout(
        height=max(400, len(df_top) * 50),
        margin=dict(l=20, r=100, t=20, b=20),
        xaxis_title="Part des mentions (%)",
        xaxis=dict(range=[0, max(df_top["pourcentage"]) * 1.25]),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif"),
    )
    st.plotly_chart(fig_top, use_container_width=True)

st.markdown("---")


# ============================================================
# SECTION 2 — H/F + DÉTAILS
# ============================================================
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("⚖️ Répartition Hommes / Femmes")

    fig_pie = go.Figure(data=[go.Pie(
        labels=["Hommes", "Femmes"],
        values=[rep["hommes"], rep["femmes"]],
        hole=0.5,
        marker=dict(colors=[COULEUR_HOMME, COULEUR_FEMME]),
        textinfo="label+percent",
        textfont=dict(size=13, color="white"),
    )])
    fig_pie.update_layout(
        height=350, showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        annotations=[dict(text=f"<b>{total_mentions}</b><br>mentions",
                          x=0.5, y=0.5, font_size=16, showarrow=False)],
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col_right:
    st.subheader("📊 Détails par genre")
    df_genre = pd.DataFrame({
        "Genre": ["Hommes", "Femmes"],
        "Mentions": [rep["hommes"], rep["femmes"]],
        "Pourcentage": [rep["pct_hommes"], rep["pct_femmes"]],
        "Personnalités": [rep["nb_hommes"], rep["nb_femmes"]],
    })
    st.dataframe(
        df_genre, use_container_width=True, hide_index=True,
        column_config={
            "Pourcentage": st.column_config.ProgressColumn(
                format="%.1f%%", min_value=0, max_value=100),
        }
    )

st.markdown("---")


# ============================================================
# SECTION 3 — PAR MÉDIA
# ============================================================
st.subheader("📺 Mentions par média (Hommes / Femmes)")

if not par_media:
    st.info("Aucune donnée par média.")
else:
    df_media = pd.DataFrame(par_media).sort_values("total", ascending=True)

    fig_media = go.Figure()
    fig_media.add_trace(go.Bar(
        y=df_media["source"], x=df_media["pct_hommes"],
        name="Hommes", orientation="h",
        marker=dict(color=COULEUR_HOMME),
        text=df_media["pct_hommes"].apply(lambda v: f"{v:.0f}%"),
        textposition="inside",
        hovertemplate="<b>%{y}</b><br>Hommes: %{x:.1f}%<extra></extra>",
    ))
    fig_media.add_trace(go.Bar(
        y=df_media["source"], x=df_media["pct_femmes"],
        name="Femmes", orientation="h",
        marker=dict(color=COULEUR_FEMME),
        text=df_media["pct_femmes"].apply(lambda v: f"{v:.0f}%"),
        textposition="inside",
        hovertemplate="<b>%{y}</b><br>Femmes: %{x:.1f}%<extra></extra>",
    ))
    fig_media.update_layout(
        barmode="stack",
        height=max(400, len(df_media) * 40),
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis_title="Répartition (%)",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                    xanchor="right", x=1),
    )
    st.plotly_chart(fig_media, use_container_width=True)

    with st.expander("📋 Voir le tableau détaillé par média"):
        df_table = df_media[["source", "hommes", "femmes", "total",
                             "pct_hommes", "pct_femmes"]].copy()
        df_table.columns = ["Média", "Hommes", "Femmes", "Total", "% H", "% F"]
        df_table = df_table.sort_values("Total", ascending=False)
        st.dataframe(df_table, use_container_width=True, hide_index=True)

st.markdown("---")


# ============================================================
# SECTION 4 — PAR PARTI
# ============================================================
st.subheader("🏛️ Répartition par parti politique")

if not par_parti:
    st.info("Aucune donnée par parti.")
else:
    df_parti = pd.DataFrame(par_parti).sort_values("total", ascending=True)

    fig_parti = go.Figure()
    fig_parti.add_trace(go.Bar(
        y=df_parti["parti"], x=df_parti["hommes"],
        name="Hommes", orientation="h",
        marker=dict(color=COULEUR_HOMME),
        text=df_parti["hommes"].apply(lambda v: str(v)),
        textposition="inside",
    ))
    fig_parti.add_trace(go.Bar(
        y=df_parti["parti"], x=df_parti["femmes"],
        name="Femmes", orientation="h",
        marker=dict(color=COULEUR_FEMME),
        text=df_parti["femmes"].apply(lambda v: str(v)),
        textposition="inside",
    ))
    fig_parti.update_layout(
        barmode="stack",
        height=max(300, len(df_parti) * 40),
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis_title="Mentions",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                    xanchor="right", x=1),
    )
    st.plotly_chart(fig_parti, use_container_width=True)

st.markdown("---")


# ============================================================
# SECTION 5 — COMPARAISON
# ============================================================
st.subheader("🔍 Comparaison entre personnalités")

toutes_persos = [p["nom_fr"] for p in cached_personnalites()]

col_c1, col_c2 = st.columns([3, 1])

with col_c1:
    noms_selectionnes = st.multiselect(
        "Sélectionnez 2 à 5 personnalités :",
        options=toutes_persos,
        default=["Kaïs Saïed", "Abir Moussi"] if "Kaïs Saïed" in toutes_persos and "Abir Moussi" in toutes_persos else [],
        max_selections=5,
    )

with col_c2:
    st.write("")
    st.write("")
    if st.button("🔄 Rafraîchir"):
        st.cache_data.clear()
        st.rerun()

if noms_selectionnes and len(noms_selectionnes) >= 2:
    comparaison = cached_comparaison(tuple(noms_selectionnes), periode)

    if comparaison:
        df_comp = pd.DataFrame(comparaison)
        df_comp["couleur"] = df_comp["genre"].apply(
            lambda g: COULEUR_HOMME if g == "homme" else COULEUR_FEMME
        )

        fig_comp = go.Figure()
        for _, row in df_comp.iterrows():
            fig_comp.add_trace(go.Bar(
                x=[row["nom_fr"]],
                y=[row["pourcentage"]],
                marker=dict(color=row["couleur"]),
                text="{}%".format(round(row["pourcentage"], 1)),
                textposition="outside",
                showlegend=False,
                hovertemplate=(
                    f"<b>{row['nom_fr']}</b><br>"
                    f"Parti: {row.get('parti') or 'N/A'}<br>"
                    f"Part: {row['pourcentage']:.1f}%<br>"
                    f"Mentions: {row['mentions']}<br>"
                    f"🇸🇦 AR: {row['mentions_ar']} | 🇫🇷 FR: {row['mentions_fr']}"
                    "<extra></extra>"
                ),
            ))
        fig_comp.update_layout(
            height=400,
            margin=dict(l=20, r=20, t=40, b=20),
            yaxis_title="Part des mentions (%)",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif"),
        )
        st.plotly_chart(fig_comp, use_container_width=True)

st.markdown("---")


# ============================================================
# SECTION 6 — TABLEAU COMPLET
# ============================================================
st.subheader("📋 Tableau complet")

if top:
    df_full = pd.DataFrame(top)
    df_full = df_full[[
        "nom_fr", "nom_ar", "genre", "parti", "fonction",
        "mentions", "mentions_ar", "mentions_fr", "pourcentage"
    ]]
    df_full.columns = [
        "Nom (FR)", "Nom (AR)", "Genre", "Parti", "Fonction",
        "Mentions", "AR", "FR", "%"
    ]
    st.dataframe(df_full, use_container_width=True, hide_index=True)


# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888; padding: 20px; font-size: 0.85rem;">
    <b>🇹🇳 TuniWatch</b> — Observatoire des médias tunisiens<br>
    Analyse des personnalités politiques — Données en temps réel<br>
    © 2026 Khadraoui Mongi
</div>
""", unsafe_allow_html=True)