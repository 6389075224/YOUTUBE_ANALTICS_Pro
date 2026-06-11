import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
"""
Page 6: AI Insights Engine — Auto-generated recommendations and forecasting
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.helpers import section_header, fmt_number, render_kpi_row
from utils import visualizations as viz
from services.analytics import best_upload_times, growth_forecast, extract_keywords


def render(channel: dict, df: pd.DataFrame, kpis: dict, health: dict, insights: list):
    section_header("🤖 AI Insights Engine", "Intelligent analysis and actionable recommendations")

    if df.empty:
        st.warning("No video data available.")
        return

    # ── All 10 AI Insights ────────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs(["💡 Recommendations", "🔮 Growth Forecast", "📊 Pattern Analysis"])

    with tab1:
        section_header("💡 10 Actionable Recommendations")
        if not insights:
            st.info("Insights not generated yet. Please re-analyze the channel.")
        else:
            for i, insight in enumerate(insights, 1):
                icon_map = {1:"🔥",2:"📅",3:"⏰",4:"📆",5:"🎬",6:"🌟",7:"📊",8:"🔑",9:"💥",10:"🏆"}
                icon = icon_map.get(i, "💡")
                st.markdown(f"""
                <div class="insight-pill" style="display:flex;gap:12px;align-items:flex-start;">
                    <span style="font-size:1.3rem;min-width:30px;">{icon}</span>
                    <div>
                        <span style="font-size:0.7rem;color:#FF0000;font-weight:700;
                            text-transform:uppercase;letter-spacing:1px;">
                            Recommendation #{i}
                        </span><br>
                        <span>{insight}</span>
                    </div>
                </div>""", unsafe_allow_html=True)

        st.divider()

        # Strategy Summary Cards
        section_header("🎯 Content Strategy Summary")
        times = best_upload_times(df)
        keywords = extract_keywords(df, top_n=5)
        top_kws = ", ".join([k[0] for k in keywords]) if keywords else "N/A"

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""
            <div class="glass-card">
                <h4 style="color:#FF0000;margin-top:0;">⏰ Optimal Upload Window</h4>
                <table width="100%">
                    <tr><td style="color:#888;padding:6px 0;">Best Day</td>
                        <td style="font-weight:700;color:#fff;">{times.get('best_day','N/A')}</td></tr>
                    <tr><td style="color:#888;padding:6px 0;">Best Month</td>
                        <td style="font-weight:700;color:#fff;">{times.get('best_month','N/A')}</td></tr>
                    <tr><td style="color:#888;padding:6px 0;">Best Hour (UTC)</td>
                        <td style="font-weight:700;color:#fff;">{times.get('best_hour','N/A')}:00</td></tr>
                </table>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="glass-card">
                <h4 style="color:#FF0000;margin-top:0;">🔑 Content Intelligence</h4>
                <table width="100%">
                    <tr><td style="color:#888;padding:6px 0;">Top Keywords</td>
                        <td style="font-weight:700;color:#fff;">{top_kws}</td></tr>
                    <tr><td style="color:#888;padding:6px 0;">Channel Health</td>
                        <td style="font-weight:700;color:#fff;">{health.get('score',0)}/100 ({health.get('grade','N/A')})</td></tr>
                    <tr><td style="color:#888;padding:6px 0;">Avg Engagement</td>
                        <td style="font-weight:700;color:#fff;">{kpis.get('avg_engagement_rate',0):.2f}%</td></tr>
                </table>
            </div>""", unsafe_allow_html=True)

    with tab2:
        section_header("🔮 Growth Forecast", "Linear trend projection for next 10 videos")
        forecast = growth_forecast(df)

        if forecast:
            render_kpi_row([
                {"label": "Growth Trend",    "value": forecast.get("trend","N/A"),     "icon": "📈", "color": "#FF0000"},
                {"label": "Forecast +1 Video","value": fmt_number(forecast["next_10_forecast"][0]), "icon": "🔮", "color": "#FF4500"},
                {"label": "Forecast +5 Videos","value": fmt_number(forecast["next_10_forecast"][4]),"icon": "📊", "color": "#AA0000"},
                {"label": "Forecast +10 Videos","value": fmt_number(forecast["next_10_forecast"][9]),"icon": "🚀","color": "#FF8800"},
            ])
            st.plotly_chart(viz.forecast_chart(forecast, df),
                            use_container_width=True, config={"displayModeBar": False})

            st.markdown(f"""
            <div class="insight-pill">
                📊 <b>Forecast Methodology:</b> Linear regression on the last {len(df)} videos.
                Current growth slope: <b>{forecast['slope']:+.0f} views/video</b>.
                This is a simplified projection — actual performance depends on content quality, trends, and promotions.
            </div>""", unsafe_allow_html=True)
        else:
            st.info("Not enough videos (need at least 5) for forecasting.")

    with tab3:
        section_header("📊 Engagement Pattern Analysis")

        c1, c2 = st.columns(2)
        with c1:
            # Best content type by duration bucket
            df_dur = df.copy()
            df_dur["duration_bucket"] = pd.cut(
                df_dur["duration_sec"],
                bins=[0, 60, 300, 600, 1200, 3600, 99999],
                labels=["<1min", "1–5min", "5–10min", "10–20min", "20–60min", "60min+"]
            )
            dur_perf = df_dur.groupby("duration_bucket", observed=True)["views"].mean().dropna()
            if not dur_perf.empty:
                fig = go.Figure(go.Bar(
                    x=dur_perf.index.astype(str),
                    y=dur_perf.values,
                    marker=dict(color=dur_perf.values, colorscale="Reds"),
                    text=[fmt_number(int(v)) for v in dur_perf.values],
                    textposition="outside",
                ))
                fig.update_layout(
                    title="🎬 Avg Views by Video Duration",
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    height=360,
                    font=dict(color="#ccc"),
                    margin=dict(l=30, r=30, t=50, b=30),
                )
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        with c2:
            # Year-over-year performance
            if "year" in df.columns:
                yoy = df.groupby("year").agg(
                    total_views=("views","sum"),
                    total_videos=("views","count"),
                    avg_er=("engagement_rate","mean"),
                ).reset_index()
                if len(yoy) > 1:
                    fig2 = go.Figure()
                    fig2.add_trace(go.Bar(x=yoy["year"], y=yoy["total_views"],
                                         name="Total Views", marker_color="#FF0000"))
                    fig2.add_trace(go.Scatter(x=yoy["year"], y=yoy["avg_er"]*100000,
                                              name="Avg ER (scaled)", mode="lines+markers",
                                              line=dict(color="white", width=2),
                                              yaxis="y2"))
                    fig2.update_layout(
                        title="📅 Year-over-Year Performance",
                        template="plotly_dark",
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        height=360,
                        font=dict(color="#ccc"),
                        margin=dict(l=30, r=30, t=50, b=30),
                        yaxis2=dict(overlaying="y", side="right", showgrid=False),
                        legend=dict(orientation="h", y=-0.15),
                    )
                    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
