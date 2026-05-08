# 📈 Pulse Analytics — Streamlit Dashboard

A polished sales & analytics dashboard built with Streamlit + Plotly.
Deploy in minutes to **Streamlit Community Cloud** (free).

---

## 🗂 Project Structure

```
streamlit-dashboard/
├── app.py                  # Main dashboard
├── requirements.txt        # Python dependencies
├── .streamlit/
│   └── config.toml         # Theme configuration
└── README.md
```

---

## 🚀 Deploy to Streamlit Community Cloud

### Step 1 — Push to GitHub

```bash
# Initialize git repo (if not already done)
git init
git add .
git commit -m "Initial commit: Pulse Analytics dashboard"

# Create a GitHub repo (via github.com or gh CLI), then:
git remote add origin https://github.com/YOUR_USERNAME/streamlit-dashboard.git
git branch -M main
git push -u origin main
```

### Step 2 — Deploy on share.streamlit.io

1. Go to **[share.streamlit.io](https://share.streamlit.io)** and sign in with GitHub
2. Click **"New app"**
3. Fill in:
   - **Repository**: `YOUR_USERNAME/streamlit-dashboard`
   - **Branch**: `main`
   - **Main file path**: `app.py`
4. Click **"Deploy!"**

✅ Your app will be live at:
`https://YOUR_USERNAME-streamlit-dashboard-app-XXXX.streamlit.app`

Streamlit Community Cloud is **free** and auto-redeploys on every `git push`.

---

## 💻 Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Launch
streamlit run app.py
```

Opens at `http://localhost:8501`

---

## 🎛 Features

| Feature | Details |
|---|---|
| **KPI Cards** | Revenue, Avg Order Value, Conversion Rate, Top Category |
| **Trend Chart** | Monthly revenue area chart with orders bar overlay |
| **Category Bar** | Horizontal bar chart by product category |
| **Region Donut** | Revenue split by geographic region |
| **Funnel** | Full conversion funnel from visitors → purchase |
| **Growth Table** | Category-level revenue and period-over-period growth |
| **Sidebar filters** | Date range picker, category multiselect, metric toggle |

---

## 🔧 Swapping in Real Data

Replace the `generate_data()` function in `app.py` with your own source:

```python
# Example: load from CSV
@st.cache_data
def load_data():
    df = pd.read_csv("your_data.csv", parse_dates=["date"])
    return df
```

```python
# Example: load from SQL
import sqlalchemy as sa

@st.cache_data
def load_data():
    engine = sa.create_engine(st.secrets["DATABASE_URL"])
    return pd.read_sql("SELECT * FROM sales", engine)
```

Store secrets (API keys, DB URLs) in Streamlit's **Secrets Manager**
(Settings → Secrets in your deployed app), not in code.

---

## 📦 Tech Stack

- [Streamlit](https://streamlit.io) — app framework
- [Plotly](https://plotly.com/python/) — interactive charts
- [Pandas](https://pandas.pydata.org) — data manipulation
- [NumPy](https://numpy.org) — data generation / math
