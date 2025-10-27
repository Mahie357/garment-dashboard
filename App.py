import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import streamlit.components.v1 as components

st.set_page_config(page_title="Garment Production Dashboard", layout="wide")

# ---------- Data ----------
data = {
    "KPI": ["Productivity", "Efficiency", "Variance from Target"],
    "Actual": [72, 68, -4],
    "Target": [75, 70, 0]
}
df = pd.DataFrame(data)

# ---------- Colors ----------
card_colors = {
    "Productivity": "#FFECEC",
    "Efficiency": "#FFF7D6",
    "Variance from Target": "#FFECEC"
}
accent_colors = {
    "Productivity": "#E63946",
    "Efficiency": "#FFB703",
    "Variance from Target": "#E63946"
}

# ---------- Title ----------
st.markdown("""
    <div style="text-align:center; padding:10px 0;">
        <h1 style="font-weight:800; color:#222;">Garment Production Dashboard</h1>
        <p style="color:gray;">High-level KPIs and trends for quick status checks (Owner's View).</p>
    </div>
""", unsafe_allow_html=True)

# ---------- Layout ----------
cols = st.columns(3)

for i, row in df.iterrows():
    kpi = row["KPI"]
    actual = row["Actual"]
    target = row["Target"]
    variance = round(actual - target, 1)
    accent = accent_colors[kpi]
    bg = card_colors[kpi]
    variance_color = "#00B050" if variance >= 0 else "#E60000"

    # Donut Chart
    fig = go.Figure(go.Pie(
        values=[abs(actual), 100 - abs(actual)],
        hole=0.75,
        marker_colors=[accent, "#EAEAEA"],
        textinfo='none'
    ))
    fig.add_annotation(text=f"{actual}%", showarrow=False, font=dict(size=14, color="black"))
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        width=70, height=70,
        showlegend=False,
        paper_bgcolor=bg
    )
    chart_html = fig.to_html(include_plotlyjs="cdn", full_html=False)

    # Card HTML
    card_html = f"""
    <div style="
        background-color:{bg};
        border-radius:16px;
        padding:18px 20px;
        height:300px;
        width:100%;
        box-shadow:0 6px 10px rgba(0,0,0,0.08);
        display:flex;
        flex-direction:column;
        justify-content:space-between;
        overflow:hidden;
    ">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; height:70px;">
            <div style="text-align:left;">
                <h4 style="margin:0; font-size:13px; font-weight:700; color:#444;">{kpi.upper()}</h4>
                <h2 style="margin:6px 0 0 0; font-size:38px; font-weight:800; color:#222;">{actual}%</h2>
            </div>
            <div style="margin-top:2px; width:70px;">{chart_html}</div>
        </div>

        <hr style="border:none; border-top:1px solid #ddd; margin:8px 0 12px 0;">

        <div style="display:flex; justify-content:space-between; align-items:center; font-size:15px; margin-bottom:8px;">
            <p style="margin:0;"><b>Target:</b> {target}%</p>
            <p style="margin:0;"><b>Variance:</b> 
            <span style="color:{variance_color};">{variance:+.1f}%</span></p>
        </div>

        <div style="text-align:center;">
            <button style="
                border:2px solid {accent};
                background-color:transparent;
                color:{accent};
                border-radius:8px;
                padding:5px 20px;
                font-weight:600;
                font-size:14px;
                cursor:pointer;
                transition:0.3s;
            " 
            onmouseover="this.style.backgroundColor='{accent}'; this.style.color='white';"
            onmouseout="this.style.backgroundColor='transparent'; this.style.color='{accent}';">
                Drill Down
            </button>
        </div>
    </div>
    """

    with cols[i]:
        components.html(card_html, height=320, scrolling=False)
