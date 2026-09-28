"""
Module status.py - Indicateur de connexion à la base de données
"""

import streamlit as st
from db_universal import get_connexion


def tester_connexion():
    """Teste la connexion à la base et retourne True/False."""
    try:
        conn = get_connexion()
        if conn is None:
            return False
        curseur = conn.cursor()
        curseur.execute("SELECT 1")
        curseur.fetchone()
        curseur.close()
        conn.close()
        return True
    except Exception:
        return False


def afficher_status():
    """
    Affiche un indicateur visuel de connexion.
    🟢 Vert = Connecté
    🔴 Rouge = Non connecté
    """
    connecte = tester_connexion()

    if connecte:
        html = (
            '<div style="display:inline-block;background:#10b981;color:white;'
            'padding:6px 14px;border-radius:20px;font-size:0.85rem;font-weight:700;'
            'box-shadow:0 2px 6px rgba(16,185,129,0.3);">'
            '🟢 Connecté'
            '</div>'
        )
    else:
        html = (
            '<div style="display:inline-block;background:#ef4444;color:white;'
            'padding:6px 14px;border-radius:20px;font-size:0.85rem;font-weight:700;'
            'box-shadow:0 2px 6px rgba(239,68,68,0.3);">'
            '🔴 Non connecté'
            '</div>'
        )

    st.markdown(html, unsafe_allow_html=True)