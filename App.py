# App.py — dashboard + drill-down views (Streamlit ≥ 1.30)

import math
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Garment Production Dashboard", layout="wide")

# ----------------------- Data loading -----------------------
@st.cache_data
def read_any_excel(path_or_url: str = "garment_data.xlsx"):
    """Tolerant reader that tries to find KPI/Value/Target/Variance columns."""
    try:
        df = pd.read_excel(path_or_url)
    except Exception:
        # If Excel isn't available / GitHub link wrong, give None to trigger demo
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
        # fuzzy contains
        for c in cols:
            cn = _norm(c)
            if any(_norm(x) in cn for x in candidates):
                return c
        return None

    kpi_col = _find_col(df.columns, ["kpi", "metric", "name", "measure", "indicator", "title", "category"])
    val_col = _find_col(df.columns, ["value", "current", "actual", "result", "score", "percent"])
    tgt_col = _find_col(df.columns, ["target", "goal", "plan", "benchmark"])
    var_col = _find_col(df.columns, ["variance", "var", "diff", "delta", "gap"])

    # fallbacks by position
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
        # Demo fallback so the UI still renders
        df = pd.DataFrame(
            {
                "KPI": ["PLAN VS ACTUAL", "EFFICIENCY", "LOST TIME"],
                "value": [80, 65, 10],
                "target": [100, 70, 5],
                "variance": [-20, -5, +5],
            }
        )
        st.info("Using demo data (couldn’t read garment_data.xlsx).")

    df["KPI"] = df["KPI"].astype(str).str.upper().str.strip()

    # normalize keys we need on the dashboard
    wanted = ["PLAN VS ACTUAL", "EFFICIENCY", "LOST TIME"]
    data = {}
    for k in wanted:
        r = df[df["KPI"] == k]
        if r.empty:
            r = df[df["KPI"].str.contains(k, na=False)]
        if r.empty:
            data[k] = {"value": 0.0, "target": 0.0, "variance": 0.0}
        else:
            row = r.iloc[0]
            def f(v):
                try:
                    return float(v)
                except:
                    return 0.0
            data[k] = {"value": f(row["value"]), "target": f(row["target"]), "variance": f(row["variance"])}
    return data, df  # dict for cards, full df for detail pages


# ----------------------- UI helpers -----------------------
def clamp_pct(p):
    try:
        return max(0.0, min(100.0, float(p)))
    except:
        return 0.0


def donut_svg(value_pct, ring_color, track="#EFEFEF", size=110, stroke=12, label_text=None):
    """
    Slightly larger donut so it’s noticeable; label is the value shown in the middle.
    """
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
              stroke-linecap="round" stroke-dasharray="{full-gap} {gap}" transform="rotate(-90 {cx} {cy})" />
      <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{ring_color}" stroke-width="{stroke}"
              stroke-linecap="round" stroke-dasharray="{value_len} {full}" transform="rotate(-90 {cx} {cy})" />
      <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle"
            font-family="Inter, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial"
            font-size="20" font-weight="700" fill="#2F2F2F">{label}</text>
    </svg>
    """


def card(title, value, target, variance, bg, ring, route_key, btn_color):
    """
    One KPI tile. The Drill Down button sets a route in session_state and reruns the app.
    The button stays at the same place; we don’t move it with absolute positioning.
    """
    val_str = f"{value:.0f}%"
    var_color = "#D92D20" if variance < 0 else "#05603A"

    # We keep the donut a bit lower, and the big value a bit higher (visual balance)
    html = f"""
    <div class="kpi-card" style="--card-bg:{bg}; --ring-color:{ring}; --btn-color:{btn_color}">
      <div class="kpi-top">
        <div class="kpi-title">{title}</div>
        <div class="kpi-ring-wrap">{donut_svg(value, ring, "#EEE", size=110, stroke=12, label_text=val_str)}</div>
      </div>
      <div class="kpi-value">{val_str}</div>
      <div class="kpi-divider"></div>
      <div class="kpi-meta">
        <div><span class="label">Target:</span> <b>{target:.0f}%</b></div>
        <div><span class="label">Variance:</span> <b style="color:{var_color};">{variance:+.0f}%</b></div>
      </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

    # Button placed right under the card content (same position as before)
    if st.button("Drill Down", key=f"dd_{route_key}", use_container_width=False):
        st.session_state["view"] = route_key
        st.rerun()  # <- modern API (replaces experimental_rerun)


# ----------------------- Styles -----------------------
CSS = """
<style>
:root{
  --shadow: 0 10px 24px rgba(16,24,40,.06), 0 1px 2px rgba(16,24,40,.05);
  --radius: 16px;
  --font: Inter, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial;
}
*{box-sizing:border-box}
body{font-family:var(--font)}
/* Header pill */
.header-pill{
  background:#8b7355;
  padding:32px 40px;
  border-radius:24px;
  color:#fff;
  box-shadow: 0 12px 28px rgba(0,0,0,.10), inset 0 -2px 0 rgba(255,255,255,.08);
  margin: 24px 0 14px;
}
.header-title{font-size:44px;font-weight:800;margin:0 0 8px}
.header-sub{font-size:18px;opacity:.95;margin:0}

/* Cards grid */
.kpi-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:28px;margin-top:6px}
.kpi-card{position:relative;background:var(--card-bg);border-radius:var(--radius);box-shadow:var(--shadow);
          padding:22px 22px 16px;min-height:260px;display:flex;flex-direction:column;justify-content:flex-start}
.kpi-top{display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:2px}
.kpi-title{font-family:var(--font);font-size:16px;letter-spacing:.02em;font-weight:700;color:#3A3A3A;text-transform:uppercase}
.kpi-ring-wrap{width:110px;height:110px; margin-top:4px;}  /* donut slightly lower */
.kpi-value{font-family:var(--font);font-size:58px;font-weight:800;color:#121212;line-height:1;margin:0 0 10px}
.kpi-divider{height:1px;width:100%;background:rgba(0,0,0,.08);margin:4px 0 10px}
.kpi-meta{display:flex;align-items:center;justify-content:space-between;font-family:var(--font);margin-bottom:6px}
.kpi-meta .label{color:#475467;font-weight:600;margin-right:6px}

/* Drill Down button styling (uses Streamlit button but keep visual spacing) */
div.stButton > button[kind="secondary"] { /* in case */
  border-radius:12px !important;
}
div.stButton > button {
  background:#fff !important;
  color:#1f2937 !important;
  border:2px solid #1f2937 !important;
  font-weight:700 !important;
  padding:10px 26px !important;
  border-radius:12px !important;
  box-shadow:0 1px 0 rgba(16,24,40,.05) !important;
}
div.stButton { margin-top:6px; }

/* Responsive */
@media(max-width:1200px){.kpi-grid{grid-template-columns:1fr}}
</style>
"""


# ----------------------- Views -----------------------
def header():
    st.markdown(
        f"""
        {CSS}
        <div class="header-pill">
          <div class="header-title">Garment Production Dashboard</div>
          <div class="header-sub">High-level KPIs and trends for quick status checks (Owner’s View).</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_dashboard():
    data, _ = load_kpis()

    header()

    pink_bg, red_ring = "#FDECEC", "#E63946"
    amber_bg, amber_ring = "#FFF2CC", "#F4A300"

    st.markdown('<div class="kpi-grid">', unsafe_allow_html=True)

    with st.container():
        card("PLAN VS ACTUAL",
             data["PLAN VS ACTUAL"]["value"],
             data["PLAN VS ACTUAL"]["target"],
             data["PLAN VS ACTUAL"]["variance"],
             pink_bg, red_ring, "PlanVsActual", "#E63946")

    with st.container():
        card("EFFICIENCY",
             data["EFFICIENCY"]["value"],
             data["EFFICIENCY"]["target"],
             data["EFFICIENCY"]["variance"],
             amber_bg, amber_ring, "Efficiency", "#F4A300")

    with st.container():
        card("LOST TIME",
             data["LOST TIME"]["value"],
             data["LOST TIME"]["target"],
             data["LOST TIME"]["variance"],
             pink_bg, red_ring, "LostTime", "#E63946")

    st.markdown('</div>', unsafe_allow_html=True)


def show_detail(kind: str):
    """Detail page for a given KPI. Uses the raw DataFrame if you want to join more info later."""
    _, df_raw = load_kpis()

    titles = {
        "PlanVsActual": "Plan vs Actual Analysis",
        "Efficiency": "Efficiency Analysis",
        "LostTime": "Lost Time Analysis",
    }
    st.button("← Back to Dashboard", on_click=lambda: st.session_state.update({"view": "Dashboard"}) or st.rerun())

    st.markdown(
        f"""
        <div class="header-pill" style="padding:18px 24px;margin-top:12px;">
          <div class="header-title" style="font-size:34px;">{titles.get(kind, "Details")}</div>
          <div class="header-sub">Line-level variance and specific root causes (Supervisor's View).</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Example static table (replace with your actual line-level breakdown if you have it in Excel)
    if kind == "PlanVsActual":
        detail = pd.DataFrame(
            {
                "Line": ["Line 1", "Line 2", "Line 3"],
                "Variance": ["-2%", "-1%", "+3%"],
                "Observed Cause": ["Training Gaps", "Fabric Quality Issues", "Good Performance"],
                "Category": ["Manpower", "Material", "None"],
                "Action": ["Analyze & Action", "Analyze & Action", "No Action Needed"],
            }
        )
    elif kind == "Efficiency":
        detail = pd.DataFrame(
            {
                "Line": ["Line 4", "Line 5", "Line 6"],
                "Variance": ["-2%", "-1%", "+3%"],
                "Observed Cause": ["Training Gaps", "Fabric Quality Issues", "Good performance"],
                "Category": ["Manpower", "Material", "None"],
                "Action": ["Analyze & Action", "Analyze & Action", "No action needed"],
            }
        )
    else:  # LostTime
        detail = pd.DataFrame(
            {
                "Line": ["Line 7", "Line 8", "Line 9"],
                "Variance": ["+1%", "+3%", "-2%"],
                "Observed Cause": ["Machine breakdown", "Material delay", "Absent operator"],
                "Category": ["Machine", "Material", "Manpower"],
                "Action": ["Analyze & Action", "Analyze & Action", "Analyze & Action"],
            }
        )

    st.dataframe(detail, use_container_width=True)


# ----------------------- Router -----------------------
if "view" not in st.session_state:
    st.session_state["view"] = "Dashboard"

view = st.session_state["view"]
if view == "Dashboard":
    show_dashboard()
elif view in ("PlanVsActual", "Efficiency", "LostTime"):
    show_detail(view)
else:
    show_dashboard()
