import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
"""
Analytics Lab — Correlation matrix, anomaly detection, clustering, distributions
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from utils.helpers import section_header, fmt_number
from utils import visualizations as viz
from services.analytics import detect_anomalies


def render(df: pd.DataFrame):
    section_header("🧪 Advanced Analytics Lab", "Correlation, anomaly detection, clustering and distributions")

    if df.empty:
        st.warning("No video data available.")
        return

    tab1, tab2, tab3, tab4 = st.tabs([
        "🔗 Correlation Matrix",
        "🚨 Anomaly Detection",
        "📦 Clustering",
        "📊 Distributions",
    ])

    with tab1:
        section_header("🔗 Full Correlation Matrix")
        st.plotly_chart(viz.correlation_matrix(df), use_container_width=True,
                        config={"displayModeBar": False})

        st.markdown("""
        <div class="insight-pill">
            <b>How to read this:</b> Values close to <b>+1</b> indicate strong positive correlation,
            <b>-1</b> strong negative, and <b>0</b> no relationship. Red = positive, Blue = negative.
        </div>""", unsafe_allow_html=True)

        # Scatter matrix
        section_header("🔵 Scatter Plot Matrix")
        numeric_cols = ["views","likes","comments","engagement_rate","viral_score"]
        sample = df[numeric_cols].sample(min(len(df), 200), random_state=42)
        fig_sm = px.scatter_matrix(
            sample,
            dimensions=numeric_cols,
            color_continuous_scale="Reds",
            opacity=0.6,
        )
        fig_sm.update_traces(marker=dict(size=3))
        fig_sm.update_layout(
            title="Scatter Matrix",
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=600,
            font=dict(color="#ccc"),
        )
        st.plotly_chart(fig_sm, use_container_width=True, config={"displayModeBar": False})

    with tab2:
        section_header("🚨 Anomaly Detection", "Statistical outlier detection using IQR method")
        anomalies = detect_anomalies(df)

        sub1, sub2, sub3 = st.columns(3)
        with sub1:
            viral_count = len(anomalies.get("viral_anomalies", []))
            st.markdown(f"""<div class="kpi-card" style="border-top:3px solid #FFD700;">
                <div class="kpi-icon">🚀</div>
                <div class="kpi-value">{viral_count}</div>
                <div class="kpi-label">Unexpected Viral Videos</div>
            </div>""", unsafe_allow_html=True)
        with sub2:
            under_count = len(anomalies.get("underperforming", []))
            st.markdown(f"""<div class="kpi-card" style="border-top:3px solid #FF4444;">
                <div class="kpi-icon">📉</div>
                <div class="kpi-value">{under_count}</div>
                <div class="kpi-label">Underperforming Videos</div>
            </div>""", unsafe_allow_html=True)
        with sub3:
            spike_count = len(anomalies.get("engagement_spikes", []))
            st.markdown(f"""<div class="kpi-card" style="border-top:3px solid #FF8800;">
                <div class="kpi-icon">⚡</div>
                <div class="kpi-value">{spike_count}</div>
                <div class="kpi-label">Engagement Spike Videos</div>
            </div>""", unsafe_allow_html=True)

        st.divider()

        # Visualize anomalies on scatter
        df_plot = df.copy()
        df_plot["anomaly_type"] = "Normal"
        if not anomalies.get("viral_anomalies", pd.DataFrame()).empty:
            df_plot.loc[df_plot["video_id"].isin(anomalies["viral_anomalies"]["video_id"]), "anomaly_type"] = "🚀 Viral Outlier"
        if not anomalies.get("underperforming", pd.DataFrame()).empty:
            df_plot.loc[df_plot["video_id"].isin(anomalies["underperforming"]["video_id"]), "anomaly_type"] = "📉 Underperformer"
        if not anomalies.get("engagement_spikes", pd.DataFrame()).empty:
            df_plot.loc[df_plot["video_id"].isin(anomalies["engagement_spikes"]["video_id"]), "anomaly_type"] = "⚡ Engagement Spike"

        color_map = {
            "Normal": "#444",
            "🚀 Viral Outlier": "#FFD700",
            "📉 Underperformer": "#FF4444",
            "⚡ Engagement Spike": "#FF8800",
        }
        fig = px.scatter(
            df_plot,
            x="views", y="engagement_rate",
            color="anomaly_type",
            hover_name="title",
            color_discrete_map=color_map,
            opacity=0.85,
        )
        fig.update_traces(marker=dict(size=9, line=dict(width=1, color="white")))
        fig.update_layout(
            title="🚨 Anomaly Detection — Views vs Engagement Rate",
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=450,
            font=dict(color="#ccc"),
            margin=dict(l=30, r=30, t=60, b=30),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        # List anomalies
        if not anomalies.get("viral_anomalies", pd.DataFrame()).empty:
            st.markdown("#### 🚀 Unexpected Viral Videos")
            vdf = anomalies["viral_anomalies"][["title","views","likes","comments","engagement_rate"]].head(10)
            vdf.index = range(1, len(vdf)+1)
            st.dataframe(vdf, use_container_width=True)

        if not anomalies.get("underperforming", pd.DataFrame()).empty:
            st.markdown("#### 📉 Underperforming Videos")
            udf = anomalies["underperforming"][["title","views","likes","comments","engagement_rate"]].head(10)
            udf.index = range(1, len(udf)+1)
            st.dataframe(udf, use_container_width=True)

    with tab3:
        section_header("📦 Performance Clustering", "K-means clustering by views, likes, and engagement")
        try:
            from sklearn.preprocessing import StandardScaler
            from sklearn.cluster import KMeans

            features = df[["views","likes","comments","engagement_rate"]].fillna(0)
            scaler = StandardScaler()
            X = scaler.fit_transform(features)

            k = st.slider("Number of Clusters", min_value=2, max_value=6, value=3)
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            df_c = df.copy()
            df_c["cluster"] = kmeans.fit_predict(X).astype(str)

            cluster_labels = {str(i): f"Cluster {i+1}" for i in range(k)}
            df_c["cluster_label"] = df_c["cluster"].map(cluster_labels)

            fig_clust = px.scatter(
                df_c,
                x="views", y="engagement_rate",
                color="cluster_label",
                hover_name="title",
                color_discrete_sequence=px.colors.qualitative.Set1,
                opacity=0.8,
            )
            fig_clust.update_traces(marker=dict(size=8, line=dict(width=1, color="white")))
            fig_clust.update_layout(
                title=f"📦 K-Means Clustering (k={k})",
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=450,
                font=dict(color="#ccc"),
            )
            st.plotly_chart(fig_clust, use_container_width=True, config={"displayModeBar": False})

            # Cluster stats
            st.markdown("#### 📊 Cluster Statistics")
            cluster_stats = df_c.groupby("cluster_label").agg(
                Videos=("views","count"),
                Avg_Views=("views","mean"),
                Avg_Likes=("likes","mean"),
                Avg_ER=("engagement_rate","mean"),
            ).round(1)
            st.dataframe(cluster_stats, use_container_width=True)

        except ImportError:
            st.error("scikit-learn is required for clustering. Install with: pip install scikit-learn")

    with tab4:
        section_header("📊 Distribution Analysis")

        dist_metric = st.selectbox("Select Metric", ["views","likes","comments","engagement_rate","viral_score"])

        c1, c2 = st.columns(2)
        with c1:
            fig_hist = go.Figure(go.Histogram(
                x=df[dist_metric],
                nbinsx=30,
                marker=dict(color="#FF0000", opacity=0.8),
            ))
            mean_v = df[dist_metric].mean()
            median_v = df[dist_metric].median()
            fig_hist.add_vline(x=mean_v, line_dash="dash", line_color="white",
                               annotation_text=f"Mean: {mean_v:.1f}")
            fig_hist.add_vline(x=median_v, line_dash="dot", line_color="#FF8800",
                               annotation_text=f"Median: {median_v:.1f}")
            fig_hist.update_layout(
                title=f"📊 {dist_metric.replace('_',' ').title()} Distribution",
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=380,
                font=dict(color="#ccc"),
                margin=dict(l=30,r=30,t=50,b=30),
            )
            st.plotly_chart(fig_hist, use_container_width=True, config={"displayModeBar": False})

        with c2:
            fig_box = go.Figure(go.Box(
                y=df[dist_metric],
                name=dist_metric,
                marker_color="#FF0000",
                line_color="#FF4500",
                fillcolor="rgba(255,0,0,0.1)",
            ))
            fig_box.update_layout(
                title=f"📦 {dist_metric.replace('_',' ').title()} Box Plot",
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=380,
                font=dict(color="#ccc"),
                margin=dict(l=30,r=30,t=50,b=30),
            )
            st.plotly_chart(fig_box, use_container_width=True, config={"displayModeBar": False})

        # Stats summary
        stats = df[dist_metric].describe().round(2)
        st.markdown("#### 📋 Descriptive Statistics")
        s1,s2,s3,s4 = st.columns(4)
        s1.metric("Mean",   f"{stats['mean']:,.2f}")
        s2.metric("Std Dev",f"{stats['std']:,.2f}")
        s3.metric("Min",    f"{stats['min']:,.2f}")
        s4.metric("Max",    f"{stats['max']:,.2f}")
