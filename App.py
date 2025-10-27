import streamlit as st
import pandas as pd
import requests
from io import BytesIO
import plotly.graph_objects as go

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="Garment Production Dashboard", layout="wide")

GITHUB_EXCEL_URL = "https://github.com/Mahie357/garment-dashboard/raw/refs/heads/main/garment_data.xlsx"

# -------------------------------
# LOAD DATA
# -------------------------------
@st.cache_data(ttl=60)
def load_data():
    try:
        response = requests.get(GITHUB_EXCEL_URL, timeout=15)
        response.raise_for_status()
        df = pd.read_excel(BytesIO(response.content))
    except Exception as e:
        st.warning(f"⚠️ Could not load Excel from GitHub. Using demo data. Error: {e}")
        df = pd.DataFrame({
            "KPI": ["PLAN VS ACTUAL", "EFFICIENCY", "LOST TIME"],
            "Actual": [90, 68, 3.5],
            "Target": [95, 70, 2.0],
        })

    df.columns = [c.strip().upper() for c in df.columns]
    df["KPI"] = df["KPI"].astype(str).str.strip().str.upper()
    df["ACTUAL"] = pd.to_numeric(df["ACTUAL"], errors="coerce").fillna(0)
    df["TARGET"] = pd.to_numeric(df["TARGET"], errors="coerce").fillna(0)

    # Normalization for robust matching
    df["KPI"] = df["KPI"].replace({
        "PLANVS ACTUAL": "PLAN VS ACTUAL",
        "PLAN V ACTUAL": "PLAN VS ACTUAL",
        "EFFECIENCY": "EFFICIENCY",
        "LOSS TIME": "LOST TIME"
    })

    # Force all three KPIs to exist
    required = ["PLAN VS ACTUAL", "EFFICIENCY", "LOST TIME"]
    result = []
    for name in required:
        row = df[df["KPI"] == name]
        if not row.empty:
            result.append(row.iloc[0])
        else:
            result.append(pd.Series({"KPI": name, "ACTUAL": 0, "TARGET": 0}))
    return pd.DataFrame(result)

df = load_data()

# -------------------------------
# HEADER
# -------------------------------
st.markdown("""
<div style="text-align:center; margin-bottom:25px;">
  <h1 style="font-size:42px; font-weight:800; margin-bottom:0;">Garment Production Dashboard</h1>
  <p style="font-size:17px; color:gray;">High-level KPIs and trends for quick status checks (Owner’s View)</p>
</div>
""", unsafe_allow_html=True)

if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

# -------------------------------
# GAUGE FUNCTION
# -------------------------------
def gauge_chart(value, color):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={'suffix': "%", 'font': {'size': 26, 'color': color}},
        gauge={
            'axis': {'range': [0, 100], 'visible': False},
            'bar': {'color': color, 'thickness': 0.35},
            'bgcolor': "white",
            'steps': [{'range': [0, 100], 'color': "#f4f4f4"}],
        }
    ))
    fig.update_layout(height=140, margin=dict(l=0, r=0, t=0, b=0))
    return fig

# -------------------------------
# CARD DESIGN
# -------------------------------
cols = st.columns(3)
bg_colors = ["#FFEAEA", "#FFF6DA", "#FFEAEA"]
ring_colors = ["#E63946", "#FFB703", "#E63946"]

for col, rec, bg, color in zip(cols, df.to_dict("records"), bg_colors, ring_colors):
    kpi = rec["KPI"].title()
    actual = rec["ACTUAL"]
    target = rec["TARGET"]
    variance = actual - target
    variance_txt = f"+{variance:.1f_
