import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
"""
Competitor Comparison Mode — Side-by-side channel analysis
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from services.youtube_api import detect_input_type, fetch_channel_data, fetch_videos
from services.analytics import build_video_df, channel_kpis, channel_health_score, generate_ai_insights
from utils.helpers import section_header, fmt_number, render_kpi_row
from utils import visualizations as viz


def _load_channel(user_input: str):
    input_type, identifier = detect_input_type(user_input)
    channel = fetch_channel_data(identifier)
    if not channel:
        return None, None, None, None
    videos = fetch_videos(channel["uploads_playlist"])
    df = build_video_df(videos)
    kpis = channel_kpis(channel, df)
    health = channel_health_score(kpis, df)
    return channel, df, kpis, health


def render():
    section_header("🆚 Competitor Comparison", "Analyse two YouTube channels head-to-head")

    c1_col, c2_col = st.columns(2)
    with c1_col:
        input_a = st.text_input("Channel A (URL / @Handle / ID)", placeholder="@MrBeast", key="comp_a")
    with c2_col:
        input_b = st.text_input("Channel B (URL / @Handle / ID)", placeholder="@PewDiePie", key="comp_b")

    if st.button("⚔️ Compare Channels", use_container_width=True):
        if not input_a or not input_b:
            st.warning("Please enter both channels.")
            return

        with st.spinner("Loading Channel A…"):
            ch_a, df_a, kpis_a, health_a = _load_channel(input_a)
        with st.spinner("Loading Channel B…"):
            ch_b, df_b, kpis_b, health_b = _load_channel(input_b)

        if not ch_a or not ch_b:
            st.error("One or both channels could not be found.")
            return

        st.session_state["comp_results"] = {
            "ch_a": ch_a, "df_a": df_a, "kpis_a": kpis_a, "health_a": health_a,
            "ch_b": ch_b, "df_b": df_b, "kpis_b": kpis_b, "health_b": health_b,
        }

    if "comp_results" not in st.session_state:
        st.markdown("""
        <div style="text-align:center;padding:60px 0;color:#555;">
            Enter two channel handles above and click Compare to begin
        </div>""", unsafe_allow_html=True)
        return

    r = st.session_state["comp_results"]
    ch_a, df_a, kpis_a, health_a = r["ch_a"], r["df_a"], r["kpis_a"], r["health_a"]
    ch_b, df_b, kpis_b, health_b = r["ch_b"], r["df_b"], r["kpis_b"], r["health_b"]

    st.divider()

    # ── Channel Headers ───────────────────────────────────────────────────────
    c1, vs_col, c2 = st.columns([5, 1, 5])
    with c1:
        if ch_a.get("thumbnail"):
            st.image(ch_a["thumbnail"], width=70)
        st.markdown(f"### {ch_a['title']}")
        st.caption(f"👥 {fmt_number(ch_a['subscribers'])} subscribers")
    with vs_col:
        st.markdown("""
        <div style="text-align:center;padding-top:30px;font-size:2rem;font-weight:800;color:#FF0000;">
            VS
        </div>""", unsafe_allow_html=True)
    with c2:
        if ch_b.get("thumbnail"):
            st.image(ch_b["thumbnail"], width=70)
        st.markdown(f"### {ch_b['title']}")
        st.caption(f"👥 {fmt_number(ch_b['subscribers'])} subscribers")

    st.divider()

    # ── KPI Comparison ─────────────────────────────────────────────────────────
    section_header("📊 Head-to-Head KPIs")

    metrics = [
        ("👥 Subscribers",     kpis_a["subscribers"],           kpis_b["subscribers"],           ""),
        ("👁️ Total Views",     kpis_a["total_views"],           kpis_b["total_views"],           ""),
        ("🎬 Total Videos",    kpis_a["total_videos"],          kpis_b["total_videos"],          ""),
        ("📈 Avg Views/Video", kpis_a["avg_views"],             kpis_b["avg_views"],             ""),
        ("🔥 Engagement Rate", kpis_a["avg_engagement_rate"],   kpis_b["avg_engagement_rate"],   "%"),
        ("💥 Avg Viral Score", df_a["viral_score"].mean() if not df_a.empty else 0,
                               df_b["viral_score"].mean() if not df_b.empty else 0, ""),
        ("❤️ Health Score",    health_a["score"],               health_b["score"],               "/100"),
    ]

    for label, val_a, val_b, unit in metrics:
        winner = "a" if val_a >= val_b else "b"
        def fmt(v, u): return f"{v:.2f}{u}" if u in ["%","/100"] else fmt_number(int(v))
        ca, cb, cc = st.columns([4, 2, 4])
        with ca:
            badge = '&nbsp;<span class="winner-badge">WINNER 🏆</span>' if winner == "a" else ""
            st.markdown(
                f'<div style="text-align:right;padding:6px 10px;background:#1e1e1e;border-radius:8px;margin-bottom:4px;">'
                f'<b style="color:{"#FF0000" if winner=="a" else "#888"}">{fmt(val_a, unit)}</b>{badge}</div>',
                unsafe_allow_html=True,
            )
        with cb:
            st.markdown(
                f'<div style="text-align:center;padding:6px 0;color:#666;font-size:0.8rem;">{label}</div>',
                unsafe_allow_html=True,
            )
        with cc:
            badge = '<span class="winner-badge">WINNER 🏆</span>&nbsp;' if winner == "b" else ""
            st.markdown(
                f'<div style="text-align:left;padding:6px 10px;background:#1e1e1e;border-radius:8px;margin-bottom:4px;">'
                f'{badge}<b style="color:{"#33B5E5" if winner=="b" else "#888"}">{fmt(val_b, unit)}</b></div>',
                unsafe_allow_html=True,
            )

    st.divider()

    # ── Comparison Bar Chart ──────────────────────────────────────────────────
    section_header("📊 Comparison Charts")
    comp_labels = ["Subscribers","Total Views","Avg Views","Avg Likes","Avg Comments"]
    vals_a = [kpis_a["subscribers"], kpis_a["total_views"], kpis_a["avg_views"],
               kpis_a["avg_likes"], kpis_a["avg_comments"]]
    vals_b = [kpis_b["subscribers"], kpis_b["total_views"], kpis_b["avg_views"],
               kpis_b["avg_likes"], kpis_b["avg_comments"]]

    st.plotly_chart(
        viz.comparison_bar(comp_labels, vals_a, vals_b,
                           [ch_a["title"][:20], ch_b["title"][:20]],
                           "📊 Channel Metrics Comparison"),
        use_container_width=True, config={"displayModeBar": False}
    )

    c1, c2 = st.columns(2)
    with c1:
        er_fig = go.Figure(go.Bar(
            x=[ch_a["title"][:20], ch_b["title"][:20]],
            y=[kpis_a["avg_engagement_rate"], kpis_b["avg_engagement_rate"]],
            marker_color=["#FF0000", "#33B5E5"],
            text=[f"{kpis_a['avg_engagement_rate']:.2f}%", f"{kpis_b['avg_engagement_rate']:.2f}%"],
            textposition="outside",
        ))
        er_fig.update_layout(title="🔥 Engagement Rate",template="plotly_dark",
                              paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                              height=300, font=dict(color="#ccc"),margin=dict(l=20,r=20,t=50,b=20))
        st.plotly_chart(er_fig, use_container_width=True, config={"displayModeBar": False})

    with c2:
        hs_fig = go.Figure(go.Bar(
            x=[ch_a["title"][:20], ch_b["title"][:20]],
            y=[health_a["score"], health_b["score"]],
            marker_color=["#FF0000", "#33B5E5"],
            text=[f"{health_a['score']}/100 ({health_a['grade']})",
                  f"{health_b['score']}/100 ({health_b['grade']})"],
            textposition="outside",
        ))
        hs_fig.update_layout(title="❤️ Health Score",template="plotly_dark",
                              paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                              height=300, font=dict(color="#ccc"),margin=dict(l=20,r=20,t=50,b=20))
        st.plotly_chart(hs_fig, use_container_width=True, config={"displayModeBar": False})

    st.divider()

    # ── AI Verdict ────────────────────────────────────────────────────────────
    section_header("🤖 AI Comparison Verdict")

    def winner_name(val_a, val_b, ch_a, ch_b):
        return ch_a["title"][:25] if val_a >= val_b else ch_b["title"][:25]

    verdicts = [
        ("📈", "Better for Growth",      winner_name(kpis_a["subscribers"],          kpis_b["subscribers"], ch_a, ch_b)),
        ("👁️", "Better for Reach",       winner_name(kpis_a["avg_views"],            kpis_b["avg_views"], ch_a, ch_b)),
        ("🔥", "Better for Engagement",  winner_name(kpis_a["avg_engagement_rate"],  kpis_b["avg_engagement_rate"], ch_a, ch_b)),
        ("❤️", "Overall Health Winner",  winner_name(health_a["score"],              health_b["score"], ch_a, ch_b)),
    ]

    # Overall winner score
    a_wins = sum(1 for _, _, w in verdicts if w == ch_a["title"][:25])
    b_wins = len(verdicts) - a_wins
    overall = ch_a["title"][:25] if a_wins >= b_wins else ch_b["title"][:25]

    for icon, cat, winner in verdicts:
        st.markdown(f"""
        <div class="insight-pill">
            {icon} <b>{cat}:</b> &nbsp;
            <span style="color:#FFD700;font-weight:700;">{winner}</span>
        </div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="glass-card" style="text-align:center;border:1px solid #FFD700;">
        <div style="font-size:1.6rem;">🏆</div>
        <div style="font-size:1.3rem;font-weight:800;color:#FFD700;margin:6px 0;">Overall Winner</div>
        <div style="font-size:1.6rem;font-weight:800;color:#fff;">{overall}</div>
        <div style="color:#888;margin-top:6px;font-size:0.85rem;">{a_wins} vs {b_wins} category wins</div>
    </div>""", unsafe_allow_html=True)
