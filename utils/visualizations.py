import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
"""
Visualizations – All Plotly chart builders for the platform.
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np


PALETTE = {
    "primary": "#FF0000",
    "secondary": "#282828",
    "accent": "#FF4500",
    "success": "#00C851",
    "warning": "#FF8800",
    "info": "#33B5E5",
    "purple": "#AA66CC",
    "gradient_start": "#FF0000",
    "gradient_end": "#FF6B35",
}

CHART_TEMPLATE = "plotly_dark"


def _base_layout(fig, title="", height=400):
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color="white")),
        height=height,
        template=CHART_TEMPLATE,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#CCCCCC"),
        margin=dict(l=40, r=40, t=50, b=40),
        showlegend=True,
    )
    return fig


def bar_top10(df: pd.DataFrame, metric: str, title: str) -> go.Figure:
    top = df.nlargest(10, metric)[["title", metric]].copy()
    top["short_title"] = top["title"].str[:40] + "…"
    colors = px.colors.sequential.Reds_r[:10] or [PALETTE["primary"]] * 10
    fig = go.Figure(go.Bar(
        x=top[metric],
        y=top["short_title"],
        orientation="h",
        marker=dict(
            color=top[metric],
            colorscale="Reds",
            showscale=False,
        ),
        text=top[metric].apply(lambda v: f"{v:,}"),
        textposition="outside",
    ))
    fig.update_yaxes(autorange="reversed")
    return _base_layout(fig, title, height=420)


def scatter_chart(df: pd.DataFrame, x: str, y: str, title: str, color_col: str = None) -> go.Figure:
    fig = px.scatter(
        df,
        x=x, y=y,
        hover_name="title",
        color=color_col if color_col else None,
        color_continuous_scale="Reds",
        opacity=0.8,
        size_max=15,
    )
    fig.update_traces(marker=dict(size=8, line=dict(width=1, color="white")))
    return _base_layout(fig, title)


def treemap_chart(df: pd.DataFrame) -> go.Figure:
    top = df.nlargest(30, "views").copy()
    top["short"] = top["title"].str[:35] + "…"
    fig = px.treemap(
        top,
        path=["short"],
        values="views",
        color="engagement_rate",
        color_continuous_scale="RdYlGn",
        hover_data=["likes", "comments"],
    )
    fig.update_traces(textinfo="label+value")
    return _base_layout(fig, "📊 Performance Treemap (Top 30 Videos)", height=500)


def upload_frequency_chart(df: pd.DataFrame) -> go.Figure:
    if df.empty or "published_dt" not in df.columns:
        return go.Figure()
    monthly = df.set_index("published_dt").resample("ME").size().reset_index()
    monthly.columns = ["date", "count"]
    fig = go.Figure(go.Scatter(
        x=monthly["date"],
        y=monthly["count"],
        mode="lines+markers",
        fill="tozeroy",
        fillcolor="rgba(255,0,0,0.15)",
        line=dict(color=PALETTE["primary"], width=2.5),
        marker=dict(size=6),
    ))
    return _base_layout(fig, "📅 Monthly Upload Frequency", height=350)


def views_distribution(df: pd.DataFrame) -> go.Figure:
    fig = px.histogram(df, x="views", nbins=30, color_discrete_sequence=[PALETTE["primary"]])
    fig.update_traces(opacity=0.8)
    return _base_layout(fig, "📊 Views Distribution", height=350)


def engagement_heatmap(df: pd.DataFrame) -> go.Figure:
    day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    if df.empty or "day_of_week" not in df.columns:
        return go.Figure()

    pivot = df.groupby(["day_of_week", "hour"])["engagement_rate"].mean().unstack(fill_value=0)
    pivot = pivot.reindex(day_order, fill_value=0)

    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        colorscale="Reds",
        showscale=True,
    ))
    fig.update_layout(xaxis_title="Hour (UTC)", yaxis_title="Day of Week")
    return _base_layout(fig, "🔥 Engagement Heatmap (Day × Hour)", height=380)


def gauge_chart(score: float, grade: str) -> go.Figure:
    color = "#00C851" if score >= 80 else "#FF8800" if score >= 60 else "#FF4444"
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        number={"font": {"size": 48, "color": color}},
        title={"text": f"Channel Health Score — Grade: {grade}", "font": {"size": 18, "color": "white"}},
        delta={"reference": 70},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "white"},
            "bar": {"color": color},
            "bgcolor": "rgba(0,0,0,0)",
            "borderwidth": 2,
            "bordercolor": "#333",
            "steps": [
                {"range": [0, 60], "color": "rgba(255,68,68,0.2)"},
                {"range": [60, 80], "color": "rgba(255,136,0,0.2)"},
                {"range": [80, 100], "color": "rgba(0,200,81,0.2)"},
            ],
            "threshold": {
                "line": {"color": "white", "width": 3},
                "thickness": 0.85,
                "value": score,
            },
        }
    ))
    return _base_layout(fig, "", height=380)


def correlation_matrix(df: pd.DataFrame) -> go.Figure:
    cols = ["views", "likes", "comments", "engagement_rate", "viral_score", "duration_sec"]
    sub = df[[c for c in cols if c in df.columns]].corr()
    fig = go.Figure(go.Heatmap(
        z=sub.values,
        x=sub.columns.tolist(),
        y=sub.index.tolist(),
        colorscale="RdBu",
        zmid=0,
        text=np.round(sub.values, 2),
        texttemplate="%{text}",
        showscale=True,
    ))
    return _base_layout(fig, "🔗 Correlation Matrix", height=420)


def forecast_chart(forecast: dict, df: pd.DataFrame) -> go.Figure:
    if not forecast:
        return go.Figure()

    fig = go.Figure()

    # Historical
    hist = df.sort_values("published_dt").tail(20)
    fig.add_trace(go.Scatter(
        x=list(range(len(hist))),
        y=hist["views"].tolist(),
        mode="lines+markers",
        name="Historical",
        line=dict(color=PALETTE["info"], width=2),
    ))

    # Forecast
    base = len(hist)
    fig.add_trace(go.Scatter(
        x=list(range(base, base + len(forecast["next_10_forecast"]))),
        y=forecast["next_10_forecast"],
        mode="lines+markers",
        name="Forecast",
        line=dict(color=PALETTE["primary"], width=2, dash="dash"),
        marker=dict(symbol="diamond", size=8),
    ))

    fig.add_vrect(x0=base, x1=base + 10, fillcolor="rgba(255,0,0,0.05)", layer="below", line_width=0)
    return _base_layout(fig, "🔮 Growth Forecast (Next 10 Videos)", height=380)


def comparison_bar(labels: list, val_a: list, val_b: list, names: list, title: str) -> go.Figure:
    fig = go.Figure([
        go.Bar(name=names[0], x=labels, y=val_a, marker_color=PALETTE["primary"]),
        go.Bar(name=names[1], x=labels, y=val_b, marker_color=PALETTE["info"]),
    ])
    fig.update_layout(barmode="group")
    return _base_layout(fig, title, height=380)


def pie_donut(labels: list, values: list, title: str) -> go.Figure:
    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.5,
        marker=dict(colors=px.colors.sequential.Reds),
    ))
    return _base_layout(fig, title, height=360)


def trend_line(df: pd.DataFrame, metric: str, title: str) -> go.Figure:
    df_s = df.sort_values("published_dt").copy()
    # Rolling average
    df_s["rolling"] = df_s[metric].rolling(5, min_periods=1).mean()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_s["published_dt"],
        y=df_s[metric],
        mode="markers",
        name="Per Video",
        marker=dict(color=PALETTE["primary"], size=5, opacity=0.5),
    ))
    fig.add_trace(go.Scatter(
        x=df_s["published_dt"],
        y=df_s["rolling"],
        mode="lines",
        name="5-Video Average",
        line=dict(color="white", width=2),
    ))
    return _base_layout(fig, title, height=380)
