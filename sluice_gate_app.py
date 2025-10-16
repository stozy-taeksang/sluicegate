# -*- coding: utf-8 -*-
"""
Sluice Gate Flow Calculator – Version 00
Author: Taeksang Kim 
Date: 10/15/2025
"""

import streamlit as st
import math
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --------------------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------------------
st.set_page_config(page_title="Sluice Gate Flow Calculator", layout="wide")

st.title("🌊 Sluice Gate Flow Calculator & Visualization Tool")

st.markdown("""
This interactive app calculates and visualizes flowrates for **16 sluice gates**, categorized as:
- 🇨🇦 *Canadian Gates (1–8)*
- 🇺🇸 *American Gates (9–16)*
""")

# --------------------------------------------------------------
# FUNCTIONS
# --------------------------------------------------------------
def gate_flow_vt_chow(G, h, Cd=0.58, b=15.91, g=9.81):
    if G <= 0 or h <= 0:
        return 0.7
    return Cd * b * G * math.sqrt(2 * g * h)

def gate_flow_corps_ref(G, h, Cd=0.61, b=15.91, g=9.81):
    if G <= 0 or h <= 0 or h <= Cd * G:
        return 0.7
    numerator = Cd * b * G * math.sqrt(2 * g * (h - Cd * G))
    denominator = math.sqrt(1 - (Cd * G / h) ** 2)
    return numerator / denominator

# --------------------------------------------------------------
# TABS
# --------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📘 Explanation",
    "🔧 Interactive Tools",
    "🧮 Flow Calculation",
    "📊 Graphical Results"
])

# --------------------------------------------------------------
# TAB 1: EXPLANATION
# --------------------------------------------------------------
with tab1:
    st.header("📘 Theoretical Background")
    st.image("A_schematic_diagram.png",
             caption="Figure 1. Definition sketch of sluice gate parameters",
             use_container_width=True)

    st.subheader("1️⃣ V.T. Chow Formula")
    st.latex(r"Q = C_d \, b \, G \, \sqrt{2gh}")
    st.markdown("""
    where  
    - \( Q \): Discharge (m³/s)  
    - \( C_d = 0.58 \): Discharge coefficient  
    - \( b = 15.91 \): Gate width (m)  
    - \( G \): Gate opening height (m)  
    - \( h \): Water depth above sill (m)
    """)

    st.subheader("2️⃣ Corps Reference Formula")
    st.latex(r"Q = \frac{C_d \, b \, G \, \sqrt{2g(h - C_d G)}}{\sqrt{1 - (C_d G / h)^2}}")
    st.markdown("""
    where  
    - \( C_d = 0.61 \): Discharge coefficient  
    - Remaining symbols are same as above
    """)

    st.markdown("""
    ### ⚙️ Parameter Definitions
    - **SWP:** Upstream surface water profile level (m)  
    - **Sill Elevation:** Height of the gate bottom (m)  
    - **Water Depth (h):** SWP − Sill  
    - **Gate Opening Height (G):** Distance between gate bottom and sill
    """)

    st.divider()
    st.subheader("💡 Simple Calculator")

    st.markdown("Try changing the parameters below to see flowrate differences between both formulas:")

    colA, colB = st.columns(2)
    with colA:
        G = st.slider("Gate Opening (G) [m]", 0.0, 2.0, 0.5, 0.01)
    with colB:
        h = st.slider("Water Depth (h) [m]", 0.0, 3.0, 1.0, 0.01)

    q1 = gate_flow_vt_chow(G, h)
    q2 = gate_flow_corps_ref(G, h)

    st.metric("V.T. Chow Flowrate (m³/s)", f"{q1:.3f}")
    st.metric("Corps Ref Flowrate (m³/s)", f"{q2:.3f}")

# --------------------------------------------------------------
# TAB 2: INTERACTIVE INPUTS
# --------------------------------------------------------------
with tab2:
    st.header("🔧 Interactive Gate Control Panel")

    with st.expander("ℹ️ Parameter Meaning", expanded=True):
        st.markdown("""
        - **SWP Level:** Surface water elevation upstream of the gate (m)  
        - **Sill Elevation:** Gate bottom elevation (m)  
        - **Gate Opening Height:** Opening distance for each gate (m)  
        - **Water Depth (h):** SWP − Sill  
        - **Gate Width (b):** 15.91 m (constant for all gates)  
        """)

    col1, col2, col3 = st.columns(3)
    with col1:
        SWP = st.number_input("SWP Level [m]", value=181.20, step=0.001)
    with col2:
        sill_1_to_4 = st.number_input("Sill Elevation Gates 1–4 [m]", value=180.05, step=0.001)
    with col3:
        sill_5_to_8 = st.number_input("Sill Elevation Gates 5–8 [m]", value=179.75, step=0.001)

    sill_9_to_16 = st.number_input("Sill Elevation Gates 9–16 [m]", value=180.05, step=0.001)

    st.subheader("Gate Opening Heights [m]")
    openings = []
    for i in range(1, 17):
        G = st.number_input(f"Gate {i}", min_value=0.0, step=0.001, format="%.3f", key=f"gate{i}")
        openings.append(G)

    st.info("🔹 Gates 1–8 correspond to **Canadian Gates**, and 9–16 correspond to **American Gates**.")

# --------------------------------------------------------------
# TAB 3: CALCULATION
# --------------------------------------------------------------
with tab3:
    st.header("🧮 Flow Calculation Results")

    sill = [sill_1_to_4]*4 + [sill_5_to_8]*4 + [sill_9_to_16]*8
    water_depth = [max(SWP - s, 0) for s in sill]

    flow_vt_chow = [gate_flow_vt_chow(G, h) for G, h in zip(openings, water_depth)]
    flow_corps_ref = [gate_flow_corps_ref(G, h) for G, h in zip(openings, water_depth)]

    relative_error = [abs((a - b)/b * 100) if b != 0 else 0 for a, b in zip(flow_vt_chow, flow_corps_ref)]

    df = pd.DataFrame({
        "Gate": range(1, 17),
        "Sill (m)": sill,
        "Opening Height (m)": openings,
        "Water Depth (m)": water_depth,
        "Flow - V.T. Chow (m³/s)": flow_vt_chow,
        "Flow - Corps Ref (m³/s)": flow_corps_ref,
        "Percent Error (%)": relative_error
    })

    st.dataframe(df.style.format("{:.3f}"))

    st.success(f"**Total Flow (V.T. Chow):** {sum(flow_vt_chow):.3f} m³/s")
    st.success(f"**Total Flow (Corps Ref):** {sum(flow_corps_ref):.3f} m³/s")

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download Results as CSV", csv, "sluice_gate_results.csv", "text/csv")

# --------------------------------------------------------------
# TAB 4: GRAPHICAL RESULTS
# --------------------------------------------------------------
with tab4:
    st.header("📊 Graphical Visualization")

    x = list(range(1, 17))

    # Graph 1
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(x=x, y=openings, name="Gate Opening [m]", marker_color="lightblue"))
    fig1.add_trace(go.Bar(x=x, y=water_depth, name="Water Depth [m]", marker_color="darkblue"))
    fig1.update_layout(title="Gate Opening vs. Water Depth", xaxis_title="Gate Number",
                       yaxis_title="Height [m]", barmode="group", xaxis=dict(dtick=1))
    st.plotly_chart(fig1, use_container_width=True)

    # Graph 2
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=x, y=flow_vt_chow, mode="lines+markers", name="V.T. Chow"))
    fig2.add_trace(go.Scatter(x=x, y=flow_corps_ref, mode="lines+markers", name="Corps Ref"))
    fig2.update_layout(title="Flowrate Comparison", xaxis_title="Gate Number", yaxis_title="Flowrate [m³/s]")
    st.plotly_chart(fig2, use_container_width=True)

    # Graph 3
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(x=x, y=relative_error, marker_color="orange"))
    fig3.update_layout(title="Percent Error Between Methods", xaxis_title="Gate", yaxis_title="Error [%]")
    st.plotly_chart(fig3, use_container_width=True)





