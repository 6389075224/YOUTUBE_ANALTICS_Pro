import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
"""
Analytics Engine – Computes all channel and video metrics.
"""

import pandas as pd
import numpy as np
from collections import Counter
import re


def build_video_df(videos: list[dict]) -> pd.DataFrame:
    if not videos:
        return pd.DataFrame()
    df = pd.DataFrame(videos)
    df["published_dt"] = pd.to_datetime(df["published_dt"], utc=True, errors="coerce")
    df["day_of_week"] = df["published_dt"].dt.day_name()
    df["month"] = df["published_dt"].dt.month_name()
    df["hour"] = df["published_dt"].dt.hour
    df["year"] = df["published_dt"].dt.year
    df["month_num"] = df["published_dt"].dt.month

    # Core metrics
    df["views"] = pd.to_numeric(df["views"], errors="coerce").fillna(0).astype(int)
    df["likes"] = pd.to_numeric(df["likes"], errors="coerce").fillna(0).astype(int)
    df["comments"] = pd.to_numeric(df["comments"], errors="coerce").fillna(0).astype(int)

    # Engagement rate
    df["engagement_rate"] = df.apply(
        lambda r: ((r["likes"] + r["comments"]) / r["views"] * 100) if r["views"] > 0 else 0, axis=1
    )

    # Viral score
    df["viral_score"] = df.apply(
        lambda r: ((r["likes"] + r["comments"]) / r["views"] * 1000) if r["views"] > 0 else 0, axis=1
    )

    # Performance score
    df["performance_score"] = (0.5 * df["likes"]) + (0.3 * df["comments"]) + (0.2 * df["views"])

    # Duration formatted
    df["duration_fmt"] = df["duration_sec"].apply(format_duration)

    return df


def format_duration(seconds: int) -> str:
    if seconds < 60:
        return f"{seconds}s"
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def channel_kpis(channel: dict, df: pd.DataFrame) -> dict:
    subs = channel.get("subscribers", 0)
    total_views = channel.get("views", 0)
    total_vids = channel.get("video_count", 0)

    avg_views = int(df["views"].mean()) if not df.empty else 0
    avg_likes = int(df["likes"].mean()) if not df.empty else 0
    avg_comments = int(df["comments"].mean()) if not df.empty else 0
    avg_er = round(df["engagement_rate"].mean(), 2) if not df.empty else 0
    sub_view_ratio = round(subs / total_views * 100, 4) if total_views > 0 else 0
    audience_attraction = round(subs / total_vids, 1) if total_vids > 0 else 0

    return {
        "subscribers": subs,
        "total_views": total_views,
        "total_videos": total_vids,
        "avg_views": avg_views,
        "avg_likes": avg_likes,
        "avg_comments": avg_comments,
        "avg_engagement_rate": avg_er,
        "sub_view_ratio": sub_view_ratio,
        "audience_attraction": audience_attraction,
    }


def extract_keywords(df: pd.DataFrame, top_n: int = 30) -> list[tuple]:
    if df.empty:
        return []
    stop_words = {
        "the","a","an","and","or","but","in","on","at","to","for","of","with",
        "is","was","are","were","be","been","has","have","had","will","would",
        "could","should","may","might","can","do","did","does","not","this",
        "that","it","i","my","your","we","you","he","she","they","how","what",
        "why","when","where","who","which","by","from","as","if","so","up",
        "out","about","into","than","then","its","our","also","more","vs",
        "ft","feat","official","video","music","full","new","2023","2024",
        "2022","2021","2020","ep","episode","part","series","season",
    }
    all_words = []
    for title in df["title"].dropna():
        words = re.findall(r'[a-zA-Z]{3,}', title.lower())
        all_words.extend([w for w in words if w not in stop_words])
    return Counter(all_words).most_common(top_n)


def best_upload_times(df: pd.DataFrame) -> dict:
    if df.empty or "day_of_week" not in df.columns:
        return {}

    day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    month_order = ["January","February","March","April","May","June",
                   "July","August","September","October","November","December"]

    day_perf = df.groupby("day_of_week")["views"].mean().reindex(day_order).dropna()
    month_perf = df.groupby("month")["views"].mean().reindex(month_order).dropna()
    hour_perf = df.groupby("hour")["views"].mean()

    return {
        "best_day": day_perf.idxmax() if not day_perf.empty else "N/A",
        "best_month": month_perf.idxmax() if not month_perf.empty else "N/A",
        "best_hour": int(hour_perf.idxmax()) if not hour_perf.empty else "N/A",
        "day_perf": day_perf,
        "month_perf": month_perf,
        "hour_perf": hour_perf,
    }


def channel_health_score(kpis: dict, df: pd.DataFrame) -> dict:
    score = 0
    breakdown = {}

    # 1. Engagement Rate (30 pts)
    er = kpis.get("avg_engagement_rate", 0)
    er_score = min(30, er * 6)
    breakdown["Engagement Rate"] = round(er_score, 1)
    score += er_score

    # 2. Upload Consistency (20 pts)
    consistency_score = 0
    if not df.empty and "published_dt" in df.columns:
        df_s = df.sort_values("published_dt")
        if len(df_s) > 1:
            gaps = df_s["published_dt"].diff().dt.days.dropna()
            cv = gaps.std() / gaps.mean() if gaps.mean() > 0 else 10
            consistency_score = max(0, min(20, 20 - cv * 2))
    breakdown["Upload Consistency"] = round(consistency_score, 1)
    score += consistency_score

    # 3. Average Views (20 pts)
    avg_views = kpis.get("avg_views", 0)
    view_score = min(20, np.log10(max(avg_views, 1)) * 4)
    breakdown["Average Views"] = round(view_score, 1)
    score += view_score

    # 4. Audience Attraction (15 pts)
    aa = kpis.get("audience_attraction", 0)
    aa_score = min(15, np.log10(max(aa, 1)) * 3)
    breakdown["Audience Attraction"] = round(aa_score, 1)
    score += aa_score

    # 5. Sub-to-View Ratio (15 pts)
    svr = kpis.get("sub_view_ratio", 0)
    svr_score = min(15, svr * 150)
    breakdown["Sub-to-View Ratio"] = round(svr_score, 1)
    score += svr_score

    score = round(min(100, max(0, score)), 1)

    if score >= 90:
        grade = "A+"
    elif score >= 80:
        grade = "A"
    elif score >= 70:
        grade = "B"
    elif score >= 60:
        grade = "C"
    else:
        grade = "D"

    return {"score": score, "grade": grade, "breakdown": breakdown}


def detect_anomalies(df: pd.DataFrame) -> dict:
    if df.empty:
        return {}

    q75_v, q25_v = df["views"].quantile(0.75), df["views"].quantile(0.25)
    iqr_v = q75_v - q25_v
    viral = df[df["views"] > q75_v + 1.5 * iqr_v].copy()
    under = df[df["views"] < q25_v - 1.5 * iqr_v].copy()

    q75_e = df["engagement_rate"].quantile(0.90)
    spikes = df[df["engagement_rate"] > q75_e].copy()

    return {
        "viral_anomalies": viral,
        "underperforming": under,
        "engagement_spikes": spikes,
    }


def generate_ai_insights(channel: dict, df: pd.DataFrame, kpis: dict, health: dict) -> list[str]:
    if df.empty:
        return ["Not enough data to generate insights."]

    times = best_upload_times(df)
    insights = []

    er = kpis.get("avg_engagement_rate", 0)
    if er > 5:
        insights.append(f"🔥 Your average engagement rate of {er:.2f}% is excellent — well above the 2–3% industry average. Your audience is highly active.")
    elif er > 2:
        insights.append(f"✅ Your engagement rate of {er:.2f}% is solid. Focus on calls-to-action to push it above 5%.")
    else:
        insights.append(f"⚠️ Your engagement rate of {er:.2f}% is below average. Try adding polls, questions, and stronger CTAs to boost interaction.")

    best_day = times.get("best_day", "N/A")
    if best_day != "N/A":
        insights.append(f"📅 Videos uploaded on **{best_day}** receive the highest average views. Schedule your content around this day.")

    best_hour = times.get("best_hour", "N/A")
    if best_hour != "N/A":
        insights.append(f"⏰ Peak performance time is around **{best_hour}:00 UTC**. Uploading in this window increases early-hour traction.")

    best_month = times.get("best_month", "N/A")
    if best_month != "N/A":
        insights.append(f"📆 **{best_month}** historically yields the best viewership. Plan major content releases during this month.")

    top_vids = df.nlargest(5, "views")
    if not top_vids.empty:
        avg_dur = top_vids["duration_sec"].mean()
        overall_avg = df["duration_sec"].mean()
        if avg_dur > overall_avg * 1.2:
            insights.append("🎬 Your top-performing videos tend to be **longer than average**. Consider producing more long-form content.")
        elif avg_dur < overall_avg * 0.8:
            insights.append("⚡ Your best videos are **shorter and punchy**. Short-form content resonates well with your audience.")

    subs = channel.get("subscribers", 0)
    if subs > 100000:
        insights.append("🌟 With 100K+ subscribers, you're in the growth phase. Consistency is key — aim for at least 2 uploads per week.")
    elif subs > 10000:
        insights.append("📈 You're in the momentum phase (10K–100K subs). Collaborate with similar-sized creators to accelerate growth.")
    else:
        insights.append("🚀 Early-stage channel detected. Focus on SEO-optimised titles, thumbnails, and niche content to build your initial audience.")

    if not df.empty:
        monthly = df.groupby("year")["views"].sum()
        if len(monthly) > 1 and monthly.iloc[-1] > monthly.iloc[-2]:
            insights.append("📊 Year-over-year views are **trending upward** — your channel is growing. Keep the momentum!")
        elif len(monthly) > 1:
            insights.append("📉 Year-over-year views have **declined**. Revisit your content strategy and experiment with new formats.")

    kws = extract_keywords(df, top_n=5)
    if kws:
        kw_str = ", ".join([k[0] for k in kws])
        insights.append(f"🔑 Most frequent keywords in your titles: **{kw_str}**. Make sure these match your target audience's search intent.")

    viral_score_top = df.nlargest(1, "viral_score")
    if not viral_score_top.empty:
        vs = viral_score_top.iloc[0]["viral_score"]
        title = viral_score_top.iloc[0]["title"][:50]
        insights.append(f"💥 Your most viral video scored **{vs:.1f} viral points**: *\"{title}...\"* — study its format, thumbnail, and topic for replication.")

    grade = health.get("grade", "C")
    h_score = health.get("score", 0)
    if grade in ["A+", "A"]:
        insights.append(f"🏆 Your channel health is **{grade} ({h_score}/100)** — outstanding! You're operating at a professional level.")
    elif grade == "B":
        insights.append(f"💪 Channel health score: **{grade} ({h_score}/100)**. You're doing well — focus on upload consistency to reach the A tier.")
    else:
        insights.append(f"🔧 Channel health score: **{grade} ({h_score}/100)**. Focus on improving engagement rate and upload frequency.")

    return insights[:10]


def growth_forecast(df: pd.DataFrame) -> dict:
    if df.empty or len(df) < 5:
        return {}

    df_s = df.sort_values("published_dt").copy()
    df_s["idx"] = range(len(df_s))

    x = df_s["idx"].values
    y = df_s["views"].values

    # Simple linear regression
    coeffs = np.polyfit(x, y, 1)
    slope = coeffs[0]
    intercept = coeffs[1]

    next_10 = [int(max(0, slope * (len(df_s) + i) + intercept)) for i in range(1, 11)]

    trend = "upward 📈" if slope > 0 else "downward 📉"

    return {
        "slope": slope,
        "trend": trend,
        "next_10_forecast": next_10,
        "forecast_labels": [f"Video +{i}" for i in range(1, 11)],
    }
