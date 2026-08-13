"""Paleta, assets y tokens de diseño Calixta."""

CREAM = "#FFFFCD"
OLIVE = "#828F59"
OLIVE_DARK = "#6B704C"
OLIVE_DEEP = "#4A5038"
PINK = "#F7C3C6"
PINK_SOFT = "#F0C7C1"
TERRACOTTA = "#B7702E"
SAGE = "#C6BA80"
TEXT = "#3D4035"
TEXT_MUTED = "#7A7F72"
WHITE = "#FFFFFF"

# Fondo suave — crema + rosa + oliva (no amarillo plano)
BG_PAGE = "#F4F3EF"
BG_GRADIENT = (
    "linear-gradient(145deg, #F8F6F2 0%, #F5F0EE 40%, #F0F2EB 100%)"
)
BG_CARD = "#FFFFFF"
BG_NAV = "#FFFFFF"
BG_NAV_TRACK = "#F0EDE8"
BORDER = "rgba(130, 143, 89, 0.12)"
SHADOW_CARD = "0 4px 24px rgba(61, 64, 53, 0.06), 0 1px 3px rgba(61, 64, 53, 0.04)"
SHADOW_NAV = "0 8px 32px rgba(61, 64, 53, 0.08)"

RADIUS_XL = "24px"
RADIUS_LG = "20px"
RADIUS_MD = "16px"
RADIUS_SM = "12px"
RADIUS_PILL = "999px"

CHART_COLORS = [OLIVE, PINK, CREAM, TERRACOTTA, SAGE, OLIVE_DARK]

CATEGORY_COLORS = {
    "Ropa": OLIVE,
    "Accesorio": PINK,
}

LOGO_PATH = "assets/calixta-logo.png"
ICON_PATH = "assets/calixta-icon.png"

NAV_ITEMS: list[tuple[str, str]] = [
    ("Inicio", "dashboard"),
    ("Productos", "productos"),
    ("Clientes", "clientes"),
    ("Pedidos", "pedidos"),
    ("Ventas", "ventas"),
    ("Contabilidad", "contabilidad"),
    ("Alertas", "alertas"),
]
