# Garment Production Dashboard - Streamlit App (Stable Excel version)

import streamlit as st
import pandas as pd
import math

st.set_page_config(page_title="Garment Production Dashboard", layout="wide")

# ---------------------- Data Loader ----------------------
@st.cache_data
def load_excel_data():
    try:
        df = pd.read_excel("garment_data.xlsx")
        df.columns = df.columns.str.strip().str.lower()

        # normalize headers
        rename_map = {
            "kpi": "KPI",
            "value": "Value",
            "target": "Target",
            "variance": "Variance"
        }
        df.rename(columns=rename_map, inplace=True)
        df["KPI"] = df["KPI"].astype(str).str.strip().str.upper()
        return df
    except Exception as e:
        st.error(f"⚠️ Could not load garment_data.xlsx: {e}")
        # fallback demo data
        return pd.DataFrame({
            "KPI": ["PLAN VS ACTUAL", "EFFICIENCY", "LOST TIME"],
            "Value": [80, 65, 10],
            "Target": [100, 70, 5],
            "Variance": [-20, -5, +5],
        })

# helper function: safe value extraction
def get_val(df, kpi, col):
    subset = df[df["KPI"].str.contains(kpi.upper(), case=False, na=False)]
    if not subset.empty:
        return float(subset.iloc[0][col])
    return 0.0

# ---------------------- Donut Chart ----------------------
def donut_chart(value, ring_color, track_color="#EFEFEF", size=120, stroke=12):
    radius = (size - stroke) / 2
    circumference = 2 * math.pi * radius
    progress = circumference * (value / 100)
    return f"""
    <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">
      <circle cx="{size/2}" cy="{size/2}" r="{radius}"
              stroke="{track_color}" stroke-width="{stroke}" fill="none" />
      <circle cx="{size/2}" cy="{size/2}" r="{radius}"
              stroke="{ring_color}" stroke-width="{stroke}" fill="none"
              stroke-dasharray="{progress} {circumference}"
              stroke-linecap="round"
              transform="rotate(-90 {size/2} {size/2})" />
      <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle"
            font-size="18" font-weight="700" fill="#333">{value:.0f}%</text>
    </svg>
    """

# ---------------------- CSS ----------------------
st.markdown("""
<style>
body {font-family: 'Inter', sans-serif;}
.header-container {
  background-color: #8b7355;
  border-radius: 18px;
  padding: 25px 40px;
  margin-bottom: 25px;
  color: white;
  box-shadow: 0px 6px 16px rgba(0,0,0,0.2);
}
.header-title {font-size: 36px; font-weight: 800; margin-bottom: 6px;}
.header-sub {font-size: 18px; opacity: 0.9;}
.kpi-container {display: flex; gap: 25px; justify-content: space-between;}
.kpi-card {
  flex: 1;
  border-radius: 18px;
  padding: 22px;
  background: var(--card-color);
  box-shadow: 0 4px 10px rgba(0,0,0,0.08);
}
.kpi-title {font-weight: 700; margin-bottom: 10px;}
.kpi-value {font-size: 52px; font-weight: 800; margin-top: -20px;}
.kpi-meta {display: flex; justify-content: space-between; margin-top: 10px; font-size: 15px;}
div.stButton > button {
  font-weight: 700 !important;
  border-radius: 8px !important;
  border: 2px solid var(--accent) !important;
  background: white !important;
  color: var(--accent) !important;
  padding: 6px 20px !important;
}
div.stButton > button:hover {
  background: var(--accent) !important;
  color: white !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------------- Header ----------------------
def render_header():
    st.markdown("""
    <div class="header-container">
        <div class="header-title">Garment Production Dashboard</div>
        <div class="header-sub">High-level KPIs and trends for quick status checks (Owner’s View)</div>
    </div>
    """, unsafe_allow_html=True)

# ---------------------- KPI Card ----------------------
def kpi_card(title, value, target, variance, bg_color, ring_color, accent_color, route):
    st.markdown(f"""
    <div class="kpi-card" style="--card-color:{bg_color}; --accent:{accent_color}">
        <div class="kpi-title">{title}</div>
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div class="kpi-value">{value:.0f}%</div>
            <div>{donut_chart(value, ring_color)}</div>
        </div>
        <div class="kpi-meta">
            <div><b>Target:</b> {target:.0f}%</div>
            <div><b>Variance:</b> {variance:+.1f}%</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Drill Down", key=f"btn_{route}"):
        st.session_state.page = route

# ---------------------- Dashboard ----------------------
def show_dashboard():
    df = load_excel_data()
    render_header()

    st.markdown('<div class="kpi-container">', unsafe_allow_html=True)
    kpi_card("PLAN VS ACTUAL",
             get_val(df, "PLAN VS ACTUAL", "Value"),
             get_val(df, "PLAN VS ACTUAL", "Target"),
             get_val(df, "PLAN VS ACTUAL", "Variance"),
             "#fdecec", "#e63946", "#e63946", "plan_actual")
    kpi_card("EFFICIENCY",
             get_val(df, "EFFICIENCY", "Value"),
             get_val(df, "EFFICIENCY", "Target"),
             get_val(df, "EFFICIENCY", "Variance"),
             "#fff2cc", "#f4a300", "#f4a300", "efficiency")
    kpi_card("LOST TIME",
             get_val(df, "LOST TIME", "Value"),
             get_val(df, "LOST TIME", "Target"),
             get_val(df, "LOST TIME", "Variance"),
             "#fdecec", "#e63946", "#e63946", "lost_time")
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------- Drill Down ----------------------
def show_detail(page):
    st.button("← Back to Dashboard", on_click=lambda: st.session_state.update({"page": "dashboard"}))
    if page == "plan_actual":
        st.header("Plan vs Actual Analysis")
        st.dataframe(pd.DataFrame({
            "Line": ["Line 1", "Line 2", "Line 3"],
            "Variance": ["-2%", "-1%", "+3%"],
            "Observed Cause": ["Training Gaps", "Fabric Quality Issues", "Good Performance"],
            "Category": ["Manpower", "Material", "None"],
            "Action": ["Analyze & Action", "Analyze & Action", "No Action Needed"]
        }))
    elif page == "efficiency":
        st.header("Efficiency Analysis")
        st.dataframe(pd.DataFrame({
            "Line": ["Line 4", "Line 5", "Line 6"],
            "Variance": ["-2%", "-1%", "+3%"],
            "Observed Cause": ["Training Gaps", "Fabric Quality Issues", "Good performance"],
            "Category": ["Manpower", "Material", "None"],
            "Action": ["Analyze & Action", "Analyze & Action", "No action needed"]
        }))
    else:
        st.header("Lost Time Analysis")
        st.dataframe(pd.DataFrame({
            "Line": ["Line 7", "Line 8", "Line 9"],
            "Variance": ["+1%", "+3%", "-2%"],
            "Observed Cause": ["Machine breakdown", "Material delay", "Absent operator"],
            "Category": ["Machine", "Material", "Manpower"],
            "Action": ["Analyze & Action", "Analyze & Action", "Analyze & Action"]
        }))

# ---------------------- Router ----------------------
if "page" not in st.session_state:
    st.session_state.page = "dashboard"

if st.session_state.page == "dashboard":
    show_dashboard()
else:
    show_detail(st.session_state.page)
