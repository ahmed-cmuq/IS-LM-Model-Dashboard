import numpy as np
import plotly.graph_objects as go
import streamlit as st

# This dashboard is designed to be self-contained and does not require
# the streamlit_js_eval library for its core functionality.
# We'll use a fixed width for responsive layout calculations.
WW = 1200 

from models import KCParams, kc_equilibrium, kc_locus

st.set_page_config(page_title="Macro Dashboard v6", layout="wide")

# Default values for all economic parameters and chart settings.
# These are loaded into the session state on first run.
DEFAULTS = dict(
    a=20.0,      # Autonomous consumption
    c=0.6,       # Marginal propensity to consume
    T=10.0,      # Taxes
    G=50.0,      # Government spending
    b0=30.0,     # Autonomous investment
    b1=0.2,      # Marginal propensity to invest
    b2=10.0,     # Investment sensitivity to interest rate
    i=0.50,      # Current interest rate
    i_max=4.0,   # Maximum interest rate for the y-axis of the IS-LM chart
    Xmax=600.0   # Maximum value for the x-axis (Income Y) on both charts
)

# Initialize session state for user inputs and baseline storage
if "inputs" not in st.session_state:
    st.session_state.inputs = DEFAULTS.copy()
if "baseline" not in st.session_state:
    st.session_state.baseline = None

def reset_all():
    """Resets all inputs to their default values and clears the baseline."""
    st.session_state.inputs = DEFAULTS.copy()
    st.session_state.baseline = None
    st.rerun()

# Set a fixed height for the charts
chart_h = 450

# --- UI LAYOUT ---
# Create a responsive layout with controls on the sides and charts in the middle.
left, mid, right = st.columns([1, 2, 1], gap="large")

# --- LEFT PANEL: CONTROLS (Consumption & Fiscal) ---
with left:
    st.header("Parameters")
    st.subheader("Consumption & Fiscal Policy")
    a = st.number_input("a (autonomous consumption)", value=float(st.session_state.inputs["a"]), min_value=0.0, step=1.0, format="%.2f", key="a")
    c = st.slider("c (MPC)", 0.01, 0.99, float(st.session_state.inputs["c"]), 0.01, key="c")
    T = st.number_input("T (taxes)", value=float(st.session_state.inputs["T"]), min_value=0.0, step=1.0, format="%.2f", key="T")
    G = st.number_input("G (gov spending)", value=float(st.session_state.inputs["G"]), min_value=0.0, step=1.0, format="%.2f", key="G")

# --- RIGHT PANEL: CONTROLS (Investment, Monetary, etc.) ---
with right:
    # This blank header helps align the subheaders visually with the left column
    st.header(" ") 
    
    # --- Investment Rule ---
    st.subheader("Investment Rule")
    st.markdown(r"I = $b_0 + b_1 \cdot Y - b_2 \cdot i$")
    b0 = st.number_input("b₀ (autonomous investment)", value=float(st.session_state.inputs["b0"]), min_value=0.0, step=1.0, format="%.2f", key="b0")
    b1 = st.slider("b₁ (propensity to invest)", 0.0, 0.99 - c, float(st.session_state.inputs["b1"]), 0.01, key="b1", help="Note: 1 - c - b₁ must be > 0 for a stable equilibrium.")
    b2 = st.number_input("b₂ (interest rate sensitivity)", value=float(st.session_state.inputs["b2"]), min_value=0.0, step=1.0, format="%.2f", key="b2")

    # --- Monetary Policy & Chart Settings ---
    st.subheader("Monetary Policy & Chart Settings")
    i_max = st.number_input("i_max (max interest rate)", value=float(st.session_state.inputs["i_max"]), min_value=0.1, step=0.1, format="%.2f", key="i_max")
    i  = st.slider("i (current interest rate)", 0.0, float(i_max), float(st.session_state.inputs["i"]), 0.01, key="i")
    Xmax = st.slider("X-axis max (Y)", min_value=100.0, max_value=1500.0, value=float(st.session_state.inputs["Xmax"]), step=50.0, key="Xmax")

    # --- Action Buttons ---
    st.subheader("Actions")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Capture baseline"):
            st.session_state.baseline = dict(inputs=st.session_state.inputs.copy())
            st.success("Baseline captured.")
    with c2:
        if st.button("Reset All"):
            reset_all()


# Update session state with the current values from the UI widgets
st.session_state.inputs.update(dict(a=a,c=c,T=T,G=G,i=i,i_max=i_max,b0=b0,b1=b1,b2=b2,Xmax=Xmax))

# --- MODEL CALCULATIONS ---
# Instantiate the parameters dataclass with the current inputs
params = KCParams(a=a, c=c, T=T, G=G, i=i, i_max=i_max, b0=b0, b1=b1, b2=b2)
# Calculate the current equilibrium point for the Keynesian Cross
kc = kc_equilibrium(params)

# Define the data grids for plotting the curves
Ygrid = np.linspace(0, Xmax, int(Xmax) + 1)
igrid = np.linspace(0, i_max, 400)

# --- CHARTING ---
def apply_axes_style(fig, Xmax, Ymax, xtick, ytick, lock=True):
    """Helper function to apply consistent styling to chart axes."""
    fig.update_xaxes(range=[0, Xmax], tick0=0, dtick=xtick, ticklabelposition="outside",
                     tickangle=0, automargin=True, fixedrange=lock)
    fig.update_yaxes(range=[0, Ymax], tick0=0, dtick=ytick, ticklabelposition="outside",
                     tickangle=0, automargin=True, fixedrange=lock)
    return fig

# Calculate a shared tick value for the Y-axis (income) to sync the charts
ytick_shared = max(50, round(Xmax / 8 / 50) * 50)

with mid:
    # --- Keynesian Cross Chart ---
    st.subheader("Keynesian Cross")
    AD = kc["AD_intercept"] + kc["AD_slope"] * Ygrid
    fig_kc = go.Figure()
    fig_kc.add_trace(go.Scatter(x=Ygrid, y=AD, mode="lines", name="AD(Y)", line=dict(width=3)))
    fig_kc.add_trace(go.Scatter(x=Ygrid, y=Ygrid, mode="lines", name="45° line", line=dict(color='grey')))
    fig_kc.add_trace(go.Scatter(x=[kc["Y_star"]], y=[kc["Y_star"]], mode="markers+text", text=["Y*"], textposition="top right", name="Equilibrium", marker=dict(size=10)))
    
    # Plot baseline if it exists
    if st.session_state.baseline is not None:
        bi = st.session_state.baseline["inputs"]
        p_b = KCParams(a=bi["a"], c=bi["c"], T=bi["T"], G=bi["G"], i=bi["i"], i_max=bi["i_max"], b0=bi["b0"], b1=bi["b1"], b2=bi["b2"])
        kc_b = kc_equilibrium(p_b)
        AD_b = kc_b["AD_intercept"] + kc_b["AD_slope"] * Ygrid
        fig_kc.add_trace(go.Scatter(x=Ygrid, y=AD_b, mode="lines", name="AD (baseline)", line=dict(dash="dash")))

    fig_kc.update_layout(height=chart_h, xaxis_title="Income (Y)", yaxis_title="Aggregate Demand (Z)", legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))
    fig_kc = apply_axes_style(fig_kc, Xmax, Xmax, ytick_shared, ytick_shared, lock=True)
    st.plotly_chart(fig_kc, use_container_width=True)

    # --- IS-LM Chart ---
    st.subheader("IS–LM")
    LM = np.full_like(Ygrid, i)
    Yvals_IS = kc_locus(params, igrid)
    fig_is = go.Figure()
    fig_is.add_trace(go.Scatter(x=Yvals_IS, y=igrid, mode="lines", name="IS", line=dict(width=3)))
    fig_is.add_trace(go.Scatter(x=Ygrid, y=LM, mode="lines", name="LM (horizontal at i)", line=dict(width=3)))
    fig_is.add_trace(go.Scatter(x=[kc["Y_star"]], y=[i], mode="markers+text", text=["(Y*, i)"], textposition="top right", name="Equilibrium", marker=dict(size=10)))
    
    # Plot baseline if it exists
    if st.session_state.baseline is not None:
        bi = st.session_state.baseline["inputs"]
        p_b = KCParams(a=bi["a"], c=bi["c"], T=bi["T"], G=bi["G"], i=bi["i"], i_max=bi["i_max"], b0=bi["b0"], b1=bi["b1"], b2=bi["b2"])
        Yb_IS = kc_locus(p_b, igrid)
        fig_is.add_trace(go.Scatter(x=Yb_IS, y=igrid, mode="lines", name="IS (baseline)", line=dict(dash="dash")))
        fig_is.add_trace(go.Scatter(x=Ygrid, y=np.full_like(Ygrid, bi["i"]), mode="lines", name="LM (baseline)", line=dict(dash="dash")))

    fig_is.update_layout(height=chart_h, xaxis_title="Income (Y)", yaxis_title="Interest Rate (i)", legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99))
    itick = max(0.1, round(i_max / 8, 2))
    fig_is = apply_axes_style(fig_is, Xmax, i_max, ytick_shared, itick, lock=True)
    st.plotly_chart(fig_is, use_container_width=True)

# --- BOTTOM PANEL: CONCEPTS ---
concepts_md = r"""
### Keynesian Cross (KC)
The Keynesian Cross illustrates equilibrium in the goods market.

- **Aggregate Demand (Z):** The total demand for goods and services in an economy.
  $$ Z(Y) = C(Y_d) + I(Y, i) + G $$

- **Consumption (C):** $ C(Y_d) = a + c \cdot Y_d $, where $Y_d = Y - T$ is disposable income.
  - *$a$*: autonomous consumption (> 0)
  - *$c$*: marginal propensity to consume (MPC), $0 < c < 1$

- **Investment (I):** $ I(Y, i) = b_0 + b_1 \cdot Y - b_2 \cdot i $
  - *$b_0$*: autonomous investment (> 0)
  - *$b_1$*: marginal propensity to invest, $0 < b_1 < 1-c$
  - *$b_2$*: sensitivity of investment to the interest rate (> 0)

- **Equilibrium:** Occurs when production (Y) equals demand (Z).
  $$ Y^* = Z(Y^*) $$
  Solving for $Y^*$ gives the equilibrium income:
  $$ Y^* = \frac{a - cT + b_0 - b_2 i + G}{1 - c - b_1} $$
  The term $1/(1-c-b_1)$ is the **Keynesian multiplier**. For a stable equilibrium, we require $c+b_1 < 1$.

---
### IS–LM Model
- **IS Curve:** Represents all combinations of interest rates (i) and income levels (Y) where the **goods market** is in equilibrium. It's derived directly from the Keynesian Cross equilibrium condition. The curve is downward sloping because a higher interest rate *i* reduces investment, which lowers aggregate demand and thus the equilibrium level of income $Y^*$.

- **LM Curve:** Represents equilibrium in the **money market**. In this simplified model, we assume the central bank sets a target interest rate *i*, so the **LM curve is horizontal** at that level. The intersection of the IS and LM curves shows the overall short-run equilibrium for the economy.
"""
st.markdown("---")
with st.expander("Key Concepts & Formulas", expanded=True):
    st.markdown(concepts_md)
