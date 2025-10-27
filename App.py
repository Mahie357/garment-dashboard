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
    card_bg = card_colors[kpi]
    variance_color = "#00B050" if variance >= 0 else "#E60000"

    # Donut chart
    fig = go.Figure(go.Pie(
        values=[abs(actual), 100 - abs(actual)],
        hole=0.75,
        marker_colors=[accent, "#EAEAEA"],
        textinfo='none'
    ))
    fig.add_annotation(text=f"{actual}%", showarrow=False, font=dict(size=16, color="black"))
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        width=90, height=90,
        showlegend=False,
        paper_bgcolor=card_bg
    )
    chart_html = fig.to_html(include_plotlyjs="cdn", full_html=False)

    # HTML layout for each card
    card_html = f"""
    <div style="
        background-color:{card_bg};
        border-radius:15px;
        padding:20px;
        height:310px;
        width:100%;
        box-shadow: 0px 6px 10px rgba(0,0,0,0.08);
        display:flex;
        flex-direction:column;
        justify-content:space-between;
    ">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div style="text-align:left;">
                <h4 style="margin:0; font-size:14px; font-weight:600; color:#444;">{kpi.upper()}</h4>
                <h2 style="margin:5px 0 0 0; font-size:42px; font-weight:800; color:#222;">{actual}%</h2>
            </div>
            <div style="width:90px;">{chart_html}</div>
        </div>

        <hr style="border:none; border-top:1px solid #ddd; margin:10px 0;">

        <div style="text-align:left;">
            <p style="margin:4px 0; font-size:16px;"><b>Target:</b> <span style="float:right;">{target}%</span></p>
            <p style="margin:4px 0; font-size:16px;"><b>Variance:</b> 
            <span style="float:right; color:{variance_color};">{variance:+.1f}%</span></p>
        </div>

        <div style="margin-top:8px; text-align:center;">
            <button style="
                border:2px solid {accent};
                background-color:transparent;
                color:{accent};
                border-radius:8px;
                padding:6px 25px;
                font-weight:600;
                font-size:15px;
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
        components.html(card_html, height=340, scrolling=False)
