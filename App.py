# app.py
import math
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import streamlit.components.v1 as components

st.set_page_config(page_title="Garment Production Dashboard", layout="wide")

# -------- Data --------
# Expect columns: KPI, Actual, Target  (Actual/Target as % or decimals)
try:
    df = pd.read_excel("garment_data.xlsx")
except Exception:
    df = pd.DataFrame({
        "KPI": ["PRODUCTIVITY", "EFFICIENCY", "VARIANCE FROM TARGET"],
        "Actual": [0.72, 0.68, -0.04],     # fallback demo
        "Target": [0.75, 0.70, 0.00],
    })

# normalize to percentages (0–1)
def to_pct(x):
    if pd.isna(x): return 0.0
    return x/100 if abs(x) > 1 else x

df["Actual"] = df["Actual"].apply(to_pct)
df["Target"] = df["Target"].apply(to_pct)
df["Variance"] = (df["Actual"] - df["Target"])

# keep only the 3 cards in the order
order = ["PRODUCTIVITY", "EFFICIENCY", "VARIANCE FROM TARGET"]
df = pd.concat([df[df["KPI"].str.upper()==k] for k in order]).reset_index(drop=True)

# -------- Theme bits --------
card_colors = {
    "PRODUCTIVITY": "#FFE5E5",
    "EFFICIENCY": "#FFF1C9",
    "VARIANCE FROM TARGET": "#FFE5E5",
}
accent_colors = {
    "PRODUCTIVITY": "#E63946",
    "EFFICIENCY": "#FFB703",
    "VARIANCE FROM TARGET": "#E63946",
}

# -------- Header --------
st.markdown(
    """
    <div style="padding:22px 28px;margin-bottom:18px;background:#fff;border:1px solid #eee;border-radius:14px;box-shadow:0 6px 18px rgba(0,0,0,.06);">
      <h1 style="margin:0;font-size:46px;line-height:1.1;">Garment Production Dashboard</h1>
      <div style="margin-top:6px;color:#666;font-size:18px;">High-level KPIs and trends for quick status checks (Owner's View).</div>
    </div>
    """,
    unsafe_allow_html=True,
)

cols = st.columns(3, gap="large")

# -------- Card builder --------
for i, row in df.iterrows():
    kpi = str(row["KPI"]).upper()
    actual = float(row["Actual"])
    target = float(row["Target"])
    variance = actual - target

    # circle progress (donut) — 72% -> 72, -4% -> 4 (positive arc), label shows signed text
    donut_val = abs(actual*100)
    donut_label = f'{actual*100:.0f}%' if kpi != "VARIANCE FROM TARGET" else f'{variance*100:.0f}%'

    # donut figure
    bg = "#f1f1f1"
    ring = accent_colors.get(kpi, "#E63946")
    fig = go.Figure()
    fig.add_trace(go.Pie(
        values=[donut_val, max(0, 100 - donut_val)],
        hole=.78, sort=False, direction="clockwise",
        marker=dict(colors=[ring, bg], line=dict(color="#fff", width=2)),
        textinfo="none", hoverinfo="skip", showlegend=False
    ))
    fig.update_layout(
        margin=dict(l=0,r=0,t=0,b=0), width=112, height=112,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    )

    donut_html = fig.to_html(include_plotlyjs="cdn", full_html=False)

    # numbers
    big_txt = f'{actual*100:.0f}%' if kpi != "VARIANCE FROM TARGET" else f'{variance*100:+.0f}%'
    tgt_txt = f'{target*100:.0f}%'
    var_txt = f'{variance*100:+.1f}%'
    var_color = "#E63946" if variance < 0 else ("#2a9d8f" if variance > 0 else "#444")

    # card HTML
    card_bg = card_colors.get(kpi, "#FFEDEA")
    btn_border = ring
    title = kpi

    card_html = f"""
    <div style="
      position:relative;background:{card_bg};border:1px solid #eee;border-radius:18px;
      padding:18px 18px 16px 18px;height:320px;box-shadow:0 8px 20px rgba(0,0,0,.06);
      display:grid;grid-template-rows:106px 1px 112px;row-gap:8px;">
      
      <div style="display:flex;justify-content:space-between;align-items:flex-start;">
        <div style="font-weight:700;letter-spacing:.6px;color:#333;">{title}</div>
        <div style="transform:translateY(-6px);">{donut_html}</div>
      </div>

      <div style="height:1px;background:#eadede;"></div>

      <div style="display:grid;grid-template-columns:1fr 1fr;column-gap:16px;align-items:center;">
        <div>
          <div style="font-size: clamp(30px,3.6vw,46px); font-weight:800; line-height:1; color:#1a1a1a; margin-bottom:12px;">
            {big_txt}
          </div>
          <div style="display:flex; gap:18px; font-size:16px;">
            <div><span style="opacity:.7;">Target:</span> <b>{tgt_txt}</b></div>
            <div><span style="opacity:.7;">Variance:</span> <b style="color:{var_color};">{var_txt}</b></div>
          </div>
        </div>
        <div style="display:flex;justify-content:flex-end;align-items:end;">
          <button style="
            padding:10px 22px;border-radius:12px;border:2px solid {btn_border};
            background:#fff;color:#222;font-weight:700;cursor:pointer;">
            Drill Down
          </button>
        </div>
      </div>
    </div>
    """

    with cols[i]:
        components.html(card_html, height=340, scrolling=False)
