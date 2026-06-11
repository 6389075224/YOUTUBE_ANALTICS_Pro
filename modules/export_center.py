import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
"""
Page 8: Export Center — CSV, Excel, PDF download
"""

import streamlit as st
import pandas as pd
from utils.helpers import section_header
from services.export_service import export_csv, export_excel, export_pdf


def render(channel: dict, df: pd.DataFrame, kpis: dict, health: dict, insights: list):
    section_header("📤 Export Center", "Download your analytics in CSV, Excel, or PDF format")

    if df.empty:
        st.warning("No data to export. Please analyze a channel first.")
        return

    channel_name = channel.get("title", "channel").replace(" ", "_")

    # ── Export Cards ──────────────────────────────────────────────────────────
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("""
        <div class="kpi-card" style="border-top:3px solid #00C851;min-height:160px;">
            <div class="kpi-icon">📄</div>
            <div class="kpi-value" style="font-size:1.1rem;">CSV Export</div>
            <div class="kpi-label" style="text-transform:none;font-size:0.82rem;margin-top:6px;">
                Raw video data table — compatible with Excel, Google Sheets, Python, R
            </div>
        </div>""", unsafe_allow_html=True)
        csv_data = export_csv(df)
        st.download_button(
            label="⬇️ Download CSV",
            data=csv_data,
            file_name=f"{channel_name}_videos.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with c2:
        st.markdown("""
        <div class="kpi-card" style="border-top:3px solid #33B5E5;min-height:160px;">
            <div class="kpi-icon">📊</div>
            <div class="kpi-value" style="font-size:1.1rem;">Excel Export</div>
            <div class="kpi-label" style="text-transform:none;font-size:0.82rem;margin-top:6px;">
                Multi-sheet workbook: Overview, Videos, Top 10 Views, Top 10 Engagement
            </div>
        </div>""", unsafe_allow_html=True)
        with st.spinner("Building Excel…"):
            excel_data = export_excel(df, channel, kpis)
        st.download_button(
            label="⬇️ Download Excel",
            data=excel_data,
            file_name=f"{channel_name}_analytics.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    with c3:
        st.markdown("""
        <div class="kpi-card" style="border-top:3px solid #FF0000;min-height:160px;">
            <div class="kpi-icon">📑</div>
            <div class="kpi-value" style="font-size:1.1rem;">PDF Report</div>
            <div class="kpi-label" style="text-transform:none;font-size:0.82rem;margin-top:6px;">
                Full branded report: Overview, KPIs, Top Videos, Health Score, AI Insights
            </div>
        </div>""", unsafe_allow_html=True)
        with st.spinner("Building PDF…"):
            pdf_data = export_pdf(channel, kpis, df, health, insights)
        st.download_button(
            label="⬇️ Download PDF",
            data=pdf_data,
            file_name=f"{channel_name}_report.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

    st.divider()

    # ── Export Preview ─────────────────────────────────────────────────────────
    section_header("👁️ Data Preview")
    preview_cols = ["title","published_at","duration_fmt","views","likes",
                    "comments","engagement_rate","viral_score","performance_score"]
    preview = df[[c for c in preview_cols if c in df.columns]].head(20).copy()
    preview.columns = [c.replace("_"," ").title() for c in preview.columns]
    preview.index = range(1, len(preview)+1)
    st.dataframe(preview, use_container_width=True, height=500)

    st.markdown(f"""
    <div class="insight-pill" style="margin-top:16px;">
        📦 <b>Export includes {len(df)} videos</b> with {len(df.columns)} fields per video.
        Data fetched from YouTube Data API v3 in real-time.
    </div>""", unsafe_allow_html=True)
