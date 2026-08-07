from ui.theme import (
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
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Syne:wght@600;700&display=swap');

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
    --radius: 20px;
    --radius-pill: 999px;
}}

/* ——— Fondo con paleta viva ——— */
html, body, [class*="css"] {{
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: var(--text);
}}

.stApp {{
    background-color: var(--cream);
    background-image:
        radial-gradient(ellipse 80% 60% at 0% 0%, rgba(247, 195, 198, 0.55) 0%, transparent 55%),
        radial-gradient(ellipse 70% 50% at 100% 10%, rgba(198, 186, 128, 0.45) 0%, transparent 50%),
        radial-gradient(ellipse 60% 40% at 50% 100%, rgba(240, 199, 193, 0.4) 0%, transparent 55%);
    background-attachment: fixed;
}}

section[data-testid="stSidebar"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="stSidebarCollapseButton"] {{
    display: none !important;
}}

section[data-testid="stMain"] .block-container {{
    max-width: 1140px;
    padding: 0.75rem 1.25rem 2.5rem;
}}

/* ——— Header ——— */
.site-header {{
    background: rgba(255, 255, 255, 0.78);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.9);
    border-radius: calc(var(--radius) + 4px);
    box-shadow: 0 12px 40px rgba(130, 143, 89, 0.12);
    padding: 1rem 1.25rem 1.1rem;
    margin-bottom: 1.75rem;
}}

/* Marca: ícono + logo */
.brand-block {{
    display: flex;
    align-items: center;
    gap: 0.85rem;
}}

.brand-icon-wrap {{
    flex-shrink: 0;
    width: 52px;
    height: 52px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(145deg, var(--pink-soft), var(--pink));
    border-radius: 16px;
    box-shadow: 0 4px 14px rgba(247, 195, 198, 0.5);
}}

.brand-icon {{
    width: 34px;
    height: 34px;
    object-fit: contain;
}}

.brand-text {{
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 0.15rem;
    min-width: 0;
}}

.brand-logo {{
    height: 32px;
    width: auto;
    object-fit: contain;
    object-position: left center;
    display: block;
}}

.brand-fallback {{
    font-family: 'Syne', sans-serif;
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--olive-dark);
    letter-spacing: -0.02em;
}}

.brand-subtitle {{
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--terracotta);
}}

.site-header [data-testid="column"]:last-child {{
    display: flex;
    align-items: flex-start;
    justify-content: flex-end;
}}

.site-header [data-testid="column"]:last-child button {{
    margin-top: 0.5rem;
    border-radius: 14px !important;
    width: 2.75rem !important;
    min-width: 2.75rem !important;
    height: 2.75rem !important;
    padding: 0 !important;
    background: var(--sage) !important;
    border: none !important;
    color: var(--white) !important;
    font-size: 1.1rem !important;
    box-shadow: 0 4px 12px rgba(198, 186, 128, 0.45) !important;
}}

.site-header [data-testid="column"]:last-child button:hover {{
    background: var(--olive) !important;
}}

/* ——— Menú pills moderno ——— */
.site-header [data-testid="stPills"] {{
    margin-top: 1rem;
}}

.site-header [data-testid="stPills"] > div {{
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 0.35rem;
    background: rgba(198, 186, 128, 0.28);
    border: 1px solid rgba(130, 143, 89, 0.15);
    border-radius: var(--radius-pill);
    padding: 0.35rem;
}}

.site-header [data-testid="stPills"] button {{
    border-radius: var(--radius-pill) !important;
    border: none !important;
    background: transparent !important;
    color: var(--olive-dark) !important;
    font-weight: 600 !important;
    font-size: 0.84rem !important;
    padding: 0.5rem 1.1rem !important;
    min-height: 2.35rem !important;
    transition: all 0.2s ease !important;
    box-shadow: none !important;
}}

.site-header [data-testid="stPills"] button:hover {{
    background: rgba(255, 255, 255, 0.55) !important;
    color: var(--olive-dark) !important;
}}

.site-header [data-testid="stPills"] button[kind="primary"],
.site-header [data-testid="stPills"] button[aria-pressed="true"] {{
    background: var(--white) !important;
    color: var(--olive-dark) !important;
    box-shadow: 0 4px 16px rgba(130, 143, 89, 0.18) !important;
}}

/* ——— Contenido ——— */
.glass-page-head {{
    background: rgba(255, 255, 255, 0.72);
    backdrop-filter: blur(14px);
    border: 1px solid rgba(255, 255, 255, 0.85);
    border-radius: var(--radius);
    border-left: 4px solid var(--terracotta);
    box-shadow: 0 8px 28px rgba(130, 143, 89, 0.1);
    padding: 1.25rem 1.4rem;
    margin-bottom: 1.5rem;
}}

.main-header {{
    font-family: 'Syne', sans-serif;
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--olive-dark);
    margin: 0 0 0.3rem;
    letter-spacing: -0.02em;
}}

.sub-header {{
    color: var(--text-muted);
    font-size: 0.95rem;
    margin: 0;
    line-height: 1.5;
}}

/* Métricas con color */
[data-testid="stMetric"] {{
    background: rgba(255, 255, 255, 0.8) !important;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.9) !important;
    border-radius: var(--radius) !important;
    border-top: 3px solid var(--olive) !important;
    padding: 1rem !important;
    box-shadow: 0 6px 20px rgba(130, 143, 89, 0.08) !important;
}}

[data-testid="stMetric"]:nth-child(2) {{
    border-top-color: var(--terracotta) !important;
}}

[data-testid="stMetric"]:nth-child(3) {{
    border-top-color: var(--pink) !important;
}}

[data-testid="stMetricValue"] {{
    font-family: 'Syne', sans-serif;
    font-size: 1.4rem !important;
    font-weight: 700 !important;
    color: var(--olive-dark) !important;
}}

[data-testid="stMetricLabel"] {{
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    color: var(--text-muted) !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}}

h3 {{
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    color: var(--olive-dark) !important;
}}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {{
    background: rgba(198, 186, 128, 0.22);
    border-radius: var(--radius-pill);
    padding: 0.3rem;
    gap: 0.25rem;
    flex-wrap: wrap;
}}

.stTabs [data-baseweb="tab"] {{
    border-radius: var(--radius-pill) !important;
    font-weight: 600;
    color: var(--text-muted);
}}

.stTabs [aria-selected="true"] {{
    background: var(--white) !important;
    color: var(--olive-dark) !important;
}}

/* Botones */
.stButton > button {{
    border-radius: var(--radius-pill) !important;
    font-weight: 600 !important;
    border: none !important;
    transition: all 0.2s ease !important;
}}

.stButton > button[kind="primary"] {{
    background: linear-gradient(135deg, var(--terracotta), #9A5E26) !important;
    color: var(--white) !important;
    box-shadow: 0 4px 16px rgba(183, 112, 46, 0.35) !important;
}}

.stButton > button[kind="secondary"] {{
    background: rgba(255, 255, 255, 0.8) !important;
    color: var(--olive-dark) !important;
    border: 1px solid rgba(130, 143, 89, 0.2) !important;
}}

.stButton > button[kind="secondary"]:hover {{
    background: var(--pink-soft) !important;
}}

[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea {{
    border-radius: 12px !important;
    border: 1px solid rgba(130, 143, 89, 0.2) !important;
    background: rgba(255, 255, 255, 0.85) !important;
}}

[data-testid="stDataFrame"] {{
    border-radius: var(--radius);
    border: 1px solid rgba(255, 255, 255, 0.9);
    background: rgba(255, 255, 255, 0.7);
    overflow: hidden;
}}

/* ——— Tablet ——— */
@media (max-width: 900px) {{
    .brand-logo {{ height: 28px; }}
    .site-header [data-testid="stPills"] button {{
        font-size: 0.78rem !important;
        padding: 0.45rem 0.75rem !important;
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
        padding: 0.5rem 0.85rem 5.5rem !important;
    }}

    .site-header {{
        padding: 0.85rem 1rem 0.5rem;
        margin-bottom: 1.25rem;
    }}

    .brand-icon-wrap {{
        width: 44px;
        height: 44px;
        border-radius: 14px;
    }}

    .brand-icon {{ width: 28px; height: 28px; }}
    .brand-logo {{ height: 26px; }}
    .brand-subtitle {{ font-size: 0.65rem; }}

    .site-header [data-testid="stPills"] {{
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        z-index: 999;
        margin: 0;
        padding: 0.5rem 0.5rem calc(0.6rem + env(safe-area-inset-bottom));
        background: rgba(255, 255, 255, 0.94);
        backdrop-filter: blur(20px);
        border-top: 1px solid rgba(130, 143, 89, 0.12);
        box-shadow: 0 -8px 32px rgba(130, 143, 89, 0.15);
    }}

    .site-header [data-testid="stPills"] > div {{
        flex-wrap: nowrap;
        overflow-x: auto;
        justify-content: flex-start;
        -webkit-overflow-scrolling: touch;
        scrollbar-width: none;
        background: rgba(198, 186, 128, 0.2);
    }}

    .site-header [data-testid="stPills"] > div::-webkit-scrollbar {{
        display: none;
    }}

    .site-header [data-testid="stPills"] button {{
        flex-shrink: 0;
        font-size: 0.72rem !important;
        padding: 0.45rem 0.85rem !important;
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
