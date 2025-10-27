# app.py
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Garment Production Dashboard", layout="wide")

# ---------------------- Data ---------------------- #
def load_df():
    try:
        df = pd.read_excel("garment_data.xlsx")
    except Exception:
        # demo data if file missing or unreadable
        return pd.DataFrame({
            "KPI": ["PRODUCTIVITY", "EFFICIENCY", "VARIANCE FROM TARGET"],
            "ACTUAL": [0.72, 0.68, -0.04],
            "TARGET": [0.75, 0.70, 0.00],
        })

    # Normalize headers (space/case insensitive) and map likely names
    df = df.copy()
    df.columns = [c.strip().upper().replace(" ", "") for c in df.columns]

    colmap = {}
    for c in df.columns:
        if c in ("KPI","METRIC","NAME"): colmap[c] = "KPI"
        elif c in ("ACTUAL","VALUE","CURRENT","RESULT"): colmap[c] = "ACTUAL"
        elif c in ("TARGET","GOAL","PLAN"): colmap[c] = "TARGET"
    df = df.rename(columns=colmap)

    # Make sure we have the three
    need = {"KPI","ACTUAL","TARGET"}
    if not need.issubset(df.columns):
        return pd.DataFrame({
            "KPI": ["PRODUCTIVITY", "EFFICIENCY", "VARIANCE FROM TARGET"],
            "ACTUAL": [0.72, 0.68, -0.04],
            "TARGET": [0.75, 0.70, 0.00],
        })

    # Normalize to 0–1 (or already fractional)
    def to_frac(x):
        if pd.isna(x): return 0.0
        try: x=float(x)
        except: return 0.0
        return x/100 if abs(x)>1 else x

    df["ACTUAL"] = df["ACTUAL"].apply(to_frac)
    df["TARGET"] = df["TARGET"].apply(to_frac)
    df["KPI"] = df["KPI"].astype(str).str.upper().str.strip()
    df["VARIANCE"] = df["ACTUAL"] - df["TARGET"]

    # Build the exact three cards in order (create missing ones with zeros)
    wanted = ["PRODUCTIVITY", "EFFICIENCY", "VARIANCE FROM TARGET"]
    out = []
    for k in wanted:
        if (df["KPI"] == k).any():
            out.append(df[df["KPI"] == k].iloc[0])
        else:
            out.append(pd.Series({"KPI": k, "ACTUAL": 0.0, "TARGET": 0.0, "VARIANCE": 0.0}))
    return pd.DataFrame(out)

df = load_df()

# ---------------------- Styles ---------------------- #
st.markdown("""
<style>
/* header card */
.header {
  padding:22px 28px; margin-bottom:18px; background:#fff;
  border:1px solid #eee; border-radius:14px;
  box-shadow:0 6px 18px rgba(0,0,0,.06);
}
.header h1{ margin:0; font-size:46px; line-height:1.1;}
.header .sub{ margin-top:6px; color:#666; font-size:18px;}

/* three cards container */
.kpi-row{
  display:flex; gap:22px; width:100%;
}
.kpi-card{
  position:relative; flex:1 1 0;
  height:320px; padding:18px; border:1px solid #eee; border-radius:18px;
  box-shadow:0 8px 20px rgba(0,0,0,.06);
  display:flex; flex-direction:column; justify-content:space-between;
}

/* top row inside card */
.kpi-top{
  position:relative; height:110px;
}
.kpi-title{
  font-weight:800; letter-spacing:.6px; color:#333; margin-bottom:8px;
}
.kpi-value{
  font-size:44px; font-weight:800; line-height:1; color:#1a1a1a;
}

/* donut ring (conic-gradient) */
.ring{
  position:absolute; top:6px; right:6px;
  width:86px; height:86px; border-radius:50%;
  background:
    conic-gradient(var(--ring-color) calc(var(--p)*1%), #ececec 0);
}
.ring::after{
  content: attr(data-label);
  position:absolute; inset:16px; display:flex; align-items:center; justify-content:center;
  background:#fff; border-radius:50%; font:700 16px/1.1 ui-sans-serif,system-ui,Segoe UI,Roboto,Arial;
  color:#333; border:2px solid #fff;
}

/* divider */
.divider{ height:1px; background:#eadede; margin:2px 0 8px 0;}

/* target/variance row */
.kpi-meta{
  display:flex; justify-content:space-between; align-items:center;
  font-size:16px;
}
.kpi-meta span.label{ opacity:.7; }

/* button row */
.kpi-btn{
  display:flex; justify-content:flex-start;
}
.kpi-btn button{
  padding:10px 22px; border-radius:12px; background:#fff; font-weight:700;
  cursor:pointer; border:2px solid var(--btn-color); color:#222;
}

/* backgrounds per card */
.bg-pink{ background:#FFE5E5; }
.bg-yellow{ background:#FFF1C9; }
.bg-pink2{ background:#FFE5E5; }
</style>
""", unsafe_allow_html=True)

# ---------------------- Header ---------------------- #
st.markdown("""
<div class="header">
  <h1>Garment Production Dashboard</h1>
  <div class="sub">High-level KPIs and trends for quick status checks (Owner's View).</div>
</div>
""", unsafe_allow_html=True)

# ---------------------- Render Cards ---------------------- #
# fixed order and colors
order = [
    ("PRODUCTIVITY",  "bg-pink",   "#E63946"),
    ("EFFICIENCY",    "bg-yellow", "#FFB703"),
    ("VARIANCE FROM TARGET","bg-pink2","#E63946")
]

# Build HTML for the row
parts = ['<div class="kpi-row">']
for kpi_name, bg_cls, accent in order:
    r = df[df["KPI"] == kpi_name].iloc[0]
    actual = float(r["ACTUAL"])
    target = float(r["TARGET"])
    variance = float(r["VARIANCE"])

    # main number in big font (value vs variance card)
    big_txt = f'{actual*100:.0f}%' if kpi_name != "VARIANCE FROM TARGET" else f'{variance*100:+.0f}%'
    donut_pct = abs(actual*100) if kpi_name != "VARIANCE FROM TARGET" else abs(variance*100)
    donut_label = f'{actual*100:.0f}%' if kpi_name != "VARIANCE FROM TARGET" else f'{variance*100:+.0f}%'

    var_color = "#E63946" if variance < 0 else ("#2a9d8f" if variance > 0 else "#444")
    target_txt = f"{target*100:.0f}%"
    variance_txt = f"{variance*100:+.1f}%"

    parts.append(f"""
      <div class="kpi-card {bg_cls}" style="--btn-color:{accent};">
        <div class="kpi-top">
          <div class="kpi-title">{kpi_name}</div>
          <div class="kpi-value">{big_txt}</div>
          <div class="ring" style="--ring-color:{accent}; --p:{max(0,min(100,donut_pct))};" data-label="{donut_label}"></div>
        </div>

        <div class="divider"></div>

        <div class="kpi-meta">
          <div><span class="label">Target:</span> <b>{target_txt}</b></div>
          <div><span class="label">Variance:</span> <b style="color:{var_color};">{variance_txt}</b></div>
        </div>

        <div class="kpi-btn"><button>Drill Down</button></div>
      </div>
    """)

parts.append('</div>')
st.markdown("\n".join(parts), unsafe_allow_html=True)
