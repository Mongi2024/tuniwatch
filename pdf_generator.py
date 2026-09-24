"""
Module pdf_generator.py - Génération de rapports PDF professionnels
Version 1.0 - Avec WeasyPrint
"""

import os
from datetime import datetime
from weasyprint import HTML, CSS
from db_universal import get_connexion


# ============================================================
# RÉCUPÉRATION DES DONNÉES
# ============================================================
def get_stats_globales():
    """Récupère les statistiques globales."""
    conn = get_connexion()
    if conn is None:
        return {}
    
    curseur = conn.cursor(dictionary=True)
    try:
        curseur.execute("""
            SELECT 
                (SELECT COUNT(*) FROM articles) AS total_articles,
                (SELECT COUNT(DISTINCT source) FROM articles) AS total_sources,
                (SELECT COUNT(*) FROM articles_themes) AS total_analyses_themes,
                (SELECT COUNT(*) FROM articles_sentiment) AS total_analyses_sentiment,
                (SELECT AVG(score) FROM articles_sentiment) AS score_moyen
        """)
        result = curseur.fetchone()
        return {
            "total_articles": int(result.get("total_articles") or 0),
            "total_sources": int(result.get("total_sources") or 0),
            "total_analyses_themes": int(result.get("total_analyses_themes") or 0),
            "total_analyses_sentiment": int(result.get("total_analyses_sentiment") or 0),
            "score_moyen": round(float(result.get("score_moyen") or 0), 2)
        }
    finally:
        curseur.close()
        conn.close()


def get_stats_sentiment():
    """Récupère la répartition des sentiments."""
    conn = get_connexion()
    if conn is None:
        return {}
    
    curseur = conn.cursor(dictionary=True)
    try:
        curseur.execute("""
            SELECT 
                SUM(CASE WHEN sentiment = 'positif' THEN 1 ELSE 0 END) AS positifs,
                SUM(CASE WHEN sentiment = 'neutre' THEN 1 ELSE 0 END) AS neutres,
                SUM(CASE WHEN sentiment = 'negatif' THEN 1 ELSE 0 END) AS negatifs
            FROM articles_sentiment
        """)
        result = curseur.fetchone()
        return {
            "positifs": int(result.get("positifs") or 0),
            "neutres": int(result.get("neutres") or 0),
            "negatifs": int(result.get("negatifs") or 0)
        }
    finally:
        curseur.close()
        conn.close()


def get_stats_themes():
    """Récupère la répartition par thème."""
    conn = get_connexion()
    if conn is None:
        return []
    
    curseur = conn.cursor(dictionary=True)
    try:
        curseur.execute("""
            SELECT theme, COUNT(DISTINCT article_id) AS nb_articles
            FROM articles_themes
            GROUP BY theme
            ORDER BY nb_articles DESC
        """)
        return curseur.fetchall()
    finally:
        curseur.close()
        conn.close()


def get_top_sources(limite=10):
    """Récupère les top sources."""
    conn = get_connexion()
    if conn is None:
        return []
    
    curseur = conn.cursor(dictionary=True)
    try:
        curseur.execute("""
            SELECT source, COUNT(*) AS nb_articles
            FROM articles
            WHERE source IS NOT NULL AND source != ''
            GROUP BY source
            ORDER BY nb_articles DESC
            LIMIT %s
        """, (limite,))
        return curseur.fetchall()
    finally:
        curseur.close()
        conn.close()


def get_top_articles(limite=10):
    """Récupère les top articles."""
    conn = get_connexion()
    if conn is None:
        return []
    
    curseur = conn.cursor(dictionary=True)
    try:
        curseur.execute("""
            SELECT 
                a.titre, a.source, a.url, a.date_publication,
                at.theme, at.score
            FROM articles_themes at
            JOIN articles a ON a.id = at.article_id
            ORDER BY at.score DESC
            LIMIT %s
        """, (limite,))
        return curseur.fetchall()
    finally:
        curseur.close()
        conn.close()


# ============================================================
# GÉNÉRATION DU HTML
# ============================================================
def generer_html_rapport():
    """Génère le HTML du rapport."""
    
    # Récupérer les données
    stats = get_stats_globales()
    sentiment = get_stats_sentiment()
    themes = get_stats_themes()
    sources = get_top_sources(10)
    articles = get_top_articles(5)
    
    # Calculer les pourcentages sentiment
    total_sent = sentiment.get("positifs", 0) + sentiment.get("neutres", 0) + sentiment.get("negatifs", 0)
    pct_pos = (sentiment.get("positifs", 0) / total_sent * 100) if total_sent > 0 else 0
    pct_neu = (sentiment.get("neutres", 0) / total_sent * 100) if total_sent > 0 else 0
    pct_neg = (sentiment.get("negatifs", 0) / total_sent * 100) if total_sent > 0 else 0
    
    # Construire les lignes des thèmes
    themes_html = ""
    max_theme = max([t["nb_articles"] for t in themes]) if themes else 1
    for t in themes[:10]:
        largeur = (t["nb_articles"] / max_theme * 100) if max_theme > 0 else 0
        themes_html += f"""
        <div class="bar-item">
            <div class="bar-label">{t['theme']}</div>
            <div class="bar-container">
                <div class="bar-fill" style="width: {largeur:.1f}%;"></div>
            </div>
            <div class="bar-value">{t['nb_articles']}</div>
        </div>
        """
    
    # Construire les lignes des sources
    sources_html = ""
    for s in sources:
        sources_html += f"""
        <tr>
            <td>{s['source'][:60]}</td>
            <td class="text-right">{s['nb_articles']}</td>
        </tr>
        """
    
    # Construire les articles
    articles_html = ""
    for i, a in enumerate(articles, 1):
        articles_html += f"""
        <div class="article">
            <div class="article-header">
                <span class="article-theme">{a.get('theme', '')}</span>
                <span class="article-score">Score : {a.get('score', 0):.2f}</span>
            </div>
            <div class="article-title">{i}. {a['titre'][:150]}</div>
            <div class="article-source">📰 {a['source']}</div>
        </div>
        """
    
    # HTML complet
    html = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <title>TuniWatch - Rapport</title>
    </head>
    <body>
        <!-- EN-TÊTE -->
        <div class="header">
    <img src="/root/tuniwatch/assets/logo_white.png" class="header-logo-img" alt="TuniWatch Logo" />
    <h1 class="header-title">TuniWatch</h1>
            <p class="header-subtitle">Observatoire des médias tunisiens</p>
            <p class="header-date">Rapport généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}</p>
        </div>
        
        <!-- SECTION 1 : RÉSUMÉ EXÉCUTIF -->
        <div class="section">
            <h2>📊 1. Résumé exécutif</h2>
            <div class="kpi-grid">
                <div class="kpi">
                    <div class="kpi-value">{stats['total_articles']:,}</div>
                    <div class="kpi-label">📰 Articles collectés</div>
                </div>
                <div class="kpi">
                    <div class="kpi-value">{stats['total_sources']}</div>
                    <div class="kpi-label">📡 Sources actives</div>
                </div>
                <div class="kpi">
                    <div class="kpi-value">{stats['total_analyses_themes']}</div>
                    <div class="kpi-label">🎯 Analyses thèmes</div>
                </div>
                <div class="kpi">
                    <div class="kpi-value">{stats['total_analyses_sentiment']}</div>
                    <div class="kpi-label">💭 Analyses sentiments</div>
                </div>
            </div>
            <p class="comment">
                📌 L'observatoire TuniWatch a collecté <b>{stats['total_articles']:,} articles</b> provenant de 
                <b>{stats['total_sources']} sources tunisiennes</b> (presse, radios, TV). 
                {stats['total_analyses_themes']} analyses thématiques et {stats['total_analyses_sentiment']} analyses 
                de sentiment ont été réalisées.
            </p>
        </div>
        
        <!-- SECTION 2 : SENTIMENT -->
        <div class="section">
            <h2>💭 2. Analyse de sentiment</h2>
            <table class="table">
                <tr>
                    <th>Sentiment</th>
                    <th class="text-right">Nombre</th>
                    <th class="text-right">Pourcentage</th>
                </tr>
                <tr>
                    <td>🟢 Positif</td>
                    <td class="text-right">{sentiment.get('positifs', 0)}</td>
                    <td class="text-right">{pct_pos:.1f}%</td>
                </tr>
                <tr>
                    <td>🟡 Neutre</td>
                    <td class="text-right">{sentiment.get('neutres', 0)}</td>
                    <td class="text-right">{pct_neu:.1f}%</td>
                </tr>
                <tr>
                    <td>🔴 Négatif</td>
                    <td class="text-right">{sentiment.get('negatifs', 0)}</td>
                    <td class="text-right">{pct_neg:.1f}%</td>
                </tr>
                <tr class="total-row">
                    <td><b>TOTAL</b></td>
                    <td class="text-right"><b>{total_sent}</b></td>
                    <td class="text-right"><b>100%</b></td>
                </tr>
            </table>
            <p class="comment">
                📌 Sur les {total_sent} articles analysés, {pct_neu:.1f}% ont un ton neutre, {pct_pos:.1f}% sont 
                positifs et {pct_neg:.1f}% sont négatifs. Le score moyen global est de {stats['score_moyen']}.
            </p>
        </div>
        
        <!-- SECTION 3 : THÈMES -->
        <div class="section">
            <h2>🎯 3. Répartition par thème</h2>
            <div class="bars">
                {themes_html}
            </div>
        </div>
        
        <!-- SECTION 4 : SOURCES -->
        <div class="section">
            <h2>📡 4. Sources les plus actives</h2>
            <table class="table">
                <tr>
                    <th>Source</th>
                    <th class="text-right">Articles</th>
                </tr>
                {sources_html}
            </table>
        </div>
        
        <!-- SECTION 5 : TOP ARTICLES -->
        <div class="section">
            <h2>🏆 5. Articles les plus pertinents</h2>
            {articles_html}
        </div>
        
        <!-- SECTION 6 : MÉTHODOLOGIE -->
        <div class="section">
            <h2>🔬 6. Méthodologie</h2>
            <p><b>Collecte :</b> Articles collectés via flux RSS et scraping.</p>
            <p><b>Analyse :</b> 14 thèmes sociétaux surveillés, 930 mots-clés (FR + AR).</p>
            <p><b>Sentiment :</b> Analyse par modèle Ollama (qwen3.5:4b).</p>
            <p><b>Limites :</b> Analyses indicatives, faux positifs possibles.</p>
        </div>
        
        <!-- PIED DE PAGE -->
        <div class="footer">
            <b>🇹🇳 TuniWatch</b> — Observatoire des médias tunisiens<br>
            Rapport généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}<br>
            © 2026 Khadraoui Mongi — Tous droits réservés
        </div>
    </body>
    </html>
    """
    
    return html


# ============================================================
# STYLE CSS POUR LE PDF
# ============================================================
CSS_PDF = """
@page {
    size: A4;
    margin: 2cm 1.5cm;
    @bottom-center {
        content: "Page " counter(page) " sur " counter(pages);
        font-size: 9pt;
        color: #999;
    }
}

body {
    font-family: 'Helvetica', 'Arial', sans-serif;
    color: #333;
    font-size: 11pt;
    line-height: 1.5;
}

/* EN-TÊTE */
.header {
    text-align: center;
    border-bottom: 3px solid #e70013;
    padding-bottom: 20px;
    margin-bottom: 30px;
}

.header-logo {
    font-size: 48pt;
    line-height: 1;
    margin-bottom: 10px;
}

.header-title {
    color: #1a1a1a;
    font-size: 28pt;
    margin: 5px 0;
    font-weight: bold;
}

.header-subtitle {
    color: #666;
    font-size: 14pt;
    margin: 5px 0;
}

.header-date {
    color: #888;
    font-size: 11pt;
    margin: 10px 0;
}

/* SECTIONS */
.section {
    margin-bottom: 30px;
    page-break-inside: avoid;
}

.section h2 {
    color: #1a1a1a;
    font-size: 16pt;
    border-bottom: 2px solid #e70013;
    padding-bottom: 8px;
    margin-bottom: 15px;
}

/* KPI */
.kpi-grid {
    display: flex;
    gap: 15px;
    margin-bottom: 20px;
}

.kpi {
    flex: 1;
    background: #f8f9fa;
    border-left: 4px solid #e70013;
    padding: 15px;
    border-radius: 5px;
    text-align: center;
}

.kpi-value {
    font-size: 24pt;
    font-weight: bold;
    color: #e70013;
    line-height: 1;
}

.kpi-label {
    font-size: 9pt;
    color: #666;
    margin-top: 5px;
}

/* TABLES */
.table {
    width: 100%;
    border-collapse: collapse;
    margin: 15px 0;
}

.table th {
    background: #1a1a1a;
    color: white;
    padding: 10px;
    text-align: left;
    font-size: 10pt;
}

.table td {
    padding: 8px 10px;
    border-bottom: 1px solid #e0e0e0;
    font-size: 10pt;
}

.table tr:nth-child(even) {
    background: #f8f9fa;
}

.total-row {
    background: #f0f0f0 !important;
    font-weight: bold;
}

.text-right {
    text-align: right;
}

/* BARS */
.bars {
    margin: 15px 0;
}

.bar-item {
    display: flex;
    align-items: center;
    margin-bottom: 8px;
    gap: 10px;
}

.bar-label {
    width: 150px;
    font-size: 9pt;
    font-weight: bold;
}

.bar-container {
    flex: 1;
    height: 20px;
    background: #f0f0f0;
    border-radius: 3px;
    overflow: hidden;
}

.bar-fill {
    height: 100%;
    background: linear-gradient(90deg, #e70013 0%, #b8000f 100%);
    border-radius: 3px;
}

.bar-value {
    width: 50px;
    text-align: right;
    font-size: 9pt;
    font-weight: bold;
    color: #e70013;
}

/* ARTICLES */
.article {
    background: #f8f9fa;
    border-left: 4px solid #e70013;
    padding: 12px 15px;
    margin-bottom: 10px;
    border-radius: 5px;
}

.article-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 5px;
}

.article-theme {
    background: #e70013;
    color: white;
    padding: 2px 8px;
    border-radius: 10px;
    font-size: 8pt;
    text-transform: uppercase;
}

.article-score {
    font-size: 9pt;
    color: #666;
}

.article-title {
    font-size: 11pt;
    font-weight: bold;
    color: #1a1a1a;
    margin: 5px 0;
}

.article-source {
    font-size: 9pt;
    color: #888;
}

/* COMMENTAIRES */
.comment {
    background: #fff8e1;
    border-left: 4px solid #f39c12;
    padding: 12px 15px;
    margin: 15px 0;
    font-size: 10pt;
    color: #555;
    border-radius: 5px;
}

/* FOOTER */
.footer {
    text-align: center;
    border-top: 2px solid #e70013;
    padding-top: 15px;
    margin-top: 30px;
    color: #666;
    font-size: 9pt;
}
"""


# ============================================================
# GÉNÉRATION DU PDF
# ============================================================
def generer_pdf(output_path=None):
    """Génère le rapport PDF complet."""
    
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"/root/tuniwatch/rapports/rapport_tuniwatch_{timestamp}.pdf"
    
    # Créer le dossier
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Générer le HTML
    html_content = generer_html_rapport()
    
    # Convertir en PDF
    HTML(string=html_content).write_pdf(
        output_path,
        stylesheets=[CSS(string=CSS_PDF)]
    )
    
    return output_path


# ============================================================
# TEST
# ============================================================
if __name__ == "__main__":
    print("Génération du rapport PDF...")
    print()
    
    try:
        pdf_path = generer_pdf()
        size = os.path.getsize(pdf_path)
        size_kb = size / 1024
        
        print(f"✅ PDF généré avec succès !")
        print(f"   Fichier : {pdf_path}")
        print(f"   Taille  : {size_kb:.1f} KB")
        print()
    except Exception as e:
        print(f"❌ Erreur : {e}")