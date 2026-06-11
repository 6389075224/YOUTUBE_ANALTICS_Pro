"""
Page 1: Executive Dashboard / Overview
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
from utils.helpers import fmt_number, fmt_date, render_kpi_row, section_header, grade_badge
from utils import visualizations as viz


def render(channel: dict, df: pd.DataFrame, kpis: dict, health: dict, insights: list):
    if channel.get("banner"):
        st.markdown(f'<img src="{channel["banner"]}" class="channel-banner"/>', unsafe_allow_html=True)

    col_img, col_info = st.columns([1, 5])
    with col_img:
        if channel.get("thumbnail"):
            st.image(channel["thumbnail"], width=90)
    with col_info:
        st.markdown(f"## {channel['title']}")
        meta = []
        if channel.get("custom_url"):
            meta.append(f"🔗 {channel['custom_url']}")
        if channel.get("country") and channel["country"] != "N/A":
            meta.append(f"🌍 {channel['country']}")
        if channel.get("published_at"):
            meta.append(f"📅 Since {fmt_date(channel['published_at'])}")
        st.markdown("  ·  ".join(meta) if meta else "")
        if channel.get("description"):
            with st.expander("📄 Channel Description"):
                st.write(channel["description"][:600])

    st.divider()

    section_header("📊 Key Performance Indicators")
    render_kpi_row([
        {"label": "Subscribers",     "value": fmt_number(kpis["subscribers"]),    "icon": "👥", "color": "#FF0000"},
        {"label": "Total Views",     "value": fmt_number(kpis["total_views"]),    "icon": "👁️", "color": "#FF4500"},
        {"label": "Total Videos",    "value": fmt_number(kpis["total_videos"]),   "icon": "🎬", "color": "#CC0000"},
        {"label": "Avg Views/Video", "value": fmt_number(kpis["avg_views"]),      "icon": "📈", "color": "#FF6B35"},
    ])
    render_kpi_row([
        {"label": "Avg Likes/Video",    "value": fmt_number(kpis["avg_likes"]),             "icon": "👍", "color": "#AA0000"},
        {"label": "Avg Comments/Video", "value": fmt_number(kpis["avg_comments"]),          "icon": "💬", "color": "#DD2200"},
        {"label": "Avg Engagement Rate","value": f"{kpis['avg_engagement_rate']:.2f}%",     "icon": "🔥", "color": "#FF8800"},
        {"label": "Sub/View Ratio",     "value": f"{kpis['sub_view_ratio']:.3f}%",          "icon": "⚖️", "color": "#FF5500"},
    ])

    h_col, trend_col = st.columns([1, 2])
    with h_col:
        section_header("❤️ Channel Health")
        color = '#00C851' if health['score'] >= 80 else '#FF8800' if health['score'] >= 60 else '#FF4444'
        st.markdown(f"""<div class="kpi-card" style="border-top:3px solid {color};">
            <div class="kpi-icon">🏆</div>
            <div class="kpi-value">{health['score']}/100</div>
            <div class="kpi-label">Health Score</div>
            <div style="margin-top:10px;">{grade_badge(health['grade'])}</div>
            </div>""", unsafe_allow_html=True)
    with trend_col:
        section_header("📅 Upload Frequency")
        if not df.empty:
            st.plotly_chart(viz.upload_frequency_chart(df), use_container_width=True, config={"displayModeBar": False})

    st.divider()

    section_header("📊 Distribution Overview")
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(viz.views_distribution(df), use_container_width=True, config={"displayModeBar": False})
    with c2:
        if not df.empty:
            st.plotly_chart(
                viz.pie_donut(
                    labels=["Top 10 Videos", "Remaining Videos"],
                    values=[
                        df.nlargest(10, "views")["views"].sum(),
                        max(0, df["views"].sum() - df.nlargest(10, "views")["views"].sum()),
                    ],
                    title="🎯 Top 10 Videos Share of Total Views"
                ), use_container_width=True, config={"displayModeBar": False})

    st.divider()
    section_header("🤖 AI Insight Highlights", "Top 4 auto-generated insights")
    if insights:
        for insight in insights[:4]:
            st.markdown(f'<div class="insight-pill">{insight}</div>', unsafe_allow_html=True)

    st.divider()
    section_header("💥 Top 5 Viral Videos")
    if not df.empty:
        top_viral = df.nlargest(5, "viral_score")
        for _, row in top_viral.iterrows():
            c1, c2, c3 = st.columns([2, 5, 3])
            with c1:
                if row.get("thumbnail"):
                    st.image(row["thumbnail"], width=130)
            with c2:
                url = f"https://www.youtube.com/watch?v={row['video_id']}"
                st.markdown(f"**[{row['title'][:70]}]({url})**")
                st.caption(f"Published: {row['published_at'][:10]}")
            with c3:
                st.metric("Viral Score", f"{row['viral_score']:.1f}")
                st.metric("Views", fmt_number(row["views"]))
                st.metric("Engagement", f"{row['engagement_rate']:.2f}%")
            st.divider()
