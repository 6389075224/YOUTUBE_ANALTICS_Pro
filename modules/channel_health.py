import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
"""
Page 7: Channel Health Report — Gauge chart, grade, detailed breakdown
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.helpers import section_header, fmt_number, render_kpi_row, grade_badge
from utils import visualizations as viz


def render(channel: dict, kpis: dict, df: pd.DataFrame, health: dict):
    section_header("❤️ Channel Health Report", "Comprehensive 0–100 health score with grade")

    score  = health.get("score", 0)
    grade  = health.get("grade", "N/A")
    breakdown = health.get("breakdown", {})

    # ── Gauge ──────────────────────────────────────────────────────────────────
    c1, c2 = st.columns([2, 3])
    with c1:
        st.plotly_chart(viz.gauge_chart(score, grade), use_container_width=True,
                        config={"displayModeBar": False})

    with c2:
        section_header("📊 Score Breakdown")
        total = sum(breakdown.values()) or 1
        for factor, pts in breakdown.items():
            pct = pts / {"Engagement Rate":30,"Upload Consistency":20,
                         "Average Views":20,"Audience Attraction":15,
                         "Sub-to-View Ratio":15}.get(factor, 20) * 100
            color = "#00C851" if pct >= 70 else "#FF8800" if pct >= 40 else "#FF4444"
            st.markdown(f"""
            <div style="margin-bottom:14px;">
                <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                    <span style="color:#ccc;font-weight:500;">{factor}</span>
                    <span style="color:{color};font-weight:700;">{pts:.1f} pts</span>
                </div>
                <div style="background:#2a2a2a;border-radius:4px;height:8px;">
                    <div style="background:{color};width:{pct:.0f}%;height:8px;border-radius:4px;
                        transition:width 0.5s;"></div>
                </div>
            </div>""", unsafe_allow_html=True)

    st.divider()

    # ── Grade Explanation ─────────────────────────────────────────────────────
    grade_info = {
        "A+": ("🏆", "#00C851", "Outstanding", "Your channel is performing at an elite level. Consistency, engagement, and growth metrics are all excellent."),
        "A":  ("🥇", "#00C851", "Excellent",   "Your channel is in great health. Minor improvements could push you to A+ tier."),
        "B":  ("🥈", "#33B5E5", "Good",         "Solid foundation with room to grow. Focus on upload consistency and engagement to reach A tier."),
        "C":  ("🥉", "#FF8800", "Average",       "Your channel needs attention. Prioritize engagement rate and regular uploads."),
        "D":  ("⚠️",  "#FF4444", "Needs Work",   "Significant improvements needed. Review your content strategy and upload frequency."),
    }
    icon, color, label, desc = grade_info.get(grade, ("📊","#888","N/A",""))

    st.markdown(f"""
    <div class="glass-card" style="border: 1px solid {color}33; text-align:center; padding:30px;">
        <div style="font-size:3rem;">{icon}</div>
        <div style="font-size:2rem;font-weight:800;color:{color};margin:8px 0;">{grade} — {label}</div>
        <div style="color:#aaa;font-size:0.95rem;max-width:600px;margin:0 auto;">{desc}</div>
    </div>""", unsafe_allow_html=True)

    st.divider()

    # ── Comparison vs Industry Benchmarks ────────────────────────────────────
    section_header("📊 Benchmark Comparison")

    benchmarks = {
        "Avg Engagement Rate (%)": (kpis.get("avg_engagement_rate", 0), 3.0, "%"),
        "Avg Views / Video":       (kpis.get("avg_views", 0), 10000, ""),
        "Avg Likes / Video":       (kpis.get("avg_likes", 0), 500, ""),
        "Avg Comments / Video":    (kpis.get("avg_comments", 0), 50, ""),
    }

    c1, c2 = st.columns(2)
    items = list(benchmarks.items())
    for i, (metric, (channel_val, benchmark_val, unit)) in enumerate(items):
        col = c1 if i % 2 == 0 else c2
        with col:
            diff_pct = ((channel_val - benchmark_val) / benchmark_val * 100) if benchmark_val else 0
            color = "#00C851" if diff_pct >= 0 else "#FF4444"
            arrow = "▲" if diff_pct >= 0 else "▼"
            fmt_v = f"{channel_val:.2f}{unit}" if unit == "%" else fmt_number(int(channel_val))
            fmt_b = f"{benchmark_val:.2f}{unit}" if unit == "%" else fmt_number(int(benchmark_val))
            st.markdown(f"""
            <div class="kpi-card" style="border-top:3px solid {color};">
                <div class="kpi-value">{fmt_v}</div>
                <div class="kpi-label">{metric}</div>
                <div style="margin-top:8px;font-size:0.8rem;color:{color};">
                    {arrow} {abs(diff_pct):.1f}% vs benchmark ({fmt_b})
                </div>
            </div>""", unsafe_allow_html=True)

    st.divider()

    # ── Improvement Roadmap ───────────────────────────────────────────────────
    section_header("🗺️ Improvement Roadmap")

    roadmap = []
    if kpis.get("avg_engagement_rate", 0) < 3:
        roadmap.append(("🔥", "Boost Engagement", "Your engagement rate is below 3%. Add polls, end screens, pinned comments, and strong CTAs to every video."))
    if breakdown.get("Upload Consistency", 0) < 12:
        roadmap.append(("📅", "Upload Consistently", "Your upload schedule is irregular. Aim for a fixed cadence (e.g., every Tuesday) to improve the algorithm's favorability."))
    if kpis.get("avg_views", 0) < 5000:
        roadmap.append(("👁️", "Increase Discoverability", "Optimize video titles, descriptions, and thumbnails for SEO. Research trending keywords in your niche."))
    if kpis.get("sub_view_ratio", 0) < 0.01:
        roadmap.append(("👥", "Convert Viewers to Subscribers", "Add subscribe CTAs at the 30-second mark and at the end. Offer a value proposition for subscribing."))
    if not roadmap:
        roadmap.append(("🏆", "Keep It Up!", "Your channel is performing well across all dimensions. Focus on scaling your content production."))

    for icon, title, desc in roadmap:
        st.markdown(f"""
        <div class="insight-pill">
            <span style="font-size:1.2rem;">{icon}</span>
            <b style="color:#FF4500;"> {title}</b><br>
            <span style="color:#bbb;">{desc}</span>
        </div>""", unsafe_allow_html=True)
