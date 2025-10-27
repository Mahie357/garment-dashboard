import math
import pandas as pd
import streamlit as st
from streamlit.components.v1 import html as st_html

st.set_page_config(page_title="Garment Production Dashboard", layout="wide")

# ---------- tolerant column detection ----------
def _norm(s):
    return str(s).strip().lower().replace(" ", "").replace("_", "")

def _find_col(cols, candidates):
    cols_n = {_norm(c): c for c in cols}
    for cand in candidates:
        key = _norm(cand)
        if key in cols_n:
            return cols_n[key]
    for c in cols:
        c_n = _norm(c)
        if any(_norm(x) in c_n for x in candidates):
            return c
    return None

def read_any_excel(path="garment_data.xlsx"):
    try:
        df = pd.read_excel(path)
        if df.empty or df.columns.size == 0:
            raise ValueError("Empty sheet")
    except Exception:
        return None

    kpi_col = _find_col(df.columns, ["kpi", "metric", "name", "measure", "indicator", "category", "title"])
    val_col = _find_col(df.columns, ["value", "current", "actual", "result", "score", "percent"])
    tgt_col = _find_col(df.columns, ["target", "goal", "plan", "benchmark"])
    var_col = _find_col(df.columns, ["variance", "var", "diff", "delta", "gap"])

    if not kpi_col and df.shape[1] >= 1:
        kpi_col = df.columns[0]
    if not val_col and df.shape[1] >= 2:
        val_col = df.columns[1]
    if not tgt_col and df.shape[1] >= 3:
        tgt_col = df.columns[2]
    if not var_col and df.shape[1] >= 4:
        var_col = df.columns[3]

    try:
        df2 = df[[kpi_col, val_col, tgt_col, var_col]].copy()
        df2.columns = ["KPI", "value", "target", "variance"]
        return df2
    except Exception:
        return None

def norm_key(s: str) -> str:
    s = str(s).upper()
    return "".join(ch for ch in s if ch.isalnum())

def load_data():
    df = read_any_excel("garment_data.xlsx")
    if df is None:
        df = pd.DataFrame({
            "KPI": ["PLAN VS ACTUAL", "EFFICIENCY", "LOST TIME"],
            "value": [80, 65, 10],
            "target": [100, 70, 5],
            "variance": [-20, -5, +5],
        })
        st.info("Using demo data (couldn’t match columns in garment_data.xlsx).")

    df["KPI"] = df["KPI"].astype(str).str.strip()
    df["KEY"] = df["KPI"].apply(norm_key)

    want_titles = ["PLAN VS ACTUAL", "EFFICIENCY", "LOST TIME"]
    want_map = {t: norm_key(t) for t in want_titles}

    out = {}
    for title, key in want_map.items():
        r = df[df["KEY"] == key]
        if r.empty:
            out[title] = {"value": 0.0, "target": 0.0, "variance": 0.0}
        else:
            row = r.iloc[0]
            def f(v):
                try:
                    return float(v)
                except:
                    return 0.0
            out[title] = {
                "value": f(row["value"]),
                "target": f(row["target"]),
                "variance": f(row["variance"]),
            }
    return out

D = load_data()

# ---------- helpers ----------
def clamp_pct(p):
    try:
        return max(0.0, min(100.0, float(p)))
    except:
        return 0.0

def donut_svg(value_pct, ring_color, track="#EFEFEF", size=120, stroke=12, label_text=None):
    pct = clamp_pct(abs(value_pct))
    cx = cy = size // 2
    r = (size - stroke) // 2
    full = 2 * math.pi * r
    gap = 0.03 * full
    value_len = (pct / 100.0) * (full - gap)
    label = f"{value_pct:.0f}%" if label_text is None else label_text

    return f"""
    <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">
      <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{track}" stroke-width="{stroke}"
              stroke-dasharray="{full-gap} {gap}" transform="rotate(-90 {cx} {cy})"/>
      <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{ring_color}" stroke-width="{stroke}"
              stroke-dasharray="{value_len} {full}" transform="rotate(-90 {cx} {cy})"/>
      <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle"
            font-family="Inter, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial"
            font-size="22" font-weight="700" fill="#2F2F2F">{label}</text>
    </svg>
    """

def card_html(title, value, target, variance, bg, ring, btn, invert_bad=False):
    val_str = f"{value:.0f}%"
    donut_label = val_str
    if invert_bad:
        var_color = "#D92D20" if variance > 0 else "#05603A"
    else:
        var_color = "#D92D20" if variance < 0 else "#05603A"
    return f"""
    <div class="kpi-card" style="--card-bg:{bg}; --ring-color:{ring}; --btn-color:{btn}">
      <div class="kpi-top">
        <div class="kpi-title">{title}</div>
        <div class="kpi-ring-wrap">{donut_svg(value, ring, "#EEE", 120, 12, donut_label)}</div>
      </div>
      <div class="kpi-value">{val_str}</div>
      <div class="kpi-divider"></div>
      <div class="kpi-meta">
        <div><span class="label">Target:</span> <b>{target:.0f}%</b></div>
        <div><span class="label">Variance:</span> <b style="color:{var_color};">{variance:+.1f}%</b></div>
      </div>
      <div class="kpi-btn"><button>Drill Down</button></div>
    </div>
    """

# ---------- CSS ----------
CSS = """
<style>
:root{
  --shadow: 0 10px 24px rgba(16,24,40,.06), 0 1px 2px rgba(16,24,40,.05);
  --radius: 16px;
  --font: Inter, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial;
}
*{box-sizing:border-box}
.kpi-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:28px;margin-top:6px}
.kpi-card{
  position:relative;
  background:var(--card-bg);
  border-radius:var(--radius);
  box-shadow:var(--shadow);
  padding:18px 22px 28px;
  min-height:270px;
  display:flex;
  flex-direction:column;
  justify-content:space-between;
}
.kpi-top{
  display:flex;
  align-items:flex-start;
  justify-content:space-between;
  margin-top:-4px;
}
/* 🔧 ADJUSTMENT AREA STARTS HERE */
.kpi-title{
  font-family:var(--font);
  font-size:16px;
  letter-spacing:.02em;
  font-weight:700;
  color:#3A3A3A;
  text-transform:uppercase;
  margin-top:-8px; /* moved up slightly */
}
.kpi-ring-wrap{
  width:120px;
  height:120px;
  margin-top:6px; /* moved down slightly */
}
.kpi-value{
  font-family:var(--font);
  font-size:58px;
  font-weight:800;
  color:#121212;
  line-height:1;
  margin-top:-28px; /* moved further up */
  text-align:left;
}
/* 🔧 ADJUSTMENT AREA ENDS HERE */
.kpi-divider{
  height:1px;
  width:100%;
  background:rgba(0,0,0,.08);
  margin:4px 0 10px;
}
.kpi-meta{
  display:flex;
  align-items:center;
  justify-content:space-between;
  font-family:var(--font);
  margin-bottom:10px;
}
.kpi-meta .label{
  color:#475467;
  font-weight:600;
  margin-right:6px;
}
.kpi-btn{
  display:flex;
  justify-content:center;
  margin-top:8px;
}
.kpi-btn button{
  background:#fff;
  color:var(--btn-color);
  border:2px solid var(--btn-color);
  font-family:var(--font);
  font-weight:700;
  font-size:16px;
  padding:10px 28px;
  border-radius:12px;
  box-shadow:0 1px 0 rgba(16,24,40,.05);
  transition:all .15s ease;
  cursor:pointer;
}
.kpi-btn button:hover{
  box-shadow:0 4px 10px rgba(16,24,40,.08);
  transform:translateY(-1px);
}
.block{
  background:#fff;
  border-radius:20px;
  box-shadow:var(--shadow);
  padding:20px 28px;
  margin-bottom:18px;
}
.h-title{
  font-family:var(--font);
  font-size:46px;
  font-weight:800;
  margin:0 0 6px;
  color:#101828;
}
.h-sub{
  font-family:var(--font);
  font-size:18px;
  color:#475467;
  margin:0;
}
@media(max-width:1200px){
  .kpi-grid{grid-template-columns:1fr}
  .kpi-card{min-height:260px}
}
</style>
"""
# ---------- HEADER ----------
st.markdown("""
<style>
.header-container {
    background: linear-gradient(90deg, #8B7355 0%, #9B8265 100%); /* Elegant coffee-gold gradient */
    color: white;
    border-radius: 16px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.2);
    padding: 22px 40px;
    margin-bottom: 24px;
}
.header-title {
    font-family: 'Inter', system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial;
    font-size: 38px;
    font-weight: 800;
    letter-spacing: 0.5px;
    margin: 0;
}
.header-sub {
    font-family: 'Inter', system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial;
    font-size: 18px;
    font-weight: 400;
    opacity: 0.9;
    margin-top: 4px;
}
</style>

<div class="header-container">
    <div class="header-title">Garment Production Dashboard</div>
    <div class="header-sub">High-level KPIs and trends for quick status checks (Owner’s View)</div>
</div>
""", unsafe_allow_html=True)

# ---------- BUILD CARDS ----------
pink_bg  = "#FDECEC"
red_ring = "#E63946"
amber_bg = "#FFF2CC"
amber_ring = "#F4A300"

cards = []
cards.append(card_html("PLAN VS ACTUAL",
                       D["PLAN VS ACTUAL"]["value"],
                       D["PLAN VS ACTUAL"]["target"],
                       D["PLAN VS ACTUAL"]["variance"],
                       pink_bg, red_ring, red_ring))
cards.append(card_html("EFFICIENCY",
                       D["EFFICIENCY"]["value"],
                       D["EFFICIENCY"]["target"],
                       D["EFFICIENCY"]["variance"],
                       amber_bg, amber_ring, amber_ring))
cards.append(card_html("LOST TIME",
                       D["LOST TIME"]["value"],
                       D["LOST TIME"]["target"],
                       D["LOST TIME"]["variance"],
                       pink_bg, red_ring, red_ring,
                       invert_bad=True))

page = f"""{CSS}<div class="kpi-grid">{cards[0]}{cards[1]}{cards[2]}</div>"""
st_html(page, height=1000, scrolling=False)
