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
}
.sub-header {
    color: #6B6560;
    font-weight: 300;
    margin-bottom: 1.5rem;
    letter-spacing: 0.02em;
}
.brand-sidebar {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.8rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #1A1A1A;
    margin-bottom: 0;
}
.metric-label {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #6B6560;
}
[data-testid="stSidebar"] {
    background-color: #FAF8F5;
    border-right: 1px solid #E8E2D9;
}
[data-testid="stMetricValue"] {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.8rem !important;
}
</style>
"""


def format_cop(value: float) -> str:
    return f"${value:,.0f} COP"
