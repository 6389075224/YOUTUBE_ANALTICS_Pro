import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
"""
Page 5: Advanced Metrics — Viral score, performance score, leaderboards
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.helpers import section_header, fmt_number, render_kpi_row
from utils import visualizations as viz


def render(channel: dict, df: pd.DataFrame, kpis: dict):
    section_header("⚡ Advanced Metrics", "Custom scoring models and performance rankings")

    if df.empty:
        st.warning("No video data available.")
        return

    # ── Metric KPIs ───────────────────────────────────────────────────────────
    render_kpi_row([
        {"label": "Avg Viral Score",       "value": f"{df['viral_score'].mean():.1f}",       "icon": "💥", "color": "#FF0000"},
        {"label": "Peak Viral Score",      "value": f"{df['viral_score'].max():.1f}",        "icon": "🚀", "color": "#FF4500"},
        {"label": "Avg Performance Score", "value": fmt_number(int(df['performance_score'].mean())), "icon": "⭐", "color": "#FF8800"},
        {"label": "Audience Attraction",   "value": fmt_number(int(kpis.get('audience_attraction', 0))), "icon": "🎯", "color": "#AA0000"},
    ])

    st.divider()

    tab1, tab2, tab3 = st.tabs(["💥 Viral Rankings", "⭐ Performance Score", "📊 Score Charts"])

    with tab1:
        section_header("💥 Top 10 Viral Videos", "Viral Score = (Likes + Comments) / Views × 1000")
        top_viral = df.nlargest(10, "viral_score")

        for i, (_, row) in enumerate(top_viral.iterrows(), 1):
            url = f"https://www.youtube.com/watch?v={row.get('video_id','')}"
            badge_color = "#FFD700" if i == 1 else "#C0C0C0" if i == 2 else "#CD7F32" if i == 3 else "#444"
            thumb = row.get("thumbnail","")
            st.markdown(f"""
            <div class="video-card" style="border-left: 4px solid {badge_color};">
                {'<img src="' + thumb + '" class="video-thumb"/>' if thumb else ''}
                <div class="video-info">
                    <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
                        <span style="background:{badge_color};color:{'#000' if i<=3 else '#fff'};
                            padding:3px 10px;border-radius:20px;font-weight:800;font-size:0.8rem;">
                            #{i}
                        </span>
                        <a href="{url}" target="_blank" class="video-title">{row['title'][:65]}</a>
                    </div>
                    <div class="video-stats">
                        💥 Viral: <b style="color:#FF4500">{row['viral_score']:.1f}</b> &nbsp;|&nbsp;
                        👁️ {fmt_number(row['views'])} &nbsp;|&nbsp;
                        👍 {fmt_number(row['likes'])} &nbsp;|&nbsp;
                        💬 {fmt_number(row['comments'])} &nbsp;|&nbsp;
                        🔥 {row['engagement_rate']:.2f}%
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

    with tab2:
        section_header("⭐ Performance Score Leaderboard",
                       "Score = (0.5 × Likes) + (0.3 × Comments) + (0.2 × Views)")
        top_perf = df.nlargest(10, "performance_score")[
            ["title","views","likes","comments","performance_score","engagement_rate"]
        ]

        fig = go.Figure(go.Bar(
            x=top_perf["performance_score"],
            y=[t[:40]+"…" for t in top_perf["title"]],
            orientation="h",
            marker=dict(color=top_perf["performance_score"], colorscale="Oranges"),
            text=[fmt_number(int(v)) for v in top_perf["performance_score"]],
            textposition="outside",
        ))
        fig.update_yaxes(autorange="reversed")
        fig.update_layout(
            title="⭐ Top 10 by Performance Score",
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=420,
            font=dict(color="#ccc"),
            margin=dict(l=10, r=60, t=50, b=30),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        st.divider()
        section_header("📋 Full Performance Rankings Table")
        ranked = df[["title","views","likes","comments","engagement_rate",
                     "viral_score","performance_score"]].sort_values("performance_score", ascending=False).copy()
        ranked.index = range(1, len(ranked)+1)
        ranked.columns = ["Title","Views","Likes","Comments","Engagement %","Viral Score","Perf Score"]
        ranked["Title"] = ranked["Title"].str[:50]
        st.dataframe(ranked.head(50), use_container_width=True, height=500)

    with tab3:
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(
                viz.scatter_chart(df, "viral_score", "performance_score",
                                  "💥 Viral Score vs ⭐ Performance Score", "views"),
                use_container_width=True, config={"displayModeBar": False}
            )
        with c2:
            # Viral score distribution
            fig_dist = go.Figure(go.Histogram(
                x=df["viral_score"], nbinsx=30,
                marker=dict(color="#FF4500", opacity=0.8),
            ))
            fig_dist.add_vline(x=df["viral_score"].mean(), line_dash="dash",
                               line_color="white",
                               annotation_text=f"Mean: {df['viral_score'].mean():.1f}")
            fig_dist.update_layout(
                title="💥 Viral Score Distribution",
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=380,
                font=dict(color="#ccc"),
                margin=dict(l=30, r=30, t=50, b=30),
            )
            st.plotly_chart(fig_dist, use_container_width=True, config={"displayModeBar": False})

        st.plotly_chart(
            viz.trend_line(df, "viral_score", "💥 Viral Score Trend Over Time"),
            use_container_width=True, config={"displayModeBar": False}
        )
