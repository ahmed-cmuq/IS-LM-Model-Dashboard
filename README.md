# Macro Dashboard v6

An interactive dashboard for teaching and learning the IS-LM and Keynesian Cross models, built with Streamlit and Plotly.

This version features a simplified and more direct control scheme for the investment function. It removes the previous indirect anchor-based calibration in favor of direct manipulation of the core economic parameters:
- **$b_0$**: autonomous investment
- **$b_1$**: the marginal propensity to invest
- **$b_2$**: interest rate sensitivity of investment

This provides a more intuitive way to explore how different components of investment affect the overall economic equilibrium.

## How to Run

1.  Ensure you have Python installed.
2.  Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```
3.  Run the Streamlit app from your terminal:
    ```bash
    streamlit run app.py
    ```
