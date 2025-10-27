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

# --- Custom Card Colors ---
card_colors = {
    "Productivity": "#ffe5e5",
    "Efficiency": "#fff6e5",
    "Lost Time": "#ffe5e5"
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

# --- KPI Layout ---
cols = st.columns(3)

for idx, row in df.iterrows():
    kpi = row["KPI"]
    actual = row["Actual"]
    target = row["Target"]
    variance = round(actual - target, 1)
    color = "green" if variance >= 0 else "red"

    # --- Create Circular Gauge (compatible with Streamlit Cloud) ---
    fig = go.Figure()

    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=actual,
        number={'suffix': "%", "font": {"size": 48, "color": "#444"}},
        title={'text': kpi, 'font': {'size': 20, 'color': '#333'}},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': '#ff4b4b'},
            'bgcolor': "white",
            'borderwidth': 1,
            'bordercolor': "#DDD",
            'steps': [
                {'range': [0, target], 'color': '#ffeeee'},
                {'range': [target, 100], 'color': '#f7f7f7'}
            ]
        }
    ))

    # Make it look like a half-donut using layout range
    fig.update_layout(
        height=300,
        margin=dict(l=10, r=10, t=50, b=0),
        paper_bgcolor=card_colors[kpi],
    )

    with cols[idx]:
        # Card Header
        st.markdown(
            f"""
            <div style='background-color:{card_colors[kpi]};
                        padding:20px;
                        border-radius:25px;
                        box-shadow:0px 4px 15px rgba(0,0,0,0.1);
                        text-align:center;'>
                <h3 style='margin-bottom:0px; color:#333;'>{kpi}</h3>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Chart
        st.plotly_chart(fig, use_container_width=True)

        # KPI Details
        st.markdown(f"🎯 **Target:** {target}%", unsafe_allow_html=True)
        st.markdown(f"📉 **Variance:** <span style='color:{color}'>{variance:+.1f}%</span>", unsafe_allow_html=True)

        # Button Styling
        st.markdown(
            """
            <style>
                div[data-testid="stButton"] button {
                    border-radius: 10px;
                    border: 1px solid #ff4b4b;
                    color: #ff4b4b;
                    background: white;
                    font-weight: 600;
                    width: 50%;
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

