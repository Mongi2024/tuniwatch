"""
Page Mots-Cles - Gestion des mots-cles de l'observatoire
Etape F - Session 2
Reserve aux administrateurs
"""

import streamlit as st
import sys
import os
import pandas as pd

# Ajout du dossier parent
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import auth
import keywords
import style
style.appliquer_style()
# Configuration
st.set_page_config(
    page_title="Mots-Cles - Monitoring",
    page_icon="📝",
    layout="wide"
)

# Protection ADMIN
auth.require_admin()

# ============================================================
# TITRE
# ============================================================
st.title("📝 Gestion des mots-clés")
st.caption("Base lexicale de l'observatoire — Français, Arabe, Arabe tunisien, Arabizi")

st.markdown("---")

# ============================================================
# SIDEBAR - FILTRES
# ============================================================
with st.sidebar:
    st.markdown("### 🎛️ Filtres")

    themes_dispo = [t["theme"] for t in keywords.lister_themes()]
    if not themes_dispo:
        themes_dispo = ["violence_femmes"]

    theme_filtre = st.selectbox(
        "📌 Thème",
        themes_dispo,
        key="kw_theme_filter"
    )

    langues_dispo = ["Toutes", "fr", "ar", "ar_tn", "arabizi"]
    langue_filtre = st.selectbox(
        "🌍 Langue",
        langues_dispo,
        key="kw_langue_filter"
    )

    afficher_inactifs = st.checkbox(
        "Afficher les mots désactivés",
        value=False,
        key="kw_show_inactive"
    )

st.markdown("---")

# ============================================================
# SECTION 1 : STATISTIQUES
# ============================================================
st.subheader("📊 Statistiques")

stats = keywords.stats_par_langue(theme_filtre)
total_theme = sum(stats.values())

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("🌍 Total", total_theme)
col2.metric("🇫🇷 Français", stats.get("fr", 0))
col3.metric("🇹🇳 Arabe std", stats.get("ar", 0))
col4.metric("🗣️ Tunisien", stats.get("ar_tn", 0))
col5.metric("🔤 Arabizi", stats.get("arabizi", 0))

st.markdown("---")

# ============================================================
# SECTION 2 : LISTE DES MOTS
# ============================================================
st.subheader(f"📋 Mots du thème : **{theme_filtre}**")

# Chargement
if langue_filtre == "Toutes":
    mots = keywords.charger_mots(theme=theme_filtre, actifs_seulement=not afficher_inactifs)
else:
    mots = keywords.charger_mots(
        theme=theme_filtre,
        langue=langue_filtre,
        actifs_seulement=not afficher_inactifs
    )

if not mots:
    st.warning("Aucun mot trouvé pour ces filtres.")
else:
    st.caption(f"**{len(mots)}** mot(s) affiché(s)")

    # Tableau interactif
    df = pd.DataFrame(mots)

    for i, row in df.iterrows():
        with st.container():
            col1, col2, col3, col4, col5, col6 = st.columns([4, 1.2, 1.2, 1.5, 1, 1])

            with col1:
                st.markdown(f"**{row['mot']}**")

            with col2:
                emoji_langue = {
                    "fr": "🇫🇷",
                    "ar": "🇹🇳",
                    "ar_tn": "🗣️",
                    "arabizi": "🔤"
                }.get(row['langue'], "🌐")
                st.write(f"{emoji_langue} {row['langue']}")

            with col3:
                st.write(f"⚖️ {row['poids']}")

            with col4:
                if st.button("✏️ Modifier", key=f"edit_{row['id']}", use_container_width=True):
                    st.session_state[f"editing_{row['id']}"] = True

            with col5:
                if st.button("❌ Désactiver", key=f"dis_{row['id']}", use_container_width=True):
                    ok, msg = keywords.desactiver_mot(row['id'])
                    if ok:
                        st.success(msg)
                        st.rerun()

            with col6:
                if st.button("🗑️", key=f"del_{row['id']}", use_container_width=True, help="Supprimer définitivement"):
                    ok, msg = keywords.supprimer_mot(row['id'])
                    if ok:
                        st.success(msg)
                        st.rerun()

            # Formulaire d'édition inline (si activé)
            if st.session_state.get(f"editing_{row['id']}", False):
                with st.form(f"form_edit_{row['id']}"):
                    nouveau_poids = st.number_input(
                        "Nouveau poids",
                        min_value=0.1,
                        max_value=5.0,
                        value=float(row['poids']),
                        step=0.1,
                        key=f"poids_{row['id']}"
                    )

                    col_a, col_b = st.columns(2)
                    with col_a:
                        save = st.form_submit_button("💾 Enregistrer", use_container_width=True)
                    with col_b:
                        cancel = st.form_submit_button("Annuler", use_container_width=True)

                    if save:
                        ok, msg = keywords.modifier_poids(row['id'], nouveau_poids)
                        if ok:
                            st.session_state[f"editing_{row['id']}"] = False
                            st.success(msg)
                            st.rerun()
                    if cancel:
                        st.session_state[f"editing_{row['id']}"] = False
                        st.rerun()

            st.markdown("---")

# ============================================================
# SECTION 3 : AJOUTER UN MOT
# ============================================================
st.subheader("➕ Ajouter un nouveau mot-clé")

with st.form("form_add_mot"):
    col1, col2 = st.columns(2)

    with col1:
        new_theme = st.text_input(
            "📌 Thème",
            value=theme_filtre,
            help="Ex: violence_femmes, discours_haine, equilibre_politique...",
            key="new_mot_theme"
        )

        new_langue = st.selectbox(
            "🌍 Langue",
            ["fr", "ar", "ar_tn", "arabizi"],
            key="new_mot_langue"
        )

    with col2:
        new_mot = st.text_input(
            "📝 Mot ou expression",
            placeholder="Ex: féminicide / العنف الأسري / 3onf",
            key="new_mot_value"
        )

        new_poids = st.slider(
            "⚖️ Poids",
            min_value=0.5,
            max_value=2.0,
            value=1.0,
            step=0.1,
            key="new_mot_poids"
        )

    submit = st.form_submit_button(
        "Ajouter le mot",
        use_container_width=True,
        type="primary"
    )

    if submit:
        if not new_theme or not new_mot:
            st.error("⚠️ Thème et mot sont obligatoires.")
        else:
            ok, msg = keywords.ajouter_mot(new_theme, new_langue, new_mot.strip(), new_poids)
            if ok:
                st.success(f"✅ {msg}")
                st.rerun()
            else:
                st.error(f"❌ {msg}")

st.markdown("---")

# ============================================================
# SECTION 4 : LISTER TOUS LES THEMES
# ============================================================
st.subheader("🗂️ Tous les thèmes disponibles")

themes = keywords.lister_themes()

if not themes:
    st.info("Aucun thème défini pour l'instant.")
else:
    df_themes = pd.DataFrame(themes)
    df_themes.columns = ["Thème", "Nombre de mots"]

    col1, col2 = st.columns([2, 1])

    with col1:
        st.dataframe(df_themes, use_container_width=True, hide_index=True)

    with col2:
        st.metric("📊 Total thèmes", len(themes))
        st.metric("📝 Total mots (actifs)", keywords.compter_total())

st.markdown("---")
st.caption("Page Mots-Cles — Version 0.1")
style.footer()