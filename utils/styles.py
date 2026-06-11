"""
Global CSS styles for YouTube Analytics Pro.
"""

DARK_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Reset & Base ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

.stApp {
    background: #0f0f0f !important;
    color: #e0e0e0 !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1a1a 0%, #111111 100%) !important;
    border-right: 1px solid #2a2a2a;
}
[data-testid="stSidebar"] .stRadio label {
    color: #ccc !important;
    padding: 8px 0 !important;
    cursor: pointer;
    transition: color 0.2s;
}
[data-testid="stSidebar"] .stRadio label:hover { color: #FF0000 !important; }

/* ── KPI Cards ── */
.kpi-card {
    background: linear-gradient(135deg, #1e1e1e 0%, #181818 100%);
    border-radius: 14px;
    padding: 22px 18px 18px;
    text-align: center;
    position: relative;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    transition: transform 0.2s, box-shadow 0.2s;
    margin-bottom: 8px;
    min-height: 120px;
    border: 1px solid #2a2a2a;
}
.kpi-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 30px rgba(255,0,0,0.15);
}
.kpi-icon { font-size: 1.6rem; margin-bottom: 6px; }
.kpi-value {
    font-size: 1.9rem;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.5px;
}
.kpi-label {
    font-size: 0.75rem;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 4px;
    font-weight: 500;
}
.kpi-delta { font-size: 0.78rem; color: #00C851; margin-top: 4px; }

/* ── Section Headers ── */
.section-header {
    border-left: 4px solid #FF0000;
    padding-left: 14px;
    margin: 28px 0 18px;
}
.section-header h2 {
    font-size: 1.35rem;
    font-weight: 700;
    color: #fff;
    margin: 0;
}
.section-header .subtitle {
    color: #888;
    font-size: 0.85rem;
    margin-top: 4px;
}

/* ── Video Cards ── */
.video-card {
    display: flex;
    gap: 14px;
    align-items: flex-start;
    background: #1a1a1a;
    border-radius: 10px;
    padding: 12px;
    margin-bottom: 10px;
    border: 1px solid #252525;
    transition: border-color 0.2s;
}
.video-card:hover { border-color: #FF0000; }
.video-thumb {
    width: 130px;
    height: 75px;
    object-fit: cover;
    border-radius: 6px;
    flex-shrink: 0;
}
.video-info { flex: 1; }
.video-title {
    font-size: 0.9rem;
    font-weight: 600;
    color: #e0e0e0;
    text-decoration: none;
    line-height: 1.4;
    display: block;
    margin-bottom: 6px;
}
.video-title:hover { color: #FF0000; }
.video-stats { font-size: 0.78rem; color: #888; }

/* ── Glass Card ── */
.glass-card {
    background: rgba(255,255,255,0.03);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 16px;
}

/* ── Insight Pills ── */
.insight-pill {
    background: #1e1e1e;
    border-left: 3px solid #FF0000;
    border-radius: 0 10px 10px 0;
    padding: 12px 16px;
    margin-bottom: 10px;
    font-size: 0.88rem;
    color: #ddd;
    line-height: 1.6;
}

/* ── Winner Badge ── */
.winner-badge {
    background: linear-gradient(135deg, #FFD700, #FFA500);
    color: #000;
    font-weight: 700;
    font-size: 0.75rem;
    padding: 3px 10px;
    border-radius: 20px;
    display: inline-block;
}

/* ── Channel Banner ── */
.channel-banner {
    width: 100%;
    height: 180px;
    object-fit: cover;
    border-radius: 12px;
    margin-bottom: 12px;
}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stSelectbox > div > div,
.stMultiSelect > div > div {
    background: #1e1e1e !important;
    border: 1px solid #333 !important;
    color: #e0e0e0 !important;
    border-radius: 8px !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #FF0000, #CC0000) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 10px 24px !important;
    font-size: 0.9rem !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

/* ── Progress bars ── */
.stProgress > div > div > div > div { background: #FF0000 !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] { gap: 6px; border-bottom: 1px solid #2a2a2a; }
.stTabs [data-baseweb="tab"] {
    background: transparent;
    border-radius: 6px 6px 0 0;
    color: #888;
    font-weight: 500;
    padding: 8px 16px;
}
.stTabs [aria-selected="true"] {
    background: rgba(255,0,0,0.12) !important;
    color: #FF0000 !important;
    border-bottom: 2px solid #FF0000 !important;
}

/* ── Dividers ── */
hr { border-color: #2a2a2a !important; }

/* ── Metric ── */
[data-testid="metric-container"] {
    background: #1a1a1a;
    border-radius: 10px;
    padding: 14px 16px;
    border: 1px solid #252525;
}

/* ── Tables ── */
.stDataFrame { border-radius: 10px; overflow: hidden; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #111; }
::-webkit-scrollbar-thumb { background: #333; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #FF0000; }

/* ── Logo / Brand ── */
.brand-logo {
    font-size: 1.6rem;
    font-weight: 800;
    background: linear-gradient(135deg, #FF0000, #FF6B35);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.5px;
}
.brand-sub {
    font-size: 0.7rem;
    color: #555;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-top: -4px;
}

/* ── Spinner ── */
.stSpinner > div { border-top-color: #FF0000 !important; }

/* ── Expander ── */
.streamlit-expanderHeader {
    background: #1a1a1a !important;
    border-radius: 8px !important;
    color: #ccc !important;
}
</style>
"""

LIGHT_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.stApp { background: #f5f5f5 !important; color: #111 !important; }
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #ffffff 0%, #f0f0f0 100%) !important;
    border-right: 1px solid #e0e0e0;
}

.kpi-card {
    background: #ffffff;
    border-radius: 14px;
    padding: 22px 18px 18px;
    text-align: center;
    box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    transition: transform 0.2s, box-shadow 0.2s;
    margin-bottom: 8px;
    min-height: 120px;
    border: 1px solid #e8e8e8;
}
.kpi-card:hover { transform: translateY(-3px); box-shadow: 0 6px 24px rgba(255,0,0,0.12); }
.kpi-icon { font-size: 1.6rem; margin-bottom: 6px; }
.kpi-value { font-size: 1.9rem; font-weight: 800; color: #111; }
.kpi-label { font-size: 0.75rem; color: #888; text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; }
.kpi-delta { font-size: 0.78rem; color: #00A040; margin-top: 4px; }

.section-header { border-left: 4px solid #FF0000; padding-left: 14px; margin: 28px 0 18px; }
.section-header h2 { font-size: 1.35rem; font-weight: 700; color: #111; margin: 0; }
.section-header .subtitle { color: #888; font-size: 0.85rem; margin-top: 4px; }

.video-card {
    display: flex; gap: 14px; align-items: flex-start;
    background: #fff; border-radius: 10px; padding: 12px;
    margin-bottom: 10px; border: 1px solid #eee; transition: border-color 0.2s;
}
.video-card:hover { border-color: #FF0000; }
.video-thumb { width: 130px; height: 75px; object-fit: cover; border-radius: 6px; flex-shrink: 0; }
.video-info { flex: 1; }
.video-title { font-size: 0.9rem; font-weight: 600; color: #111; text-decoration: none; display: block; margin-bottom: 6px; }
.video-title:hover { color: #FF0000; }
.video-stats { font-size: 0.78rem; color: #888; }

.insight-pill {
    background: #fff8f8;
    border-left: 3px solid #FF0000;
    border-radius: 0 10px 10px 0;
    padding: 12px 16px;
    margin-bottom: 10px;
    font-size: 0.88rem;
    color: #333;
}

.brand-logo {
    font-size: 1.6rem; font-weight: 800;
    background: linear-gradient(135deg, #FF0000, #FF6B35);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.brand-sub { font-size: 0.7rem; color: #aaa; text-transform: uppercase; letter-spacing: 2px; }
.stButton > button {
    background: linear-gradient(135deg, #FF0000, #CC0000) !important;
    color: white !important; border: none !important; border-radius: 8px !important;
    font-weight: 600 !important;
}
</style>
"""

CHART_TEMPLATE_LIGHT = "plotly_white"
CHART_TEMPLATE_DARK = "plotly_dark"
