import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import streamlit.components.v1 as components

st.set_page_config(page_title="Garment Production Dashboard", layout="wide")

# ---------- Sample Data ----------
data = {
    "KPI": ["Productivity", "Efficiency", "Variance From Target"],
    "Actual": [72, 68, -4],
    "Target": [75, 70, 0]
}
df = pd.DataFrame(data)

# ---------- Colors ----------
card_colors = {
    "Productivity": "#FFECEC",
    "Efficiency": "#FFF7D6",
    "Variance From Target": "#FFECEC"
}
accent_colors = {
    "Productivity": "#E63946",
    "Efficiency": "#FFB703",
    "Variance From Target": "#E63946"
}

# ---------- Header ----------
st.markdown("""
<h1 style='text-align:center; font-weight:800; color:#1e1e1e;'>Garment Production Dashboard</h1>
<p style='text-align:center; color:gray;'>High-level KPIs and trends for quick status checks (Owner’s View)</p>
""", unsafe_allow_html=True)

# ---------- Layout ----------
cols = st.columns(3)

for i, row in df.iterrows():
    kpi = row["KPI"]
    actual = row["Actual"]
    target = row["Target"]
    variance = round(actual - target, 1)
    accent = accent_colors[kpi]
    color = "#00B050" if variance >= 0 else "#E60000"

    # Create small circular gauge
    gauge = go.Figure(go.Indicator(
        mode="gauge",
        value=actual,
        gauge={
            "axis": {"range": [0, 100], "visible": False},
            "bar": {"color": accent, "thickness": 0.25},
            "bgcolor": "#f5f5f5",
            "borderwidth": 0,
            "steps": [{"range": [0, target], "color": "#f2f2f2"}],
        }
    ))
    gauge.update_layout(width=80, height=80, margin=dict(l=0, r=0, t=0, b=0),
                        paper_bgcolor=card_colors[kpi])
    gauge_html = gauge.to_html(include_plotlyjs="cdn", full_html=False)

    # Combine HTML & Gauge inside one box
    card_html = f"""
    <div style="
        background-color:{card_colors[kpi]};
        border-radius:20px;
        box-shadow:0px 4px 10px rgba(0,0,0,0.1);
        padding:20px;
        height:300px;
        text-align:center;
        position:relative;
    ">
        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
            <h4 style="color:#1E1E1E; font-size:16px; margin:0; text-transform:uppercase;">{kpi}</h4>
            <div style="width:85px;">{gauge_html}</div>
        </div>

        <h2 style="font-weight:800; font-size:38px; margin:20px 0 10px 0; color:#1E1E1E;">{actual}%</h2>

        <div style="display:flex; justify-content:space-around; margin-top:10px;">
            <p style="margin:0; font-size:15px;">🎯 <b>Target:</b> {target}%</p>
            <p style="margin:0; font-size:15px;">📉 <b>Variance:</b> 
            <span style="color:{color};">{variance:+.1f}%</span></p>
        </div>

        <div style="text-align:center; margin-top:25px;">
            <button style="
                background-color:white;
                color:{accent};
                border:2px solid {accent};
                border-radius:8px;
                padding:6px 25px;
                font-weight:600;
                cursor:pointer;
                transition:0.3s;
            "
            onmouseover="this.style.backgroundColor='{accent}'; this.style.color='white';"
            onmouseout="this.style.backgroundColor='white'; this.style.color='{accent}';">
                Drill Down
            </button>
        </div>
    </div>
    """

    with cols[i]:
        components.html(card_html, height=330, scrolling=False)
