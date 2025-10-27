# App.py
import math
import pandas as pd
import streamlit as st
from streamlit.components.v1 import html as st_html

st.set_page_config(page_title="Garment Production Dashboard", layout="wide")

# ---------- data ----------
def load_data():
    try:
        df = pd.read_excel("garment_data.xlsx")
    except Exception:
        # Fallback demo data (so you can see the layout immediately)
        df = pd.DataFrame(
            {
                "KPI": ["PRODUCTIVITY", "EFFICIENCY", "VARIANCE FROM TARGET"],
                "value": [72, 68, -4],       # % numbers; last tile is negative
                "target": [75, 70, 0],       # rightmost tile target is 0% (variance)
                "variance": [-3, -2, -4],    # variance vs target, % (right tile repeats)
            }
        )
    # Normalize KPI keys
    df["KPI"] = df["KPI"].str.upper().str.strip()
    need = ["PRODUCTIVITY", "EFFICIENCY", "VARIANCE FROM TARGET"]
    out = {}
    for k in need:
        row = df[df["KPI"] == k]
        if row.empty:
            out[k] = {"value": 0, "target": 0, "variance": 0}
        else:
            r = row.iloc[0]
            out[k] = {
                "value": float(r["value"]),
                "target": float(r["target"]),
                "variance": float(r["variance"]),
            }
    return out

D = load_data()

# ---------- helpers ----------
def clamp_pct(p):
    try:
        return max(0.0, min(100.0, float(p)))
    except Exception:
        return 0.0

def donut_svg(pct: float, ring_color: str, track="#EFEFEF", size=92, stroke=10, label_text=None):
    """
    Clean crisp circular gauge with a small 'tick' gap at the top.
    Using SVG so it renders sharp on Streamlit Cloud.
    """
    pct = clamp_pct(pct)
    cx = cy = size // 2
    r = (size - stroke) // 2
    full = 2 * math.pi * r
    # tiny gap (3%) so you get a 'cut' like the reference
    gap = 0.03 * full
    value_len = (pct / 100.0) * (full - gap)

    svg = f"""
    <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" class="kpi-ring">
      <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{track}" stroke-width="{stroke}" stroke-linecap="round"
              stroke-dasharray="{full-gap} {gap}" transform="rotate(-90 {cx} {cy})" />
      <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{ring_color}" stroke-width="{stroke}" stroke-linecap="round"
              stroke-dasharray="{value_len} {full}" transform="rotate(-90 {cx} {cy})" />
      <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle"
            font-family="Inter, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, 'Apple Color Emoji', 'Segoe UI Emoji'"
            font-size="18" font-weight="700" fill="#2F2F2F">{label_text if label_text is not None else f"{int(round(pct))}%"}</text>
    </svg>
    """
    return svg

def card_html(title, value, target, variance, bg, ring, btn):
    """
    Build one KPI card matching the requested style.
    """
    # big value (left)
    val_str = f"{value:.0f}%" if title != "VARIANCE FROM TARGET" else f"{value:.0f}%"
    # donut label (inside ring)
    donut_label = val_str
    # sign color for variance
    var_color = "#D92D20" if variance < 0 else "#05603A"

    return f"""
    <div class="kpi-card" style="--card-bg:{bg}; --ring-color:{ring}; --btn-color:{btn}">
      <div class="kpi-top">
        <div class="kpi-title">{title}</div>
        <div class="kpi-ring-wrap">
            {donut_svg(abs(value), ring, "#EEE", 92, 10, donut_label)}
        </div>
      </div>

      <div class="kpi-value">{val_str}</div>

      <div class="kpi-divider"></div>

      <div class="kpi-meta">
        <div><span class="label">Target:</span> <b>{target:.0f}%</b></div>
        <div><span class="label">Variance:</span> <b style="color:{var_color};">{variance:+.0f}%</b></div>
      </div>

      <div class="kpi-btn">
        <button>Drill Down</button>
      </div>
    </div>
    """

# ---------- styles + layout ----------
CSS = """
<style>
:root{
  --shadow: 0 10px 24px rgba(16,24,40,.06), 0 1px 2px rgba(16,24,40,.05);
  --radius: 16px;
  --font: Inter, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, 'Apple Color Emoji','Segoe UI Emoji';
}
*{box-sizing:border-box}
.kpi-grid{
  display:grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 28px;
  margin-top: 6px;
}
.kpi-card{
  position:relative;
  background: var(--card-bg);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 22px 22px 20px 22px;
  min-height: 270px;
  display:flex;
  flex-direction:column;
  justify-content:space-between;
}
.kpi-top{
  display:flex;
  align-items:flex-start;
  justify-content:space-between;
  margin-bottom: 6px;
}
.kpi-title{
  font-family: var(--font);
  font-size: 16px;
  letter-spacing:.02em;
  font-weight: 700;
  color:#3A3A3A;
  text-transform: uppercase;
}
.kpi-ring-wrap{ width: 92px; height:92px; }
.kpi-ring{ display:block }

.kpi-value{
  font-family: var(--font);
  font-size: 56px;
  font-weight: 800;
  color:#121212;
  line-height:1.0;
  margin: 4px 0 6px 0;
}

.kpi-divider{
  height:1px;
  width:100%;
  background:rgba(0,0,0,.08);
  margin: 6px 0 10px 0;
}

.kpi-meta{
  display:flex;
  align-items:center;
  justify-content:space-between;
  font-family: var(--font);
  margin-bottom: 10px;
}
.kpi-meta .label{
  color:#475467;
  font-weight:600;
  margin-right:6px;
}

.kpi-btn{
  display:flex;
  justify-content:center;
  margin-top:6px;
}
.kpi-btn button{
  background:#fff;
  color: var(--btn-color);
  border:2px solid var(--btn-color);
  font-family: var(--font);
  font-weight:700;
  font-size:16px;
  padding:10px 28px;
  border-radius:12px;
  box-shadow: 0 1px 0 rgba(16,24,40,.05);
  transition: all .15s ease;
  cursor:pointer;
}
.kpi-btn button:hover{
  box-shadow: 0 4px 10px rgba(16,24,40,.08);
  transform: translateY(-1px);
}

/* Heading block styles (matches screenshot mood) */
.block{
  background:#fff;
  border-radius:20px;
  box-shadow:var(--shadow);
  padding:26px 28px;
  margin-bottom:22px;
}
.h-title{
  font-family: var(--font);
  font-size: 46px;
  font-weight: 800;
  margin:0 0 10px 0;
  color:#101828;
}
.h-sub{
  font-family: var(--font);
  font-size: 18px;
  color:#475467;
  margin:0;
}

/* responsive */
@media(max-width:1200px){
  .kpi-grid{ grid-template-columns: 1fr; }
  .kpi-card{ min-height: 260px; }
}
</style>
"""

# ---------- page ----------
st.markdown(
    """
<div class="block">
  <div class="h-title">Garment Production Dashboard</div>
  <p class="h-sub">High-level KPIs and trends for quick status checks (Owner’s View).</p>
</div>
""",
    unsafe_allow_html=True,
)

# build three cards
cards_html = []
# colors aligned with the example look
pink_bg = "#FDECEC"      # soft pink tile
red_ring = "#E63946"     # red ring
amber_bg = "#FFF2CC"     # soft warm yellow tile
amber_ring = "#F4A300"   # amber ring

cards_html.append(
    card_html(
        "PRODUCTIVITY",
        D["PRODUCTIVITY"]["value"],
        D["PRODUCTIVITY"]["target"],
        D["PRODUCTIVITY"]["variance"],
        pink_bg,
        red_ring,
        red_ring,
    )
)

cards_html.append(
    card_html(
        "EFFICIENCY",
        D["EFFICIENCY"]["value"],
        D["EFFICIENCY"]["target"],
        D["EFFICIENCY"]["variance"],
        amber_bg,
        amber_ring,
        amber_ring,
    )
)

cards_html.append(
    card_html(
        "VARIANCE FROM TARGET",
        D["VARIANCE FROM TARGET"]["value"],
        D["VARIANCE FROM TARGET"]["target"],
        D["VARIANCE FROM TARGET"]["variance"],
        pink_bg,
        red_ring,   # small red tick / ring
        red_ring,
    )
)

page = f"""
{CSS}
<div class="kpi-grid">
  {cards_html[0]}
  {cards_html[1]}
  {cards_html[2]}
</div>
"""

# Render with HTML component (no escaping)
st_html(page, height=1000, scrolling=False)
