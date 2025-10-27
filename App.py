import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Garment Production Dashboard", layout="wide")

# ---------------- DATA ----------------
data = {
    "KPI": ["Productivity", "Efficiency", "Variance From Target"],
    "Actual": [72, 68, -4],
    "Target": [75, 70, 0]
}
df = pd.DataFrame(data)

# ---------------- COLORS ----------------
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

# ---------------- TITLE ----------------
st.markdown(
    """
    <h1 style='text-align:center; font-weight:800; color:#1e1e1e;'>Garment Production Dashboard</h1>
    <p style='text-align:center; color:gray;'>High-level KPIs and trends for quick status checks (Owner’s View)</p>
    """,
    unsafe_allow_html=True
)

# ---------------- DASHBOARD ----------------
cols = st.columns(3)

for i, row in df.iterrows():
    kpi = row["KPI"]
    actual = row["Actual"]
    target = row["Target"]
    variance = round(actual - target, 1)
    accent = accent_colors[kpi]
    color = "#00B050" if variance >= 0 else "#E60000"

    # --------- SMALL CLEAN GAUGE ---------
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=actual,
        number={
            "suffix": "%",
            "font": {"size": 36, "color": "#1E1E1E", "family": "Arial Black"}
        },
        gauge={
            "axis": {"range": [min(0, target - 10), 100], "visible": False},
            "bar": {"color": accent, "thickness": 0.35},
            "bgcolor": "#f5f5f5",
            "borderwidth": 0,
            "steps": [{"range": [0, target], "color": "#f2f2f2"}],
        },
        domain={'x': [0, 1], 'y': [0, 1]}
    ))

    fig.update_layout(
        height=180,
        margin=dict(l=0, r=0, t=20, b=0),
        paper_bgcolor=card_colors[kpi]
    )

    # --------- CARD LAYOUT ---------
    with cols[i]:
        st.markdown(
            f"""
            <div style="
                background-color:{card_colors[kpi]};
                border-radius:20px;
                box-shadow:0px 4px 10px rgba(0,0,0,0.1);
                padding:25px 20px 15px 20px;
                text-align:center;
                ">
                <h4 style="color:#1E1E1E; font-size:16px; margin-bottom:10px; text-transform:uppercase;">
                    {kpi}
                </h4>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Gauge chart centered
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        # Target and variance neatly inside same card
        st.markdown(
            f"""
            <div style="text-align:center; line-height:1.8; font-size:15px;">
                🎯 <b>Target:</b> {target}%<br>
                📉 <b>Variance:</b> <span style="color:{color};">{variance:+.1f}%</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        # --------- BUTTON ---------
        st.markdown(
            f"""
            <div style="text-align:center; margin-top:10px;">
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
            """,
            unsafe_allow_html=True
        )
