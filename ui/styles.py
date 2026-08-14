from ui.theme import (
    BG_CARD,
    BG_GRADIENT,
    BG_NAV,
    BG_NAV_TRACK,
    BG_PAGE,
    BORDER,
    CREAM,
    OLIVE,
    OLIVE_DARK,
    OLIVE_DEEP,
    PINK,
    PINK_SOFT,
    RADIUS_LG,
    RADIUS_MD,
    RADIUS_PILL,
    RADIUS_SM,
    RADIUS_XL,
    SAGE,
    SHADOW_CARD,
    SHADOW_NAV,
    TERRACOTTA,
    TEXT,
    TEXT_MUTED,
    WHITE,
)

CALIXTA_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

:root {{
    --cream: {CREAM};
    --olive: {OLIVE};
    --olive-dark: {OLIVE_DARK};
    --olive-deep: {OLIVE_DEEP};
    --pink: {PINK};
    --pink-soft: {PINK_SOFT};
    --terra: {TERRACOTTA};
    --sage: {SAGE};
    --text: {TEXT};
    --muted: {TEXT_MUTED};
    --white: {WHITE};
    --bg: {BG_PAGE};
    --card: {BG_CARD};
    --border: {BORDER};
    --shadow-card: {SHADOW_CARD};
    --shadow-nav: {SHADOW_NAV};
    --r-xl: {RADIUS_XL};
    --r-lg: {RADIUS_LG};
    --r-md: {RADIUS_MD};
    --r-sm: {RADIUS_SM};
    --r-pill: {RADIUS_PILL};
}}

html, body, [class*="css"] {{
    font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
    color: var(--text);
    -webkit-font-smoothing: antialiased;
}}

.stApp {{
    background: {BG_GRADIENT};
    background-attachment: fixed;
}}

.stApp::before {{
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 0;
    background:
        radial-gradient(ellipse 60% 50% at 0% 0%, rgba(247,195,198,0.28) 0%, transparent 55%),
        radial-gradient(ellipse 50% 40% at 100% 10%, rgba(198,186,128,0.22) 0%, transparent 50%),
        radial-gradient(ellipse 40% 35% at 50% 100%, rgba(130,143,89,0.10) 0%, transparent 45%);
}}

.stApp [data-testid="stAppViewContainer"] {{ position: relative; z-index: 1; }}

section[data-testid="stSidebar"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="stSidebarCollapseButton"] {{ display: none !important; }}

/* Quitar espacio vacío arriba (header Streamlit) */
header[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
#MainMenu,
footer,
.viewerBadge_container {{
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
    min-height: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
}}

section[data-testid="stMain"] > div {{
    padding-top: 0 !important;
}}

[data-testid="stAppViewContainer"],
[data-testid="stMainBlockContainer"],
section[data-testid="stMain"] {{
    padding-top: 0 !important;
}}

section[data-testid="stMain"] .block-container {{
    max-width: 1280px;
    padding: 0 1.25rem 2rem !important;
}}

section[data-testid="stMain"] .block-container > div:first-child {{
    padding-top: 0 !important;
    margin-top: 0 !important;
}}

section[data-testid="stMain"] [data-testid="stElementContainer"]:has([data-testid="stEmpty"]) {{
    display: none !important;
    height: 0 !important;
    min-height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
}}

.main-content {{
    margin-top: 0;
}}

/* ── Welcome ── */
.welcome-block {{
    margin-bottom: 1.25rem;
}}

.welcome-title {{
    font-size: 1.85rem;
    font-weight: 700;
    color: var(--olive-deep);
    margin: 0 0 0.35rem;
    letter-spacing: -0.03em;
}}

.welcome-sub {{
    font-size: 0.95rem;
    color: var(--muted);
    margin: 0;
    font-weight: 400;
}}

/* Stat chips — fondos con paleta */
.stat-chip {{
    background: var(--card);
    border-radius: var(--r-lg);
    padding: 1.1rem 1rem;
    box-shadow: var(--shadow-card);
    border: none;
    height: 100%;
}}

.stat-chip--olive {{ background: linear-gradient(160deg, rgba(130,143,89,0.14) 0%, var(--card) 70%); }}
.stat-chip--terra {{ background: linear-gradient(160deg, rgba(183,112,46,0.12) 0%, var(--card) 70%); }}
.stat-chip--pink {{ background: linear-gradient(160deg, rgba(247,195,198,0.35) 0%, var(--card) 70%); }}
.stat-chip--sage {{ background: linear-gradient(160deg, rgba(198,186,128,0.28) 0%, var(--card) 70%); }}
.stat-chip--cream {{ background: linear-gradient(160deg, rgba(255,255,205,0.55) 0%, var(--card) 70%); }}

.stat-chip-label {{
    display: block;
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--muted);
    margin-bottom: 0.35rem;
}}

.stat-chip-value {{
    display: block;
    font-size: 1.35rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    margin-bottom: 0.2rem;
}}

.stat-chip-detail {{
    font-size: 0.78rem;
    color: var(--muted);
}}

.stat-chip--olive .stat-chip-value {{ color: var(--olive); }}
.stat-chip--terra .stat-chip-value {{ color: var(--terra); }}
.stat-chip--pink .stat-chip-value {{ color: #C97B7F; }}
.stat-chip--sage .stat-chip-value {{ color: #9A8F5E; }}
.stat-chip--cream .stat-chip-value {{ color: var(--olive-deep); }}

/* Paneles nativos Streamlit */
[data-testid="stVerticalBlockBorderWrapper"] {{
    border-radius: var(--r-lg) !important;
    border-color: rgba(130, 143, 89, 0.15) !important;
    background: var(--card) !important;
    box-shadow: var(--shadow-card) !important;
    padding: 0.25rem 0.5rem 0.75rem !important;
    margin-bottom: 0.75rem;
}}

.panel-heading {{
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--olive-deep);
    margin: 0.25rem 0 0.85rem;
    padding-left: 0.65rem;
    border-left: 3px solid var(--olive);
}}

.panel-heading--pink {{ border-left-color: var(--pink); }}
.panel-heading--terra {{ border-left-color: var(--terra); }}
.panel-heading--sage {{ border-left-color: var(--sage); }}
.panel-heading--olive {{ border-left-color: var(--olive); }}
.panel-heading--cream {{ border-left-color: var(--cream); }}

.filter-bar-title {{
    font-size: 0.78rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--muted);
    margin: 0.15rem 0 0.65rem 0.35rem;
}}

.stat-chip-row-spacer {{
    margin-bottom: 1rem;
}}

.metrics-charts-gap {{
    height: 1.25rem;
    margin-bottom: 1.25rem;
}}

/* Sección de gráficos */
.dashboard-section-title {{
    font-size: 0.78rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--muted);
    margin: 0 0 0.85rem 0.35rem;
    padding: 0.65rem 0.85rem;
    border-radius: var(--r-lg);
    background: linear-gradient(135deg, rgba(255,255,205,0.35) 0%, rgba(247,195,198,0.22) 55%, rgba(240,199,193,0.18) 100%);
    border: 1px solid rgba(130, 143, 89, 0.1);
}}

.chart-empty-msg {{
    margin: 2.5rem 0.5rem;
    padding: 2rem 1rem;
    text-align: center;
    font-size: 0.92rem;
    font-weight: 500;
    color: #8B4A6B;
    background: rgba(247, 195, 198, 0.18);
    border-radius: var(--r-md);
    border: 1px dashed rgba(130, 143, 89, 0.2);
}}

/* Gráficos Plotly — contenedor suave */
[data-testid="stPlotlyChart"] {{
    background: rgba(255, 255, 255, 0.65);
    border-radius: var(--r-md);
    overflow: hidden;
    padding: 0.5rem 0.35rem 0.25rem;
    border: 1px solid rgba(198, 186, 128, 0.25);
    box-shadow: inset 0 2px 8px rgba(198, 186, 128, 0.12);
}}

[data-testid="stPlotlyChart"] .js-plotly-plot,
[data-testid="stPlotlyChart"] .plot-container {{
    border-radius: var(--r-md);
}}

/* Summary panel */
.summary-panel {{
    background: var(--card);
    border-radius: var(--r-lg);
    padding: 1rem 1.15rem;
    box-shadow: var(--shadow-card);
    border: 1px solid var(--border);
}}

.summary-stat {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.55rem 0;
    border-bottom: 1px solid rgba(130,143,89,0.1);
    font-size: 0.88rem;
}}

.summary-stat:last-child {{ border-bottom: none; }}
.summary-stat span {{ color: var(--muted); }}
.summary-stat strong {{ color: var(--olive-deep); font-weight: 700; }}

/* Quick items */
.quick-item {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.85rem 1rem;
    border-radius: var(--r-md);
    margin-bottom: 0.5rem;
    border: 1px solid var(--border);
    background: var(--white);
}}

.quick-item--olive {{ border-left: 4px solid var(--olive); }}
.quick-item--pink {{ border-left: 4px solid var(--pink); }}
.quick-item--terra {{ border-left: 4px solid var(--terra); }}
.quick-item--sage {{ border-left: 4px solid var(--sage); }}
.quick-item--cream {{ border-left: 4px solid var(--cream); background: rgba(255,255,205,0.2); }}

.quick-item-text strong {{
    display: block;
    font-size: 0.9rem;
    color: var(--olive-deep);
    margin-bottom: 0.15rem;
}}

.quick-item-text span {{
    font-size: 0.78rem;
    color: var(--muted);
}}

.quick-item-arrow {{
    color: var(--sage);
    font-size: 1.2rem;
}}

/* Progress bars */
.progress-row {{ margin-bottom: 0.85rem; }}
.progress-row-head {{
    display: flex;
    justify-content: space-between;
    font-size: 0.82rem;
    margin-bottom: 0.35rem;
    color: var(--olive-dark);
}}
.progress-track {{
    height: 8px;
    background: rgba(198,186,128,0.25);
    border-radius: var(--r-pill);
    overflow: hidden;
}}
.progress-fill {{
    height: 100%;
    border-radius: var(--r-pill);
}}
.progress-fill--olive {{ background: var(--olive); }}
.progress-fill--pink {{ background: var(--pink); }}
.progress-fill--terra {{ background: var(--terra); }}
.progress-fill--sage {{ background: var(--sage); }}

/* Page hero (otras páginas) */
.page-hero {{
    margin-bottom: 0.55rem;
    padding: 0 0.35rem 0;
}}
.page-title {{
    font-size: 1.65rem;
    font-weight: 700;
    color: var(--olive-deep);
    margin: 0 0 0.3rem;
}}
.page-subtitle {{
    color: var(--muted);
    margin: 0 0 0.15rem;
    font-size: 0.92rem;
}}

section[data-testid="stMain"] [data-testid="stElementContainer"]:has(.page-hero) {{
    margin-bottom: 0.7rem !important;
}}

section[data-testid="stMain"] [data-testid="stElementContainer"]:has(.page-hero)
    + [data-testid="stElementContainer"] [data-testid="stVerticalBlockBorderWrapper"] {{
    margin-top: 0.15rem !important;
}}

.page-section-inner {{
    padding: 0.15rem 0.35rem 0.5rem;
}}

.stButton > button[kind="primary"] {{
    background: var(--olive) !important;
    border: none !important;
    color: var(--white) !important;
    border-radius: var(--r-pill) !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 14px rgba(130,143,89,0.3) !important;
}}

.stButton > button[kind="primary"]:hover {{
    background: var(--olive-dark) !important;
}}

.stButton > button[kind="secondary"] {{
    border: 1px solid var(--border) !important;
    border-radius: var(--r-pill) !important;
    color: var(--olive-dark) !important;
    background: var(--white) !important;
}}

[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea {{
    border-radius: var(--r-sm) !important;
    border: 1px solid var(--border) !important;
}}

[data-testid="stTextInput"] input:focus {{
    border-color: var(--olive) !important;
    box-shadow: 0 0 0 2px rgba(247,195,198,0.5) !important;
}}

/* Tablas Calixta */
.calixta-table-frame {{
    display: none;
}}

.calixta-table-frame + [data-testid="stElementContainer"] {{
    margin-bottom: 0.15rem !important;
    padding: 0.35rem 0.45rem 0.4rem !important;
    border-radius: var(--r-md) !important;
    border: 1px solid rgba(130, 143, 89, 0.24) !important;
    border-top: 3px solid {OLIVE} !important;
    background: linear-gradient(
        165deg,
        rgba(255, 255, 255, 0.99) 0%,
        rgba(247, 195, 198, 0.07) 38%,
        rgba(248, 246, 242, 0.97) 100%
    ) !important;
    box-shadow: 0 10px 26px rgba(107, 112, 76, 0.07) !important;
}}

.calixta-table-frame + [data-testid="stElementContainer"] [data-testid="stDataFrame"],
section[data-testid="stMain"] [data-testid="stDataFrame"] {{
    border-radius: calc(var(--r-md) - 2px) !important;
    border: 1px solid rgba(130, 143, 89, 0.14) !important;
    background: rgba(255, 255, 255, 0.94) !important;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.85) !important;
    overflow: hidden !important;
}}

.calixta-table-meta {{
    margin: 0.45rem 0 0.1rem;
    padding: 0.42rem 0.85rem;
    text-align: center;
    font-size: 0.78rem;
    letter-spacing: 0.01em;
    color: {OLIVE_DARK};
    background: linear-gradient(
        90deg,
        rgba(198, 186, 128, 0.12) 0%,
        rgba(247, 195, 198, 0.18) 50%,
        rgba(198, 186, 128, 0.12) 100%
    );
    border: 1px solid rgba(130, 143, 89, 0.18);
    border-radius: var(--r-pill);
}}

/* Solo paginador real (con número de página), no contador suelto */
.calixta-table-meta:not(:has(strong)) {{
    display: none !important;
}}

.calixta-table-meta strong {{
    color: {OLIVE_DEEP};
    font-weight: 600;
}}

.calixta-table-frame ~ [data-testid="stHorizontalBlock"] {{
    margin-top: 0.15rem !important;
    padding: 0.2rem 0.35rem 0.05rem !important;
    border-radius: var(--r-md) !important;
    border: 1px solid rgba(130, 143, 89, 0.12) !important;
    background: rgba(255, 255, 255, 0.72) !important;
}}

.calixta-table-frame ~ [data-testid="stHorizontalBlock"] .stButton > button[kind="secondary"] {{
    border-color: rgba(130, 143, 89, 0.28) !important;
    color: {OLIVE_DARK} !important;
    background: rgba(255, 255, 255, 0.92) !important;
    font-size: 0.78rem !important;
    min-height: 2rem !important;
    font-weight: 500 !important;
}}

.calixta-table-frame ~ [data-testid="stHorizontalBlock"] .stButton > button[kind="secondary"]:hover:not(:disabled) {{
    border-color: {OLIVE} !important;
    color: {OLIVE_DEEP} !important;
    background: rgba(255, 255, 205, 0.45) !important;
}}

.calixta-table-frame ~ [data-testid="stHorizontalBlock"] .stButton > button[kind="secondary"]:disabled {{
    opacity: 0.45 !important;
}}

/* Autocompletado integrado */
iframe[title*="calixta_autocomplete"] {{
    border: 0 !important;
    background: transparent !important;
    width: 100% !important;
}}

[data-testid="stIFrame"]:has(iframe[title*="calixta_autocomplete"]) {{
    margin-bottom: 0 !important;
    background: transparent !important;
}}

[data-testid="stAlert"] {{
    border-radius: var(--r-md) !important;
}}

/* Móvil */
@media (max-width: 768px) {{
    section[data-testid="stMain"] .block-container {{
        padding: 0.2rem 0.85rem 4.5rem !important;
    }}

    .welcome-title {{ font-size: 1.45rem; }}
}}
</style>
"""

CALIXTA_NAV_CSS = f"""
<style>
/* Menú principal — minimalista tipo píldora */
.st-key-calixta_nav {{
    width: 100vw;
    max-width: 100vw;
    margin-left: calc(50% - 50vw);
    margin-right: calc(50% - 50vw);
    margin-top: 0;
    margin-bottom: 0;
    padding: 0.35rem 1.5rem 0.15rem;
    box-sizing: border-box;
}}

.st-key-calixta_nav [data-testid="stElementContainer"]:has(.calixta-nav-root) {{
    display: none !important;
    height: 0 !important;
    min-height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
}}

.st-key-calixta_nav .calixta-nav-logo {{
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    width: 100% !important;
    margin: 0 auto 1.1rem auto !important;
    padding: 0 !important;
}}

.st-key-calixta_nav .calixta-nav-root {{
    display: none !important;
}}

.st-key-calixta_nav [data-testid="stHorizontalBlock"]:has(.calixta-nav-logo) {{
    justify-content: center !important;
    margin-bottom: 0 !important;
}}

.st-key-calixta_nav .calixta-nav-logo img {{
    width: 118px !important;
    max-width: 118px !important;
    height: auto !important;
    max-height: none !important;
    object-fit: contain !important;
    display: block !important;
    margin: 0 auto !important;
}}

.st-key-calixta_nav [data-testid="stHorizontalBlock"]:has([class*="st-key-nav_btn_"]) {{
    justify-content: center !important;
    gap: 0.35rem !important;
    flex-wrap: nowrap !important;
}}

.st-key-calixta_nav [class*="st-key-nav_btn_"] {{
    flex: 0 1 auto !important;
    width: auto !important;
    min-width: unset !important;
}}

.st-key-calixta_nav [class*="st-key-nav_btn_"] .stButton {{
    margin: 0 !important;
}}

.st-key-calixta_nav [class*="st-key-nav_btn_"] .stButton > button {{
    border-radius: {RADIUS_PILL} !important;
    clip-path: none !important;
    white-space: nowrap !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.01em;
    min-height: 2.15rem !important;
    padding: 0.42rem 1.05rem !important;
    width: auto !important;
    transition: background 0.18s ease, color 0.18s ease, box-shadow 0.18s ease;
}}

.st-key-calixta_nav [class*="st-key-nav_btn_"] .stButton > button[kind="secondary"] {{
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: {TEXT_MUTED} !important;
}}

.st-key-calixta_nav [class*="st-key-nav_btn_"] .stButton > button[kind="secondary"]:hover {{
    background: rgba(198, 186, 128, 0.18) !important;
    color: {OLIVE_DARK} !important;
}}

.st-key-calixta_nav [class*="st-key-nav_btn_"] .stButton > button[kind="primary"],
.st-key-calixta_nav [class*="st-key-nav_btn_"] .stButton > button[data-testid="stBaseButton-primary"] {{
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: {OLIVE_DEEP} !important;
    font-weight: 700 !important;
    text-decoration: underline !important;
    text-underline-offset: 0.28rem !important;
    text-decoration-color: {OLIVE} !important;
    text-decoration-thickness: 2px !important;
}}

.st-key-calixta_nav [class*="st-key-nav_btn_"] .stButton > button[kind="primary"]:hover,
.st-key-calixta_nav [class*="st-key-nav_btn_"] .stButton > button[data-testid="stBaseButton-primary"]:hover {{
    background: transparent !important;
    background-color: transparent !important;
    color: {OLIVE_DEEP} !important;
    border: none !important;
    text-decoration-color: {OLIVE_DARK} !important;
}}

@media (max-width: 1100px) {{
    .st-key-calixta_nav {{
        padding: 0.25rem 0.85rem 0.15rem;
    }}

    .st-key-calixta_nav [class*="st-key-nav_btn_"] .stButton > button {{
        font-size: 0.76rem !important;
        padding: 0.38rem 0.72rem !important;
        min-height: 1.95rem !important;
    }}
}}

@media (max-width: 768px) {{
    .st-key-calixta_nav {{
        padding: 0.2rem 0.55rem 0.1rem;
    }}

    .st-key-calixta_nav [data-testid="stHorizontalBlock"]:has([class*="st-key-nav_btn_"]) {{
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        scrollbar-width: none;
        justify-content: flex-start !important;
        padding-bottom: 0.15rem;
    }}

    .st-key-calixta_nav [class*="st-key-nav_btn_"] {{
        min-width: 4.8rem;
    }}

    .st-key-calixta_nav [class*="st-key-nav_btn_"] .stButton > button {{
        font-size: 0.7rem !important;
        padding: 0.34rem 0.55rem !important;
    }}
}}

/* Ocultar botón refresh legacy */
.st-key-nav_refresh,
[class*="st-key-nav_refresh"] {{
    display: none !important;
    height: 0 !important;
    min-height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: hidden !important;
}}

/* Menú → contenido: menos aire */
section[data-testid="stMain"] .block-container {{
    gap: 0.2rem !important;
}}

section[data-testid="stMain"] .block-container > [data-testid="stVerticalBlock"] {{
    gap: 0.25rem !important;
}}

section[data-testid="stMain"] [data-testid="stVerticalBlock"]:has(.st-key-calixta_nav) {{
    margin-bottom: 0 !important;
    padding-bottom: 0 !important;
    gap: 0.2rem !important;
}}

.st-key-calixta_nav + [data-testid="stElementContainer"],
.st-key-calixta_nav ~ [data-testid="stElementContainer"] {{
    margin-top: 0 !important;
    padding-top: 0 !important;
}}
</style>
"""

# CSS de pestañas internas — bloque aparte para que Streamlit no sirva versión en caché.
CALIXTA_MODULE_TABS_CSS = f"""
<style id="calixta-module-tabs-v3">
section[data-testid="stMain"] [data-testid="stTabs"],
section[data-testid="stMain"] .stTabs {{
    width: 100% !important;
    max-width: 100% !important;
    margin-top: 0.1rem !important;
    margin-bottom: 0.25rem !important;
}}

/* Fila de pestañas (Streamlit 1.60: react-aria TabList) */
section[data-testid="stMain"] [data-testid="stTabs"] > div > div:first-child,
section[data-testid="stMain"] [data-testid="stTabs"] [class*="e1ac7blb3"] {{
    display: flex !important;
    align-items: stretch !important;
    gap: 0 !important;
    width: 100% !important;
    box-sizing: border-box !important;
    background: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    padding: 0 !important;
    box-shadow: none !important;
    overflow-x: auto !important;
    scrollbar-width: none !important;
    position: relative !important;
}}

section[data-testid="stMain"] [data-testid="stTabs"] > div > div:first-child::-webkit-scrollbar {{
    display: none !important;
}}

/* Línea inferior continua */
section[data-testid="stMain"] [data-testid="stTabs"] > div > div:first-child::after,
section[data-testid="stMain"] [data-testid="stTabs"] [class*="e1ac7blb3"]::after {{
    display: block !important;
    content: "" !important;
    position: absolute !important;
    bottom: 0 !important;
    left: 0 !important;
    right: 0 !important;
    height: 1px !important;
    background-color: rgba(130, 143, 89, 0.24) !important;
    border-radius: 0 !important;
    z-index: 0 !important;
}}

section[data-testid="stMain"] [data-testid="stTabs"] [data-testid="stTabPanel"] {{
    width: 100% !important;
    max-width: 100% !important;
    padding-top: 0.85rem !important;
}}

section[data-testid="stMain"] [data-testid="stTabs"] [data-testid="stTab"],
section[data-testid="stMain"] [data-testid="stTabs"] [class*="e1ac7blb4"] {{
    position: relative !important;
    border-radius: 0 !important;
    color: {OLIVE_DARK} !important;
    font-weight: 500 !important;
    font-size: 0.86rem !important;
    padding: 0.62rem 1.15rem !important;
    min-height: unset !important;
    height: auto !important;
    background: transparent !important;
    background-image: none !important;
    border: none !important;
    border-right: 1px solid rgba(130, 143, 89, 0.2) !important;
    box-shadow: none !important;
    white-space: nowrap !important;
    transition: color 0.16s ease !important;
}}

section[data-testid="stMain"] [data-testid="stTabs"] [data-testid="stTab"]::before,
section[data-testid="stMain"] [data-testid="stTabs"] [class*="e1ac7blb4"]::before {{
    content: none !important;
    display: none !important;
}}

section[data-testid="stMain"] [data-testid="stTabs"] [data-testid="stTab"]:last-child {{
    border-right: none !important;
}}

section[data-testid="stMain"] [data-testid="stTabs"] [data-testid="stTab"] .react-aria-SelectionIndicator {{
    display: block !important;
    bottom: 0 !important;
    left: 0 !important;
    width: 100% !important;
    height: 3px !important;
    background: transparent !important;
    border-radius: 0 !important;
    z-index: 2 !important;
    transition: background-color 0.16s ease !important;
}}

section[data-testid="stMain"] [data-testid="stTabs"] [data-testid="stTab"]:hover:not([data-selected]) {{
    color: {OLIVE} !important;
    background: transparent !important;
    background-image: none !important;
}}

section[data-testid="stMain"] [data-testid="stTabs"] [data-testid="stTab"][data-selected],
section[data-testid="stMain"] [data-testid="stTabs"] [class*="e1ac7blb4"][data-selected] {{
    color: {OLIVE} !important;
    font-weight: 600 !important;
    background: transparent !important;
    background-image: none !important;
    border-color: rgba(130, 143, 89, 0.2) !important;
    box-shadow: none !important;
}}

section[data-testid="stMain"] [data-testid="stTabs"] [data-testid="stTab"][data-selected] .react-aria-SelectionIndicator {{
    background-color: {OLIVE} !important;
}}

@media (max-width: 768px) {{
    section[data-testid="stMain"] [data-testid="stTabs"] > div > div:first-child {{
        flex-wrap: nowrap !important;
    }}

    section[data-testid="stMain"] [data-testid="stTabs"] [data-testid="stTab"] {{
        font-size: 0.78rem !important;
        padding: 0.52rem 0.85rem !important;
    }}
}}
</style>
"""


def format_cop(value: float) -> str:
    return f"${value:,.0f}"
