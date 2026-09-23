# ============================================================
# TuniWatch - Correction encodage des articles en base
# Fichier : fix_encodage.py
# Description : Répare les articles corrompus dans PostgreSQL
# ============================================================

import os
import psycopg2
import ftfy
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# ============================================================
# CONNEXION À LA BASE
# ============================================================
# ⚠️ À ADAPTER selon votre configuration
DB_CONFIG = {
    "host": "localhost",           # ou votre IP VPS
    "database": "tuniwatch",       # nom de votre base
    "user": "postgres",            # utilisateur
    "password": "VOTRE_MOT_DE_PASSE",  # ⚠️ à remplacer
    "port": 5432
}

def reparer_texte(texte):
    """Répare un texte corrompu avec ftfy."""
    if not texte:
        return texte
    return ftfy.fix_text(str(texte))

def main():
    print("🔌 Connexion à la base PostgreSQL...")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        print("✅ Connexion réussie !")
    except Exception as e:
        print(f"❌ Erreur de connexion : {e}")
        return

    # ============================================================
    # TROUVER LES ARTICLES CORROMPUS
    # ============================================================
    print("\n🔍 Recherche des articles avec encodage corrompu...")
    
    # Caractères typiques du Mojibake
    motifs = ['鈥', '茅', '猫', '锚', '毛', '卯', '茂', '么', '没', '脿', '芒', '莽', '鹿']
    
    # Construire la requête
    conditions = " OR ".join([f"titre LIKE '%{m}%'" for m in motifs])
    conditions += " OR " + " OR ".join([f"description LIKE '%{m}%'" for m in motifs])
    
    cur.execute(f"""
        SELECT id, titre, description 
        FROM articles 
        WHERE {conditions}
    """)
    
    articles = cur.fetchall()
    print(f"📊 {len(articles)} articles corrompus trouvés.\n")

    if not articles:
        print("✨ Aucun article à corriger !")
        cur.close()
        conn.close()
        return

    # ============================================================
    # CORRIGER CHAQUE ARTICLE
    # ============================================================
    corrections = 0
    for art_id, titre, description in articles:
        nouveau_titre = reparer_texte(titre)
        nouvelle_desc = reparer_texte(description)
        
        # Vérifier qu'il y a un vrai changement
        if nouveau_titre != titre or nouvelle_desc != description:
            cur.execute("""
                UPDATE articles 
                SET titre = %s, description = %s 
                WHERE id = %s
            """, (nouveau_titre, nouvelle_desc, art_id))
            corrections += 1
            
            if corrections <= 5:  # Afficher les 5 premiers
                print(f"✏️  ID {art_id}:")
                print(f"   AVANT : {titre[:80]}")
                print(f"   APRÈS : {nouveau_titre[:80]}")
                print()

    # ============================================================
    # SAUVEGARDER
    # ============================================================
    conn.commit()
    print(f"\n✅ {corrections} articles corrigés et sauvegardés !")
    
    cur.close()
    conn.close()
    print("🔌 Connexion fermée.")


if __name__ == "__main__":
    main()