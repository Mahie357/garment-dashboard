import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ---------------- Streamlit Page Setup ----------------
st.set_page_config(page_title="Garment Production Dashboard", layout="wide")

# ---------------- Sample Data ----------------
data = {
    "KPI": ["Productivity", "Efficiency", "Variance From Target"],
    "Actual": [72, 68, -4],
    "Target": [75, 70, 0],
}
df = pd.DataFrame(data)

# ---------------- Custom Colors ----------------
card_colors = {
    "Productivity": "#FFECEC",
    "Efficiency": "#FFF7D6",
    "Variance From Target": "#FFECEC",
}
accent_colors = {
    "Productivity": "#E63946",
    "Efficiency": "#FFB703",
    "Variance From Target": "#E63946",
}

# ---------------- Page Title ----------------
st.markdown(
    """
    <h1 style='text-align:center; font-weight:800; color:#1e1e1e;'>Garment Production Dashboard</h1>
    <p style='text-align:center; color:gray;'>High-level KPIs and trends for quick status checks (Owner’s View)</p>
    """,
    unsafe_allow_html=True
)

# ---------------- Layout ----------------
cols = st.columns(3)

for i, row in df.iterrows():
    kpi = row["KPI"]
    actual = row["Actual"]
    target = row["Target"]
    variance = round(actual - target, 1)
    color = "#00B050" if variance >= 0 else "#E60000"

    # ---------------- Gauge ----------------
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=actual,
        number={'suffix': "%", "font": {"size": 28, "color": "#1E1E1E", "family": "Arial Black"}},
        gauge={
            'axis': {'range': [min(-10, target - 20), 100], 'visible': False},
            'bar': {'color': accent_colors[kpi], 'thickness': 0.35},
            'bgcolor': "white",
            'borderwidth': 0,
            'steps': [{'range': [0, target], 'color': '#F8F8F8'}]
        },
        domain={'x': [0, 1], 'y': [0, 1]},
    ))

    fig.update_layout(
        height=160,
        margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor=card_colors[kpi],
    )

    # ---------------- Card ----------------
    with cols[i]:
        st.markdown(
            f"""
            <div style="
                background-color:{card_colors[kpi]};
                border-radius:20px;
                box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
                padding:25px 20px;
                text-align:center;
                ">
                <h4 style="color:#1E1E1E; font-size:18px; margin-bottom:5px;">{kpi.upper()}</h4>
                <h2 style="font-weight:800; font-size:36px; margin-top:0; color:#1E1E1E;">{actual}%</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        st.markdown(
            f"""
            <div style="text-align:left; padding:0 25px;">
                <p style="margin:4px 0;">🎯 <b>Target:</b> <span style="float:right;">{target}%</span></p>
                <p style="margin:4px 0;">📉 <b>Variance:</b> 
                <span style="float:right; color:{color};">{variance:+.1f}%</span></p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # ---------------- Drill Down Button ----------------
        st.markdown(
            f"""
            <div style="text-align:center; margin-top:10px;">
                <button style="
                    background-color:white;
                    color:{accent_colors[kpi]};
                    border:2px solid {accent_colors[kpi]};
                    border-radius:8px;
                    padding:6px 25px;
                    font-weight:600;
                    cursor:pointer;
                    transition:0.3s;
                " 
                onmouseover="this.style.backgroundColor='{accent_colors[kpi]}'; this.style.color='white';"
                onmouseout="this.style.backgroundColor='white'; this.style.color='{accent_colors[kpi]}';">
                Drill Down
                </button>
            </div>
            """,
            unsafe_allow_html=True
        )
