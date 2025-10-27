import streamlit as st
import pandas as pd

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Garment Production Dashboard", layout="wide")

# ---------- LOAD EXCEL DATA ----------
# Ensure you have garment_data.xlsx in same folder
df = pd.read_excel("garment_data.xlsx")

# Extract values dynamically
prod = df.loc[df['Metric'] == 'Productivity', 'Actual'].values[0]
prod_target = df.loc[df['Metric'] == 'Productivity', 'Target'].values[0]
prod_var = df.loc[df['Metric'] == 'Productivity', 'Variance'].values[0]

eff = df.loc[df['Metric'] == 'Efficiency', 'Actual'].values[0]
eff_target = df.loc[df['Metric'] == 'Efficiency', 'Target'].values[0]
eff_var = df.loc[df['Metric'] == 'Efficiency', 'Variance'].values[0]

lost = df.loc[df['Metric'] == 'Lost Time', 'Actual'].values[0]
lost_target = df.loc[df['Metric'] == 'Lost Time', 'Target'].values[0]
lost_var = df.loc[df['Metric'] == 'Lost Time', 'Variance'].values[0]

# ---------- STYLE ----------
st.markdown("""
<style>
    .main {background-color: #f8f9fa;}
    .card {
        padding: 15px; border-radius: 15px; text-align: center; margin: 5px;
        box-shadow: 0 3px 5px rgba(0,0,0,0.1);
    }
    .red {background-color: #ffe5e5;}
    .yellow {background-color: #fff7e6;}
    .metric-value {font-size: 36px; font-weight: bold;}
    .metric-target {font-size: 16px; color: gray;}
    .metric-var {font-size: 18px; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

# ---------- PAGE NAVIGATION ----------
if "page" not in st.session_state:
    st.session_state.page = "main"

# ---------- PAGE 1 : MAIN DASHBOARD ----------
if st.session_state.page == "main":
    st.title("Garment Production Dashboard")
    st.caption("High-level KPIs for quick status checks (Owner's View)")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f'<div class="card red">'
                    f'<div class="metric-value">{prod}%</div>'
                    f'<div>PRODUCTIVITY</div>'
                    f'<div class="metric-target">Target: {prod_target}%</div>'
                    f'<div class="metric-var" style="color:red;">Variance: {prod_var}%</div>'
                    '</div>', unsafe_allow_html=True)
        if st.button("Drill Down - Productivity"):
            st.session_state.page = "prod"

    with col2:
        st.markdown(f'<div class="card yellow">'
                    f'<div class="metric-value">{eff}%</div>'
                    f'<div>EFFICIENCY</div>'
                    f'<div class="metric-target">Target: {eff_target}%</div>'
                    f'<div class="metric-var" style="color:red;">Variance: {eff_var}%</div>'
                    '</div>', unsafe_allow_html=True)
        if st.button("Drill Down - Efficiency"):
            st.session_state.page = "eff"

    with col3:
        st.markdown(f'<div class="card red">'
                    f'<div class="metric-value">{lost}%</div>'
                    f'<div>LOST TIME</div>'
                    f'<div class="metric-target">Target: {lost_target}%</div>'
                    f'<div class="metric-var" style="color:red;">Variance: {lost_var}%</div>'
                    '</div>', unsafe_allow_html=True)
        if st.button("Drill Down - Lost Time"):
            st.session_state.page = "lost"

# ---------- PAGE 2 : PRODUCTIVITY ----------
elif st.session_state.page == "prod":
    st.subheader("Productivity – Line-level Variance and Root Causes")
    st.write("""
**Line 1:** -5% – Machine Breakdowns (Needle snapping)  
**Line 2:** +1% – Good performance  
**Line 3:** -8% – High Changeover Time  
    """)
    if st.button("⬅ Back to Dashboard"):
        st.session_state.page = "main"

# ---------- PAGE 3 : EFFICIENCY ----------
elif st.session_state.page == "eff":
    st.subheader("Efficiency – Analysis and Improvement Plan")
    st.write("""
**Observations:** Slight underperformance due to operator fatigue and rework.  
**Actions:**  
1️⃣ Introduce mid-shift rotation.  
2️⃣ Monitor operator cycle time.  
3️⃣ Provide on-floor micro breaks.
    """)
    if st.button("⬅ Back to Dashboard"):
        st.session_state.page = "main"

# ---------- PAGE 4 : LOST TIME ----------
elif st.session_state.page == "lost":
    st.subheader("Lost Time – Breakdown and Actions")
    st.write("""
**Root Cause:** Machine idle hours and long style changeover.  
**Actions:**  
1️⃣ Optimize scheduling and changeover process.  
2️⃣ Implement SMED (Single-Minute Exchange of Die) practices.  
3️⃣ Conduct weekly performance review.
    """)
    if st.button("⬅ Back to Dashboard"):
        st.session_state.page = "main"
