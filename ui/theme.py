"""Paleta, assets y tokens de diseño Calixta."""

# Paleta de marca
CREAM = "#FFFFCD"
OLIVE = "#828F59"
OLIVE_DARK = "#6B704C"
PINK = "#F7C3C6"
PINK_SOFT = "#F0C7C1"
TERRACOTTA = "#B7702E"
SAGE = "#C6BA80"
TEXT = "#3D4230"
TEXT_MUTED = "#6B7058"
WHITE = "#FFFFFF"
BORDER = "rgba(130, 143, 89, 0.18)"

# Glass / superficies
BG_GRADIENT = (
    "linear-gradient(145deg, #FFFFCD 0%, #F7E8E0 28%, #EDE8D4 55%, #F0C7C1 100%)"
)
GLASS_BG = "rgba(255, 255, 255, 0.62)"
GLASS_BORDER = "rgba(255, 255, 255, 0.75)"
GLASS_SHADOW = "0 8px 32px rgba(107, 112, 76, 0.10)"
RADIUS_LG = "28px"
RADIUS_MD = "18px"
RADIUS_PILL = "999px"

CHART_COLORS = [OLIVE, TERRACOTTA, SAGE, PINK, OLIVE_DARK, PINK_SOFT]

LOGO_PATH = "assets/calixta-logo.png"
ICON_PATH = "assets/calixta-icon.png"

# Para agregar secciones nuevas: añade una tupla (etiqueta, id_unico) aquí
# y registra la función de página en app.py → pages dict.
NAV_ITEMS: list[tuple[str, str]] = [
    ("Inicio", "dashboard"),
    ("Productos", "productos"),
    ("Clientes", "clientes"),
    ("Pedidos", "pedidos"),
    ("Ventas", "ventas"),
    ("Alertas", "alertas"),
]
