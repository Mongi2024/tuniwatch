"""
Module placeholder.py - Images par défaut selon le thème
Utilise Unsplash (libre de droits, pas de licence requise)
"""

# Images Unsplash par thème (URLs publiques stables)
PLACEHOLDERS = {
    "politique": "https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?w=800&h=450&fit=crop",
    "societe": "https://images.unsplash.com/photo-1521737604893-d14cc237f11d?w=800&h=450&fit=crop",
    "economie": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&h=450&fit=crop",
    "sport": "https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=800&h=450&fit=crop",
    "culture": "https://images.unsplash.com/photo-1514306191717-452ec28c7814?w=800&h=450&fit=crop",
    "technologie": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800&h=450&fit=crop",
    "sante": "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=800&h=450&fit=crop",
    "default": "https://images.unsplash.com/photo-1495020689067-958852a7765e?w=800&h=450&fit=crop",
}


def get_placeholder(theme=None):
    """Retourne une URL d'image par défaut selon le thème."""
    if theme:
        theme_lower = theme.lower().strip()
        if theme_lower in PLACEHOLDERS:
            return PLACEHOLDERS[theme_lower]
    return PLACEHOLDERS["default"]


def get_image_or_placeholder(image_url, theme=None):
    """
    Retourne l'image de l'article si présente, sinon le placeholder.
    - image_url : URL de l'image de l'article (peut être None ou vide)
    - theme : thème de l'article (pour choisir le bon placeholder)
    """
    if image_url and image_url.strip() and image_url.startswith("http"):
        return image_url
    return get_placeholder(theme)