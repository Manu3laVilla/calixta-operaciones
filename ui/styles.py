CALIXTA_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=Montserrat:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Montserrat', sans-serif;
}

.main-header {
    font-family: 'Cormorant Garamond', serif;
    font-size: 2.4rem;
    font-weight: 600;
    color: #1A1A1A;
    letter-spacing: 0.08em;
    margin-bottom: 0.2rem;
    text-transform: uppercase;
    line-height: 1.15;
}

.sub-header {
    color: #6B6560;
    font-weight: 300;
    margin-bottom: 1.5rem;
    letter-spacing: 0.02em;
    line-height: 1.5;
}

.brand-sidebar {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.8rem;
    letter-spacing: 0.15em;
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
[data-testid="stTable"],
[data-testid="stDataFrame"] > div,
.stDataFrame {
    overflow-x: auto !important;
    -webkit-overflow-scrolling: touch;
}

[data-testid="stVerticalBlock"] > div:has(> [data-testid="stDataFrame"]) {
    overflow-x: auto;
}

.block-container {
    padding-top: 1.25rem;
    padding-bottom: 2rem;
    max-width: 100%;
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
        gap: 0.75rem;
        flex-wrap: wrap !important;
    }

    div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
        flex: 1 1 calc(50% - 0.5rem) !important;
        min-width: calc(50% - 0.5rem) !important;
        width: calc(50% - 0.5rem) !important;
    }
}

/* Mobile */
@media (max-width: 768px) {
    .main-header {
        font-size: 1.65rem;
        letter-spacing: 0.05em;
    }

    .sub-header {
        font-size: 0.95rem;
        margin-bottom: 1rem;
    }

    .brand-sidebar {
        font-size: 1.45rem;
        letter-spacing: 0.1em;
    }

    .mobile-hint {
        display: block;
    }

    .block-container {
        padding-left: 0.85rem !important;
        padding-right: 0.85rem !important;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.25rem !important;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.78rem !important;
    }

    div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
        flex: 1 1 100% !important;
        min-width: 100% !important;
        width: 100% !important;
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
}

/* Small phones */
@media (max-width: 480px) {
    .main-header {
        font-size: 1.4rem;
    }

    .sub-header {
        font-size: 0.88rem;
    }

    [data-testid="stSidebar"] {
        min-width: min(88vw, 320px) !important;
    }

    .stButton > button {
        width: 100%;
    }
}
</style>
"""


def format_cop(value: float) -> str:
    return f"${value:,.0f} COP"
