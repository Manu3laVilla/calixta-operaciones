from ui.theme import (
    BG_GRADIENT,
    BORDER,
    CREAM,
    GLASS_BG,
    GLASS_BORDER,
    GLASS_SHADOW,
    OLIVE,
    OLIVE_DARK,
    PINK,
    PINK_SOFT,
    RADIUS_LG,
    RADIUS_MD,
    RADIUS_PILL,
    SAGE,
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
    --pink: {PINK};
    --pink-soft: {PINK_SOFT};
    --terracotta: {TERRACOTTA};
    --sage: {SAGE};
    --text: {TEXT};
    --text-muted: {TEXT_MUTED};
    --white: {WHITE};
    --glass-bg: {GLASS_BG};
    --glass-border: {GLASS_BORDER};
    --glass-shadow: {GLASS_SHADOW};
    --radius-lg: {RADIUS_LG};
    --radius-md: {RADIUS_MD};
    --radius-pill: {RADIUS_PILL};
}}

/* ——— Base ——— */
html, body, [class*="css"] {{
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: var(--text);
}}

.stApp {{
    background: {BG_GRADIENT};
    background-attachment: fixed;
}}

.stApp::before {{
    content: "";
    position: fixed;
    inset: 0;
    background:
        radial-gradient(circle at 12% 18%, rgba(247, 195, 198, 0.45) 0%, transparent 42%),
        radial-gradient(circle at 88% 12%, rgba(198, 186, 128, 0.35) 0%, transparent 38%),
        radial-gradient(circle at 70% 85%, rgba(255, 255, 205, 0.5) 0%, transparent 45%);
    pointer-events: none;
    z-index: 0;
}}

.stApp [data-testid="stAppViewContainer"] {{
    position: relative;
    z-index: 1;
}}

section[data-testid="stSidebar"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="stSidebarCollapseButton"] {{
    display: none !important;
}}

section[data-testid="stMain"] .block-container {{
    max-width: 1200px;
    padding: 1rem 1.25rem 2.5rem;
}}

/* ——— Header glass ——— */
.glass-header {{
    background: var(--glass-bg);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-lg);
    box-shadow: var(--glass-shadow);
    padding: 0.85rem 1.1rem 0.95rem;
    margin-bottom: 1.75rem;
}}

.brand-fallback {{
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--olive-dark);
    letter-spacing: 0.04em;
}}

.glass-header [data-testid="column"]:last-child button {{
    margin-top: 0.15rem;
    border-radius: 50% !important;
    width: 2.6rem !important;
    min-width: 2.6rem !important;
    height: 2.6rem !important;
    padding: 0 !important;
    background: rgba(255, 255, 255, 0.85) !important;
    border: 1px solid var(--glass-border) !important;
    color: var(--olive) !important;
    box-shadow: 0 2px 10px rgba(107, 112, 76, 0.08) !important;
}}

/* ——— Nav pills (un solo menú) ——— */
.glass-nav [data-testid="stRadio"],
.glass-header [data-testid="stRadio"] {{
    margin: 0.65rem 0 0;
}}

.glass-nav [data-testid="stRadio"] > div,
.glass-header [data-testid="stRadio"] > div {{
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 0.2rem;
    background: rgba(255, 255, 255, 0.35);
    border: 1px solid rgba(255, 255, 255, 0.55);
    border-radius: var(--radius-pill);
    padding: 0.28rem;
}}

.glass-nav [data-testid="stRadio"] label,
.glass-header [data-testid="stRadio"] label {{
    background: transparent !important;
    border: none !important;
    border-radius: var(--radius-pill) !important;
    padding: 0.5rem 1rem !important;
    margin: 0 !important;
    font-size: 0.86rem !important;
    font-weight: 600 !important;
    color: var(--text-muted) !important;
    transition: all 0.2s ease;
    white-space: nowrap;
}}

.glass-nav [data-testid="stRadio"] label:hover,
.glass-header [data-testid="stRadio"] label:hover {{
    color: var(--olive-dark) !important;
}}

.glass-nav [data-testid="stRadio"] label[data-checked="true"],
.glass-header [data-testid="stRadio"] label[data-checked="true"] {{
    background: var(--white) !important;
    color: var(--olive-dark) !important;
    box-shadow: 0 4px 14px rgba(107, 112, 76, 0.12) !important;
}}

.glass-nav [data-testid="stRadio"] div[role="radiogroup"] > label > div:first-child,
.glass-header [data-testid="stRadio"] div[role="radiogroup"] > label > div:first-child {{
    display: none !important;
}}

/* ——— Contenido ——— */
.glass-page-head {{
    background: var(--glass-bg);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-lg);
    box-shadow: var(--glass-shadow);
    padding: 1.35rem 1.5rem;
    margin-bottom: 1.5rem;
}}

.main-header {{
    font-size: 1.85rem;
    font-weight: 700;
    color: var(--olive-dark);
    margin: 0 0 0.35rem;
    line-height: 1.2;
    letter-spacing: -0.02em;
}}

.sub-header {{
    color: var(--text-muted);
    font-size: 0.95rem;
    font-weight: 400;
    margin: 0;
    line-height: 1.5;
}}

/* Métricas = mini cards glass */
[data-testid="stMetric"] {{
    background: var(--glass-bg) !important;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid var(--glass-border) !important;
    border-radius: var(--radius-md) !important;
    padding: 1rem 1.1rem !important;
    box-shadow: var(--glass-shadow) !important;
}}

[data-testid="stMetricValue"] {{
    font-size: 1.45rem !important;
    font-weight: 700 !important;
    color: var(--olive-dark) !important;
}}

[data-testid="stMetricLabel"] {{
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    color: var(--text-muted) !important;
    text-transform: uppercase;
    letter-spacing: 0.07em;
}}

/* Gráficos y bloques */
[data-testid="stVerticalBlock"] > div:has(.js-plotly-plot),
.element-container:has([data-testid="stDataFrame"]) {{
    background: var(--glass-bg);
    backdrop-filter: blur(12px);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-lg);
    box-shadow: var(--glass-shadow);
    padding: 0.5rem;
}}

h3, [data-testid="stMarkdownContainer"] h3 {{
    font-weight: 700 !important;
    color: var(--olive-dark) !important;
    font-size: 1.05rem !important;
    letter-spacing: -0.01em;
}}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {{
    background: rgba(255, 255, 255, 0.4);
    border-radius: var(--radius-pill);
    padding: 0.25rem;
    border: 1px solid var(--glass-border);
    gap: 0.2rem;
    flex-wrap: wrap;
}}

.stTabs [data-baseweb="tab"] {{
    border-radius: var(--radius-pill) !important;
    font-weight: 600;
    font-size: 0.85rem;
    color: var(--text-muted);
    min-height: 2.4rem;
}}

.stTabs [aria-selected="true"] {{
    background: var(--white) !important;
    color: var(--olive-dark) !important;
    box-shadow: 0 2px 10px rgba(107, 112, 76, 0.1) !important;
}}

/* Botones */
.stButton > button {{
    border-radius: var(--radius-pill) !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    min-height: 2.5rem;
    border: 1px solid var(--glass-border) !important;
    background: rgba(255, 255, 255, 0.7) !important;
    transition: all 0.2s ease !important;
}}

.stButton > button[kind="primary"] {{
    background: var(--olive) !important;
    border-color: var(--olive) !important;
    color: var(--white) !important;
    box-shadow: 0 4px 16px rgba(130, 143, 89, 0.3) !important;
}}

.stButton > button[kind="primary"]:hover {{
    background: var(--olive-dark) !important;
}}

.stButton > button[kind="secondary"]:hover {{
    background: var(--pink-soft) !important;
    border-color: var(--pink) !important;
}}

/* Inputs glass */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
    border-radius: 14px !important;
    border-color: var(--glass-border) !important;
    background: rgba(255, 255, 255, 0.75) !important;
    backdrop-filter: blur(6px);
}}

[data-testid="stDataFrame"] {{
    border-radius: var(--radius-md);
    border: 1px solid var(--glass-border);
    overflow: hidden;
    background: rgba(255, 255, 255, 0.55);
}}

/* Alertas / info */
[data-testid="stAlert"] {{
    border-radius: var(--radius-md) !important;
    backdrop-filter: blur(8px);
}}

/* ——— Tablet ——— */
@media (max-width: 960px) {{
    .glass-header {{
        padding: 0.75rem;
    }}

    .glass-header [data-testid="stRadio"] label {{
        font-size: 0.78rem !important;
        padding: 0.45rem 0.65rem !important;
    }}

    .main-header {{
        font-size: 1.55rem;
    }}

    div[data-testid="stHorizontalBlock"] {{
        flex-wrap: wrap !important;
        gap: 0.65rem !important;
    }}
}}

/* ——— Móvil ——— */
@media (max-width: 768px) {{
    header[data-testid="stHeader"],
    [data-testid="stDecoration"],
    [data-testid="stToolbar"] {{
        display: none !important;
    }}

    section[data-testid="stMain"] .block-container {{
        padding: 0.65rem 0.75rem 5.75rem !important;
    }}

    .glass-header {{
        padding: 0.7rem 0.75rem 0.5rem;
        margin-bottom: 1.25rem;
        border-radius: var(--radius-md);
    }}

    .glass-header > div[data-testid="stHorizontalBlock"]:first-child {{
        margin-bottom: 0 !important;
    }}

    .glass-nav {{
        height: 0;
        overflow: visible;
    }}

    .glass-nav [data-testid="stRadio"],
    .glass-header [data-testid="stRadio"] {{
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        z-index: 999;
        margin: 0;
        padding: 0.45rem 0.4rem calc(0.55rem + env(safe-area-inset-bottom));
        background: rgba(255, 255, 255, 0.88);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-top: 1px solid var(--glass-border);
        box-shadow: 0 -8px 30px rgba(107, 112, 76, 0.12);
    }}

    .glass-nav [data-testid="stRadio"] > div,
    .glass-header [data-testid="stRadio"] > div {{
        justify-content: space-between;
        flex-wrap: nowrap;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        scrollbar-width: none;
        background: rgba(255, 255, 255, 0.5);
    }}

    .glass-nav [data-testid="stRadio"] > div::-webkit-scrollbar,
    .glass-header [data-testid="stRadio"] > div::-webkit-scrollbar {{
        display: none;
    }}

    .glass-nav [data-testid="stRadio"] label,
    .glass-header [data-testid="stRadio"] label {{
        flex: 1 0 auto;
        font-size: 0.68rem !important;
        padding: 0.45rem 0.55rem !important;
        text-align: center;
    }}

    .glass-page-head {{
        padding: 1rem 1.1rem;
        border-radius: var(--radius-md);
    }}

    div[data-testid="stHorizontalBlock"] {{
        flex-direction: column !important;
    }}

    div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {{
        width: 100% !important;
        min-width: 0 !important;
    }}

    .stButton > button {{
        width: 100%;
    }}
}}
</style>
"""


def format_cop(value: float) -> str:
    return f"${value:,.0f} COP"
