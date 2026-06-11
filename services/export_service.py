import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
"""
Export Service – CSV, Excel, and PDF generation.
"""

import io
import pandas as pd
from fpdf import FPDF
from datetime import datetime


def export_csv(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")


def export_excel(df: pd.DataFrame, channel: dict, kpis: dict) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        # Channel Overview sheet
        overview = pd.DataFrame([{
            "Channel": channel.get("title",""),
            "Subscribers": kpis.get("subscribers",0),
            "Total Views": kpis.get("total_views",0),
            "Total Videos": kpis.get("total_videos",0),
            "Avg Views/Video": kpis.get("avg_views",0),
            "Avg Likes/Video": kpis.get("avg_likes",0),
            "Avg Comments/Video": kpis.get("avg_comments",0),
            "Avg Engagement Rate (%)": kpis.get("avg_engagement_rate",0),
        }])
        overview.to_excel(writer, sheet_name="Channel Overview", index=False)

        # Videos sheet
        cols = ["title","published_at","views","likes","comments",
                "engagement_rate","viral_score","performance_score","duration_fmt"]
        export_df = df[[c for c in cols if c in df.columns]].copy()
        export_df.to_excel(writer, sheet_name="Videos", index=False)

        # Top 10 by Views
        df.nlargest(10,"views")[cols[:7]].to_excel(writer, sheet_name="Top 10 Views", index=False)

        # Top 10 by Engagement
        df.nlargest(10,"engagement_rate")[cols[:7]].to_excel(writer, sheet_name="Top 10 Engagement", index=False)

    return buf.getvalue()


class YTPdf(FPDF):
    def header(self):
        self.set_fill_color(255, 0, 0)
        self.rect(0, 0, 210, 18, "F")
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(255, 255, 255)
        self.cell(0, 18, "  YouTube Analytics Pro — Channel Report", ln=True, align="L")
        self.set_text_color(0, 0, 0)

    def footer(self):
        self.set_y(-14)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Generated {datetime.now().strftime('%Y-%m-%d %H:%M')} UTC  |  Page {self.page_no()}", align="C")

    def section_title(self, text: str):
        self.ln(5)
        self.set_fill_color(30, 30, 30)
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 11)
        self.cell(0, 9, f"  {text}", ln=True, fill=True)
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def kv_row(self, key: str, value: str, shade: bool = False):
        if shade:
            self.set_fill_color(245, 245, 245)
        else:
            self.set_fill_color(255, 255, 255)
        self.set_font("Helvetica", "B", 9)
        self.cell(70, 7, key, border=0, fill=True)
        self.set_font("Helvetica", "", 9)
        self.cell(0, 7, str(value), ln=True, fill=True)

    def insight_row(self, idx: int, text: str):
        clean = text.replace("**", "").replace("*", "").encode("latin-1", "replace").decode("latin-1")
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(200, 0, 0)
        self.cell(10, 7, f"{idx}.")
        self.set_font("Helvetica", "", 9)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 7, clean)
        self.ln(1)


def export_pdf(channel: dict, kpis: dict, df: pd.DataFrame,
               health: dict, insights: list[str]) -> bytes:
    pdf = YTPdf()
    pdf.set_auto_page_break(auto=True, margin=14)
    pdf.add_page()

    # ── Title ──
    pdf.ln(8)
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(255, 0, 0)
    name = channel.get("title","Channel").encode("latin-1","replace").decode("latin-1")
    pdf.cell(0, 12, name, ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 8, f"Analytics Report  |  Generated {datetime.now().strftime('%B %d, %Y')}", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(4)

    # ── Channel Overview ──
    pdf.section_title("1. Channel Overview")
    pairs = [
        ("Custom URL", channel.get("custom_url","N/A")),
        ("Country", channel.get("country","N/A")),
        ("Created", channel.get("published_at","")[:10]),
        ("Description", (channel.get("description","")[:200] + "…") if channel.get("description") else "N/A"),
    ]
    for i, (k, v) in enumerate(pairs):
        v_clean = str(v).encode("latin-1","replace").decode("latin-1")
        pdf.kv_row(k, v_clean, shade=i % 2 == 0)

    # ── KPI Summary ──
    pdf.section_title("2. KPI Summary")
    kpi_pairs = [
        ("Subscribers", f"{kpis.get('subscribers',0):,}"),
        ("Total Views", f"{kpis.get('total_views',0):,}"),
        ("Total Videos", f"{kpis.get('total_videos',0):,}"),
        ("Avg Views / Video", f"{kpis.get('avg_views',0):,}"),
        ("Avg Likes / Video", f"{kpis.get('avg_likes',0):,}"),
        ("Avg Comments / Video", f"{kpis.get('avg_comments',0):,}"),
        ("Avg Engagement Rate", f"{kpis.get('avg_engagement_rate',0):.2f}%"),
        ("Sub-to-View Ratio", f"{kpis.get('sub_view_ratio',0):.4f}%"),
        ("Audience Attraction", f"{kpis.get('audience_attraction',0):,.0f} subs/video"),
    ]
    for i, (k, v) in enumerate(kpi_pairs):
        pdf.kv_row(k, v, shade=i % 2 == 0)

    # ── Top 10 Videos ──
    pdf.section_title("3. Top 10 Videos by Views")
    if not df.empty:
        top = df.nlargest(10, "views")[["title","views","likes","comments","engagement_rate"]]
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_fill_color(255, 0, 0)
        pdf.set_text_color(255, 255, 255)
        headers = ["Title", "Views", "Likes", "Comments", "ER%"]
        widths = [90, 22, 22, 28, 20]
        for h, w in zip(headers, widths):
            pdf.cell(w, 7, h, fill=True)
        pdf.ln()
        pdf.set_text_color(0, 0, 0)
        for i, (_, row) in enumerate(top.iterrows()):
            pdf.set_fill_color(245, 245, 245) if i % 2 == 0 else pdf.set_fill_color(255, 255, 255)
            t = str(row["title"])[:45].encode("latin-1","replace").decode("latin-1")
            pdf.set_font("Helvetica", "", 8)
            pdf.cell(widths[0], 7, t, fill=True)
            pdf.cell(widths[1], 7, f"{int(row['views']):,}", fill=True)
            pdf.cell(widths[2], 7, f"{int(row['likes']):,}", fill=True)
            pdf.cell(widths[3], 7, f"{int(row['comments']):,}", fill=True)
            pdf.cell(widths[4], 7, f"{row['engagement_rate']:.2f}%", fill=True, ln=True)

    # ── Channel Health ──
    pdf.section_title("4. Channel Health Report")
    score = health.get("score", 0)
    grade = health.get("grade", "N/A")
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(200, 0, 0)
    pdf.cell(0, 10, f"Health Score: {score}/100  |  Grade: {grade}", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 9)
    for i, (factor, pts) in enumerate(health.get("breakdown", {}).items()):
        pdf.kv_row(factor, f"{pts} pts", shade=i % 2 == 0)

    # ── AI Insights ──
    pdf.section_title("5. AI Insights & Recommendations")
    for idx, insight in enumerate(insights, 1):
        pdf.insight_row(idx, insight)

    # ── Viral Videos ──
    pdf.section_title("6. Top 5 Viral Videos")
    if not df.empty:
        viral = df.nlargest(5, "viral_score")[["title","viral_score","views","likes","comments"]]
        for i, (_, row) in enumerate(viral.iterrows()):
            t = str(row["title"])[:60].encode("latin-1","replace").decode("latin-1")
            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(0, 7, f"#{i+1}  {t}", ln=True)
            pdf.set_font("Helvetica", "", 8)
            pdf.set_text_color(150, 150, 150)
            pdf.cell(0, 6, f"     Viral Score: {row['viral_score']:.1f}  |  Views: {int(row['views']):,}  |  Likes: {int(row['likes']):,}", ln=True)
            pdf.set_text_color(0, 0, 0)

    buf = io.BytesIO()
    pdf.output(buf)
    return buf.getvalue()
