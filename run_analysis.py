"""
Script de lancement de l'analyse complète.
À exécuter sur le VPS ou en local pour analyser tous les articles.
"""

from analyzer import (
    analyser_articles_en_base,
    analyser_sentiments_en_base,
    compter_analyses,
    stats_themes
)

print("=" * 70)
print("LANCEMENT DE L'ANALYSE COMPLÈTE")
print("=" * 70)
print()

# Étape 1 : Analyser les thèmes
print("📊 ÉTAPE 1 : Analyse des thèmes...")
print("-" * 70)
resultat_themes = analyser_articles_en_base()
print()

# Étape 2 : Analyser les sentiments
print("💭 ÉTAPE 2 : Analyse des sentiments...")
print("-" * 70)
resultat_sentiments = analyser_sentiments_en_base()
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
print(f"📈 Total analyses en base : {compter_analyses()}")
print()

print("✅ Analyse terminée !")