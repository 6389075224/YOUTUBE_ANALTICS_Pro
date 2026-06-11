import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
"""
Page 3: Content Insights — Keywords, word cloud, upload timing, patterns
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io
from utils.helpers import section_header, fmt_number
from services.analytics import extract_keywords, best_upload_times


def render(df: pd.DataFrame):
    section_header("💡 Content Insights", "Patterns, keywords, and optimal upload strategy")

    if df.empty:
        st.warning("No video data available.")
        return

    times = best_upload_times(df)
    keywords = extract_keywords(df, top_n=40)

    # ── Best Upload Times KPIs ────────────────────────────────────────────────
    section_header("⏰ Best Time To Upload")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""<div class="kpi-card" style="border-top:3px solid #FF0000;">
            <div class="kpi-icon">📅</div>
            <div class="kpi-value">{times.get('best_day','N/A')}</div>
            <div class="kpi-label">Best Day</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="kpi-card" style="border-top:3px solid #FF4500;">
            <div class="kpi-icon">🗓️</div>
            <div class="kpi-value">{times.get('best_month','N/A')}</div>
            <div class="kpi-label">Best Month</div></div>""", unsafe_allow_html=True)
    with c3:
        hour = times.get('best_hour', 'N/A')
        hour_fmt = f"{hour}:00 UTC" if hour != 'N/A' else 'N/A'
        st.markdown(f"""<div class="kpi-card" style="border-top:3px solid #CC0000;">
            <div class="kpi-icon">⏰</div>
            <div class="kpi-value">{hour_fmt}</div>
            <div class="kpi-label">Best Hour</div></div>""", unsafe_allow_html=True)

    st.divider()

    # ── Upload Timing Charts ──────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs(["☁️ Word Cloud", "📅 Upload Timing", "🏆 Best/Worst", "🔑 Keywords Table"])

    with tab1:
        section_header("☁️ Word Cloud — Video Titles")
        if keywords:
            word_freq = {w: c for w, c in keywords}
            wc = WordCloud(
                width=900, height=420,
                background_color=None, mode="RGBA",
                colormap="Reds",
                max_words=80,
                prefer_horizontal=0.8,
            ).generate_from_frequencies(word_freq)

            fig_wc, ax = plt.subplots(figsize=(12, 5))
            ax.imshow(wc, interpolation="bilinear")
            ax.axis("off")
            fig_wc.patch.set_alpha(0)
            st.pyplot(fig_wc, use_container_width=True)
            plt.close(fig_wc)
        else:
            st.info("Not enough title data for word cloud.")

    with tab2:
        day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        month_order = ["January","February","March","April","May","June",
                       "July","August","September","October","November","December"]

        c1, c2 = st.columns(2)
        with c1:
            day_perf = times.get("day_perf")
            if day_perf is not None and not day_perf.empty:
                fig = go.Figure(go.Bar(
                    x=day_perf.index.tolist(),
                    y=day_perf.values,
                    marker=dict(color=day_perf.values, colorscale="Reds", showscale=False),
                    text=[fmt_number(int(v)) for v in day_perf.values],
                    textposition="outside",
                ))
                fig.update_layout(
                    title="📅 Avg Views by Day of Week",
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    height=350,
                    font=dict(color="#ccc"),
                    margin=dict(l=30, r=30, t=50, b=30),
                )
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        with c2:
            month_perf = times.get("month_perf")
            if month_perf is not None and not month_perf.empty:
                fig = go.Figure(go.Bar(
                    x=month_perf.index.tolist(),
                    y=month_perf.values,
                    marker=dict(color=month_perf.values, colorscale="Reds", showscale=False),
                    text=[fmt_number(int(v)) for v in month_perf.values],
                    textposition="outside",
                ))
                fig.update_layout(
                    title="🗓️ Avg Views by Month",
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    height=350,
                    font=dict(color="#ccc"),
                    margin=dict(l=30, r=30, t=50, b=30),
                )
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        hour_perf = times.get("hour_perf")
        if hour_perf is not None and not hour_perf.empty:
            fig = go.Figure(go.Scatter(
                x=hour_perf.index.tolist(),
                y=hour_perf.values,
                mode="lines+markers",
                fill="tozeroy",
                fillcolor="rgba(255,0,0,0.12)",
                line=dict(color="#FF0000", width=2.5),
                marker=dict(size=6),
            ))
            fig.update_layout(
                title="⏰ Avg Views by Upload Hour (UTC)",
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=300,
                font=dict(color="#ccc"),
                margin=dict(l=30, r=30, t=50, b=30),
                xaxis_title="Hour (UTC)",
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with tab3:
        c1, c2 = st.columns(2)
        with c1:
            section_header("🏆 Best Performing Videos")
            best = df.nlargest(5, "views")
            for i, (_, row) in enumerate(best.iterrows(), 1):
                url = f"https://www.youtube.com/watch?v={row['video_id']}"
                st.markdown(f"""
                <div class="insight-pill">
                    <b>#{i}</b> <a href="{url}" target="_blank" style="color:#FF4500;text-decoration:none;">
                    {row['title'][:60]}…</a><br>
                    <small>👁️ {fmt_number(row['views'])} &nbsp;|&nbsp; 👍 {fmt_number(row['likes'])}</small>
                </div>""", unsafe_allow_html=True)

        with c2:
            section_header("📉 Worst Performing Videos")
            worst = df.nsmallest(5, "views")
            for i, (_, row) in enumerate(worst.iterrows(), 1):
                url = f"https://www.youtube.com/watch?v={row['video_id']}"
                st.markdown(f"""
                <div class="insight-pill" style="border-left-color:#888;">
                    <b>#{i}</b> <a href="{url}" target="_blank" style="color:#aaa;text-decoration:none;">
                    {row['title'][:60]}…</a><br>
                    <small>👁️ {fmt_number(row['views'])} &nbsp;|&nbsp; 👍 {fmt_number(row['likes'])}</small>
                </div>""", unsafe_allow_html=True)

        # Upload frequency summary
        st.divider()
        section_header("📊 Upload Frequency Analysis")
        if not df.empty and "published_dt" in df.columns:
            monthly = df.set_index("published_dt").resample("ME").size().reset_index()
            monthly.columns = ["Month", "Uploads"]
            avg_monthly = monthly["Uploads"].mean()
            max_month = monthly.loc[monthly["Uploads"].idxmax(), "Month"].strftime("%b %Y")
            m1, m2, m3 = st.columns(3)
            m1.metric("Total Months Active", len(monthly))
            m2.metric("Avg Uploads / Month", f"{avg_monthly:.1f}")
            m3.metric("Most Active Month", max_month)

    with tab4:
        section_header("🔑 Top Keywords")
        if keywords:
            kw_df = pd.DataFrame(keywords, columns=["Keyword", "Frequency"])
            c1, c2 = st.columns([2, 3])
            with c1:
                st.dataframe(kw_df, use_container_width=True, height=480)
            with c2:
                fig = go.Figure(go.Bar(
                    x=kw_df["Frequency"],
                    y=kw_df["Keyword"],
                    orientation="h",
                    marker=dict(color=kw_df["Frequency"], colorscale="Reds"),
                    text=kw_df["Frequency"],
                    textposition="outside",
                ))
                fig.update_yaxes(autorange="reversed")
                fig.update_layout(
                    title="🔑 Keyword Frequency",
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    height=520,
                    font=dict(color="#ccc"),
                    margin=dict(l=10, r=40, t=50, b=30),
                )
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
