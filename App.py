import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- Streamlit Page Setup ---
st.set_page_config(page_title="Garment Production Dashboard", layout="wide")

# --- Load Data ---
data = {
    "KPI": ["Productivity", "Efficiency", "Lost Time"],
    "Actual": [72, 68, 3.5],
    "Target": [75, 70, 2]
}
df = pd.DataFrame(data)

# --- Card Theme Colors ---
card_colors = {
    "Productivity": "#FFE6E6",
    "Efficiency": "#FFF7E6",
    "Lost Time": "#FFE6E6"
}

# --- Page Title ---
st.markdown(
    "<h1 style='text-align:center;'>Garment Production Dashboard</h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<p style='text-align:center;color:gray;'>High-level KPIs for quick status checks (Owner’s View)</p>",
    unsafe_allow_html=True
)

# --- Create 3 Columns ---
cols = st.columns(3)

for idx, row in df.iterrows():
    kpi = row["KPI"]
    actual = row["Actual"]
    target = row["Target"]
    variance = round(actual - target, 1)
    color = "#00B050" if variance >= 0 else "#E60000"

    # --- Create a Custom Gauge ---
    fig = go.Figure()

    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=actual,
        number={
            'suffix': "%",
            'font': {'size': 48, 'color': '#333', 'family': "Arial Black"}
        },
        title={'text': f"{kpi}", 'font': {'size': 20, 'color': '#444'}},
        gauge={
            'axis': {'range': [0, 100], 'tickfont': {'size': 10}, 'tickcolor': 'gray'},
            'bar': {'color': '#ff4b4b', 'thickness': 0.25},
            'bgcolor': "#fefefe",
            'borderwidth': 1,
            'bordercolor': "#ddd",
            'steps': [
                {'range': [0, target], 'color': '#ffeaea'},
                {'range': [target, 100], 'color': '#f7f7f7'}
            ]
        },
        domain={'x': [0, 1], 'y': [0, 1]}
    ))

    # --- Format Layout to be Centered & Semi-Circular ---
    fig.update_layout(
        height=250,
        margin=dict(l=5, r=5, t=40, b=0),
        paper_bgcolor=card_colors[kpi],
    )

    # --- Card Layout ---
    with cols[idx]:
        st.markdown(
            f"""
            <div style='background-color:{card_colors[kpi]};
                        padding:25px;
                        border-radius:20px;
                        box-shadow:0px 4px 15px rgba(0,0,0,0.08);
                        text-align:center;
                        margin-bottom:20px;'>
                <h2 style='margin-bottom:15px; color:#333;'>{kpi}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown(
            f"""
            <div style='text-align:center; line-height:1.8;'>
                🎯 <b>Target:</b> {target}%<br>
                📉 <b>Variance:</b> <span style='color:{color}'>{variance:+.1f}%</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        # --- Button Style ---
        st.markdown(
            """
            <style>
                div[data-testid="stButton"] button {
                    border-radius: 10px;
                    border: 1px solid #ff4b4b;
                    color: #ff4b4b;
                    background: white;
                    font-weight: 600;
                    width: 60%;
                    margin-top: 15px;
                }
                div[data-testid="stButton"] button:hover {
                    background-color: #ff4b4b;
                    color: white;
                }
            </style>
            """,
            unsafe_allow_html=True
        )
        st.button("Drill Down", key=kpi)
