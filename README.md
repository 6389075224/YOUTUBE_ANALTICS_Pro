# ▶ YouTube Analytics Pro

> Enterprise-grade real-time YouTube channel intelligence platform.  
> Built with Python · Streamlit · Plotly · YouTube Data API v3

---

## 🚀 Features

| Module | Description |
|--------|-------------|
| 🏠 Executive Dashboard | Channel overview, KPI cards, health score, viral videos |
| 📊 Video Analytics | 100-video table with search/sort/filter + 7 charts |
| 💡 Content Insights | Word cloud, keywords, best upload day/month/hour |
| 🔥 Engagement Analytics | Heatmap, leaderboard, trend, correlation matrix |
| ⚡ Advanced Metrics | Viral score, performance score, rankings |
| 🤖 AI Insights Engine | 10 auto-generated recommendations + growth forecast |
| ❤️ Channel Health | 0–100 score, A+–D grade, benchmark comparison |
| 🆚 Competitor Compare | Head-to-head channel analysis with winner badges |
| 🧪 Analytics Lab | Clustering, anomaly detection, distributions |
| 📤 Export Center | CSV, Excel (multi-sheet), branded PDF report |

---

## ⚙️ Setup

### 1. Clone / Download

```bash
git clone https://github.com/yourname/youtube-analytics-pro.git
cd youtube_analytics_pro
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Add Your API Key

Create a `.env` file in the project root:

```
YOUTUBE_API_KEY=your_youtube_data_api_v3_key_here
```

> Get a key at: https://console.cloud.google.com → Enable **YouTube Data API v3** → Create Credentials → API Key

### 4. Run the App

```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`

---

## 📁 Project Structure

```
youtube_analytics_pro/
├── app.py                     # Main entrypoint & routing
├── .env                       # API key (never commit this)
├── requirements.txt
├── pages/
│   ├── overview.py            # Executive Dashboard
│   ├── video_analytics.py     # Video table & charts
│   ├── content_insights.py    # Word cloud & timing
│   ├── engagement.py          # Engagement deep-dive
│   ├── advanced_metrics.py    # Viral & performance scores
│   ├── ai_insights.py         # AI recommendations
│   ├── channel_health.py      # Health score & grade
│   ├── competitor.py          # Competitor comparison
│   ├── analytics_lab.py       # Advanced analysis
│   └── export_center.py       # CSV / Excel / PDF
├── services/
│   ├── youtube_api.py         # YouTube Data API v3 layer
│   ├── analytics.py           # Metrics calculation engine
│   └── export_service.py      # Export generators
└── utils/
    ├── visualizations.py      # All Plotly chart builders
    ├── helpers.py             # UI components & formatters
    └── styles.py              # Dark/Light theme CSS
```

---

## 🔐 Security

- API key loaded exclusively from `.env` — never exposed in the UI
- `.env` is listed in `.gitignore` by default
- All API responses are cached (1 hour for channel data, 30 min for videos)

---

## 📊 Metrics Glossary

| Metric | Formula |
|--------|---------|
| Engagement Rate | `(Likes + Comments) / Views × 100` |
| Viral Score | `(Likes + Comments) / Views × 1000` |
| Performance Score | `0.5×Likes + 0.3×Comments + 0.2×Views` |
| Audience Attraction | `Subscribers / Total Videos` |
| Sub-to-View Ratio | `Subscribers / Total Views × 100` |

---

## 🏥 Health Score Breakdown

| Factor | Max Points |
|--------|-----------|
| Engagement Rate | 30 |
| Upload Consistency | 20 |
| Average Views | 20 |
| Audience Attraction | 15 |
| Sub-to-View Ratio | 15 |
| **Total** | **100** |

Grades: **A+** (90–100) · **A** (80–89) · **B** (70–79) · **C** (60–69) · **D** (<60)

---

## 🛠 Tech Stack

- **Python 3.11+**
- **Streamlit** — UI framework
- **Plotly** — Interactive charts
- **Pandas / NumPy** — Data processing
- **WordCloud / Matplotlib** — Word cloud generation
- **scikit-learn** — K-means clustering
- **google-api-python-client** — YouTube Data API v3
- **FPDF2** — PDF generation
- **OpenPyXL** — Excel export
- **python-dotenv** — Environment variable management
- **isodate** — ISO 8601 duration parsing

---

## 📄 License

MIT — free to use, modify, and distribute.
