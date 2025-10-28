# Garment Production Dashboard - Streamlit App (Final)
# Author: ChatGPT Assistant

import math
import pandas as pd
import streamlit as st

# ---------------------- Page Config ----------------------
st.set_page_config(page_title="Garment Production Dashboard", layout="wide")

# ---------------------- Data Loader ----------------------
@st.cache_data
def read_any_excel(path_or_url: str = "garment_data.xlsx"):
    try:
        df = pd.read_excel(path_or_url)
    except Exception:
        return None
    if df is None or df.empty:
        return None

    def _norm(s):
        return str(s).strip().lower().replace(" ", "").replace("_", "")

    def _find_col(cols, candidates):
        cols_n = {_norm(c): c for c in cols}
        for cand in candidates:
            key = _norm(cand)
            if key in cols_n:
                return cols_n[key]
        for c in cols:
            cn = _norm(c)
            if any(_norm(x) in cn for x in candidates):
                return c
        return None

    kpi_col = _find_col(df.columns, ["kpi", "metric", "name", "measure"])
    val_col = _find_col(df.columns, ["value", "actual", "result"])
    tgt_col = _find_col(df.columns, ["target", "goal", "plan"])
    var_col = _find_col(df.columns, ["variance", "var", "diff"])

    if not kpi_col and df.shape[1] >= 1: kpi_col = df.columns[0]
    if not val_col and df.shape[1] >= 2: val_col = df.columns[1]
    if not tgt_col and df.shape[1] >= 3: tgt_col = df.columns[2]
    if not var_col and df.shape[1] >= 4: var_col = df.columns[3]

    try:
        out = df[[kpi_col, val_col, tgt_col, var_col]].copy()
        out.columns = ["KPI", "value", "target", "variance"]
        return out
    except Exception:
        return None


def load_kpis():
    df = read_any_excel("garment_data.xlsx")

    if df is None:
        df = pd.DataFrame({
            "KPI": ["PLAN VS ACTUAL", "EFFICIENCY", "LOST TIME"],
            "value": [80, 65, 10],
            "target": [100, 70, 5],
            "variance": [-20, -5, +5],
        })
        st.info("Using demo data (couldn’t read garment_data.xlsx).")

    df["KPI"] = df["KPI"].astype(str).str.upper().str.strip()
    wanted = ["PLAN VS ACTUAL", "EFFICIENCY", "LOST TIME"]
    data = {}
    for k in wanted:
        r = df[df["KPI"].str.contains(k, na=False)]
        if r.empty:
            data[k] = {"value": 0.0, "target": 0.0, "variance": 0.0}
        else:
            row = r.iloc[0]
            f = lambda v: float(v) if pd.notna(v) else 0.0
            data[k] = {"value": f(row["value"]), "target": f(row["target"]), "variance": f(row["variance"])}
    return data, df


# ---------------------- Donut Chart ----------------------
def donut_svg(value_pct, ring_color, track="#EFEFEF", size=110, stroke=12):
    pct = max(0, min(100, value_pct))
    cx = cy = size // 2
    r = (size - stroke) // 2
    full = 2 * math.pi * r
    gap = 0.03 * full
    val = (pct / 100.0) * (full - gap)
    return f"""
    <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">
      <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{track}" stroke-width="{stroke}"
              stroke-dasharray="{full-gap} {gap}" transform="rotate(-90 {cx} {cy})" />
      <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{ring_color}" stroke-width="{stroke}"
              stroke-dasharray="{val} {full}" transform="rotate(-90 {cx} {cy})" />
      <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle"
            font-size="20" font-weight="700" fill="#2F2F2F">{value_pct:.0f}%</text>
    </svg>
    """


# ---------------------- CSS ----------------------
st.markdown("""
<style>
:root {--font: 'Inter', sans-serif;}
body {font-family: var(--font);}
.header-pill {
  background: #8b7355;
  padding: 28px 40px;
  border-radius: 18px;
  color: white;
  box-shadow: 0 8px 18px rgba(0,0,0,0.2);
  margin-bottom: 30px;
}
.header-title {font-size: 38px; font-weight: 800; margin: 0;}
.header-sub {font-size: 18px; margin-top: 4px; opacity: 0.9;}

.kpi-grid {display: grid; grid-template-columns: repeat(3,1fr); gap: 24px;}
.kpi-card {background: var(--bg); border-radius: 18px; box-shadow: 0 6px 14px rgba(0,0,0,.08);
  padding: 20px 22px; display:flex; flex-direction:column;}
.kpi-title {font-weight: 700; color: #333; margin-bottom: 8px;}
.kpi-ring {align-self: flex-end; margin-top: -60px;}
.kpi-value {font-size: 56px; font-weight: 800; margin-top: -30px;}
.kpi-meta {display:flex; justify-content:space-between; margin-top: 6px; font-size: 15px;}
div.stButton > button {
  border: 2px solid #333 !important; background: white !important; color: #333 !important;
  font-weight: 700 !important; border-radius: 10px !important; padding: 8px 24px !important;
}
</style>
""", unsafe_allow_html=True)


# ---------------------- Header ----------------------
def header():
    st.markdown(
        """
        <div class="header-pill">
            <div class="header-title">Garment Production Dashboard</div>
            <div class="header-sub">High-level KPIs and trends for quick status checks (Owner’s View)</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ---------------------- KPI Card ----------------------
def card(title, value, target, variance, bg, ring, route_key):
    st.markdown(f"""
    <div class="kpi-card" style="--bg:{bg};">
        <div class="kpi-title">{title}</div>
        <div class="kpi-ring">{donut_svg(value, ring)}</div>
        <div class="kpi-value">{value:.0f}%</div>
        <div class="kpi-meta">
            <div><b>Target:</b> {target:.0f}%</div>
            <div><b>Variance:</b> {variance:+.0f}%</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Drill Down", key=f"dd_{route_key}"):
        st.session_state["view"] = route_key
        st.rerun()


# ---------------------- Dashboard ----------------------
def show_dashboard():
    data, _ = load_kpis()
    header()
    st.markdown('<div class="kpi-grid">', unsafe_allow_html=True)
    with st.container():
        card("PLAN VS ACTUAL", data["PLAN VS ACTUAL"]["value"], data["PLAN VS ACTUAL"]["target"],
             data["PLAN VS ACTUAL"]["variance"], "#FDECEC", "#E63946", "PlanVsActual")
    with st.container():
        card("EFFICIENCY", data["EFFICIENCY"]["value"], data["EFFICIENCY"]["target"],
             data["EFFICIENCY"]["variance"], "#FFF2CC", "#F4A300", "Efficiency")
    with st.container():
        card("LOST TIME", data["LOST TIME"]["value"], data["LOST TIME"]["target"],
             data["LOST TIME"]["variance"], "#FDECEC", "#E63946", "LostTime")
    st.markdown('</div>', unsafe_allow_html=True)


# ---------------------- Drill Down Pages ----------------------
def show_detail(kind):
    st.button("← Back to Dashboard", on_click=lambda: st.session_state.update({"view": "Dashboard"}) or st.rerun())
    if kind == "PlanVsActual":
        st.header("Plan vs Actual Analysis")
        st.dataframe(pd.DataFrame({
            "Line": ["Line 1", "Line 2", "Line 3"],
            "Variance": ["-2%", "-1%", "+3%"],
            "Observed Cause": ["Training Gaps", "Fabric Quality Issues", "Good Performance"],
            "Category": ["Manpower", "Material", "None"],
            "Action": ["Analyze & Action", "Analyze & Action", "No Action Needed"],
        }), use_container_width=True)
    elif kind == "Efficiency":
        st.header("Efficiency Analysis")
        st.dataframe(pd.DataFrame({
            "Line": ["Line 4", "Line 5", "Line 6"],
            "Variance": ["-2%", "-1%", "+3%"],
            "Observed Cause": ["Training Gaps", "Fabric Quality Issues", "Good performance"],
            "Category": ["Manpower", "Material", "None"],
            "Action": ["Analyze & Action", "Analyze & Action", "No action needed"],
        }), use_container_width=True)
    else:
        st.header("Lost Time Analysis")
        st.dataframe(pd.DataFrame({
            "Line": ["Line 7", "Line 8", "Line 9"],
            "Variance": ["+1%", "+3%", "-2%"],
            "Observed Cause": ["Machine breakdown", "Material delay", "Absent operator"],
            "Category": ["Machine", "Material", "Manpower"],
            "Action": ["Analyze & Action", "Analyze & Action", "Analyze & Action"],
        }), use_container_width=True)


# ---------------------- Routing ----------------------
if "view" not in st.session_state:
    st.session_state["view"] = "Dashboard"

if st.session_state["view"] == "Dashboard":
    show_dashboard()
else:
    show_detail(st.session_state["view"])
