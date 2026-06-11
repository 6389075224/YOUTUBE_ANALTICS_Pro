import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
"""
Page 2: Video Analytics — Table, search, sort, filter, charts
"""

import streamlit as st
import pandas as pd
from utils.helpers import fmt_number, section_header, paginate_df, video_card_html
from utils import visualizations as viz


def render(df: pd.DataFrame):
    section_header("📊 Video Analytics", f"Analysing {len(df)} videos")

    if df.empty:
        st.warning("No video data available.")
        return

    # ── Filters Row ──────────────────────────────────────────────────────────
    with st.container():
        f1, f2, f3, f4 = st.columns([3, 2, 2, 2])
        with f1:
            search = st.text_input("🔍 Search titles", placeholder="Type keyword…", label_visibility="collapsed")
        with f2:
            sort_by = st.selectbox("Sort by", ["views", "likes", "comments", "engagement_rate", "viral_score", "published_at"], label_visibility="collapsed")
        with f3:
            sort_order = st.selectbox("Order", ["Descending", "Ascending"], label_visibility="collapsed")
        with f4:
            view_mode = st.selectbox("View", ["Card View", "Table View"], label_visibility="collapsed")

    # Apply filters
    filtered = df.copy()
    if search:
        filtered = filtered[filtered["title"].str.contains(search, case=False, na=False)]

    ascending = sort_order == "Ascending"
    filtered = filtered.sort_values(sort_by, ascending=ascending)

    st.caption(f"Showing {len(filtered)} videos")
    st.divider()

    # ── Charts Tabs ──────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Video List", "📊 Top Charts", "🔗 Correlation", "🗺️ Treemap"])

    with tab1:
        paged = paginate_df(filtered, page_size=10, key="vid_page")
        if view_mode == "Card View":
            for _, row in paged.iterrows():
                st.markdown(video_card_html(row.to_dict()), unsafe_allow_html=True)
        else:
            display_cols = ["title", "published_at", "duration_fmt", "views", "likes",
                            "comments", "engagement_rate", "viral_score"]
            show = paged[[c for c in display_cols if c in paged.columns]].copy()
            show.columns = [c.replace("_", " ").title() for c in show.columns]
            st.dataframe(show, use_container_width=True, height=480)

    with tab2:
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(viz.bar_top10(df, "views", "👁️ Top 10 by Views"),
                            use_container_width=True, config={"displayModeBar": False})
            st.plotly_chart(viz.bar_top10(df, "comments", "💬 Top 10 by Comments"),
                            use_container_width=True, config={"displayModeBar": False})
        with c2:
            st.plotly_chart(viz.bar_top10(df, "likes", "👍 Top 10 by Likes"),
                            use_container_width=True, config={"displayModeBar": False})
            st.plotly_chart(viz.bar_top10(df, "engagement_rate", "🔥 Top 10 by Engagement Rate"),
                            use_container_width=True, config={"displayModeBar": False})

    with tab3:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.plotly_chart(viz.scatter_chart(df, "views", "likes", "👁️ Views vs 👍 Likes", "engagement_rate"),
                            use_container_width=True, config={"displayModeBar": False})
        with c2:
            st.plotly_chart(viz.scatter_chart(df, "views", "comments", "👁️ Views vs 💬 Comments", "engagement_rate"),
                            use_container_width=True, config={"displayModeBar": False})
        with c3:
            st.plotly_chart(viz.scatter_chart(df, "likes", "comments", "👍 Likes vs 💬 Comments", "viral_score"),
                            use_container_width=True, config={"displayModeBar": False})

    with tab4:
        st.plotly_chart(viz.treemap_chart(df), use_container_width=True, config={"displayModeBar": False})
