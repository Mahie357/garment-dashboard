import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Garment Production Dashboard", layout="wide")

# Example data (replace this with your Excel/SharePoint data)
data = {
    "KPI": ["Productivity", "Efficiency", "Lost Time"],
    "Actual": [72, 68, 3.5],
    "Target": [75, 70, 2]
}
df = pd.DataFrame(data)

st.markdown("## 👕 Garment Production Dashboard")
st.write("High-level KPIs and trends for quick status checks (Owner's View)")

# Define colors for each card
card_colors = {
    "Productivity": "#ffe5e5",
    "Efficiency": "#fff6e5",
    "Lost Time": "#ffe5e5"
}

# Layout for KPI cards
cols = st.columns(3)

for idx, row in df.iterrows():
    kpi = row["KPI"]
    actual = row["Actual"]
    target = row["Target"]
    variance = actual - target
    color = "red" if variance < 0 else "green"

    # Plotly donut chart
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=actual,
        title={'text': f"{kpi}", 'font': {'size': 20}},
        number={'suffix': "%"},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': '#FF4B4B'},
            'bgcolor': "white",
            'steps': [{'range': [0, target], 'color': '#ffeeee'}],
        }
    ))

    with cols[idx]:
        st.markdown(
            f"""
            <div style='background-color:{card_colors[kpi]}; padding:20px; border-radius:20px; text-align:center; box-shadow:0 0 10px rgba(0,0,0,0.1);'>
                <h3 style='margin-bottom:-10px'>{kpi}</h3>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(f"🎯 **Target:** {target}%")
        st.markdown(f"📉 **Variance:** <span style='color:{color}'>{variance:.1f}%</span>", unsafe_allow_html=True)
        st.button("Drill Down", key=kpi)
