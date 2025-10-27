import streamlit as st
import pandas as pd
import requests
from io import BytesIO
import plotly.graph_objects as go

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="Garment Production Dashboard", layout="wide")

# GitHub Excel link
GITHUB_EXCEL_URL = "https://github.com/Mahie357/garment-dashboard/raw/refs/heads/main/garment_data.xlsx"

# -----------------------------
# LOAD DATA FUNCTION
# -----------------------------
@st.cache_data(ttl=60)
def load_data():
    try:
        response = requests.get(GITHUB_EXCEL_URL, timeout=15)
        response.raise_for_status()
        df = pd.read_excel(BytesIO(response.content))
    except Exception as e:
        st.warning(f"⚠️ Could not load Excel from GitHub. Using sample data. Error: {e}")
        df = pd.DataFrame({
            "KPI": ["PLAN VS ACTUAL", "EFFICIENCY", "LOST TIME"],
            "Actual": [90, 68, 3.5],
            "Target": [95, 70, 2.0],
        })
    
    # Normalize columns
    df.columns = [c.strip().upper() for c in df.columns]
    if not {"KPI", "ACTUAL", "TARGET"}.issubset(df.columns):
        raise ValueError(f"Excel must contain columns: KPI, Actual, Target. Found: {list(df.columns)}")

    df["KPI"] = df["KPI"].astype(str).str.strip().str.upper()
    df["ACTUAL"] = pd.to_numeric(df["ACTUAL"], errors="coerce").fillna(0)
    df["TARGET"] = pd.to_numeric(df["TARGET"], errors="coerce").fillna(0)

    # Maintain consistent order
    order = ["PLAN VS ACTUAL", "EFFICIENCY", "LOST TIME"]
    df = pd.concat([df[df["KPI"] == k] for k in order]).reset_index(drop=True)
    return df

df = load_data()

# -----------------------------
# DASHBOARD HEADER
# -----------------------------
st.markdown("""
<div style="text-align:center; margin-bottom:20px;">
  <h1 style="font-size:45px; font-weight:800; margin-bottom:0;">Garment Production Dashboard</h1>
  <p style="font-size:17px; color:gray;">High-level KPIs and trends for quick status checks (Owner’s View)</p>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# REFRESH BUTTON
# -----------------------------
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

# -----------------------------
# KPI GAUGE CREATOR
# -----------------------------
def create_gauge(value, color):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={'suffix': "%", 'font': {'size': 28, 'color': color}},
        gauge={
            'axis': {'range': [0, 100], 'visible': False},
            'bar': {'color': color, 'thickness': 0.3},
            'bgcolor': "white",
            'borderwidth': 0,
            'steps': [{'range': [0, 100], 'color': "#f5f5f5"}],
        },
        domain={'x': [0, 1], 'y': [0, 1]},
    ))
    fig.update_layout(height=180, margin=dict(l=0, r=0, t=10, b=0))
    return fig.to_html(include_plotlyjs="cdn", full_html=False)

# -----------------------------
# KPI CARD LAYOUT
# -----------------------------
col1, col2, col3 = st.columns(3, gap="large")
kpi_colors = ["#E63946", "#FFB703", "#E63946"]
bg_colors = ["#FFEAEA", "#FFF6DA", "#FFEAEA"]

records = df.to_dict("records")

for col, rec, color, bg in zip([col1, col2, col3], records, kpi_colors, bg_colors):
    kpi = rec["KPI"]
    actual = rec["ACTUAL"]
    target = rec["TARGET"]
    variance = actual - target
    variance_text = f"+{variance:.1f}%" if variance > 0 else f"{variance:.1f}%"
    variance_color = "green" if variance > 0 else "#E63946"

    with col:
        st.markdown(
            f"""
            <div style="
                background-color:{bg};
                padding:25px;
                border-radius:20px;
                box-shadow:0 2px 6px rgba(0,0,0,0.1);
                height:400px;
                display:flex;
                flex-direction:column;
                justify-content:space-between;">
                
                <!-- TOP -->
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h4 style="margin:0; font-weight:800;">{kpi}</h4>
                    <div style="width:120px;">{create_gauge(actual, color)}</div>
                </div>

                <!-- ACTUAL -->
                <div style="text-align:left; margin-top:10px;">
                    <h2 style="font-size:48px; font-weight:800; margin:5px 0;">{actual:.1f}%</h2>
                </div>

                <hr style="border:1px solid #ddd; margin:8px 0;"/>

                <!-- TARGET & VARIANCE -->
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <p style="margin:0; font-size:16px;"><b>Target:</b> {target:.1f}%</p>
                    <p style="margin:0; font-size:16px;"><b>Variance:</b> 
                    <span style="color:{variance_color};">{variance_text}</span></p>
                </div>

                <!-- BUTTON -->
                <div style="text-align:center; margin-top:15px;">
                    <button style="
                        background-color:white;
                        color:{color};
                        border:2px solid {color};
                        padding:8px 25px;
                        border-radius:10px;
                        cursor:pointer;
                        font-weight:600;
                        font-size:15px;">Drill Down</button>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
