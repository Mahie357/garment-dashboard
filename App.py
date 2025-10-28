import math
import pandas as pd
import streamlit as st
from streamlit.components.v1 import html as st_html

st.set_page_config(page_title="Garment Production Dashboard", layout="wide")

# ---------- DATA LOADING ----------
def read_excel_data(path="garment_data.xlsx"):
    try:
        df = pd.read_excel(path)
        if df.empty:
            raise ValueError
        return df
    except Exception:
        st.warning("Using demo data (garment_data.xlsx not found or unreadable).")
        return pd.DataFrame({
            "KPI": ["PLAN VS ACTUAL", "EFFICIENCY", "LOST TIME"],
            "value": [80, 65, 10],
            "target": [100, 70, 5],
            "variance": [-20, -5, +5],
        })

D = read_excel_data()

# ---------- BASIC HELPERS ----------
def clamp_pct(p):
    try:
        return max(0.0, min(100.0, float(p)))
    except:
        return 0.0

def donut_svg(value_pct, ring_color, track="#EFEFEF", size=120, stroke=12):
    pct = clamp_pct(abs(value_pct))
    cx = cy = size // 2
    r = (size - stroke) // 2
    full = 2 * math.pi * r
    gap = 0.03 * full
    value_len = (pct / 100.0) * (full - gap)

    label = f"{value_pct:.0f}%"
    return f"""
    <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">
      <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{track}" stroke-width="{stroke}"
              stroke-dasharray="{full-gap} {gap}" transform="rotate(-90 {cx} {cy})"/>
      <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{ring_color}" stroke-width="{stroke}"
              stroke-dasharray="{value_len} {full}" transform="rotate(-90 {cx} {cy})"/>
      <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle"
            font-family="Inter" font-size="22" font-weight="700" fill="#2F2F2F">{label}</text>
    </svg>
    """

# ---------- MAIN DASHBOARD ----------
def show_dashboard():
    st.markdown("""
    <style>
    .header-container {
        background: linear-gradient(90deg, #8B7355 0%, #9B8265 100%);
        color: white;
        border-radius: 16px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.2);
        padding: 22px 40px;
        margin-bottom: 24px;
    }
    .header-title {
        font-size: 38px; font-weight: 800; margin: 0;
    }
    .header-sub {
        font-size: 18px; opacity: 0.9; margin-top: 4px;
    }
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 28px;
    }
    .kpi-card {
        background: var(--card-bg);
        border-radius: 16px;
        box-shadow: 0 8px 18px rgba(0,0,0,0.05);
        padding: 24px 24px 30px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .kpi-top {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
    }
    .kpi-title {
        font-size: 16px;
        font-weight: 700;
        color: #3A3A3A;
        text-transform: uppercase;
        margin-top: -8px;
    }
    .kpi-ring-wrap {
        width: 120px;
        height: 120px;
        margin-top: 8px;
    }
    .kpi-value {
        font-size: 58px;
        font-weight: 800;
        color: #121212;
        margin-top: -20px;
    }
    .kpi-meta {
        display: flex;
        justify-content: space-between;
        font-size: 16px;
        margin-top: 8px;
    }
    .kpi-btn {
        text-align: center;
        margin-top: 12px;
    }
    .drill-btn {
        background: #fff;
        border: 2px solid var(--btn-color);
        color: var(--btn-color);
        font-weight: 700;
        font-size: 16px;
        padding: 10px 28px;
        border-radius: 10px;
        cursor: pointer;
        transition: 0.2s ease;
    }
    .drill-btn:hover {
        background: var(--btn-color);
        color: white;
    }
    </style>
    <div class="header-container">
        <div class="header-title">Garment Production Dashboard</div>
        <div class="header-sub">High-level KPIs and trends for quick status checks (Owner’s View)</div>
    </div>
    """, unsafe_allow_html=True)

    pink_bg = "#FDECEC"
    red_ring = "#E63946"
    amber_bg = "#FFF2CC"
    amber_ring = "#F4A300"

    col1, col2, col3 = st.columns(3, gap="large")

    with col1:
        card("PLAN VS ACTUAL", 80, 100, -20, pink_bg, red_ring, "PlanVsActual")
    with col2:
        card("EFFICIENCY", 65, 70, -5, amber_bg, amber_ring, "Efficiency")
    with col3:
        card("LOST TIME", 10, 5, +5, pink_bg, red_ring, "LostTime", invert_bad=True)

# ---------- CARD FUNCTION (FIXED BUTTON POSITION) ----------
def card(title, value, target, variance, bg, ring, key, invert_bad=False):
    var_color = "#D92D20" if (variance > 0 and invert_bad) or (variance < 0 and not invert_bad) else "#05603A"

    button_html = f"""
    <form action="" method="get">
        <button name="clicked" value="{key}" class="drill-btn">Drill Down</button>
    </form>
    """

    st.markdown(f"""
    <div class="kpi-card" style="--card-bg:{bg}; --btn-color:{ring};">
      <div class="kpi-top">
        <div class="kpi-title">{title}</div>
        <div class="kpi-ring-wrap">{donut_svg(value, ring)}</div>
      </div>
      <div class="kpi-value">{value:.0f}%</div>
      <div class="kpi-meta">
        <div><b>Target:</b> {target:.0f}%</div>
        <div><b>Variance:</b> <span style="color:{var_color};">{variance:+.1f}%</span></div>
      </div>
      <div class="kpi-btn">{button_html}</div>
    </div>
    """, unsafe_allow_html=True)

    # Detect which "Drill Down" was clicked
    if "clicked" in st.query_params and st.query_params["clicked"] == key:
        st.session_state["view"] = key
        st.experimental_rerun()

# ---------- DETAIL PAGES ----------
def show_detail_page(title, key):
    st.markdown(f"""
    <style>
    .detail-header {{
        background: #F9FAFB;
        border-radius: 14px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        padding: 22px 30px;
        margin-bottom: 20px;
    }}
    .detail-header h2 {{
        margin: 0;
        font-size: 32px;
        font-weight: 800;
        color: #101828;
    }}
    .detail-sub {{
        color: #475467;
        font-size: 17px;
    }}
    </style>
    """, unsafe_allow_html=True)

    if st.button("← Back to Dashboard"):
        st.session_state["view"] = "dashboard"

    st.markdown(f"""
    <div class="detail-header">
        <h2>{title} Analysis</h2>
        <p class="detail-sub">Line-level variance and specific root causes (Supervisor’s View).</p>
    </div>
    """, unsafe_allow_html=True)

    detail_df = pd.DataFrame({
        "Line": ["Line 1", "Line 2", "Line 3"],
        "Variance": ["-2%", "-1%", "+3%"],
        "Observed Cause": ["Training Gaps", "Fabric Quality Issues", "Good Performance"],
        "Category": ["Manpower", "Material", "None"],
        "Action": ["Analyze & Action", "Analyze & Action", "No Action Needed"],
    })

    st.dataframe(detail_df, use_container_width=True)

# ---------- NAVIGATION CONTROL ----------
if "view" not in st.session_state:
    st.session_state["view"] = "dashboard"

if st.session_state["view"] == "dashboard":
    show_dashboard()
elif st.session_state["view"] == "PlanVsActual":
    show_detail_page("Plan vs Actual", "PlanVsActual")
elif st.session_state["view"] == "Efficiency":
    show_detail_page("Efficiency", "Efficiency")
elif st.session_state["view"] == "LostTime":
    show_detail_page("Lost Time", "LostTime")
