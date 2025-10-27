# App.py — Garment Production Dashboard (auto-update from GitHub Excel)

import math
import pandas as pd
import streamlit as st
from streamlit.components.v1 import html as st_html

st.set_page_config(page_title="Garment Production Dashboard", layout="wide")

# ============================================================
# 1️⃣ CONFIGURE YOUR GITHUB EXCEL RAW LINK HERE
# ============================================================
GITHUB_EXCEL_URL = "https://raw.githubusercontent.com/<your-username>/<your-repo>/main/garment_data.xlsx"
# Example: https://raw.githubusercontent.com/johndoe/garment-dashboard/main/garment_data.xlsx
# Make sure this is the RAW link, not the HTML page link.

# ============================================================
# 2️⃣ LOAD DATA FROM GITHUB
# ============================================================
def load_data():
    try:
        df = pd.read_excel(GITHUB_EXCEL_URL)
        st.success("✅ Live data loaded from GitHub successfully.")
    except Exception as e:
        st.warning(f"⚠️ Could not load Excel from GitHub. Using sample demo data.\nError: {e}")
        df = pd.DataFrame({
            "KPI": ["PLAN VS ACTUAL", "EFFICIENCY", "LOST TIME"],
            "value": [90, 68, 3.5],
            "target": [95, 70, 2],
            "variance": [-5, -2, 1.5],
        })
    df["KPI"] = df["KPI"].astype(str).str.upper().str.strip()
    return df

# ============================================================
# 3️⃣ DATA PROCESSING
# ============================================================
def get_kpi(df, name):
    r = df[df["KPI"] == name.upper()]
    if r.empty:
        return {"value": 0, "target": 0, "variance": 0}
    row = r.iloc[0]
    return {
        "value": float(row.get("value", 0)),
        "target": float(row.get("target", 0)),
        "variance": float(row.get("variance", 0))
    }

D = {}
data = load_data()
for k in ["PLAN VS ACTUAL", "EFFICIENCY", "LOST TIME"]:
    D[k] = get_kpi(data, k)

# ============================================================
# 4️⃣ CHART & CARD HELPERS
# ============================================================
def clamp_pct(p):
    try: return max(0.0, min(100.0, float(p)))
    except: return 0.0

def donut_svg(value_pct, ring_color, track="#EFEFEF", size=92, stroke=10, label_text=None):
    pct = clamp_pct(abs(value_pct))
    cx = cy = size // 2
    r = (size - stroke) // 2
    full = 2 * math.pi * r
    gap = 0.03 * full
    value_len = (pct / 100.0) * (full - gap)
    label = f"{value_pct:.1f}%" if label_text is None else label_text
    return f"""
    <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">
      <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{track}" stroke-width="{stroke}" stroke-linecap="round"
              stroke-dasharray="{full-gap} {gap}" transform="rotate(-90 {cx} {cy})" />
      <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{ring_color}" stroke-width="{stroke}" stroke-linecap="round"
              stroke-dasharray="{value_len} {full}" transform="rotate(-90 {cx} {cy})" />
      <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle"
            font-family="Inter, system-ui" font-size="18" font-weight="700" fill="#2F2F2F">{label}</text>
    </svg>
    """

def card_html(title, value, target, variance, bg, ring, btn):
    var_color = "#D92D20" if variance < 0 else "#05603A"
    donut_label = f"{value:.1f}%"
    return f"""
    <div class="kpi-card" style="--card-bg:{bg}; --ring-color:{ring}; --btn-color:{btn}">
      <div class="kpi-top">
        <div class="kpi-title">{title}</div>
        <div class="kpi-ring-wrap">{donut_svg(value, ring, "#EEE", 92, 10, donut_label)}</div>
      </div>
      <div class="kpi-value">{value:.1f}%</div>
      <div class="kpi-divider"></div>
      <div class="kpi-meta">
        <div><span class="label">Target:</span> <b>{target:.1f}%</b></div>
        <div><span class="label">Variance:</span> <b style="color:{var_color};">{variance:+.1f}%</b></div>
      </div>
      <div class="kpi-btn"><button>Drill Down</button></div>
    </div>
    """

# ============================================================
# 5️⃣ STYLES
# ============================================================
CSS = """
<style>
:root{
  --shadow: 0 10px 24px rgba(16,24,40,.06), 0 1px 2px rgba(16,24,40,.05);
  --radius: 16px;
  --font: Inter, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial;
}
*{box-sizing:border-box}
.kpi-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:28px;margin-top:6px}
.kpi-card{position:relative;background:var(--card-bg);border-radius:var(--radius);box-shadow:var(--shadow);padding:22px 22px 20px;min-height:270px;display:flex;flex-direction:column;justify-content:space-between}
.kpi-top{display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:6px}
.kpi-title{font-family:var(--font);font-size:16px;letter-spacing:.02em;font-weight:700;color:#3A3A3A;text-transform:uppercase}
.kpi-ring-wrap{width:92px;height:92px}
.kpi-value{font-family:var(--font);font-size:56px;font-weight:800;color:#121212;line-height:1;margin:4px 0 6px}
.kpi-divider{height:1px;width:100%;background:rgba(0,0,0,.08);margin:6px 0 10px}
.kpi-meta{display:flex;align-items:center;justify-content:space-between;font-family:var(--font);margin-bottom:10px}
.kpi-meta .label{color:#475467;font-weight:600;margin-right:6px}
.kpi-btn{display:flex;justify-content:center;margin-top:6px}
.kpi-btn button{background:#fff;color:var(--btn-color);border:2px solid var(--btn-color);font-family:var(--font);font-weight:700;font-size:16px;padding:10px 28px;border-radius:12px;box-shadow:0 1px 0 rgba(16,24,40,.05);transition:all .15s ease;cursor:pointer}
.kpi-btn button:hover{box-shadow:0 4px 10px rgba(16,24,40,.08);transform:translateY(-1px)}
.block{background:#fff;border-radius:20px;box-shadow:var(--shadow);padding:26px 28px;margin-bottom:22px}
.h-title{font-family:var(--font);font-size:46px;font-weight:800;margin:0 0 10px;color:#101828}
.h-sub{font-family:var(--font);font-size:18px;color:#475467;margin:0}
@media(max-width:1200px){.kpi-grid{grid-template-columns:1fr}.kpi-card{min-height:260px}}
</style>
"""

# ============================================================
# 6️⃣ DASHBOARD HEADER
# ============================================================
st.markdown(
    """
<div class="block">
  <div class="h-title">Garment Production Dashboard</div>
  <p class="h-sub">High-level KPIs and trends for quick status checks (Owner’s View).</p>
</div>
""",
    unsafe_allow_html=True,
)

# ============================================================
# 7️⃣ BUILD CARDS IN CORRECT ORDER
# ============================================================
pink_bg  = "#FDECEC"
red_ring = "#E63946"
amber_bg = "#FFF2CC"
amber_ring = "#F4A300"

cards_html = []
cards_html.append(card_html("PLAN VS ACTUAL", D["PLAN VS ACTUAL"]["value"], D["PLAN VS ACTUAL"]["target"], D["PLAN VS ACTUAL"]["variance"], pink_bg, red_ring, red_ring))
cards_html.append(card_html("EFFICIENCY", D["EFFICIENCY"]["value"], D["EFFICIENCY"]["target"], D["EFFICIENCY"]["variance"], amber_bg, amber_ring, amber_ring))
cards_html.append(card_html("LOST TIME", D["LOST TIME"]["value"], D["LOST TIME"]["target"], D["LOST TIME"]["variance"], pink_bg, red_ring, red_ring))

page = f"{CSS}<div class='kpi-grid'>{cards_html[0]}{cards_html[1]}{cards_html[2]}</div>"
st_html(page, height=1000, scrolling=False)
