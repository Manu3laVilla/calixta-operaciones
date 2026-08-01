CALIXTA_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=Montserrat:wght@300;400;500&display=swap');

html, body {
    font-family: 'Montserrat', sans-serif;
    overflow-x: hidden;
}

.stApp {
    overflow-x: hidden;
}

.main-header {
    font-family: 'Cormorant Garamond', serif;
    font-size: 2.4rem;
    font-weight: 600;
    color: #1A1A1A;
    letter-spacing: 0.06em;
    margin-bottom: 0.2rem;
    text-transform: uppercase;
    line-height: 1.2;
    overflow-wrap: anywhere;
}

.sub-header {
    color: #6B6560;
    font-weight: 300;
    margin-bottom: 1.5rem;
    letter-spacing: 0.01em;
    line-height: 1.5;
}

.brand-sidebar {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.8rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #1A1A1A;
    margin-bottom: 0;
}

.mobile-hint {
    display: none;
    font-size: 0.8rem;
    color: #6B6560;
    margin-top: 0.5rem;
    line-height: 1.4;
}

[data-testid="stSidebar"] {
    background-color: #FAF8F5;
    border-right: 1px solid #E8E2D9;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label {
    padding: 0.65rem 0.5rem;
    border-radius: 8px;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background-color: #F0EBE3;
}

[data-testid="stMetricValue"] {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.8rem !important;
    line-height: 1.2 !important;
    word-break: break-word;
}

[data-testid="stMetricLabel"] {
    font-size: 0.85rem !important;
}

.stTabs [data-baseweb="tab-list"] {
    flex-wrap: wrap;
    gap: 0.35rem;
}

.stTabs [data-baseweb="tab"] {
    height: auto !important;
    min-height: 2.75rem;
    white-space: normal;
    text-align: center;
}

.stButton > button {
    min-height: 2.75rem;
    border-radius: 8px;
}

[data-testid="stDataFrame"],
[data-testid="stTable"] {
    overflow-x: auto !important;
    -webkit-overflow-scrolling: touch;
    max-width: 100%;
}

section[data-testid="stMain"] {
    overflow-x: hidden;
}

section[data-testid="stMain"] .block-container {
    max-width: 100%;
    padding-top: 1.25rem;
    padding-bottom: 2rem;
}

/* Tablet */
@media (max-width: 992px) {
    .main-header {
        font-size: 2rem;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.5rem !important;
    }

    div[data-testid="stHorizontalBlock"] {
        flex-wrap: wrap !important;
        gap: 0.75rem !important;
    }

    div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
        flex: 1 1 45% !important;
        min-width: 0 !important;
        max-width: 100% !important;
        width: auto !important;
    }
}

/* Mobile */
@media (max-width: 768px) {
    [data-testid="stAppViewContainer"] {
        overflow-x: hidden;
    }

    section[data-testid="stSidebar"] {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        height: 100vh !important;
        z-index: 999999 !important;
        transition: transform 0.2s ease, visibility 0.2s ease !important;
    }

    section[data-testid="stSidebar"][aria-expanded="false"] {
        transform: translateX(-100%) !important;
        width: 0 !important;
        min-width: 0 !important;
        max-width: 0 !important;
        overflow: hidden !important;
        visibility: hidden !important;
        pointer-events: none !important;
    }

    section[data-testid="stSidebar"][aria-expanded="true"] {
        width: min(85vw, 300px) !important;
        min-width: min(85vw, 300px) !important;
        max-width: 300px !important;
        transform: translateX(0) !important;
        visibility: visible !important;
        pointer-events: auto !important;
    }

    section[data-testid="stMain"] {
        width: 100% !important;
        margin-left: 0 !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
    }

    section[data-testid="stMain"] > div.block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        padding-top: 2.5rem !important;
        max-width: 100% !important;
        margin-left: 0 !important;
        margin-right: 0 !important;
    }

    .main-header {
        font-size: 1.55rem;
        letter-spacing: 0.02em;
    }

    .sub-header {
        font-size: 0.95rem;
        margin-bottom: 1rem;
    }

    .brand-sidebar {
        font-size: 1.45rem;
        letter-spacing: 0.06em;
    }

    .mobile-hint {
        display: block;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.2rem !important;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.78rem !important;
    }

    div[data-testid="stHorizontalBlock"] {
        flex-direction: column !important;
        flex-wrap: nowrap !important;
        gap: 0.5rem !important;
        width: 100% !important;
    }

    div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
        width: 100% !important;
        min-width: 0 !important;
        max-width: 100% !important;
        flex: none !important;
    }

    .stTabs [data-baseweb="tab"] {
        font-size: 0.82rem;
        padding-left: 0.65rem !important;
        padding-right: 0.65rem !important;
    }

    [data-testid="stExpander"] details summary p {
        font-size: 0.95rem;
    }

    h3 {
        font-size: 1.1rem !important;
    }

    [data-testid="stSelectbox"] > div,
    [data-testid="stTextInput"] > div,
    [data-testid="stNumberInput"] > div,
    [data-testid="stTextArea"] > div {
        font-size: 16px !important;
    }

    .js-plotly-plot, .plot-container {
        max-width: 100% !important;
        overflow-x: auto !important;
    }
}

/* Small phones */
@media (max-width: 480px) {
    .main-header {
        font-size: 1.35rem;
    }

    .sub-header {
        font-size: 0.88rem;
    }

    section[data-testid="stMain"] > div.block-container {
        padding-left: 0.85rem !important;
        padding-right: 0.85rem !important;
    }

    .stButton > button {
        width: 100%;
    }
}
</style>
"""


def format_cop(value: float) -> str:
    return f"${value:,.0f} COP"
