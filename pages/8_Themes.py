"""
Page Themes - Analyse des themes detectes dans les articles
Etape D - Session 1
"""
import stats_themes_sentiments
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
import analyzer
import style
style.appliquer_style()
# Configuration
st.set_page_config(
    page_title="Themes - Monitoring",
    page_icon="📊",
    layout="wide"
)

# Protection
auth.require_login()

# ============================================================
# PALETTE DE COULEURS PAR THEME
# ============================================================
COULEURS_THEMES = {
    "violence_femmes": "#e74c3c",       # Rouge
    "discours_haine": "#c0392b",         # Rouge fonce
    "presence_femmes": "#9b59b6",        # Violet
    "presence_handicapes": "#3498db",    # Bleu
    "presence_jeunes": "#f39c12",        # Orange
    "equilibre_politique": "#2c3e50",    # Bleu fonce
    "equilibre_regional": "#27ae60"      # Vert
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
# FONCTIONS DE LECTURE
# ============================================================
def get_stats_globales():
    """Statistiques globales de l'analyse."""
    conn = analyzer.get_connexion()
    if conn is None:
        return {}
    curseur = conn.cursor(dictionary=True)
    try:
        curseur.execute("""
            SELECT 
                COUNT(*) AS total_analyses,
                COUNT(DISTINCT article_id) AS total_articles_classes,
                COUNT(DISTINCT theme) AS total_themes,
                AVG(score) AS score_moyen,
                MAX(score) AS score_max
            FROM articles_themes
        """)
        return curseur.fetchone()
    finally:
        curseur.close()
        conn.close()


def get_stats_par_theme():
    """Statistiques detaillees par theme."""
    conn = analyzer.get_connexion()
    if conn is None:
        return []
    curseur = conn.cursor(dictionary=True)
    try:
        curseur.execute("""
            SELECT 
                theme,
                COUNT(DISTINCT article_id) AS nb_articles,
                ROUND(AVG(score), 2) AS score_moyen,
                ROUND(MAX(score), 2) AS score_max,
                SUM(nb_mots_trouves) AS total_mots
            FROM articles_themes
            GROUP BY theme
            ORDER BY nb_articles DESC
        """)
        return curseur.fetchall()
    finally:
        curseur.close()
        conn.close()


def get_top_articles(limite=15):
    """Articles les plus pertinents (tous themes confondus)."""
    conn = analyzer.get_connexion()
    if conn is None:
        return []
    curseur = conn.cursor(dictionary=True)
    try:
        curseur.execute("""
            SELECT 
                a.id,
                a.titre,
                a.source,
                a.url,
                at.theme,
                at.score,
                at.mots_trouves,
                a.date_publication
            FROM articles_themes at
            JOIN articles a ON a.id = at.article_id
            ORDER BY at.score DESC
            LIMIT %s
        """, (limite,))
        return curseur.fetchall()
    finally:
        curseur.close()
        conn.close()


def get_articles_par_theme(theme, limite=20):
    """Articles d'un theme specifique."""
    conn = analyzer.get_connexion()
    if conn is None:
        return []
    curseur = conn.cursor(dictionary=True)
    try:
        curseur.execute("""
            SELECT 
                a.id,
                a.titre,
                a.source,
                a.url,
                at.score,
                at.mots_trouves,
                a.date_publication
            FROM articles_themes at
            JOIN articles a ON a.id = at.article_id
            WHERE at.theme = %s
            ORDER BY at.score DESC
            LIMIT %s
        """, (theme, limite))
        return curseur.fetchall()
    finally:
        curseur.close()
        conn.close()


# ============================================================
# EN-TETE
# ============================================================
st.title("📊 Analyse par thème")
st.caption("Détection automatique des thèmes dans les médias tunisiens")

st.markdown("---")

# ============================================================
# SECTION 1 : KPIs GLOBAUX
# ============================================================
stats = get_stats_globales()

if not stats or stats["total_analyses"] == 0:
    st.warning("⚠️ Aucune analyse disponible pour le moment.")
    st.info(
        "💡 Allez sur la page **📝 Mots Cles** pour ajouter des mots-clés, "
        "puis lancez `analyser_tout.py` pour analyser les articles."
    )
    st.stop()

st.subheader("🎯 Indicateurs globaux")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("📰 Articles classés", stats["total_articles_classes"])
col2.metric("🏷️ Thèmes actifs", stats["total_themes"])
col3.metric("🔍 Analyses totales", stats["total_analyses"])
col4.metric("📊 Score moyen", f"{stats['score_moyen']:.2f}")
col5.metric("🏆 Score max", f"{stats['score_max']:.2f}")

st.markdown("---")

# ============================================================
# SECTION 2 : REPARTITION PAR THEME (CAMEMBERT + BARRES)
# ============================================================
st.subheader("📈 Répartition par thème")

stats_themes = get_stats_par_theme()

if stats_themes:
    df_themes = pd.DataFrame(stats_themes)

    # Ajouter emoji + couleur
    df_themes["emoji"] = df_themes["theme"].apply(lambda t: EMOJIS_THEMES.get(t, "🌐"))
    df_themes["label"] = df_themes["emoji"] + " " + df_themes["theme"]
    df_themes["couleur"] = df_themes["theme"].apply(lambda t: COULEURS_THEMES.get(t, "#95a5a6"))

    col1, col2 = st.columns([1, 1])

    with col1:
        # --- Camembert ---
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
            height=400,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        # --- Barres horizontales ---
        fig_bar = px.bar(
            df_themes.sort_values("nb_articles"),
            x="nb_articles",
            y="label",
            orientation="h",
            color="nb_articles",
            color_continuous_scale="Blues",
            text="nb_articles"
        )
        fig_bar.update_traces(textposition="outside")
        fig_bar.update_layout(
            height=400,
            xaxis_title="Nombre d'articles",
            yaxis_title="",
            showlegend=False,
            coloraxis_showscale=False,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")

    # ============================================================
    # SECTION 3 : TABLEAU DETAILLE
    # ============================================================
    st.subheader("📋 Tableau détaillé par thème")

    df_tableau = df_themes[["emoji", "theme", "nb_articles", "score_moyen", "score_max", "total_mots"]].copy()
    df_tableau.columns = ["", "Thème", "Articles", "Score moyen", "Score max", "Mots trouvés"]

    st.dataframe(
        df_tableau,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    # ============================================================
    # SECTION 4 : TOP ARTICLES
    # ============================================================
    st.subheader("🏆 Top 15 des articles les plus pertinents")

    top_articles = get_top_articles(15)

    if top_articles:
        for i, art in enumerate(top_articles, 1):
            emoji = EMOJIS_THEMES.get(art["theme"], "🌐")
            couleur = COULEURS_THEMES.get(art["theme"], "#95a5a6")

            with st.container():
                col1, col2 = st.columns([4, 1])

                with col1:
                    # Titre avec emoji du theme
                    if art["url"]:
                        st.markdown(f"**{i}. {emoji} [{art['titre']}]({art['url']})**")
                    else:
                        st.markdown(f"**{i}. {emoji} {art['titre']}**")

                    st.caption(
                        f"📰 **{art['source']}** • "
                        f"🏷️ `{art['theme']}` • "
                        f"🔑 {art['mots_trouves'][:80]}"
                    )

                with col2:
                    st.metric("Score", f"{art['score']:.1f}", label_visibility="collapsed")

                st.markdown("---")

    st.markdown("---")

    # ============================================================
    # SECTION 5 : DETAIL PAR THEME (EXPANDABLE)
    # ============================================================
    st.subheader("🔍 Détail par thème")

    for row in stats_themes:
        theme = row["theme"]
        emoji = EMOJIS_THEMES.get(theme, "🌐")

        with st.expander(f"{emoji} **{theme}** — {row['nb_articles']} article(s) • score moyen {row['score_moyen']}"):
            articles_theme = get_articles_par_theme(theme, 20)

            if not articles_theme:
                st.info("Aucun article dans ce thème.")
                continue

            for i, art in enumerate(articles_theme, 1):
                col1, col2 = st.columns([4, 1])

                with col1:
                    if art["url"]:
                        st.markdown(f"**{i}.** [{art['titre']}]({art['url']})")
                    else:
                        st.markdown(f"**{i}.** {art['titre']}")
                    st.caption(
                        f"📰 {art['source']} • "
                        f"🔑 {art['mots_trouves'][:100]}"
                    )

                with col2:
                    st.metric("Score", f"{art['score']:.1f}", label_visibility="collapsed")

                if i < len(articles_theme):
                    st.markdown("")

else:
    st.warning("Aucune statistique par thème disponible.")

st.markdown("---")

# ============================================================
# SECTION 6 : ACTIONS
# ============================================================
st.subheader("🔄 Actions")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔄 Rafraîchir", use_container_width=True):
        st.rerun()

with col2:
    # Export CSV
    if stats_themes:
        csv = df_themes.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Export CSV",
            data=csv,
            file_name=f"themes_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True
        )

with col3:
    st.caption(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}")

st.markdown("---")
# ============================================================
# SECTION 7 : SENTIMENTS PAR THEME
# ============================================================
st.markdown("---")
st.subheader("😊 Sentiments par thème")

detail = stats_themes_sentiments.stats_par_theme_detail()

if detail:
    df_detail = pd.DataFrame(detail)

    # --- Graphique 1 : Sentiment par thème (barres empilées) ---
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("#### Répartition des sentiments")

        df_stack = df_detail[["theme", "nb_positifs", "nb_neutres", "nb_negatifs"]].copy()
        df_stack = df_stack.melt(
            id_vars="theme",
            var_name="sentiment",
            value_name="nb"
        )
        df_stack["sentiment"] = df_stack["sentiment"].replace({
            "nb_positifs": "Positifs",
            "nb_neutres": "Neutres",
            "nb_negatifs": "Négatifs"
        })

        fig_stack = px.bar(
            df_stack,
            x="theme",
            y="nb",
            color="sentiment",
            color_discrete_map={
                "Positifs": "#27ae60",
                "Neutres": "#f39c12",
                "Négatifs": "#e74c3c"
            },
            barmode="stack",
            labels={"theme": "Thème", "nb": "Nombre d'articles", "sentiment": "Sentiment"}
        )
        fig_stack.update_layout(
            height=400,
            xaxis_tickangle=-30,
            margin=dict(l=20, r=20, t=20, b=100)
        )
        st.plotly_chart(fig_stack, use_container_width=True)

    with col2:
        st.markdown("#### Score de sentiment par thème")
        st.caption("Positif (+1) / Neutre (0) / Négatif (-1)")

        df_score = df_detail.sort_values("score_moyen_sentiment")
        
        def couleur_score(score):
            if score > 0.1:
                return "#27ae60"
            elif score < -0.1:
                return "#e74c3c"
            return "#f39c12"

        df_score["couleur"] = df_score["score_moyen_sentiment"].apply(couleur_score)

        fig_score = go.Figure(go.Bar(
            x=df_score["score_moyen_sentiment"],
            y=df_score["theme"],
            orientation="h",
            marker_color=df_score["couleur"],
            text=df_score["score_moyen_sentiment"].round(2),
            textposition="outside"
        ))
        fig_score.update_layout(
            height=400,
            xaxis_title="Score moyen",
            yaxis_title="",
            xaxis=dict(range=[-1, 1]),
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig_score, use_container_width=True)

    # --- Tableau détaillé ---
    st.markdown("#### Tableau récapitulatif")

    df_table = df_detail.copy()
    df_table.columns = ["Thème", "Articles", "Score sentiment", "🟢 Positifs", "🟡 Neutres", "🔴 Négatifs"]
    df_table = df_table.sort_values("Articles", ascending=False)

    st.dataframe(df_table, use_container_width=True, hide_index=True)

    # --- Langues par thème ---
    st.markdown("#### Répartition linguistique par thème")

    langue_data = stats_themes_sentiments.stats_par_langue_theme()

    if langue_data:
        df_langue = pd.DataFrame(langue_data)

        fig_langue = px.bar(
            df_langue,
            x="theme",
            y="nb",
            color="langue",
            barmode="group",
            text="nb",
            labels={"theme": "Thème", "nb": "Articles", "langue": "Langue"},
            color_discrete_map={"fr": "#3498db", "ar": "#e67e22", "inconnu": "#95a5a6"}
        )
        fig_langue.update_layout(
            height=400,
            xaxis_tickangle=-30,
            margin=dict(l=20, r=20, t=20, b=100)
        )
        st.plotly_chart(fig_langue, use_container_width=True)
else:
    st.info("Aucune donnée de sentiment liée aux thèmes.")
    st.caption("💡 Lancez `analyser_sentiment.py` puis relancez l'analyse des thèmes.")
st.caption("Page Thèmes — Version 0.1 | Observatoire des médias tunisiens")
style.footer()