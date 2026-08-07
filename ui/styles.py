from ui.theme import (
    BORDER,
    CREAM,
    CREAM_SOFT,
    OLIVE,
    OLIVE_DARK,
    PINK,
    PINK_SOFT,
    SAGE,
    TERRACOTTA,
    TEXT,
    TEXT_MUTED,
    WHITE,
)

CALIXTA_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Outfit:wght@300;400;500;600&display=swap');

:root {{
    --cream: {CREAM};
    --cream-soft: {CREAM_SOFT};
    --olive: {OLIVE};
    --olive-dark: {OLIVE_DARK};
    --pink: {PINK};
    --pink-soft: {PINK_SOFT};
    --terracotta: {TERRACOTTA};
    --sage: {SAGE};
    --text: {TEXT};
    --text-muted: {TEXT_MUTED};
    --white: {WHITE};
    --border: {BORDER};
    --shadow: 0 8px 28px rgba(74, 80, 53, 0.08);
    --radius: 14px;
}}

html, body, [class*="css"] {{
    font-family: 'Outfit', sans-serif;
    color: var(--text);
}}

.stApp {{
    background: linear-gradient(165deg, var(--cream) 0%, var(--cream-soft) 45%, #FFF9F0 100%);
    overflow-x: hidden;
}}

/* Ocultar sidebar — menú superior moderno */
section[data-testid="stSidebar"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="stSidebarCollapseButton"] {{
    display: none !important;
}}

section[data-testid="stMain"] {{
    overflow-x: hidden;
}}

section[data-testid="stMain"] .block-container {{
    max-width: 1180px;
    padding-top: 0.5rem;
    padding-bottom: 2rem;
}}

/* ——— Barra de navegación ——— */
.calixta-nav-shell {{
    background: rgba(255, 255, 255, 0.72);
    backdrop-filter: blur(12px);
    border: 1px solid var(--border);
    border-radius: calc(var(--radius) + 4px);
    padding: 0.65rem 1rem 0.75rem;
    margin-bottom: 1.5rem;
    box-shadow: var(--shadow);
}}

.nav-logo-fallback {{
    font-family: 'Fraunces', serif;
    font-size: 1.6rem;
    color: var(--olive-dark);
    margin: 0;
    letter-spacing: 0.04em;
}}

#desktop-nav-anchor ~ div[data-testid="stHorizontalBlock"] {{
    gap: 0.35rem !important;
    margin: 0 !important;
}}

#desktop-nav-anchor ~ div[data-testid="stHorizontalBlock"] button {{
    border-radius: 999px !important;
    border: 1.5px solid transparent !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    padding: 0.45rem 0.55rem !important;
    min-height: 2.4rem !important;
    transition: all 0.2s ease !important;
    background: transparent !important;
    color: var(--text-muted) !important;
}}

#desktop-nav-anchor ~ div[data-testid="stHorizontalBlock"] button:hover {{
    background: var(--pink-soft) !important;
    color: var(--olive-dark) !important;
    border-color: var(--pink) !important;
}}

#desktop-nav-anchor ~ div[data-testid="stHorizontalBlock"] button[kind="primary"],
#desktop-nav-anchor ~ div[data-testid="stHorizontalBlock"] button[data-testid="stBaseButton-primary"] {{
    background: var(--olive) !important;
    color: var(--white) !important;
    border-color: var(--olive) !important;
    box-shadow: 0 4px 14px rgba(130, 143, 89, 0.35) !important;
}}

#desktop-nav-anchor ~ div[data-testid="stHorizontalBlock"] button[kind="primary"]:hover {{
    background: var(--olive-dark) !important;
    border-color: var(--olive-dark) !important;
}}

.calixta-nav-shell [data-testid="column"]:last-child button {{
    border-radius: 50% !important;
    width: 2.5rem !important;
    min-width: 2.5rem !important;
    height: 2.5rem !important;
    padding: 0 !important;
    background: var(--pink-soft) !important;
    color: var(--terracotta) !important;
    border: 1px solid var(--pink) !important;
}}

/* Mobile nav oculto en desktop */
#mobile-nav-anchor,
#mobile-nav-anchor ~ div[data-testid="stHorizontalBlock"] {{
    display: none;
}}

.mobile-top-bar {{
    display: none;
}}

/* ——— Tipografía de página ——— */
.main-header {{
    font-family: 'Fraunces', serif;
    font-size: 2.35rem;
    font-weight: 600;
    color: var(--olive-dark);
    letter-spacing: 0.02em;
    margin-bottom: 0.15rem;
    line-height: 1.15;
}}

.sub-header {{
    color: var(--text-muted);
    font-weight: 300;
    margin-bottom: 1.5rem;
    font-size: 1.02rem;
    line-height: 1.5;
}}

/* ——— Métricas y tarjetas ——— */
[data-testid="stMetric"] {{
    background: var(--white);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 0.85rem 1rem;
    box-shadow: var(--shadow);
}}

[data-testid="stMetricValue"] {{
    font-family: 'Fraunces', serif;
    font-size: 1.65rem !important;
    color: var(--terracotta) !important;
    line-height: 1.2 !important;
    word-break: break-word;
}}

[data-testid="stMetricLabel"] {{
    font-size: 0.82rem !important;
    color: var(--text-muted) !important;
    font-weight: 500 !important;
}}

/* ——— Tabs ——— */
.stTabs [data-baseweb="tab-list"] {{
    gap: 0.4rem;
    flex-wrap: wrap;
    background: rgba(255, 255, 255, 0.5);
    border-radius: 999px;
    padding: 0.3rem;
    border: 1px solid var(--border);
}}

.stTabs [data-baseweb="tab"] {{
    height: auto !important;
    min-height: 2.5rem;
    border-radius: 999px !important;
    white-space: normal;
    text-align: center;
    font-weight: 500;
    color: var(--text-muted);
}}

.stTabs [aria-selected="true"] {{
    background: var(--olive) !important;
    color: var(--white) !important;
}}

/* ——— Botones generales ——— */
.stButton > button {{
    border-radius: 999px !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 500 !important;
    min-height: 2.65rem;
    border: 1.5px solid var(--border) !important;
    transition: all 0.2s ease !important;
}}

.stButton > button[kind="primary"] {{
    background: var(--terracotta) !important;
    border-color: var(--terracotta) !important;
    color: var(--white) !important;
}}

.stButton > button[kind="primary"]:hover {{
    background: #9A5E26 !important;
    border-color: #9A5E26 !important;
}}

.stButton > button[kind="secondary"]:hover {{
    background: var(--pink-soft) !important;
    border-color: var(--pink) !important;
    color: var(--olive-dark) !important;
}}

/* ——— Inputs ——— */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stSelectbox"] div[data-baseweb="select"] {{
    border-radius: 12px !important;
    border-color: var(--border) !important;
}}

[data-testid="stDataFrame"],
[data-testid="stTable"] {{
    border-radius: var(--radius);
    overflow: hidden;
    border: 1px solid var(--border);
    box-shadow: var(--shadow);
}}

h3 {{
    font-family: 'Fraunces', serif !important;
    color: var(--olive-dark) !important;
    font-weight: 600 !important;
}}

/* ——— Tablet ——— */
@media (max-width: 992px) {{
    .main-header {{
        font-size: 1.9rem;
    }}

    [data-testid="stMetricValue"] {{
        font-size: 1.35rem !important;
    }}

    #desktop-nav-anchor ~ div[data-testid="stHorizontalBlock"] button {{
        font-size: 0.72rem !important;
        padding: 0.4rem 0.3rem !important;
    }}

    div[data-testid="stHorizontalBlock"] {{
        flex-wrap: wrap !important;
        gap: 0.75rem !important;
    }}

    div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {{
        flex: 1 1 45% !important;
        min-width: 0 !important;
        max-width: 100% !important;
    }}
}}

/* ——— Mobile ——— */
@media (max-width: 768px) {{
    header[data-testid="stHeader"],
    [data-testid="stDecoration"],
    [data-testid="stToolbar"],
    [data-testid="stToolbarActions"],
    [data-testid="stStatusWidget"] {{
        display: none !important;
    }}

    .calixta-nav-shell {{
        padding: 0.5rem 0.75rem;
        margin-bottom: 1rem;
        border-radius: var(--radius);
    }}

    .calixta-nav-shell [data-testid="column"]:nth-child(2) {{
        display: none !important;
    }}

    .calixta-nav-shell [data-testid="column"]:last-child {{
        display: flex;
        justify-content: flex-end;
        align-items: center;
    }}

    #desktop-nav-anchor,
    #desktop-nav-anchor ~ div[data-testid="stHorizontalBlock"] {{
        display: none !important;
    }}

    #mobile-nav-anchor ~ div[data-testid="stHorizontalBlock"] {{
        display: flex !important;
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        z-index: 999999;
        background: rgba(255, 255, 255, 0.92);
        backdrop-filter: blur(14px);
        border-top: 1px solid var(--border);
        padding: 0.35rem 0.2rem calc(0.45rem + env(safe-area-inset-bottom, 0px));
        box-shadow: 0 -6px 24px rgba(74, 80, 53, 0.1);
        margin: 0 !important;
        gap: 0.1rem !important;
    }}

    #mobile-nav-anchor ~ div[data-testid="stHorizontalBlock"] button {{
        border-radius: 12px !important;
        min-height: 3rem !important;
        font-size: 0.55rem !important;
        line-height: 1.15 !important;
        white-space: pre-line !important;
        padding: 0.3rem 0.05rem !important;
        border: none !important;
        background: transparent !important;
        color: var(--text-muted) !important;
    }}

    #mobile-nav-anchor ~ div[data-testid="stHorizontalBlock"] button[kind="primary"] {{
        background: var(--pink-soft) !important;
        color: var(--olive-dark) !important;
        font-weight: 600 !important;
    }}

    section[data-testid="stMain"] > div.block-container {{
        padding-left: 0.9rem !important;
        padding-right: 0.9rem !important;
        padding-bottom: 5.75rem !important;
    }}

    .main-header {{
        font-size: 1.5rem;
    }}

    .sub-header {{
        font-size: 0.92rem;
    }}

    div[data-testid="stHorizontalBlock"] {{
        flex-direction: column !important;
        flex-wrap: nowrap !important;
        gap: 0.5rem !important;
        width: 100% !important;
    }}

    #mobile-nav-anchor ~ div[data-testid="stHorizontalBlock"] {{
        flex-direction: row !important;
    }}

    div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {{
        width: 100% !important;
        min-width: 0 !important;
        max-width: 100% !important;
        flex: none !important;
    }}

    #mobile-nav-anchor ~ div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {{
        flex: 1 1 0 !important;
        width: auto !important;
    }}

    [data-testid="stSelectbox"] > div,
    [data-testid="stTextInput"] > div,
    [data-testid="stNumberInput"] > div,
    [data-testid="stTextArea"] > div {{
        font-size: 16px !important;
    }}

    .stButton > button {{
        width: 100%;
    }}
}}
</style>
"""


def format_cop(value: float) -> str:
    return f"${value:,.0f} COP"
