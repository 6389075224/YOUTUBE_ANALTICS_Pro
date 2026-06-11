import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
"""
Helpers – Formatting, number utilities, and shared UI components.
"""

import streamlit as st
import pandas as pd
from datetime import datetime


def fmt_number(n: int | float) -> str:
    """Format large numbers with K/M/B suffixes."""
    if n >= 1_000_000_000:
        return f"{n/1_000_000_000:.2f}B"
    if n >= 1_000_000:
        return f"{n/1_000_000:.2f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(int(n))


def fmt_date(date_str: str) -> str:
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        return dt.strftime("%b %d, %Y")
    except Exception:
        return date_str or "N/A"


def kpi_card(label: str, value: str, delta: str = "", icon: str = "📊", color: str = "#FF0000") -> str:
    """Return HTML for a premium KPI card."""
    delta_html = f'<div class="kpi-delta">{delta}</div>' if delta else ""
    return f"""
    <div class="kpi-card" style="border-top: 3px solid {color};">
        <div class="kpi-icon">{icon}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-label">{label}</div>
        {delta_html}
    </div>
    """


def render_kpi_row(cards: list[dict]):
    """Render a row of KPI cards. Each dict: label, value, icon, color, delta."""
    cols = st.columns(len(cards))
    for col, card in zip(cols, cards):
        with col:
            st.markdown(
                kpi_card(
                    card.get("label",""),
                    card.get("value",""),
                    card.get("delta",""),
                    card.get("icon","📊"),
                    card.get("color","#FF0000"),
                ),
                unsafe_allow_html=True,
            )


def section_header(title: str, subtitle: str = ""):
    st.markdown(f"""
    <div class="section-header">
        <h2>{title}</h2>
        {'<p class="subtitle">' + subtitle + '</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)


def grade_badge(grade: str) -> str:
    colors = {"A+": "#00C851", "A": "#00C851", "B": "#33B5E5",
               "C": "#FF8800", "D": "#FF4444"}
    c = colors.get(grade, "#888")
    return f'<span style="background:{c};color:white;padding:4px 14px;border-radius:20px;font-weight:700;font-size:1.1rem">{grade}</span>'


def video_card_html(video: dict) -> str:
    thumb = video.get("thumbnail","")
    title = video.get("title","")[:55] + ("…" if len(video.get("title","")) > 55 else "")
    views = fmt_number(video.get("views",0))
    likes = fmt_number(video.get("likes",0))
    comments = fmt_number(video.get("comments",0))
    er = f"{video.get('engagement_rate',0):.2f}%"
    vid_id = video.get("video_id","")
    url = f"https://www.youtube.com/watch?v={vid_id}"

    return f"""
    <div class="video-card">
        <a href="{url}" target="_blank">
            <img src="{thumb}" class="video-thumb" alt="thumbnail"/>
        </a>
        <div class="video-info">
            <a href="{url}" target="_blank" class="video-title">{title}</a>
            <div class="video-stats">
                👁️ {views} &nbsp;|&nbsp; 👍 {likes} &nbsp;|&nbsp; 💬 {comments} &nbsp;|&nbsp; 🔥 {er}
            </div>
        </div>
    </div>
    """


def paginate_df(df: pd.DataFrame, page_size: int = 10, key: str = "page") -> pd.DataFrame:
    total_pages = max(1, (len(df) - 1) // page_size + 1)
    page = st.number_input("Page", min_value=1, max_value=total_pages,
                            value=1, step=1, key=key,
                            label_visibility="collapsed")
    start = (page - 1) * page_size
    st.caption(f"Page {page} of {total_pages} — {len(df)} total videos")
    return df.iloc[start : start + page_size]
