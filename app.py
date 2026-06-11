"""
YouTube Analytics Pro — Main Entry Point
"""

import streamlit as st
import sys
import os

# ── Path fix for Streamlit Cloud & local ─────────────────────────────────────
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from utils.styles import DARK_CSS, LIGHT_CSS
from services.youtube_api import detect_input_type, fetch_channel_data, fetch_videos
from services.analytics import build_video_df, channel_kpis, channel_health_score, generate_ai_insights, growth_forecast
from utils.helpers import fmt_number, fmt_date, section_header

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="YouTube Analytics Pro",
    page_icon="▶️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session State Init ────────────────────────────────────────────────────────
if "theme" not in st.session_state:
    st.session_state.theme = "dark"
if "channel" not in st.session_state:
    st.session_state.channel = None
if "df" not in st.session_state:
    st.session_state.df = None
if "kpis" not in st.session_state:
    st.session_state.kpis = None
if "health" not in st.session_state:
    st.session_state.health = None
if "insights" not in st.session_state:
    st.session_state.insights = None
if "page" not in st.session_state:
    st.session_state.page = "🏠 Executive Dashboard"

# ── Theme CSS ─────────────────────────────────────────────────────────────────
st.markdown(DARK_CSS if st.session_state.theme == "dark" else LIGHT_CSS, unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="brand-logo">▶ YT Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">Enterprise Intelligence</div>', unsafe_allow_html=True)
    st.divider()

    # Theme toggle
    theme_label = "☀️ Light Mode" if st.session_state.theme == "dark" else "🌙 Dark Mode"
    if st.button(theme_label, use_container_width=True):
        st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
        st.rerun()

    st.divider()

    # Channel input
    st.markdown("**🔍 Analyze Channel**")
    user_input = st.text_input(
        "Channel URL, @Handle, or ID",
        placeholder="@MrBeast or channel URL...",
        label_visibility="collapsed",
    )

    if st.button("🚀 Analyze", use_container_width=True):
        if user_input.strip():
            with st.spinner("Fetching channel data…"):
                input_type, identifier = detect_input_type(user_input)
                channel = fetch_channel_data(identifier)
                if channel:
                    st.session_state.channel = channel
                    with st.spinner("Fetching videos (up to 100)…"):
                        videos = fetch_videos(channel["uploads_playlist"])
                    df = build_video_df(videos)
                    kpis = channel_kpis(channel, df)
                    health = channel_health_score(kpis, df)
                    insights = generate_ai_insights(channel, df, kpis, health)
                    st.session_state.df = df
                    st.session_state.kpis = kpis
                    st.session_state.health = health
                    st.session_state.insights = insights
                    st.session_state.page = "🏠 Executive Dashboard"
                    st.success(f"✅ Loaded: {channel['title']}")
                else:
                    st.error("Channel not found. Check the URL or handle.")
        else:
            st.warning("Please enter a channel URL or handle.")

    st.divider()

    # Navigation
    st.markdown("**📂 Navigation**")
    pages = [
        "🏠 Executive Dashboard",
        "📊 Video Analytics",
        "💡 Content Insights",
        "🔥 Engagement Analytics",
        "⚡ Advanced Metrics",
        "🤖 AI Insights Engine",
        "❤️ Channel Health",
        "🆚 Competitor Compare",
        "🧪 Analytics Lab",
        "📤 Export Center",
    ]
    selected = st.radio("nav", pages, index=pages.index(st.session_state.page),
                        label_visibility="collapsed")
    if selected != st.session_state.page:
        st.session_state.page = selected
        st.rerun()

    st.divider()
    if st.session_state.channel:
        ch = st.session_state.channel
        c1, c2 = st.columns([1, 2])
        with c1:
            if ch.get("thumbnail"):
                st.image(ch["thumbnail"], width=50)
        with c2:
            st.markdown(f"**{ch['title'][:20]}**")
            st.caption(f"👥 {fmt_number(ch['subscribers'])}")

# ── Main Content ──────────────────────────────────────────────────────────────
page = st.session_state.page

if not st.session_state.channel and page != "🆚 Competitor Compare":
    # Landing / Welcome
    st.markdown("""
    <div style="text-align:center;padding:80px 20px 40px;">
        <div style="font-size:4rem;">▶️</div>
        <h1 style="font-size:2.8rem;font-weight:800;background:linear-gradient(135deg,#FF0000,#FF6B35);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:8px;">
            YouTube Analytics Pro
        </h1>
        <p style="color:#888;font-size:1.1rem;max-width:600px;margin:0 auto 32px;">
            Enterprise-grade real-time intelligence for any YouTube channel.
            Powered by YouTube Data API v3.
        </p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    features = [
        ("📊", "Deep Analytics", "100+ metrics across 8 analytics modules"),
        ("🤖", "AI Insights", "10 auto-generated actionable recommendations"),
        ("❤️", "Health Score", "0–100 channel health with grade system"),
        ("📤", "Export", "CSV, Excel, and professional PDF reports"),
    ]
    for col, (icon, title, desc) in zip([c1, c2, c3, c4], features):
        with col:
            st.markdown(f"""
            <div class="kpi-card" style="border-top:3px solid #FF0000;">
                <div class="kpi-icon">{icon}</div>
                <div class="kpi-value" style="font-size:1rem;font-weight:700;">{title}</div>
                <div class="kpi-label" style="font-size:0.8rem;text-transform:none;margin-top:6px;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center;margin-top:40px;color:#555;font-size:0.9rem;">
        ← Enter a YouTube channel in the sidebar to begin
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Route to pages ────────────────────────────────────────────────────────────
channel = st.session_state.channel
df = st.session_state.df
kpis = st.session_state.kpis
health = st.session_state.health
insights = st.session_state.insights

if page == "🏠 Executive Dashboard":
    from modules.overview import render
    render(channel, df, kpis, health, insights)

elif page == "📊 Video Analytics":
    from modules.video_analytics import render
    render(df)

elif page == "💡 Content Insights":
    from modules.content_insights import render
    render(df)

elif page == "🔥 Engagement Analytics":
    from modules.engagement import render
    render(df)

elif page == "⚡ Advanced Metrics":
    from modules.advanced_metrics import render
    render(channel, df, kpis)

elif page == "🤖 AI Insights Engine":
    from modules.ai_insights import render
    render(channel, df, kpis, health, insights)

elif page == "❤️ Channel Health":
    from modules.channel_health import render
    render(channel, kpis, df, health)

elif page == "🆚 Competitor Compare":
    from modules.competitor import render
    render()

elif page == "🧪 Analytics Lab":
    from modules.analytics_lab import render
    render(df)

elif page == "📤 Export Center":
    from modules.export_center import render
    render(channel, df, kpis, health, insights)
