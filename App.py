import streamlit as st
import pandas as pd
import requests
from io import BytesIO
from streamlit.components.v1 import html

st.set_page_config(page_title="Garment Production Dashboard", layout="wide")

# ---- GitHub Excel (raw) ----
EXCEL_URL = "https://github.com/Mahie357/garment-dashboard/raw/refs/heads/main/garment_data.xlsx"


# -----------------------------
# Data loader
# -----------------------------
@st.cache_data(ttl=60)
def load_data_from_github():
    try:
        r = requests.get(EXCEL_URL, timeout=20)
        r.raise_for_status()
        df = pd.read_excel(BytesIO(r.content))
    except Exception as e:
        st.error(f"Could not load Excel from GitHub. Using sample data. Error: {e}")
        df = pd.DataFrame(
            {
                "KPI": ["PLAN VS ACTUAL", "EFFICIENCY", "LOST TIME"],
                "ACTUAL": [90, 68, 3.5],
                "TARGET": [95, 70, 2],
            }
        )

    # Normalize columns
    df.columns = df.columns.str.strip().str.upper()
    for col in ["KPI", "ACTUAL", "TARGET"]:
        if col not in df.columns:
            df[col] = 0

    df["KPI"] = df["KPI"].astype(str).str.upper().str.strip()
    df["ACTUAL"] = pd.to_numeric(df["ACTUAL"], errors="coerce").fillna(0)
    df["TARGET"] = pd.to_numeric(df["TARGET"], errors="coerce").fillna(0)

    # Ensure all three KPIs exist in the right order
    wanted = ["PLAN VS ACTUAL", "EFFICIENCY", "LOST TIME"]
    rows = []
    for w in wanted:
        m = df[df["KPI"] == w]
        if m.empty:
            rows.append(pd.Series({"KPI": w, "ACTUAL": 0.0, "TARGET": 0.0}))
        else:
            rows.append(m.iloc[0])
    df2 = pd.DataFrame(rows)
    return df2


df = load_data_from_github()

# -----------------------------
# Header
# -----------------------------
st.markdown(
    """
<div style="text-align:center; margin: 8px 0 24px;">
  <h1 style="font-size:42px; font-weight:800; margin:0;">Garment Production Dashboard</h1>
  <p style="font-size:17px; color:gray; margin:6px 0 0;">
    High-level KPIs and trends for quick status checks (Owner’s View)
  </p>
</div>
""",
    unsafe_allow_html=True,
)

if st.button("🔄 Refresh Data", type="secondary"):
    st.cache_data.clear()
    st.rerun()


# -----------------------------
# HTML card renderer
# -----------------------------
def kpi_card_html(
    title: str,
    actual: float,
    target: float,
    bg="#FFEAEA",
    accent="#E63946",
    ring_track="#EDEDED",
) -> str:
    """
    Build a self-contained KPI card with a small donut gauge at top-right,
    big % number, target + variance line, and a button.
    The donut is SVG so it never escapes the card.
    """
    # donut math
    # small full donut (starts at top)
    r = 24
    circumference = 2 * 3.1415926535 * r
    pct = max(0.0, min(100.0, float(actual)))
    dash = circumference * (pct / 100.0)
    gap = circumference - dash

    variance = actual - target
    variance_txt = f"+{variance:.1f}%" if variance > 0 else f"{variance:.1f}%"
    variance_color = "#2E7D32" if variance > 0 else "#E63946"

    # card HTML/CSS
    return f"""
<style>
.kpi-card {{
  background:{bg};
  border-radius:20px;
  padding:22px;
  box-shadow:0 2px 8px rgba(0,0,0,.08);
  height: 360px;
  display:flex;
  flex-direction:column;
}}
.kpi-top {{
  display:flex; justify-content:space-between; align-items:flex-start;
}}
.kpi-title {{
  margin:0; font-weight:800; font-size:22px;
}}
.g-wrap {{
  width:72px; height:72px; position:relative;
}}
.g-label {{
  position:absolute; inset:0; display:flex; align-items:center; justify-content:center;
  font-size:13px; font-weight:700; color:#444;
}}
hr.kpi-line {{
  border:none; height:1px; background:#e1e1e1; margin:8px 0 10px;
}}
.kpi-primary {{
  font-size:46px; font-weight:800; margin:6px 0 2px;
}}
.kpi-meta {{
  display:flex; justify-content:space-between; align-items:center;
  font-size:16px;
}}
.kpi-btn {{
  background:white;
  border:2px solid {accent};
  color:{accent};
  padding:8px 22px;
  border-radius:10px;
  font-weight:700;
  cursor:pointer;
}}
</style>

<div class="kpi-card">
  <div class="kpi-top">
    <h4 class="kpi-title">{title}</h4>

    <!-- small donut -->
    <div class="g-wrap">
      <svg viewBox="0 0 60 60" width="72" height="72" style="transform:rotate(-90deg)">
        <circle cx="30" cy="30" r="{r}" fill="none" stroke="{ring_track}" stroke-width="8"/>
        <circle cx="30" cy="30" r="{r}" fill="none" stroke="{accent}"
                stroke-width="8" stroke-linecap="round"
                stroke-dasharray="{dash:.2f} {gap:.2f}" />
      </svg>
      <div class="g-label">{actual:.1f}%</div>
    </div>
  </div>

  <div style="flex:1;"></div>

  <div>
    <div class="kpi-primary">{actual:.1f}%</div>
    <hr class="kpi-line" />
    <div class="kpi-meta">
      <div><b>Target:</b> {target:.1f}%</div>
      <div><b>Variance:</b> <span style="color:{variance_color};">{variance_txt}</span></div>
    </div>
    <div style="text-align:center; margin-top:14px;">
      <button class="kpi-btn">Drill Down</button>
    </div>
  </div>
</div>
"""


# -----------------------------
# Map KPIs to colors & render
# -----------------------------
# desired order
order = ["PLAN VS ACTUAL", "EFFICIENCY", "LOST TIME"]
bg_colors  = ["#FFEAEA", "#FFF6DA", "#FFEAEA"]
accents    = ["#E63946", "#FFB703", "#E63946"]

cols = st.columns(3)

for col, kpi_name, bg, acc in zip(cols, order, bg_colors, accents):
    row = df[df["KPI"] == kpi_name].iloc[0]
    actual = float(row["ACTUAL"])
    target = float(row["TARGET"])

    # nice titles
    title = kpi_name.title()

    with col:
        card = kpi_card_html(title, actual, target, bg=bg, accent=acc)
        html(card, height=390)  # one self-contained card
