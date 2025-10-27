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

    # -------- SMALL TOP-RIGHT GAUGE --------
    gauge = go.Figure(go.Indicator(
        mode="gauge",
        value=actual,
        gauge={
            "axis": {"range": [0, 100], "visible": False},
            "bar": {"color": accent, "thickness": 0.2},
            "bgcolor": "#f5f5f5",
            "borderwidth": 0,
            "steps": [{"range": [0, target], "color": "#f2f2f2"}],
        },
        domain={'x': [0, 1], 'y': [0, 1]}
    ))
    gauge.update_layout(
        width=100,
        height=100,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor=card_colors[kpi],
    )

    # ---------------- CARD ----------------
    with cols[i]:
        st.markdown(
            f"""
            <div style="
                background-color:{card_colors[kpi]};
                border-radius:20px;
                box-shadow:0px 4px 10px rgba(0,0,0,0.1);
                padding:20px;
                position:relative;
                height:290px;
                text-align:center;
            ">
                <!-- KPI Title -->
                <div style="text-align:left;">
                    <h4 style="color:#1E1E1E; font-size:16px; margin:0; text-transform:uppercase;">
                        {kpi}
                    </h4>
                </div>
            """,
            unsafe_allow_html=True
        )

        # Place gauge top-right (smaller)
        gauge_html = gauge.to_html(include_plotlyjs="cdn", full_html=False)
        st.markdown(
            f"""
            <div style="position:absolute; top:15px; right:15px; width:85px;">
                {gauge_html}
            </div>
            """,
            unsafe_allow_html=True
        )

        # Main KPI number
        st.markdown(
            f"""
            <div style="margin-top:60px;">
                <h2 style="font-weight:800; font-size:40px; margin:0; color:#1E1E1E;">{actual}%</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Target and variance side by side
        st.markdown(
            f"""
            <div style="display:flex; justify-content:space-around; margin-top:15px;">
                <p style="margin:0; font-size:15px;">🎯 <b>Target:</b> {target}%</p>
                <p style="margin:0; font-size:15px;">📉 <b>Variance:</b> <span style="color:{color};">{variance:+.1f}%</span></p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Drill Down button
        st.markdown(
            f"""
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
            """,
            unsafe_allow_html=True
        )
