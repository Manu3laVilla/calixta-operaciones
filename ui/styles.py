from ui.theme import (
    BORDER,
    CREAM,
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
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,400&family=DM+Serif+Display&display=swap');

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
    --border: {BORDER};
    --bg: #FAFAF8;
    --surface: #FFFFFF;
    --radius: 16px;
    --shadow-sm: 0 1px 3px rgba(74, 80, 53, 0.06);
    --shadow-md: 0 8px 30px rgba(74, 80, 53, 0.07);
}}

/* Base */
html, body, [class*="css"] {{
    font-family: 'DM Sans', sans-serif;
    color: var(--text);
}}

.stApp {{
    background: var(--bg);
}}

section[data-testid="stSidebar"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="stSidebarCollapseButton"] {{
    display: none !important;
}}

section[data-testid="stMain"] .block-container {{
    max-width: 1100px;
    padding-top: 0.75rem;
    padding-bottom: 2.5rem;
}}

/* ——— Header ——— */
.site-header {{
    margin: -1rem -1rem 2rem;
    padding: 1.25rem 1.5rem 0;
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    box-shadow: var(--shadow-sm);
}}

.logo-fallback {{
    font-family: 'DM Serif Display', serif;
    font-size: 1.75rem;
    color: var(--olive-dark);
}}

.site-tagline {{
    margin: 1.6rem 0 0;
    font-size: 0.8rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--text-muted);
    font-weight: 500;
}}

.site-header [data-testid="column"]:last-child button {{
    margin-top: 1.1rem;
    border-radius: 10px !important;
    font-size: 0.8rem !important;
    min-height: 2.25rem !important;
    background: var(--bg) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-muted) !important;
}}

.site-header [data-testid="column"]:last-child button:hover {{
    border-color: var(--olive) !important;
    color: var(--olive-dark) !important;
}}

/* ——— Un solo menú (radio horizontal) ——— */
.site-header [data-testid="stRadio"] {{
    margin: 1rem 0 0;
    padding-bottom: 0;
}}

.site-header [data-testid="stRadio"] > div {{
    display: flex;
    flex-direction: row;
    flex-wrap: wrap;
    gap: 0.35rem;
    background: transparent;
}}

.site-header [data-testid="stRadio"] label {{
    background: transparent !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.55rem 1rem !important;
    margin: 0 !important;
    font-size: 0.9rem !important;
    font-weight: 500 !important;
    color: var(--text-muted) !important;
    transition: color 0.15s, background 0.15s;
    cursor: pointer;
}}

.site-header [data-testid="stRadio"] label:hover {{
    color: var(--olive-dark) !important;
    background: var(--cream) !important;
}}

.site-header [data-testid="stRadio"] label[data-checked="true"] {{
    color: var(--olive-dark) !important;
    background: var(--cream) !important;
    box-shadow: inset 0 -2px 0 var(--terracotta);
}}

.site-header [data-testid="stRadio"] div[role="radiogroup"] > label > div:first-child {{
    display: none !important;
}}

/* ——— Página ——— */
.main-header {{
    font-family: 'DM Serif Display', serif;
    font-size: 2.1rem;
    font-weight: 400;
    color: var(--olive-dark);
    margin-bottom: 0.25rem;
    line-height: 1.2;
}}

.sub-header {{
    color: var(--text-muted);
    font-size: 1rem;
    font-weight: 400;
    margin-bottom: 1.75rem;
    line-height: 1.55;
}}

/* Métricas */
[data-testid="stMetric"] {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem 1.1rem;
    box-shadow: var(--shadow-sm);
}}

[data-testid="stMetricValue"] {{
    font-family: 'DM Serif Display', serif;
    font-size: 1.55rem !important;
    color: var(--olive-dark) !important;
}}

[data-testid="stMetricLabel"] {{
    font-size: 0.78rem !important;
    color: var(--text-muted) !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}}

/* Tabs internas */
.stTabs [data-baseweb="tab-list"] {{
    gap: 0.25rem;
    border-bottom: 1px solid var(--border);
    background: transparent;
}}

.stTabs [data-baseweb="tab"] {{
    background: transparent !important;
    border-radius: 0 !important;
    color: var(--text-muted);
    font-weight: 500;
    border-bottom: 2px solid transparent;
    min-height: 2.75rem;
}}

.stTabs [aria-selected="true"] {{
    color: var(--olive-dark) !important;
    border-bottom-color: var(--terracotta) !important;
}}

/* Botones */
.stButton > button {{
    border-radius: 10px !important;
    font-weight: 500 !important;
    min-height: 2.5rem;
    border: 1px solid var(--border) !important;
}}

.stButton > button[kind="primary"] {{
    background: var(--olive) !important;
    border-color: var(--olive) !important;
    color: var(--white) !important;
}}

.stButton > button[kind="primary"]:hover {{
    background: var(--olive-dark) !important;
}}

/* Inputs */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea {{
    border-radius: 10px !important;
    border-color: var(--border) !important;
    background: var(--surface) !important;
}}

[data-testid="stDataFrame"] {{
    border: 1px solid var(--border);
    border-radius: var(--radius);
    overflow: hidden;
}}

h3 {{
    font-family: 'DM Serif Display', serif !important;
    color: var(--olive-dark) !important;
    font-weight: 400 !important;
}}

/* ——— Tablet ——— */
@media (max-width: 900px) {{
    .site-header {{
        margin: -0.5rem -0.5rem 1.5rem;
        padding: 1rem;
    }}

    .site-tagline {{
        margin-top: 0.5rem;
    }}

    .main-header {{
        font-size: 1.75rem;
    }}
}}

/* ——— Móvil: mismo menú, fijo abajo ——— */
@media (max-width: 768px) {{
    header[data-testid="stHeader"],
    [data-testid="stDecoration"],
    [data-testid="stToolbar"] {{
        display: none !important;
    }}

    .site-header {{
        margin: -0.5rem -0.75rem 1.25rem;
        padding: 0.85rem 0.9rem 0;
    }}

    .site-header [data-testid="column"]:nth-child(2) {{
        display: none;
    }}

    .site-header [data-testid="stRadio"] {{
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        z-index: 999;
        margin: 0;
        padding: 0.5rem 0.35rem calc(0.55rem + env(safe-area-inset-bottom));
        background: rgba(255, 255, 255, 0.96);
        backdrop-filter: blur(16px);
        border-top: 1px solid var(--border);
        box-shadow: 0 -4px 20px rgba(74, 80, 53, 0.08);
    }}

    .site-header [data-testid="stRadio"] > div {{
        justify-content: space-between;
        flex-wrap: nowrap;
        gap: 0.15rem;
    }}

    .site-header [data-testid="stRadio"] label {{
        flex: 1;
        text-align: center;
        font-size: 0.68rem !important;
        padding: 0.45rem 0.2rem !important;
        border-radius: 8px !important;
    }}

    .site-header [data-testid="stRadio"] label[data-checked="true"] {{
        box-shadow: none;
        background: var(--pink-soft) !important;
    }}

    section[data-testid="stMain"] .block-container {{
        padding-bottom: 5.5rem !important;
    }}

    div[data-testid="stHorizontalBlock"] {{
        flex-direction: column !important;
    }}

    div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {{
        width: 100% !important;
    }}
}}
</style>
"""


def format_cop(value: float) -> str:
    return f"${value:,.0f} COP"
