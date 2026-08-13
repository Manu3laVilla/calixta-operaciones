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

section[data-testid="stMain"] .block-container {{
    max-width: 1280px;
    padding: 0 1.25rem 2rem !important;
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
    margin-bottom: 1rem;
    padding: 0.15rem 0.35rem;
}}
.page-title {{
    font-size: 1.65rem;
    font-weight: 700;
    color: var(--olive-deep);
    margin: 0 0 0.3rem;
}}
.page-subtitle {{ color: var(--muted); margin: 0; font-size: 0.92rem; }}

.page-section-inner {{
    padding: 0.15rem 0.35rem 0.5rem;
}}

.main-content .stTabs {{
    margin-top: 0.25rem;
}}

.stTabs [data-baseweb="tab"] {{
    border-radius: var(--r-pill) !important;
    color: var(--olive-dark) !important;
    font-weight: 500 !important;
    padding: 0.45rem 1rem !important;
}}

/* Widgets globales */
.stTabs [data-baseweb="tab-list"] {{
    background: {BG_NAV_TRACK};
    border-radius: var(--r-pill);
    padding: 0.25rem;
    border: 1px solid var(--border);
}}

.stTabs [aria-selected="true"] {{
    background: var(--olive) !important;
    color: var(--white) !important;
    border-radius: var(--r-pill) !important;
    font-weight: 600 !important;
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

[data-testid="stDataFrame"] {{
    border-radius: var(--r-md);
    border: 1px solid var(--border);
    overflow: hidden;
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

/* ── Menú tabs (solo barra de navegación, no afecta dashboard) ── */
[data-testid="stElementContainer"]:has([data-testid="stMarkdown"] .calixta-nav-root) {{
    display: none !important;
    height: 0 !important;
    min-height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: hidden !important;
}}

[data-testid="stElementContainer"]:has([data-testid="stMarkdown"] .calixta-nav-root) + [data-testid="stElementContainer"] {{
    width: 100vw;
    max-width: 100vw;
    margin-left: calc(50% - 50vw);
    margin-right: calc(50% - 50vw);
    padding: 0 1.1rem 0.65rem;
    margin-bottom: 0.5rem;
    box-sizing: border-box;
}}

[data-testid="stElementContainer"]:has([data-testid="stMarkdown"] .calixta-nav-root) + [data-testid="stElementContainer"] [data-testid="stHorizontalBlock"] {{
    background: linear-gradient(
        180deg,
        rgba(255, 255, 205, 0.92) 0%,
        rgba(255, 252, 220, 0.82) 100%
    );
    border-radius: 14px;
    padding: 0.42rem 0.55rem 0.42rem 0.7rem;
    border: 1px solid rgba(198, 186, 128, 0.45);
    box-shadow: 0 1px 3px rgba(61, 64, 53, 0.04);
    gap: 0.12rem !important;
    align-items: center !important;
}}

[data-testid="stElementContainer"]:has([data-testid="stMarkdown"] .calixta-nav-root) + [data-testid="stElementContainer"] [data-testid="stImage"] {{
    margin: 0 !important;
    padding: 0 0.15rem 0 0.1rem !important;
}}

[data-testid="stElementContainer"]:has([data-testid="stMarkdown"] .calixta-nav-root) + [data-testid="stElementContainer"] [data-testid="stImage"] img {{
    max-height: 34px !important;
    width: auto !important;
    display: block;
}}

[data-testid="stElementContainer"]:has([data-testid="stMarkdown"] .calixta-nav-root) + [data-testid="stElementContainer"] .stButton {{
    margin: 0 !important;
}}

[data-testid="stElementContainer"]:has([data-testid="stMarkdown"] .calixta-nav-root) + [data-testid="stElementContainer"] .stButton > button[kind="secondary"] {{
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: {OLIVE_DARK} !important;
    font-size: 0.9rem !important;
    font-weight: 500 !important;
    padding: 0.58rem 0.65rem !important;
    min-height: 2.55rem !important;
    border-radius: 12px !important;
    white-space: nowrap !important;
}}

[data-testid="stElementContainer"]:has([data-testid="stMarkdown"] .calixta-nav-root) + [data-testid="stElementContainer"] .stButton > button[kind="secondary"]:hover {{
    background: rgba(255, 255, 255, 0.28) !important;
    color: {OLIVE_DEEP} !important;
    border: none !important;
}}

[data-testid="stElementContainer"]:has([data-testid="stMarkdown"] .calixta-nav-root) + [data-testid="stElementContainer"] .stButton > button[kind="primary"] {{
    background: linear-gradient(
        90deg,
        rgba(247, 195, 198, 0.92) 0%,
        rgba(255, 255, 205, 0.55) 52%,
        rgba(255, 252, 220, 0.25) 100%
    ) !important;
    border: none !important;
    border-left: 4px solid {OLIVE_DEEP} !important;
    border-radius: 12px !important;
    box-shadow: none !important;
    color: {OLIVE_DEEP} !important;
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    padding: 0.58rem 0.65rem 0.58rem 0.75rem !important;
    min-height: 2.55rem !important;
    white-space: nowrap !important;
}}

[data-testid="stElementContainer"]:has([data-testid="stMarkdown"] .calixta-nav-root) + [data-testid="stElementContainer"] .stButton > button[kind="primary"]:hover {{
    background: linear-gradient(
        90deg,
        rgba(247, 195, 198, 1) 0%,
        rgba(255, 255, 205, 0.65) 100%
    ) !important;
    color: {OLIVE_DEEP} !important;
    border-left: 4px solid {OLIVE_DEEP} !important;
}}

[data-testid="stElementContainer"]:has([data-testid="stMarkdown"] .calixta-nav-root) + [data-testid="stElementContainer"] > div > [data-testid="stHorizontalBlock"] > [data-testid="column"]:last-child .stButton > button {{
    width: 2rem !important;
    min-width: 2rem !important;
    height: 2rem !important;
    min-height: 2rem !important;
    padding: 0 !important;
    border-radius: 9px !important;
    background: rgba(255, 255, 255, 0.35) !important;
    border: 1px solid rgba(130, 143, 89, 0.14) !important;
    color: {OLIVE_DARK} !important;
    box-shadow: none !important;
    font-size: 0.95rem !important;
    font-weight: 400 !important;
}}

@media (max-width: 900px) {{
    [data-testid="stElementContainer"]:has([data-testid="stMarkdown"] .calixta-nav-root) + [data-testid="stElementContainer"] {{
        padding: 0 0.55rem 0.5rem;
    }}

    [data-testid="stElementContainer"]:has([data-testid="stMarkdown"] .calixta-nav-root) + [data-testid="stElementContainer"] .stButton > button {{
        font-size: 0.74rem !important;
        padding: 0.45rem 0.25rem !important;
        min-height: 2.1rem !important;
    }}
}}
</style>
"""


def format_cop(value: float) -> str:
    return f"${value:,.0f}"
