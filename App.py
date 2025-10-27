import streamlit as st
import pandas as pd
import requests
from io import BytesIO
import plotly.graph_objects as go

# -------------------------------------
# PAGE CONFIG
# -------------------------------------
st.set_page_config(page_title="Garment Production Dashboard", layout="wide")

# GitHub Excel link
GITHUB_EXCEL_URL = "https://github.com/Mahie357/garment-dashboard/raw/refs/heads/main/garment_data.xlsx"

# -------------------------------------
# LOAD DATA FUNCTION
# -------------------------------------
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

    # Normalize column names
    df.columns = [c.strip().upper() for c in df.columns]
    required = {"KPI", "ACTUAL", "TARGET"}
    if not required.issubset(df.columns):
        raise ValueError(f"Missing columns in Excel. Found: {list(df.columns)}")

    # Clean and uppercase values
    df["KPI"] = df["KPI"].astype(str).str.strip().str.upper()
    df["ACTUAL"] = pd.to_numeric(df["ACTUAL"], errors="coerce").fillna(0)
    df["TARGET"] = pd.to_numeric(df["TARGET"], errors="coerce").fillna(0)

    # Ensure order even if Excel order differs
    order = ["PLAN VS ACTUAL", "EFFICIENCY", "LOST TIME"]
    data_ordered = []
    for k in order:
        subset = df[df["KPI"].str.upper() == k]
        if not subset.empty:
            data_ordered.append(subset)
        else:
            # Fill missing KPI with placeholder if absent
            data_ordered.append(pd.DataFrame({
                "KPI": [k], "ACTUAL": [0], "TARGET": [0]
            }))
    return pd.concat(data_ordered).reset_index(drop=True)

df = load_data()

# -------------------------------------
# HEADER SECTION
# -------------------------------------
st.markdown("""
<div style="text-align:center; margin-bottom:20px;">
  <h1 style="font-size:45px; font-weight:800; margin-bottom:0;">Garment Production Dashboard</h1>
  <p style="font-size:17px; color:gray;">High-level KPIs and trends for quick status checks (Owner’s View)</p>
</div>
""", unsafe_allow_html=True)

# -------------------------------------
# REFRESH BUTTON
# -------------------------------------
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

# -------------------------------------
# GAUGE CHART FUNCTION
# -------------------------------------
def gauge_chart(value, color):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={'suffix': "%", 'font': {'size': 26, 'color': color}},
        gauge={
            'axis': {'range': [0, 100], 'visible': False},
            'bar': {'color': color, 'thickness': 0.3},
            'bgcolor': "white",
            'steps': [{'range': [0, 100], 'color': "#f0f0f0"}],
        }
    ))
    fig.update_layout(height=150, margin=dict(l=0, r=0, t=0, b=0))
    return fig

# -------------------------------------
# KPI CARDS
# -------------------------------------
col1, col2, col3 = st.columns(3)
bg_colors = ["#FFEAEA", "#FFF6DA", "#FFEAEA"]
ring_colors = ["#E63946", "#FFB703", "#E63946"]

for col, rec, bg, color in zip([col1, col2, col3], df.to_dict("records"), bg_colors, ring_colors):
    kpi = rec["KPI"].title()
    actual = rec["ACTUAL"]
    target = rec["TARGET"]
    variance = actual - target
    variance_text = f"+{variance:.1f}%" if variance > 0 else f"{variance:.1f}%"
    variance_color = "green" if variance > 0 else "#E63946"

    with col:
        with st.container():
            st.markdown(
                f"""
                <div style="
                    background-color:{bg};
                    padding:25px;
                    border-radius:20px;
                    box-shadow:0 2px 6px rgba(0,0,0,0.1);
                    height:410px;
                    display:flex;
                    flex-direction:column;
                    justify-content:space-between;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <h4 style="margin:0; font-weight:800;">{kpi}</h4>
                    </div>
                """,
                unsafe_allow_html=True
            )

            # Add gauge chart inside card
            st.plotly_chart(gauge_chart(actual, color), use_container_width=True)

            st.markdown(
                f"""
                <div style="text-align:left;">
                    <h2 style="font-size:48px; font-weight:800; margin:5px 0;">{actual:.1f}%</h2>
                </div>
                <hr style="border:1px solid #ddd; margin:8px 0;"/>
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <p style="margin:0; font-size:16px;"><b>Target:</b> {target:.1f}%</p>
                    <p style="margin:0; font-size:16px;"><b>Variance:</b>
                    <span style="color:{variance_color};">{variance_text}</span></p>
                </div>
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
