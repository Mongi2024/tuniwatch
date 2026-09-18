"""
Page Sentiments - Analyse visuelle des sentiments
Etape F - Session 2 (version PostgreSQL compatible)
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
import sentiment_analyzer

# Configuration
st.set_page_config(
    page_title="Sentiments - TuniWatch",
    page_icon="😊",
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

EMOJIS_SENTIMENT = {
    "positif": "🟢",
    "neutre": "🟡",
    "negatif": "🔴"
}


# ============================================================
# FONCTIONS DE LECTURE
# ============================================================
def get_stats_globales():
    """Stats globales de sentiment (compatible PostgreSQL)."""
    conn = sentiment_analyzer.get_connexion()
    if conn is None:
        return {}
    curseur = conn.cursor(dictionary=True)
    try:
        # Pas de ROUND dans le SQL (compatible PostgreSQL/MySQL/SQLite)
        curseur.execute("""
            SELECT 
                COUNT(*) AS total,
                SUM(CASE WHEN sentiment = 'positif' THEN 1 ELSE 0 END) AS positifs,
                SUM(CASE WHEN sentiment = 'neutre' THEN 1 ELSE 0 END) AS neutres,
                SUM(CASE WHEN sentiment = 'negatif' THEN 1 ELSE 0 END) AS negatifs,
                AVG(score) AS score_moyen
            FROM articles_sentiment
        """)
        result = curseur.fetchone()
        if result:
            return {
                "total": int(result.get("total") or 0),
                "positifs": int(result.get("positifs") or 0),
                "neutres": int(result.get("neutres") or 0),
                "negatifs": int(result.get("negatifs") or 0),
                "score_moyen": round(float(result.get("score_moyen") or 0), 2)
            }
        return {}
    finally:
        curseur.close()
        conn.close()


def get_stats_par_langue():
    """Repartition par langue."""
    conn = sentiment_analyzer.get_connexion()
    if conn is None:
        return []
    curseur = conn.cursor(dictionary=True)
    try:
        curseur.execute("""
            SELECT 
                langue_detectee AS langue,
                sentiment,
                COUNT(*) AS nb
            FROM articles_sentiment
            GROUP BY langue_detectee, sentiment
            ORDER BY langue_detectee, sentiment
        """)
        rows = curseur.fetchall()
        return [
            {
                "langue": r["langue"],
                "sentiment": r["sentiment"],
                "nb": int(r["nb"])
            }
            for r in rows
        ]
    finally:
        curseur.close()
        conn.close()


def get_top_articles(sentiment, limite=10):
    """Top articles par sentiment."""
    conn = sentiment_analyzer.get_connexion()
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
                s.score,
                s.confiance,
                s.langue_detectee
            FROM articles_sentiment s
            JOIN articles a ON a.id = s.article_id
            WHERE s.sentiment = %s
            ORDER BY ABS(s.score) DESC, s.confiance DESC
            LIMIT %s
        """, (sentiment, limite))
        rows = curseur.fetchall()
        return [
            {
                "id": int(r["id"]),
                "titre": r["titre"],
                "source": r["source"],
                "url": r["url"],
                "score": float(r["score"] or 0),
                "confiance": float(r["confiance"] or 0),
                "langue_detectee": r["langue_detectee"]
            }
            for r in rows
        ]
    finally:
        curseur.close()
        conn.close()


def get_evolution_temporelle():
    """Evolution du sentiment par jour."""
    conn = sentiment_analyzer.get_connexion()
    if conn is None:
        return []
    curseur = conn.cursor(dictionary=True)
    try:
        curseur.execute("""
            SELECT 
                DATE(a.date_ajout) AS jour,
                s.sentiment,
                COUNT(*) AS nb
            FROM articles_sentiment s
            JOIN articles a ON a.id = s.article_id
            WHERE a.date_ajout IS NOT NULL
            GROUP BY DATE(a.date_ajout), s.sentiment
            ORDER BY jour, s.sentiment
        """)
        rows = curseur.fetchall()
        return [
            {
                "jour": str(r["jour"]),
                "sentiment": r["sentiment"],
                "nb": int(r["nb"])
            }
            for r in rows
        ]
    finally:
        curseur.close()
        conn.close()


# ============================================================
# EN-TETE
# ============================================================
st.title("😊 Analyse de sentiment")
st.caption("Détection automatique du ton émotionnel des articles")

st.markdown("---")

# ============================================================
# SECTION 1 : KPIs
# ============================================================
stats = get_stats_globales()

if not stats or stats["total"] == 0:
    st.warning("⚠️ Aucune analyse de sentiment disponible.")
    st.info("💡 Lancez `analyser_sentiment.py` pour analyser les articles.")
    st.stop()

st.subheader("🎯 Vue d'ensemble")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("📰 Articles analysés", stats["total"])
col2.metric("🟢 Positifs", stats["positifs"], 
            delta=f"{stats['positifs']/stats['total']*100:.0f}%")
col3.metric("🟡 Neutres", stats["neutres"],
            delta=f"{stats['neutres']/stats['total']*100:.0f}%")
col4.metric("🔴 Négatifs", stats["negatifs"],
            delta=f"{stats['negatifs']/stats['total']*100:.0f}%")
col5.metric("📊 Score moyen", f"{stats['score_moyen']:.2f}")

st.markdown("---")

# ============================================================
# SECTION 2 : REPARTITION (Camembert + Jauge)
# ============================================================
st.subheader("📈 Répartition des sentiments")

col1, col2 = st.columns([1, 1])

with col1:
    df_pie = pd.DataFrame({
        "Sentiment": ["Positif", "Neutre", "Négatif"],
        "Nombre": [stats["positifs"], stats["neutres"], stats["negatifs"]]
    })

    fig_pie = px.pie(
        df_pie,
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
        textinfo="percent+label+value",
        hovertemplate="<b>%{label}</b><br>%{value} articles<br>%{percent}<extra></extra>"
    )
    fig_pie.update_layout(
        showlegend=False,
        height=400,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    score_global = stats["score_moyen"]
    
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score_global,
        domain={"x": [0, 1], "y": [0, 1]},
        title={"text": "Sentiment global", "font": {"size": 20}},
        delta={"reference": 0},
        gauge={
            "axis": {"range": [-1, 1], "tickwidth": 1},
            "bar": {"color": COULEURS_SENTIMENT["neutre"], "thickness": 0.3},
            "steps": [
                {"range": [-1, -0.2], "color": "#fadbd8"},
                {"range": [-0.2, 0.2], "color": "#fcf3cf"},
                {"range": [0.2, 1], "color": "#d5f4e6"}
            ],
            "threshold": {
                "line": {"color": "red", "width": 4},
                "thickness": 0.75,
                "value": score_global
            }
        },
        number={"font": {"size": 50}}
    ))
    fig_gauge.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=60, b=20)
    )
    st.plotly_chart(fig_gauge, use_container_width=True)

st.markdown("---")

# ============================================================
# SECTION 3 : REPARTITION PAR LANGUE
# ============================================================
st.subheader("🌍 Répartition par langue")

stats_langue = get_stats_par_langue()

if stats_langue:
    df_langue = pd.DataFrame(stats_langue)

    fig_langue = px.bar(
        df_langue,
        x="langue",
        y="nb",
        color="sentiment",
        color_discrete_map=COULEURS_SENTIMENT,
        barmode="group",
        text="nb",
        labels={"langue": "Langue", "nb": "Nombre d'articles", "sentiment": "Sentiment"}
    )
    fig_langue.update_traces(textposition="outside")
    fig_langue.update_layout(
        height=350,
        xaxis_title="Langue détectée",
        yaxis_title="Nombre d'articles",
        margin=dict(l=20, r=20, t=20, b=20)
    )
    st.plotly_chart(fig_langue, use_container_width=True)
else:
    st.info("Pas de données par langue.")

st.markdown("---")

# ============================================================
# SECTION 4 : TOP ARTICLES
# ============================================================
st.subheader("🏆 Articles les plus marquants")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🟢 Top 10 positifs")
    top_positifs = get_top_articles("positif", 10)

    for i, art in enumerate(top_positifs, 1):
        emoji_langue = {"fr": "🇫🇷", "ar": "🇹🇳", "inconnu": "🌐"}.get(art["langue_detectee"], "🌐")
        
        with st.container():
            if art["url"]:
                st.markdown(f"**{i}.** {emoji_langue} [{art['titre'][:80]}...]({art['url']})")
            else:
                st.markdown(f"**{i}.** {emoji_langue} {art['titre'][:80]}...")
            st.caption(f"📰 {art['source']} • Score : **{art['score']:.2f}** • Confiance : {art['confiance']:.2f}")

with col2:
    st.markdown("### 🔴 Top 10 négatifs")
    top_negatifs = get_top_articles("negatif", 10)

    for i, art in enumerate(top_negatifs, 1):
        emoji_langue = {"fr": "🇫🇷", "ar": "🇹🇳", "inconnu": "🌐"}.get(art["langue_detectee"], "🌐")
        
        with st.container():
            if art["url"]:
                st.markdown(f"**{i}.** {emoji_langue} [{art['titre'][:80]}...]({art['url']})")
            else:
                st.markdown(f"**{i}.** {emoji_langue} {art['titre'][:80]}...")
            st.caption(f"📰 {art['source']} • Score : **{art['score']:.2f}** • Confiance : {art['confiance']:.2f}")

st.markdown("---")

# ============================================================
# SECTION 5 : EVOLUTION TEMPORELLE
# ============================================================
st.subheader("📈 Évolution temporelle")

evolution = get_evolution_temporelle()

if evolution:
    df_evol = pd.DataFrame(evolution)

    fig_evol = px.line(
        df_evol,
        x="jour",
        y="nb",
        color="sentiment",
        color_discrete_map=COULEURS_SENTIMENT,
        markers=True,
        labels={"jour": "Date", "nb": "Nombre d'articles", "sentiment": "Sentiment"}
    )
    fig_evol.update_layout(
        height=400,
        xaxis_title="Date",
        yaxis_title="Nombre d'articles",
        hovermode="x unified"
    )
    st.plotly_chart(fig_evol, use_container_width=True)
else:
    st.info("Pas assez de données pour l'évolution temporelle.")

st.markdown("---")

# ============================================================
# SECTION 6 : ACTIONS
# ============================================================
st.subheader("🔄 Actions")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔄 Rafraîchir", use_container_width=True, key="sentiment_refresh"):
        st.rerun()

with col2:
    df_export = pd.DataFrame({
        "Sentiment": ["Positif", "Neutre", "Négatif"],
        "Nombre": [stats["positifs"], stats["neutres"], stats["negatifs"]]
    })
    csv = df_export.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Export CSV",
        data=csv,
        file_name=f"sentiments_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
        use_container_width=True
    )

with col3:
    st.caption(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}")

st.markdown("---")

# Footer
style.footer()