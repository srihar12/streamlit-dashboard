import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import random

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Pulse Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

  html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
  }

  /* Dark sidebar */
  section[data-testid="stSidebar"] {
    background: #0d1117;
    border-right: 1px solid #21262d;
  }
  section[data-testid="stSidebar"] * {
    color: #e6edf3 !important;
  }

  /* Main background */
  .main .block-container {
    background: #f5f3ef;
    padding: 2rem 2.5rem;
    max-width: 1400px;
  }

  /* KPI cards */
  .kpi-card {
    background: #fff;
    border: 1px solid #e2ddd6;
    border-radius: 12px;
    padding: 1.4rem 1.6rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    transition: box-shadow 0.2s;
  }
  .kpi-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.08); }
  .kpi-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #8b7e74;
    margin-bottom: 0.3rem;
  }
  .kpi-value {
    font-family: 'DM Serif Display', serif;
    font-size: 2.1rem;
    color: #1a1208;
    line-height: 1.1;
  }
  .kpi-delta-pos { color: #2a9d5c; font-size: 0.82rem; font-weight: 600; }
  .kpi-delta-neg { color: #e05c3a; font-size: 0.82rem; font-weight: 600; }

  /* Section title */
  .section-title {
    font-family: 'DM Serif Display', serif;
    font-size: 1.4rem;
    color: #1a1208;
    margin: 1.6rem 0 0.8rem;
  }

  /* Chart cards */
  .chart-card {
    background: #fff;
    border: 1px solid #e2ddd6;
    border-radius: 12px;
    padding: 1rem 1.2rem 0.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
  }

  /* Hide default streamlit chrome */
  #MainMenu, footer, header { visibility: hidden; }

  /* Sidebar logo area */
  .sidebar-brand {
    font-family: 'DM Serif Display', serif;
    font-size: 1.5rem;
    color: #e6c87a !important;
    padding: 0.5rem 0 1.5rem;
    border-bottom: 1px solid #21262d;
    margin-bottom: 1.5rem;
  }
</style>
""", unsafe_allow_html=True)

# ── Data generation ───────────────────────────────────────────────────────────
@st.cache_data
def generate_data(seed=42):
    np.random.seed(seed)
    random.seed(seed)

    # Daily sales — 18 months
    dates = pd.date_range(end=datetime.today(), periods=540, freq="D")
    trend = np.linspace(12000, 28000, 540)
    noise = np.random.normal(0, 2200, 540)
    seasonal = 3000 * np.sin(np.linspace(0, 4 * np.pi, 540))
    revenue = np.maximum(trend + noise + seasonal, 5000)

    df_daily = pd.DataFrame({
        "date": dates,
        "revenue": revenue.round(2),
        "orders": (revenue / np.random.uniform(80, 130, 540)).round().astype(int),
        "new_customers": np.random.poisson(38, 540),
    })
    df_daily["month"] = df_daily["date"].dt.to_period("M").astype(str)

    # Product categories
    categories = ["Electronics", "Apparel", "Home & Garden", "Sports", "Beauty"]
    cat_revenue = [138400, 92100, 74300, 61800, 45200]
    cat_growth  = [12.4, -3.1, 8.7, 22.3, 5.9]
    df_cat = pd.DataFrame({"category": categories, "revenue": cat_revenue, "growth": cat_growth})

    # Regional data
    regions = ["North", "South", "East", "West", "Central"]
    region_rev = np.random.dirichlet(np.ones(5)) * 450000
    df_region = pd.DataFrame({"region": regions, "revenue": region_rev.round(2)})

    # Funnel
    funnel_stages = ["Visitors", "Product Views", "Add to Cart", "Checkout", "Purchased"]
    funnel_vals   = [100000, 62000, 24800, 14200, 9100]
    df_funnel = pd.DataFrame({"stage": funnel_stages, "users": funnel_vals})

    return df_daily, df_cat, df_region, df_funnel

df_daily, df_cat, df_region, df_funnel = generate_data()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-brand">📈 Pulse</div>', unsafe_allow_html=True)

    st.markdown("**Date range**")
    date_options = {"Last 30 days": 30, "Last 90 days": 90, "Last 6 months": 180, "All time": 540}
    selected_range = st.selectbox("", list(date_options.keys()), index=1, label_visibility="collapsed")
    days = date_options[selected_range]

    st.markdown("---")
    st.markdown("**Category filter**")
    all_cats = df_cat["category"].tolist()
    selected_cats = st.multiselect("", all_cats, default=all_cats, label_visibility="collapsed")

    st.markdown("---")
    st.markdown("**Metric**")
    metric = st.radio("", ["Revenue", "Orders", "New Customers"], label_visibility="collapsed")

# ── Filter data ───────────────────────────────────────────────────────────────
df_filtered = df_daily.tail(days).copy()
df_cat_filtered = df_cat[df_cat["category"].isin(selected_cats)]

metric_col = {"Revenue": "revenue", "Orders": "orders", "New Customers": "new_customers"}[metric]
metric_prefix = "$" if metric == "Revenue" else ""
metric_fmt = ",.0f"

# ── KPI calculations ──────────────────────────────────────────────────────────
half = len(df_filtered) // 2
cur = df_filtered.tail(half)
prev = df_filtered.head(half)

total_cur  = cur[metric_col].sum()
total_prev = prev[metric_col].sum()
delta_pct  = (total_cur - total_prev) / total_prev * 100 if total_prev else 0

avg_order = (df_filtered["revenue"] / df_filtered["orders"]).mean()
conv_rate = (df_funnel["users"].iloc[-1] / df_funnel["users"].iloc[0]) * 100
top_cat   = df_cat_filtered.loc[df_cat_filtered["revenue"].idxmax(), "category"] if not df_cat_filtered.empty else "—"

# ── Plotly theme ──────────────────────────────────────────────────────────────
PALETTE = ["#c9923a", "#2a6eb5", "#2a9d5c", "#e05c3a", "#7c5cbf", "#4eada0"]
CHART_BG = "#ffffff"
FONT_CLR  = "#1a1208"
GRID_CLR  = "#efe9e0"

def base_layout(title=""):
    return dict(
        paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
        font=dict(family="DM Sans", color=FONT_CLR, size=12),
        title=dict(text=title, font=dict(family="DM Serif Display", size=16, color=FONT_CLR), x=0.01),
        margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
    )

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    f'<h1 style="font-family:\'DM Serif Display\',serif;font-size:2rem;color:#1a1208;margin-bottom:0.2rem">'
    f'Analytics Dashboard</h1>'
    f'<p style="color:#8b7e74;font-size:0.88rem;margin-bottom:1.6rem">'
    f'Showing <b>{selected_range.lower()}</b> · Updated {datetime.today().strftime("%b %d, %Y")}</p>',
    unsafe_allow_html=True
)

# ── KPI row ───────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
kpis = [
    (metric, f"{metric_prefix}{total_cur:{metric_fmt}}", delta_pct, True),
    ("Avg Order Value", f"${avg_order:,.2f}", 4.3, True),
    ("Conversion Rate", f"{conv_rate:.1f}%", -0.8, False),
    ("Top Category", top_cat, None, None),
]
for col, (label, val, delta, pos) in zip([k1, k2, k3, k4], kpis):
    with col:
        if delta is not None:
            sign = "▲" if delta >= 0 else "▼"
            cls  = "kpi-delta-pos" if (pos and delta >= 0) or (not pos and delta < 0) else "kpi-delta-neg"
            delta_html = f'<div class="{cls}">{sign} {abs(delta):.1f}% vs prior period</div>'
        else:
            delta_html = '<div style="height:1.1rem"></div>'
        st.markdown(
            f'<div class="kpi-card">'
            f'  <div class="kpi-label">{label}</div>'
            f'  <div class="kpi-value">{val}</div>'
            f'  {delta_html}'
            f'</div>',
            unsafe_allow_html=True
        )

# ── Revenue trend ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Trend</div>', unsafe_allow_html=True)

df_monthly = df_filtered.groupby("month").agg(
    revenue=("revenue", "sum"),
    orders=("orders", "sum"),
    new_customers=("new_customers", "sum"),
).reset_index()

fig_trend = make_subplots(specs=[[{"secondary_y": True}]])
fig_trend.add_trace(
    go.Scatter(
        x=df_monthly["month"], y=df_monthly[metric_col],
        name=metric, fill="tozeroy",
        fillcolor="rgba(201,146,58,0.12)", line=dict(color=PALETTE[0], width=2.5),
        hovertemplate=f"%{{x}}<br>{metric}: {metric_prefix}%{{y:{metric_fmt}}}<extra></extra>",
    ), secondary_y=False
)
fig_trend.add_trace(
    go.Bar(
        x=df_monthly["month"], y=df_monthly["orders"],
        name="Orders", marker_color="rgba(42,110,181,0.18)",
        hovertemplate="%{x}<br>Orders: %{y:,}<extra></extra>",
    ), secondary_y=True
)
fig_trend.update_layout(**base_layout(), height=300,
    xaxis=dict(showgrid=False, tickangle=-30, tickfont=dict(size=10)),
    yaxis=dict(showgrid=True, gridcolor=GRID_CLR, zeroline=False),
    yaxis2=dict(showgrid=False, zeroline=False),
)
st.plotly_chart(fig_trend, use_container_width=True)

# ── Category + Region ─────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Breakdown</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)

with c1:
    df_cat_sorted = df_cat_filtered.sort_values("revenue", ascending=True)
    fig_cat = go.Figure(go.Bar(
        x=df_cat_sorted["revenue"], y=df_cat_sorted["category"],
        orientation="h",
        marker=dict(
            color=df_cat_sorted["revenue"],
            colorscale=[[0, "#f5ebe0"], [1, PALETTE[0]]],
            showscale=False,
        ),
        text=[f"${v/1000:.0f}k" for v in df_cat_sorted["revenue"]],
        textposition="outside",
        hovertemplate="%{y}<br>Revenue: $%{x:,.0f}<extra></extra>",
    ))
    fig_cat.update_layout(**base_layout("Revenue by Category"), height=280,
        xaxis=dict(showgrid=True, gridcolor=GRID_CLR, zeroline=False),
        yaxis=dict(showgrid=False),
    )
    st.plotly_chart(fig_cat, use_container_width=True)

with c2:
    fig_pie = go.Figure(go.Pie(
        labels=df_region["region"], values=df_region["revenue"],
        hole=0.52,
        marker=dict(colors=PALETTE, line=dict(color="#fff", width=2)),
        textinfo="label+percent",
        hovertemplate="%{label}<br>$%{value:,.0f}<extra></extra>",
    ))
    fig_pie.update_layout(**base_layout("Revenue by Region"), height=280)
    st.plotly_chart(fig_pie, use_container_width=True)

# ── Funnel + Growth table ─────────────────────────────────────────────────────
st.markdown('<div class="section-title">Funnel & Category Growth</div>', unsafe_allow_html=True)
c3, c4 = st.columns([1.2, 1])

with c3:
    pct = (df_funnel["users"] / df_funnel["users"].iloc[0] * 100).round(1)
    fig_funnel = go.Figure(go.Funnel(
        y=df_funnel["stage"], x=df_funnel["users"],
        textinfo="value+percent initial",
        marker=dict(color=[f"rgba(201,146,58,{0.3+i*0.14})" for i in range(5)]),
        connector=dict(line=dict(color="#e2ddd6", width=1)),
    ))
    fig_funnel.update_layout(**base_layout("Conversion Funnel"), height=300,
        margin=dict(l=10, r=10, t=40, b=10),
    )
    st.plotly_chart(fig_funnel, use_container_width=True)

with c4:
    st.markdown("<br>", unsafe_allow_html=True)
    df_growth = df_cat_filtered[["category", "revenue", "growth"]].copy()
    df_growth["revenue_fmt"] = df_growth["revenue"].apply(lambda x: f"${x/1000:.1f}k")
    df_growth["growth_fmt"]  = df_growth["growth"].apply(
        lambda x: f"{'▲' if x>=0 else '▼'} {abs(x):.1f}%"
    )
    df_growth["color"] = df_growth["growth"].apply(
        lambda x: "#2a9d5c" if x >= 0 else "#e05c3a"
    )

    rows = ""
    for _, row in df_growth.iterrows():
        rows += (
            f'<tr style="border-bottom:1px solid #efe9e0">'
            f'<td style="padding:0.55rem 0.4rem;font-weight:500">{row.category}</td>'
            f'<td style="padding:0.55rem 0.4rem;text-align:right">{row.revenue_fmt}</td>'
            f'<td style="padding:0.55rem 0.4rem;text-align:right;color:{row.color};font-weight:600">{row.growth_fmt}</td>'
            f'</tr>'
        )

    st.markdown(
        f'<div class="chart-card" style="padding:1.2rem">'
        f'<div style="font-family:\'DM Serif Display\',serif;font-size:1rem;color:#1a1208;margin-bottom:0.8rem">Category Performance</div>'
        f'<table style="width:100%;border-collapse:collapse;font-size:0.85rem">'
        f'<thead><tr style="border-bottom:2px solid #1a1208">'
        f'<th style="text-align:left;padding:0.3rem 0.4rem;font-size:0.7rem;letter-spacing:0.07em;text-transform:uppercase;color:#8b7e74">Category</th>'
        f'<th style="text-align:right;padding:0.3rem 0.4rem;font-size:0.7rem;letter-spacing:0.07em;text-transform:uppercase;color:#8b7e74">Revenue</th>'
        f'<th style="text-align:right;padding:0.3rem 0.4rem;font-size:0.7rem;letter-spacing:0.07em;text-transform:uppercase;color:#8b7e74">Growth</th>'
        f'</tr></thead><tbody>{rows}</tbody></table></div>',
        unsafe_allow_html=True
    )

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(
    '<div style="margin-top:2.5rem;padding-top:1rem;border-top:1px solid #e2ddd6;'
    'color:#b0a090;font-size:0.75rem;text-align:center">'
    'Pulse Analytics · Built with Streamlit · Data is synthetic for demo purposes'
    '</div>',
    unsafe_allow_html=True
)
