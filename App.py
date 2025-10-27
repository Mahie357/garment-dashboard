import streamlit as st
import pandas as pd
import requests
from io import BytesIO
import plotly.graph_objects as go

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="Garment Production Dashboard", layout="wide")

GITHUB_EXCEL_URL = (
    "https://github.com/Mahie357/garment-dashboard/raw/refs/heads/main/garment_data.xlsx"
)

TITLE_HTML = """
<div style="text-align:center; margin-bottom:20px;">
  <h1 style="font-size:45px; font-weight:800; margin-bottom:0;">
    Garment Production Dashboard
  </h1>
  <p style="font-size:17px; color:gray;">
    High-level KPIs and trends for quick status checks (Owner’s View)
  </p>
</div>
"""

# -----------------------------
# DATA
# -----------------------------
@st.cache_data(ttl=60)
def load_data():
    try:
        r = requests.get(GITHUB_EXCEL_URL, timeout=20)
        r.raise_for_status()
        df = pd.read_excel(BytesIO(r.content))
    except Exception as e:
        st.warning(
            f"⚠️ Could not load Excel from GitHub. Using sample demo data. Error: {e}"
        )
        df = pd.DataFrame({
            "KPI": ["PLAN VS ACTUAL", "EFFICIENCY", "LOST TIME"],
            "Actual": [90, 68, 3.5],
            "Target": [95, 70, 2.0],
        })

    # normalize columns (remove spaces, upper-case)
    df.columns = [str(c).strip().upper() for c in df.columns]
    # keep only the columns we need if available
    need = {"KPI", "ACTUAL", "TARGET"}
    missing = need - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns in Excel: {missing}")

    # force numeric for safety
    df["ACTUAL"] = pd.to_numeric(df["ACTUAL"], errors="coerce").fillna(0.0)
    df["TARGET"] = pd.to_numeric(df["TARGET"], errors="coerce").fillna(0.0)

    # ensure 3 cards in the order we want
    order = ["PLAN VS ACTUAL", "EFFICIENCY", "LOST TIME"]
    df["KPI"] = df["KPI"].str.strip().str.upper()
    df = pd.concat([df[df["KPI"] == k] for k in order]).reset_index(drop=True)

    # if any missing, pad with zeros so layout still holds
    if len(df) < 3:
        for k in order:
            if not (df["KPI"] == k).any():
                df = pd.concat(
                    [df, pd.DataFrame([{"KPI": k, "ACTUAL": 0.0, "TARGET": 0.0}])]
                )
        df = df.reset_index(drop=True)

    return df

df = load_data()

# -----------------------------
# HEADER + REFRESH
# -----------------------------
st.markdown(TITLE_HTML, unsafe_allow_html=True)

if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

# -----------------------------
# GAUGE
# -----------------------------
def gauge_html(value, color, label):
    """Return Plotly gauge as HTML string (small, clean)."""
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
    return fig.to_html(include_plotlyjs="cdn", full_html=False)

# -----------------------------
# LAYOUT
# -----------------------------
col1, col2, col3 = st.columns(3, gap="large")
kpi_colors = ["#E63946", "#FFB703", "#E63946"]
bg_colors  = ["#FFEAEA", "#FFF6DA", "#FFEAEA"]

records = df.to_dict("records")  # safe, dict-based access

for col, rec, color, bg in zip([col1, col2, col3], records, kpi_colors, bg_colors):
    kpi     = str(rec.get("KPI", "")).upper()
    actual  = float(rec.get("ACTUAL", 0.0))
    target  = float(rec.get("TARGET", 0.0))
    variance = actual - target
    var_txt  = f"+{variance:.1f}%" if variance > 0 else f"{variance:.1f}%"
    var_col  = "green" if variance > 0 else "#E63946"

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
                
                <!-- top -->
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h4 style="margin:0; font-weight:800;">{kpi}</h4>
                    <div style="width:120px;">{gauge_html(actual, color, kpi)}</div>
                </div>

                <!-- actual -->
                <div style="text-align:left; margin-top:10px;">
                    <h2 style="font-size:48px; font-weight:800; margin:5px 0;">{actual:.1f}%</h2>
                </div>

                <hr style="border:1px solid #ddd; margin:8px 0;"/>

                <!-- target & variance -->
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <p style="margin:0; font-size:16px;"><b>Target:</b> {target:.1f}%</p>
                    <p style="margin:0; font-size:16px;"><b>Variance:</b> <span style="color:{var_col};">{var_txt}</span></p>
                </div>

                <!-- button -->
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
