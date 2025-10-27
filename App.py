import streamlit as st
import pandas as pd
import requests
from io import BytesIO
import plotly.graph_objects as go

# -----------------------------
# CONFIGURATION
# -----------------------------
st.set_page_config(page_title="Garment Production Dashboard", layout="wide")

# ✅ Replace with your GitHub Excel URL
GITHUB_EXCEL_URL = "https://github.com/Mahie357/garment-dashboard/raw/refs/heads/main/garment_data.xlsx"

# -----------------------------
# DATA LOADING FUNCTION
# -----------------------------
@st.cache_data(ttl=60)
def load_data():
    try:
        response = requests.get(GITHUB_EXCEL_URL)
        response.raise_for_status()
        return pd.read_excel(BytesIO(response.content))
    except Exception as e:
        st.warning(f"⚠️ Could not load Excel from GitHub. Using sample demo data. Error: {e}")
        return pd.DataFrame({
            'KPI': ['PLAN VS ACTUAL', 'EFFICIENCY', 'LOST TIME'],
            'Actual': [90, 68, 3.5],
            'Target': [95, 70, 2.0]
        })

df = load_data()

# -----------------------------
# PAGE TITLE
# -----------------------------
st.markdown(
    """
    <div style="text-align:center; margin-bottom:20px;">
        <h1 style="font-size:45px; font-weight:800; margin-bottom:0;">Garment Production Dashboard</h1>
        <p style="font-size:17px; color:gray;">High-level KPIs and trends for quick status checks (Owner’s View)</p>
    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# REFRESH DATA BUTTON
# -----------------------------
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

# -----------------------------
# KPI GAUGE CREATOR
# -----------------------------
def create_gauge_chart(value, color, label):
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
        title={'text': label, 'font': {'size': 16}}
    ))
    fig.update_layout(height=180, margin=dict(l=0, r=0, t=20, b=0))
    return fig

# -----------------------------
# KPI CARD LAYOUT
# -----------------------------
col1, col2, col3 = st.columns(3, gap="large")

# Assign colors for KPI cards
kpi_colors = ["#E63946", "#FFB703", "#E63946"]
background_colors = ["#FFEAEA", "#FFF6DA", "#FFEAEA"]

# Loop through 3 KPIs
for col, row, color, bg in zip([col1, col2, col3], df.itertuples(), kpi_colors, background_colors):
    with col:
        kpi = row.KPI.upper()
        actual = float(row.Actual)
        target = float(row.Target)
        variance = actual - target
        variance_text = f"+{variance:.1f}%" if variance > 0 else f"{variance:.1f}%"
        variance_color = "green" if variance > 0 else "#E63946"

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
                
                <!-- TOP SECTION -->
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h4 style="margin:0; font-weight:800;">{kpi}</h4>
                    <div style="width:120px;">{create_gauge_chart(actual, color, kpi).to_html(include_plotlyjs='cdn', full_html=False)}</div>
                </div>

                <!-- ACTUAL VALUE -->
                <div style="text-align:left; margin-top:10px;">
                    <h2 style="font-size:48px; font-weight:800; margin:5px 0;">{actual:.1f}%</h2>
                </div>

                <hr style="border:1px solid #ddd; margin:8px 0;"/>

                <!-- TARGET & VARIANCE -->
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <p style="margin:0; font-size:16px;"><b>Target:</b> {target:.1f}%</p>
                    <p style="margin:0; font-size:16px;"><b>Variance:</b> <span style="color:{variance_color};">{variance_text}</span></p>
                </div>

                <!-- DRILL DOWN BUTTON -->
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
