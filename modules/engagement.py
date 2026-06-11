import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
"""
Page 4: Engagement Analytics — Heatmap, leaderboard, trends, correlations
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.helpers import section_header, fmt_number, render_kpi_row
from utils import visualizations as viz


def render(df: pd.DataFrame):
    section_header("🔥 Engagement Analytics", "Deep dive into audience interaction patterns")

    if df.empty:
        st.warning("No video data available.")
        return

    # ── Engagement KPIs ───────────────────────────────────────────────────────
    avg_er   = df["engagement_rate"].mean()
    max_er   = df["engagement_rate"].max()
    min_er   = df["engagement_rate"].min()
    med_er   = df["engagement_rate"].median()

    render_kpi_row([
        {"label": "Avg Engagement Rate", "value": f"{avg_er:.2f}%",  "icon": "🔥", "color": "#FF0000"},
        {"label": "Peak Engagement",     "value": f"{max_er:.2f}%",  "icon": "🚀", "color": "#FF4500"},
        {"label": "Lowest Engagement",   "value": f"{min_er:.2f}%",  "icon": "📉", "color": "#AA0000"},
        {"label": "Median Engagement",   "value": f"{med_er:.2f}%",  "icon": "📊", "color": "#DD2200"},
    ])

    st.divider()

    # ── Tabs ─────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs(["🏆 Leaderboard", "🔥 Heatmap", "📈 Trend", "🔗 Correlations"])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            section_header("🏆 Most Engaging Videos")
            top_eng = df.nlargest(10, "engagement_rate")[
                ["title","views","likes","comments","engagement_rate","viral_score"]
            ].copy()
            for i, (_, row) in enumerate(top_eng.iterrows(), 1):
                url = f"https://www.youtube.com/watch?v={row['video_id']}" if "video_id" in row else "#"
                er_color = "#00C851" if row["engagement_rate"] > 5 else "#FF8800" if row["engagement_rate"] > 2 else "#FF4444"
                st.markdown(f"""
                <div class="video-card">
                    <div style="font-size:1.4rem;font-weight:800;color:{er_color};min-width:32px;">#{i}</div>
                    <div class="video-info">
                        <a href="{url}" target="_blank" class="video-title">{row['title'][:55]}…</a>
                        <div class="video-stats">
                            🔥 <b style="color:{er_color}">{row['engagement_rate']:.2f}%</b> &nbsp;|&nbsp;
                            👁️ {fmt_number(row['views'])} &nbsp;|&nbsp;
                            👍 {fmt_number(row['likes'])} &nbsp;|&nbsp;
                            💬 {fmt_number(row['comments'])}
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True)

        with c2:
            section_header("📉 Least Engaging Videos")
            bot_eng = df[df["views"] > 100].nsmallest(10, "engagement_rate")[
                ["title","views","likes","comments","engagement_rate"]
            ]
            for i, (_, row) in enumerate(bot_eng.iterrows(), 1):
                url = f"https://www.youtube.com/watch?v={row['video_id']}" if "video_id" in row else "#"
                st.markdown(f"""
                <div class="video-card" style="border-color:#333;">
                    <div style="font-size:1.4rem;font-weight:800;color:#666;min-width:32px;">#{i}</div>
                    <div class="video-info">
                        <a href="{url}" target="_blank" class="video-title" style="color:#999;">{row['title'][:55]}…</a>
                        <div class="video-stats">
                            📉 <b>{row['engagement_rate']:.2f}%</b> &nbsp;|&nbsp;
                            👁️ {fmt_number(row['views'])} &nbsp;|&nbsp;
                            👍 {fmt_number(row['likes'])}
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True)

    with tab2:
        section_header("🔥 Engagement Heatmap", "Average engagement rate by day and hour of upload")
        st.plotly_chart(viz.engagement_heatmap(df), use_container_width=True, config={"displayModeBar": False})

        st.divider()
        section_header("📊 Engagement Distribution")
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=df["engagement_rate"],
            nbinsx=30,
            marker=dict(color="#FF0000", opacity=0.8),
            name="Engagement Rate",
        ))
        fig.add_vline(x=df["engagement_rate"].mean(), line_dash="dash",
                      line_color="white", annotation_text=f"Mean: {df['engagement_rate'].mean():.2f}%")
        fig.update_layout(
            title="📊 Engagement Rate Distribution",
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=350,
            font=dict(color="#ccc"),
            margin=dict(l=30, r=30, t=50, b=30),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with tab3:
        section_header("📈 Engagement Trend Over Time")
        st.plotly_chart(
            viz.trend_line(df, "engagement_rate", "📈 Engagement Rate Over Time"),
            use_container_width=True, config={"displayModeBar": False}
        )
        st.plotly_chart(
            viz.trend_line(df, "views", "👁️ Views Trend Over Time"),
            use_container_width=True, config={"displayModeBar": False}
        )

    with tab4:
        section_header("🔗 Correlation Analysis")
        st.plotly_chart(viz.correlation_matrix(df), use_container_width=True, config={"displayModeBar": False})

        c1, c2, c3 = st.columns(3)
        with c1:
            st.plotly_chart(viz.scatter_chart(df, "views", "likes", "Views vs Likes", "engagement_rate"),
                            use_container_width=True, config={"displayModeBar": False})
        with c2:
            st.plotly_chart(viz.scatter_chart(df, "views", "comments", "Views vs Comments", "engagement_rate"),
                            use_container_width=True, config={"displayModeBar": False})
        with c3:
            st.plotly_chart(viz.scatter_chart(df, "likes", "comments", "Likes vs Comments", "viral_score"),
                            use_container_width=True, config={"displayModeBar": False})
