"""
Script de lancement de l'analyse complète.
Version 2.0 - Avec logs d'activité
"""

from analyzer import (
    analyser_articles_en_base,
    analyser_sentiments_en_base,
    compter_analyses,
)
from datetime import datetime

# Import des fonctions de log
try:
    from activity_logger import log_run_analysis, log_error
    LOGS_ACTIFS = True
except ImportError:
    LOGS_ACTIFS = False
    def log_run_analysis(a, d): pass
    def log_error(u, e): pass


print("=" * 70)
print("LANCEMENT DE L'ANALYSE COMPLÈTE")
print("=" * 70)
print()

debut = datetime.now()

# Étape 1 : Analyser les thèmes
print("📊 ÉTAPE 1 : Analyse des thèmes...")
print("-" * 70)

try:
    resultat_themes = analyser_articles_en_base()
except Exception as e:
    print(f"❌ Erreur : {e}")
    if LOGS_ACTIFS:
        log_error("system", f"analyser_articles_en_base: {e}")
    resultat_themes = None

print()

# Étape 2 : Analyser les sentiments
print("💭 ÉTAPE 2 : Analyse des sentiments...")
print("-" * 70)

try:
    resultat_sentiments = analyser_sentiments_en_base()
except Exception as e:
    print(f"❌ Erreur : {e}")
    if LOGS_ACTIFS:
        log_error("system", f"analyser_sentiments_en_base: {e}")
    resultat_sentiments = None

print()

# Résumé
print("=" * 70)
print("RÉSUMÉ")
print("=" * 70)

if resultat_themes:
    print(f"✅ Thèmes analysés     : {resultat_themes['articles_traites']} articles")
    print(f"   Analyses créées    : {resultat_themes['analyses']}")
    print(f"   Durée              : {resultat_themes['duree']:.1f}s")
else:
    print("❌ Erreur analyse thèmes")

print()

if resultat_sentiments:
    print(f"✅ Sentiments analysés : {resultat_sentiments['articles_traites']} articles")
    print(f"   Analyses créées    : {resultat_sentiments['analyses']}")
    print(f"   Durée              : {resultat_sentiments['duree']:.1f}s")
else:
    print("❌ Erreur analyse sentiments")

print()
total_analyses = compter_analyses()
print(f"📈 Total analyses en base : {total_analyses}")

# Log dans activity_logger
if LOGS_ACTIFS:
    duree_totale = (datetime.now() - debut).total_seconds()
    articles_total = 0
    if resultat_themes:
        articles_total += resultat_themes['articles_traites']
    if resultat_sentiments:
        articles_total += resultat_sentiments['articles_traites']
    
    log_run_analysis(articles_total, duree_totale)

print()
print("✅ Analyse terminée !")
print()