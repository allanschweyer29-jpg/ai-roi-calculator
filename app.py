"""
AI Investment ROI Calculator and Work Redesigner
Emphasizes the critical role of work design in realizing AI value
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np

# Page configuration
st.set_page_config(
    page_title="AI Investment ROI Calculator and Work Redesigner",
    page_icon="🤖",
    layout="wide"
)

# Logo and title
col_logo, col_title = st.columns([1, 6])
with col_logo:
    st.image("tcb_logoUpdate.png", width=180)
with col_title:
    st.title("🤖 AI Investment ROI Calculator and Work Redesigner")
st.markdown("""
### The Value of AI Depends on Work Design, Not Just Technology

This tool models how **strategic reallocation of human capacity** creates value—not the AI itself.
The critical variables are all about **how you manage people and work**, not which AI you buy.
""")

# Sidebar for inputs
st.sidebar.header("📊 Organization Setup")

# Organization Context
org_name = st.sidebar.text_input("Department/Organization", "Marketing Operations")
team_size = st.sidebar.number_input("Team Size (FTE)", min_value=1, value=25, step=1)
avg_compensation = st.sidebar.number_input("Average Fully Loaded Compensation ($)", 
                                           min_value=50000, value=120000, step=5000)

st.sidebar.markdown("---")
st.sidebar.header("🤖 AI Implementation")

# AI Parameters
hours_savable = st.sidebar.number_input("Total Annual Hours Savable", 
                                        min_value=100, value=5450, step=100,
                                        help="Hours that AI could theoretically save per year")

adoption_speed = st.sidebar.selectbox(
    "Adoption Speed",
    ["Cautious (40/75/95%)", "Moderate (50/85/95%)", "Aggressive (60/90/98%)"],
    index=1,
    help="Percentage of savable hours actually achieved in each phase"
)

tech_cost = st.sidebar.number_input("Monthly Technology Cost ($)", 
                                    min_value=0, value=10000, step=1000)
governance_cost = st.sidebar.number_input("Monthly Governance Cost ($)", 
                                          min_value=0, value=3000, step=500)

st.sidebar.markdown("---")
st.sidebar.header("💡 Work Design Parameters")

st.sidebar.markdown("""
**These are the variables that determine success:**
- **RR**: Are you *deliberately* reinvesting freed time?
- **PM**: Is new work *more productive*?
- **QP**: Are outcomes *higher quality*?
- **IV**: Are you *innovating* with freed capacity?
""")

scenario_type = st.sidebar.selectbox(
    "Scenario Type",
    ["Conservative", "Expected", "Optimistic", "Custom"],
    index=1
)

# Define scenario parameters
scenarios = {
    "Conservative": {
        "rr": [0.35, 0.50, 0.60],
        "pm": [0.10, 0.20, 0.30],
        "qp": [0.05, 0.15, 0.25],
        "iv_start": 15,
        "iv_peak": 80000,
        "change_mgmt": [8000, 2000, 500],
        "co_hours": [90, 60, 40]
    },
    "Expected": {
        "rr": [0.40, 0.60, 0.70],
        "pm": [0.15, 0.30, 0.40],
        "qp": [0.10, 0.25, 0.35],
        "iv_start": 12,
        "iv_peak": 160000,
        "change_mgmt": [8000, 2000, 500],
        "co_hours": [90, 50, 35]
    },
    "Optimistic": {
        "rr": [0.50, 0.70, 0.80],
        "pm": [0.20, 0.40, 0.60],
        "qp": [0.15, 0.35, 0.50],
        "iv_start": 9,
        "iv_peak": 250000,
        "change_mgmt": [6000, 1500, 500],
        "co_hours": [70, 40, 25]
    }
}

# Get adoption curve
adoption_curves = {
    "Cautious (40/75/95%)": [0.40, 0.75, 0.95],
    "Moderate (50/85/95%)": [0.50, 0.85, 0.95],
    "Aggressive (60/90/98%)": [0.60, 0.90, 0.98]
}
adoption_curve = adoption_curves[adoption_speed]

# Custom scenario inputs
if scenario_type == "Custom":
    st.sidebar.markdown("#### Phase 1 (Months 1-6): Learning")
    rr1 = st.sidebar.slider("Reinvestment Rate (%)", 0, 100, 40, help="% of freed time redirected to productive work") / 100
    pm1 = st.sidebar.slider("Productivity Multiplier (%)", 0, 100, 15, help="% increase in output per hour") / 100
    qp1 = st.sidebar.slider("Quality Premium (%)", 0, 100, 10, help="% improvement in outcome value") / 100
    
    st.sidebar.markdown("#### Phase 2 (Months 7-12): Scaling")
    rr2 = st.sidebar.slider("Reinvestment Rate (%) ", 0, 100, 60, key="rr2") / 100
    pm2 = st.sidebar.slider("Productivity Multiplier (%) ", 0, 100, 30, key="pm2") / 100
    qp2 = st.sidebar.slider("Quality Premium (%) ", 0, 100, 25, key="qp2") / 100
    
    st.sidebar.markdown("#### Phase 3 (Months 13-18): Maturity")
    rr3 = st.sidebar.slider("Reinvestment Rate (%)  ", 0, 100, 70, key="rr3") / 100
    pm3 = st.sidebar.slider("Productivity Multiplier (%)  ", 0, 100, 40, key="pm3") / 100
    qp3 = st.sidebar.slider("Quality Premium (%)  ", 0, 100, 35, key="qp3") / 100
    
    st.sidebar.markdown("#### Innovation Value")
    iv_start = st.sidebar.number_input("Start Month", 1, 24, 12)
    iv_peak = st.sidebar.number_input("Peak Monthly Value ($)", 0, 500000, 160000, step=10000)
    
    params = {
        "rr": [rr1, rr2, rr3],
        "pm": [pm1, pm2, pm3],
        "qp": [qp1, qp2, qp3],
        "iv_start": iv_start,
        "iv_peak": iv_peak,
        "change_mgmt": [8000, 2000, 500],
        "co_hours": [90, 50, 35]
    }
else:
    params = scenarios[scenario_type]

# Calculate hourly rate
hourly_rate = avg_compensation / 2000

# Function to get phase
def get_phase(month):
    if month <= 6:
        return 0
    elif month <= 12:
        return 1
    else:
        return 2

# Function to calculate hours saved
def calculate_hours_saved(month, adoption_curve, hours_savable):
    phase = get_phase(month)
    monthly_savable = hours_savable / 12
    return monthly_savable * adoption_curve[phase]

# Function to calculate innovation value
def calculate_innovation_value(month, iv_start, iv_peak):
    if month < iv_start:
        return 0
    months_since_start = month - iv_start
    # Ramp up over 6 months
    if months_since_start <= 6:
        return iv_peak * (months_since_start / 6)
    return iv_peak

# Function to calculate coordination overhead
def calculate_coordination_overhead(month, co_hours, hourly_rate):
    phase = get_phase(month)
    return co_hours[phase] * hourly_rate

# Calculate monthly values
def calculate_monthly_roi(month, params, adoption_curve, hours_savable, hourly_rate, 
                         tech_cost, governance_cost):
    phase = get_phase(month)
    
    # Hours saved
    hs = calculate_hours_saved(month, adoption_curve, hours_savable)
    
    # Get phase parameters
    rr = params["rr"][phase]
    pm = params["pm"][phase]
    qp = params["qp"][phase]
    
    # Calculate value creation
    capacity_value = hs * hourly_rate * rr
    multiplier_effect = (1 + pm) * (1 + qp)
    reinvestment_value = capacity_value * multiplier_effect
    
    # Innovation value
    iv = calculate_innovation_value(month, params["iv_start"], params["iv_peak"])
    
    value_created = reinvestment_value + iv
    
    # Calculate costs
    rc = tech_cost + governance_cost + params["change_mgmt"][phase]
    co = calculate_coordination_overhead(month, params["co_hours"], hourly_rate)
    
    value_destroyed = rc + co
    
    # Net value
    net_value = value_created - value_destroyed
    
    return {
        "month": month,
        "phase": phase + 1,
        "hours_saved": hs,
        "reinvestment_rate": rr,
        "productivity_mult": pm,
        "quality_premium": qp,
        "capacity_value": capacity_value,
        "reinvestment_value": reinvestment_value,
        "innovation_value": iv,
        "value_created": value_created,
        "tech_costs": tech_cost,
        "governance_costs": governance_cost,
        "change_mgmt_costs": params["change_mgmt"][phase],
        "coordination_overhead": co,
        "total_costs": value_destroyed,
        "net_value": net_value
    }

# Generate 24 months of data
months = range(1, 25)
results = [calculate_monthly_roi(m, params, adoption_curve, hours_savable, hourly_rate, 
                                 tech_cost, governance_cost) for m in months]

# Create DataFrame
df = pd.DataFrame(results)
df["cumulative_value"] = df["net_value"].cumsum()

# Main content area
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
    "📈 Executive Summary",
    "💰 Value Over Time",
    "🔍 Sensitivity Analysis",
    "⚙️ Work Design Impact",
    "📊 Detailed Breakdown",
    "📋 Metrics Guide",
    "🔬 Task Deconstruction",
    "🏗️ Redeployment Dashboard",
    "🤖 AI Type Recommender"
])

with tab1:
    st.header("Executive Summary")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    breakeven_month = df[df["cumulative_value"] >= 0]["month"].min() if any(df["cumulative_value"] >= 0) else "Not reached"
    total_18mo_value = df[df["month"] <= 18]["net_value"].sum()
    total_24mo_value = df["net_value"].sum()
    avg_monthly_value_final = df[df["month"] >= 13]["net_value"].mean()
    
    with col1:
        st.metric("Breakeven Month", 
                 f"Month {breakeven_month}" if breakeven_month != "Not reached" else "Not in 24mo")
    with col2:
        st.metric("18-Month Value", f"${total_18mo_value:,.0f}")
    with col3:
        st.metric("24-Month Value", f"${total_24mo_value:,.0f}")
    with col4:
        st.metric("Avg Monthly (Phase 3)", f"${avg_monthly_value_final:,.0f}")
    
    st.markdown("---")
    
    # Key insights
    st.subheader("💡 Key Insights")
    
    phase3_rr = params["rr"][2]
    phase3_pm = params["pm"][2]
    phase3_qp = params["qp"][2]
    
    insights = []
    
    if phase3_rr < 0.60:
        insights.append(f"⚠️ **Low Reinvestment Rate ({phase3_rr:.0%})**: You're only redirecting {phase3_rr:.0%} of freed time to productive work. This is the #1 limiter of value. Consider: Are roles being redesigned? Is there accountability for strategic work?")
    elif phase3_rr >= 0.70:
        insights.append(f"✅ **Strong Reinvestment ({phase3_rr:.0%})**: You're effectively redirecting freed capacity to productive work. This requires excellent work design and governance.")
    
    if phase3_pm < 0.25:
        insights.append(f"⚠️ **Low Productivity Gains ({phase3_pm:.0%})**: The new work isn't significantly more productive. Consider: Do people have the skills for elevated work? Are workflows optimized?")
    elif phase3_pm >= 0.40:
        insights.append(f"✅ **High Productivity ({phase3_pm:+.0%})**: Your team is generating substantially more output with reinvested time. This suggests good capability match.")
    
    if phase3_qp < 0.20:
        insights.append(f"⚠️ **Marginal Quality Improvement ({phase3_qp:.0%})**: Outcomes aren't much better despite elevated work. Consider: Are people working on truly higher-value activities?")
    elif phase3_qp >= 0.35:
        insights.append(f"✅ **Quality Premium ({phase3_qp:+.0%})**: Work quality is significantly improved. This drives revenue, margin, and competitive advantage.")
    
    if params["iv_peak"] < 100000:
        insights.append(f"⚠️ **Limited Innovation**: Freed capacity isn't generating new capabilities or revenue streams. Consider: Are you being strategic enough with reclaimed time?")
    elif params["iv_peak"] >= 150000:
        insights.append(f"✅ **Innovation Value (${params['iv_peak']:,.0f}/mo)**: You're using freed capacity to build new capabilities. This is where exponential value lives.")
    
    for insight in insights:
        st.markdown(insight)
    
    st.markdown("---")
    
    # The equation
    st.subheader("📐 The ROI Equation")
    st.latex(r"\text{Monthly Value} = \text{Value Created} - \text{Costs}")
    st.latex(r"\text{Value Created} = [HS \times Rate \times RR \times (1 + PM) \times (1 + QP)] + IV")
    st.latex(r"\text{Costs} = RC + CO")
    
    st.markdown("""
    **Where:**
    - **HS** = Hours Saved by AI
    - **Rate** = Hourly compensation
    - **RR** = Reinvestment Rate (% of freed time productively redirected)
    - **PM** = Productivity Multiplier (output increase per hour)
    - **QP** = Quality Premium (outcome value improvement)
    - **IV** = Innovation Value (new revenue streams)
    - **RC** = Risk Cost (tech + governance + change management)
    - **CO** = Coordination Overhead (new friction costs)
    """)

with tab2:
    st.header("Value Creation Over Time")
    
    # Create value over time chart
    fig = make_subplots(
        rows=2, cols=1,
        row_heights=[0.7, 0.3],
        subplot_titles=("Cumulative Value", "Monthly Net Value"),
        vertical_spacing=0.15
    )
    
    # Cumulative value
    fig.add_trace(
        go.Scatter(x=df["month"], y=df["cumulative_value"],
                  mode='lines+markers',
                  name='Cumulative Value',
                  line=dict(color='rgb(31, 119, 180)', width=3),
                  fill='tozeroy',
                  fillcolor='rgba(31, 119, 180, 0.2)'),
        row=1, col=1
    )
    
    # Add breakeven line
    fig.add_hline(y=0, line_dash="dash", line_color="gray", row=1, col=1)
    
    # Monthly value
    colors = ['red' if x < 0 else 'green' for x in df["net_value"]]
    fig.add_trace(
        go.Bar(x=df["month"], y=df["net_value"],
              name='Monthly Value',
              marker_color=colors),
        row=2, col=1
    )
    
    fig.update_xaxes(title_text="Month", row=2, col=1)
    fig.update_yaxes(title_text="Cumulative Value ($)", row=1, col=1)
    fig.update_yaxes(title_text="Monthly Value ($)", row=2, col=1)
    
    fig.update_layout(height=700, showlegend=False)
    st.plotly_chart(fig, width="stretch")
    
    # Value breakdown stacked area
    st.subheader("Value Components Over Time")
    
    fig2 = go.Figure()
    
    fig2.add_trace(go.Scatter(
        x=df["month"], y=df["capacity_value"],
        mode='lines',
        name='Base Capacity Value',
        stackgroup='one',
        line=dict(width=0.5)
    ))
    
    fig2.add_trace(go.Scatter(
        x=df["month"], y=df["reinvestment_value"] - df["capacity_value"],
        mode='lines',
        name='Productivity & Quality Gains',
        stackgroup='one',
        line=dict(width=0.5)
    ))
    
    fig2.add_trace(go.Scatter(
        x=df["month"], y=df["innovation_value"],
        mode='lines',
        name='Innovation Value',
        stackgroup='one',
        line=dict(width=0.5)
    ))
    
    fig2.update_layout(
        title="How Value is Created",
        xaxis_title="Month",
        yaxis_title="Monthly Value ($)",
        height=400
    )
    
    st.plotly_chart(fig2, width="stretch")

with tab3:
    st.header("Sensitivity Analysis: What Matters Most?")
    
    st.markdown("""
    This analysis shows how much total 18-month value changes when each variable moves ±10%.
    **The wider the bar, the more that variable controls your success.**
    """)
    
    # Calculate baseline 18-month value
    baseline_value = df[df["month"] <= 18]["net_value"].sum()
    
    # Test sensitivity for key parameters
    sensitivity_results = []
    
    def calculate_total_value_18mo(params_modified):
        results_mod = [calculate_monthly_roi(m, params_modified, adoption_curve, hours_savable, 
                                            hourly_rate, tech_cost, governance_cost) 
                      for m in range(1, 19)]
        df_mod = pd.DataFrame(results_mod)
        return df_mod["net_value"].sum()
    
    # Test RR
    params_test = params.copy()
    params_test["rr"] = [x * 1.1 for x in params["rr"]]
    value_rr_up = calculate_total_value_18mo(params_test)
    params_test["rr"] = [x * 0.9 for x in params["rr"]]
    value_rr_down = calculate_total_value_18mo(params_test)
    sensitivity_results.append({
        "Variable": "Reinvestment Rate (RR)",
        "Impact": (value_rr_up - value_rr_down) / 2,
        "% Change": ((value_rr_up - value_rr_down) / 2) / baseline_value * 100 if baseline_value != 0 else 0
    })
    
    # Test PM
    params_test = params.copy()
    params_test["pm"] = [x * 1.1 for x in params["pm"]]
    value_pm_up = calculate_total_value_18mo(params_test)
    params_test["pm"] = [x * 0.9 for x in params["pm"]]
    value_pm_down = calculate_total_value_18mo(params_test)
    sensitivity_results.append({
        "Variable": "Productivity Multiplier (PM)",
        "Impact": (value_pm_up - value_pm_down) / 2,
        "% Change": ((value_pm_up - value_pm_down) / 2) / baseline_value * 100 if baseline_value != 0 else 0
    })
    
    # Test QP
    params_test = params.copy()
    params_test["qp"] = [x * 1.1 for x in params["qp"]]
    value_qp_up = calculate_total_value_18mo(params_test)
    params_test["qp"] = [x * 0.9 for x in params["qp"]]
    value_qp_down = calculate_total_value_18mo(params_test)
    sensitivity_results.append({
        "Variable": "Quality Premium (QP)",
        "Impact": (value_qp_up - value_qp_down) / 2,
        "% Change": ((value_qp_up - value_qp_down) / 2) / baseline_value * 100 if baseline_value != 0 else 0
    })
    
    # Test IV
    params_test = params.copy()
    params_test["iv_peak"] = params["iv_peak"] * 1.1
    value_iv_up = calculate_total_value_18mo(params_test)
    params_test["iv_peak"] = params["iv_peak"] * 0.9
    value_iv_down = calculate_total_value_18mo(params_test)
    sensitivity_results.append({
        "Variable": "Innovation Value (IV)",
        "Impact": (value_iv_up - value_iv_down) / 2,
        "% Change": ((value_iv_up - value_iv_down) / 2) / baseline_value * 100 if baseline_value != 0 else 0
    })
    
    # Test adoption speed
    adoption_up = [min(1.0, x * 1.1) for x in adoption_curve]
    adoption_down = [x * 0.9 for x in adoption_curve]
    results_adoption_up = [calculate_monthly_roi(m, params, adoption_up, hours_savable, 
                                                 hourly_rate, tech_cost, governance_cost) 
                          for m in range(1, 19)]
    results_adoption_down = [calculate_monthly_roi(m, params, adoption_down, hours_savable, 
                                                   hourly_rate, tech_cost, governance_cost) 
                            for m in range(1, 19)]
    value_adoption_up = pd.DataFrame(results_adoption_up)["net_value"].sum()
    value_adoption_down = pd.DataFrame(results_adoption_down)["net_value"].sum()
    sensitivity_results.append({
        "Variable": "Adoption Speed",
        "Impact": (value_adoption_up - value_adoption_down) / 2,
        "% Change": ((value_adoption_up - value_adoption_down) / 2) / baseline_value * 100 if baseline_value != 0 else 0
    })
    
    sens_df = pd.DataFrame(sensitivity_results)
    sens_df = sens_df.sort_values("Impact", ascending=True)
    
    # Create tornado chart
    fig_sens = go.Figure()
    
    colors_sens = ['#d62728' if x < 0 else '#2ca02c' for x in sens_df["Impact"]]
    
    fig_sens.add_trace(go.Bar(
        y=sens_df["Variable"],
        x=sens_df["Impact"],
        orientation='h',
        marker_color=colors_sens,
        text=[f"${x:,.0f}" for x in sens_df["Impact"]],
        textposition='outside'
    ))
    
    fig_sens.update_layout(
        title="Impact of ±10% Change in Each Variable on 18-Month Value",
        xaxis_title="Change in Total Value ($)",
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig_sens, width="stretch")
    
    st.markdown("### 💡 What This Tells You")
    
    top_driver = sens_df.iloc[-1]
    st.markdown(f"""
    **{top_driver['Variable']}** is your most sensitive variable. A 10% improvement here creates 
    **${top_driver['Impact']:,.0f}** in additional value.
    
    This is why **work design matters more than technology selection**. The variables you control through 
    leadership decisions (RR, PM, QP) typically dominate the technology variables.
    """)

with tab4:
    st.header("Work Design Impact Scenarios")
    
    st.markdown("""
    Compare three different approaches to managing freed capacity. Same AI, same team, same costs—
    but radically different outcomes based on **how you design and govern the work**.
    """)
    
    # Define three work design scenarios
    poor_design = {
        "name": "Poor Work Design",
        "description": "No role redesign, minimal governance, freed time drifts",
        "rr": [0.25, 0.35, 0.45],
        "pm": [0.05, 0.10, 0.15],
        "qp": [0.02, 0.08, 0.12],
        "iv_start": 18,
        "iv_peak": 40000,
        "change_mgmt": [5000, 1000, 500],
        "co_hours": [120, 90, 70]
    }
    
    good_design = {
        "name": "Good Work Design",
        "description": "Deliberate role redesign, active governance, strategic focus",
        "rr": [0.50, 0.65, 0.75],
        "pm": [0.20, 0.35, 0.45],
        "qp": [0.15, 0.28, 0.38],
        "iv_start": 11,
        "iv_peak": 180000,
        "change_mgmt": [9000, 2500, 500],
        "co_hours": [80, 45, 30]
    }
    
    excellent_design = {
        "name": "Excellent Work Design",
        "description": "Comprehensive transformation, clear accountability, innovation focus",
        "rr": [0.60, 0.75, 0.85],
        "pm": [0.25, 0.45, 0.65],
        "qp": [0.20, 0.38, 0.52],
        "iv_start": 9,
        "iv_peak": 280000,
        "change_mgmt": [12000, 3000, 800],
        "co_hours": [70, 35, 20]
    }
    
    # Calculate for all three scenarios
    scenarios_comparison = []
    
    for scenario_params in [poor_design, good_design, excellent_design]:
        results_scenario = [calculate_monthly_roi(m, scenario_params, adoption_curve, hours_savable,
                                                  hourly_rate, tech_cost, governance_cost) 
                          for m in range(1, 25)]
        df_scenario = pd.DataFrame(results_scenario)
        df_scenario["cumulative_value"] = df_scenario["net_value"].cumsum()
        df_scenario["scenario"] = scenario_params["name"]
        scenarios_comparison.append(df_scenario)
    
    df_all_scenarios = pd.concat(scenarios_comparison)
    
    # Plot comparison
    fig_comp = go.Figure()
    
    for scenario_name, color in [("Poor Work Design", "red"), 
                                  ("Good Work Design", "blue"), 
                                  ("Excellent Work Design", "green")]:
        df_scen = df_all_scenarios[df_all_scenarios["scenario"] == scenario_name]
        fig_comp.add_trace(go.Scatter(
            x=df_scen["month"],
            y=df_scen["cumulative_value"],
            mode='lines+markers',
            name=scenario_name,
            line=dict(width=3, color=color)
        ))
    
    fig_comp.add_hline(y=0, line_dash="dash", line_color="gray")
    
    fig_comp.update_layout(
        title="Same AI, Same Team, Different Work Design = Radically Different Results",
        xaxis_title="Month",
        yaxis_title="Cumulative Value ($)",
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig_comp, width="stretch")
    
    # Show the differences
    st.subheader("24-Month Results Comparison")
    
    col1, col2, col3 = st.columns(3)
    
    poor_24mo = df_all_scenarios[df_all_scenarios["scenario"] == "Poor Work Design"]["net_value"].sum()
    good_24mo = df_all_scenarios[df_all_scenarios["scenario"] == "Good Work Design"]["net_value"].sum()
    excellent_24mo = df_all_scenarios[df_all_scenarios["scenario"] == "Excellent Work Design"]["net_value"].sum()
    
    with col1:
        st.metric("Poor Work Design", 
                 f"${poor_24mo:,.0f}",
                 delta=None)
        st.caption("Minimal reinvestment, low governance")
    
    with col2:
        st.metric("Good Work Design", 
                 f"${good_24mo:,.0f}",
                 delta=f"+${good_24mo - poor_24mo:,.0f} vs Poor",
                 delta_color="normal")
        st.caption("Deliberate role redesign")
    
    with col3:
        st.metric("Excellent Work Design", 
                 f"${excellent_24mo:,.0f}",
                 delta=f"+${excellent_24mo - poor_24mo:,.0f} vs Poor",
                 delta_color="normal")
        st.caption("Full transformation + innovation")
    
    st.markdown("---")
    
    st.markdown(f"""
    ### 🎯 The Work Design Premium
    
    The difference between poor and excellent work design is **${excellent_24mo - poor_24mo:,.0f}** over 24 months—
    with the **exact same AI technology**.
    
    **This is why two companies with identical AI get radically different results.**
    
    The determining factors:
    - **Role Redesign**: Are jobs explicitly redefined for higher-value work?
    - **Governance**: Is there accountability for productive reinvestment?
    - **Capability Development**: Do people have skills for elevated responsibilities?
    - **Strategic Intent**: Are you using freed capacity for innovation vs. just efficiency?
    - **Change Investment**: Are you investing in the transformation, not just the technology?
    """)

with tab5:
    st.header("Detailed Monthly Breakdown")
    
    # Format the dataframe for display
    display_df = df[[
        "month", "phase", "hours_saved", "reinvestment_rate", 
        "productivity_mult", "quality_premium",
        "value_created", "total_costs", "net_value", "cumulative_value"
    ]].copy()
    
    display_df.columns = [
        "Month", "Phase", "Hours Saved", "RR", "PM", "QP",
        "Value Created", "Costs", "Net Value", "Cumulative"
    ]
    
    # Format percentages
    display_df["RR"] = display_df["RR"].apply(lambda x: f"{x:.1%}")
    display_df["PM"] = display_df["PM"].apply(lambda x: f"{x:+.1%}")
    display_df["QP"] = display_df["QP"].apply(lambda x: f"{x:+.1%}")
    
    # Format currency
    for col in ["Value Created", "Costs", "Net Value", "Cumulative"]:
        display_df[col] = display_df[col].apply(lambda x: f"${x:,.0f}")
    
    # Format hours
    display_df["Hours Saved"] = display_df["Hours Saved"].apply(lambda x: f"{x:.0f}")
    
    st.dataframe(display_df, width="stretch", height=600)
    
    # Download button
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download Full Data (CSV)",
        data=csv,
        file_name=f"ai_roi_analysis_{org_name.replace(' ', '_')}.csv",
        mime="text/csv"
    )

with tab6:
    st.header("📋 Metrics Guide: Measuring Higher-Value Work")
    
    st.markdown("""
    Use this guide to define what "higher-value work" means for your department and how to measure 
    the **Productivity Multiplier (PM)** and **Quality Premium (QP)** in your context.
    """)
    
    # Department selector
    department = st.selectbox(
        "Select Your Department/Function",
        [
            "Sales & Business Development",
            "Customer Success & Support",
            "Product & Engineering",
            "Marketing",
            "Finance & Accounting",
            "Human Resources",
            "Legal & Compliance",
            "Operations & Supply Chain",
            "Research & Development",
            "Executive Leadership",
            "Custom (Define Your Own)"
        ]
    )
    
    # Define metrics for each department
    metrics_library = {
        "Sales & Business Development": {
            "pm_metrics": [
                "Sales calls per week (e.g., 15 → 22 = +47% PM)",
                "Deals closed per quarter (e.g., 8 → 12 = +50% PM)",
                "Proposals completed (e.g., 10 → 14 = +40% PM)",
                "Strategic account meetings (e.g., 5 → 8 = +60% PM)",
                "Pipeline opportunities created (e.g., 20 → 28 = +40% PM)"
            ],
            "qp_metrics": [
                "Win rate improvement (e.g., 25% → 30% = +20% QP)",
                "Average deal size increase (e.g., $45K → $52K = +16% QP)",
                "Sales cycle time reduction (e.g., 90 days → 75 days = +17% QP)",
                "Customer lifetime value growth (e.g., $180K → $220K = +22% QP)",
                "Pipeline velocity increase (e.g., 60 days/stage → 45 days = +25% QP)"
            ],
            "typical_pm": "+30% to +50%",
            "typical_qp": "+25% to +40%",
            "notes": "Sales teams often see high PM gains from freed capacity going to customer-facing activities. QP improvements come from better deal quality and strategic engagement."
        },
        "Customer Success & Support": {
            "pm_metrics": [
                "Complex cases resolved per week (e.g., 25 → 32 = +28% PM)",
                "Proactive outreach volume (e.g., 10 → 15 accounts/week = +50% PM)",
                "Strategic account reviews completed (e.g., 5 → 8 per month = +60% PM)",
                "Customer training sessions delivered (e.g., 3 → 5 per week = +67% PM)",
                "Health score assessments completed (e.g., 20 → 28 = +40% PM)"
            ],
            "qp_metrics": [
                "Customer retention rate improvement (e.g., 88% → 92% = +5% QP)",
                "Net Promoter Score increase (e.g., 42 → 51 = +21% QP)",
                "CSAT score improvement (e.g., 82% → 89% = +9% QP)",
                "Time to resolution reduction (e.g., 4 hours → 3 hours = +25% QP)",
                "Account expansion revenue (e.g., $50K → $65K = +30% QP)"
            ],
            "typical_pm": "+25% to +40%",
            "typical_qp": "+15% to +30%",
            "notes": "Support teams benefit from focusing on complex issues and proactive engagement. QP gains show up in retention and customer satisfaction metrics."
        },
        "Product & Engineering": {
            "pm_metrics": [
                "Features shipped per sprint (e.g., 8 → 11 = +38% PM)",
                "Story points completed (e.g., 45 → 63 = +40% PM)",
                "Architecture decisions made (e.g., 2 → 4 per quarter = +100% PM)",
                "Technical debt items addressed (e.g., 5 → 8 per sprint = +60% PM)",
                "Innovation experiments run (e.g., 3 → 6 per quarter = +100% PM)"
            ],
            "qp_metrics": [
                "System uptime improvement (e.g., 99.5% → 99.9% = +0.4% uptime, high $ value)",
                "Post-release bug reduction (e.g., 12 → 6 per sprint = +50% QP)",
                "Code review quality scores (e.g., 3.2 → 3.8 out of 5 = +19% QP)",
                "Technical debt reduction (measured in downtime/maintenance cost avoided)",
                "Patent applications filed (e.g., 1 → 3 per year = innovation premium)"
            ],
            "typical_pm": "+30% to +45%",
            "typical_qp": "+25% to +40%",
            "notes": "Engineering sees PM gains from focusing on architecture vs. bug fixes. QP improvements in reliability and quality have high business value."
        },
        "Marketing": {
            "pm_metrics": [
                "Campaigns launched per quarter (e.g., 8 → 12 = +50% PM)",
                "Content pieces created (e.g., 40 → 65 per month = +63% PM)",
                "Market research studies completed (e.g., 2 → 4 per quarter = +100% PM)",
                "A/B tests run (e.g., 10 → 16 per month = +60% PM)",
                "Strategic audience segments analyzed (e.g., 5 → 8 = +60% PM)"
            ],
            "qp_metrics": [
                "Campaign ROI improvement (e.g., 3.2x → 4.3x = +34% QP)",
                "Conversion rate increase (e.g., 2.1% → 2.8% = +33% QP)",
                "Lead quality score improvement (e.g., avg 6.5 → 8.2 = +26% QP)",
                "Customer acquisition cost reduction (e.g., $850 → $680 = +20% QP)",
                "Brand engagement metrics (e.g., engagement depth +40%)"
            ],
            "typical_pm": "+40% to +60%",
            "typical_qp": "+25% to +40%",
            "notes": "Marketing often sees highest PM gains from volume increase. QP improvements in targeting and messaging directly impact conversion and CAC."
        },
        "Finance & Accounting": {
            "pm_metrics": [
                "Strategic analyses completed (e.g., 3 → 7 per quarter = +133% PM)",
                "Financial models built (e.g., 2 → 4 per month = +100% PM)",
                "Risk assessments conducted (e.g., 5 → 9 per quarter = +80% PM)",
                "Business partner meetings (e.g., 10 → 16 per month = +60% PM)",
                "Process improvement initiatives (e.g., 2 → 4 per quarter = +100% PM)"
            ],
            "qp_metrics": [
                "Forecast accuracy improvement (e.g., ±8% variance → ±3% = +63% QP)",
                "Close cycle time reduction (e.g., 8 days → 5 days = +38% QP)",
                "Audit findings reduction (e.g., 12 → 4 findings = +67% QP)",
                "Working capital optimization (measurable $ value)",
                "Strategic insights influencing decisions (tracked by business impact)"
            ],
            "typical_pm": "+50% to +80%",
            "typical_qp": "+15% to +25%",
            "notes": "Finance sees dramatic PM gains as time shifts from processing to analysis. QP shows in accuracy and strategic value of insights."
        },
        "Human Resources": {
            "pm_metrics": [
                "Hires completed per quarter (e.g., 12 → 18 = +50% PM)",
                "Strategic workforce planning projects (e.g., 1 → 3 per year = +200% PM)",
                "Leadership development sessions (e.g., 8 → 13 per quarter = +63% PM)",
                "Organizational design initiatives (e.g., 2 → 4 per year = +100% PM)",
                "Culture programs launched (e.g., 3 → 6 per year = +100% PM)"
            ],
            "qp_metrics": [
                "Time to fill reduction (e.g., 45 days → 32 days = +29% QP)",
                "Quality of hire improvement (e.g., 90-day rating 3.2 → 3.7 = +16% QP)",
                "Employee engagement scores (e.g., 72% → 81% = +13% QP)",
                "High performer retention (e.g., 85% → 92% = +8% QP)",
                "Cost per hire reduction (e.g., $5,000 → $3,800 = +24% QP)"
            ],
            "typical_pm": "+40% to +60%",
            "typical_qp": "+20% to +35%",
            "notes": "HR shifts from administrative to strategic talent work. QP gains in hire quality and retention have compounding business value."
        },
        "Legal & Compliance": {
            "pm_metrics": [
                "Contracts reviewed per week (e.g., 15 → 20 = +33% PM)",
                "Policy updates completed (e.g., 5 → 12 per year = +140% PM)",
                "Risk assessments conducted (e.g., 10 → 16 per quarter = +60% PM)",
                "Strategic counsel sessions (e.g., 8 → 13 per month = +63% PM)",
                "Proactive compliance reviews (e.g., 20% → 40% of time = +100% PM)"
            ],
            "qp_metrics": [
                "Contract cycle time reduction (e.g., 12 days → 8 days = +33% QP)",
                "Risk issue identification rate (e.g., 60% → 85% caught early = +42% QP)",
                "Regulatory compliance score (e.g., 88% → 96% = +9% QP)",
                "Litigation prevention rate (measured in avoided legal costs)",
                "Deal velocity improvement (faster contract execution = revenue impact)"
            ],
            "typical_pm": "+30% to +50%",
            "typical_qp": "+20% to +30%",
            "notes": "Legal teams move from reactive review to strategic counsel. QP shows in risk prevention and deal velocity."
        },
        "Operations & Supply Chain": {
            "pm_metrics": [
                "Process improvement initiatives (e.g., 4 → 7 per quarter = +75% PM)",
                "Supplier relationship reviews (e.g., 10 → 16 per quarter = +60% PM)",
                "Strategic sourcing projects (e.g., 3 → 6 per year = +100% PM)",
                "Predictive analytics models built (e.g., 2 → 5 per quarter = +150% PM)",
                "Cross-functional optimization projects (e.g., 2 → 4 per quarter = +100% PM)"
            ],
            "qp_metrics": [
                "On-time delivery improvement (e.g., 92% → 97% = +5% QP)",
                "Inventory carrying cost reduction (e.g., $2M → $1.5M = +25% QP)",
                "Cost per unit reduction (e.g., $42 → $38 = +10% QP)",
                "Supply chain resilience (measured in disruption response time)",
                "Supplier quality improvement (e.g., defect rate 3% → 1% = +67% QP)"
            ],
            "typical_pm": "+35% to +55%",
            "typical_qp": "+20% to +35%",
            "notes": "Ops teams shift from reactive firefighting to strategic optimization. QP gains show in cost, quality, and resilience metrics."
        },
        "Research & Development": {
            "pm_metrics": [
                "Research experiments completed (e.g., 12 → 18 per quarter = +50% PM)",
                "Patent applications filed (e.g., 2 → 4 per year = +100% PM)",
                "Prototypes developed (e.g., 5 → 8 per quarter = +60% PM)",
                "Cross-functional innovation projects (e.g., 3 → 6 per year = +100% PM)",
                "External collaboration partnerships (e.g., 2 → 4 per year = +100% PM)"
            ],
            "qp_metrics": [
                "Prototype to production timeline (e.g., 18 months → 12 months = +33% QP)",
                "Research insights converted to products (e.g., 20% → 35% = +75% QP)",
                "Grant funding secured (measurable $ value)",
                "Breakthrough vs incremental innovations (tracked by impact)",
                "Technical publications in top journals (reputation/recruiting value)"
            ],
            "typical_pm": "+40% to +70%",
            "typical_qp": "+30% to +50%",
            "notes": "R&D sees high PM from focus on innovation vs. maintenance. QP measured in breakthrough rate and commercialization speed."
        },
        "Executive Leadership": {
            "pm_metrics": [
                "Strategic initiatives launched (e.g., 4 → 7 per year = +75% PM)",
                "Market opportunities evaluated (e.g., 8 → 13 per quarter = +63% PM)",
                "Organizational capability projects (e.g., 3 → 6 per year = +100% PM)",
                "M&A opportunities assessed (e.g., 5 → 9 per year = +80% PM)",
                "Culture transformation milestones (e.g., 6 → 10 per year = +67% PM)"
            ],
            "qp_metrics": [
                "Strategic initiative success rate (e.g., 60% → 80% = +33% QP)",
                "Stakeholder satisfaction scores (board, investors, employees)",
                "Organizational capability gaps closed (measured by performance improvement)",
                "Market share gains (competitive positioning)",
                "Long-term value creation (measured in enterprise value growth)"
            ],
            "typical_pm": "+50% to +100%",
            "typical_qp": "+30% to +60%",
            "notes": "Leadership shifts from operational firefighting to strategic thinking. QP shows in initiative success and long-term value creation."
        }
    }
    
    # Display selected department guidance
    if department != "Custom (Define Your Own)":
        dept_metrics = metrics_library[department]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Productivity Multiplier (PM)")
            st.markdown("**Measures: How much more OUTPUT per hour on reinvested work**")
            st.markdown("**Track these metrics:**")
            for metric in dept_metrics["pm_metrics"]:
                st.markdown(f"• {metric}")
            
            st.info(f"**Typical PM Range for {department}:** {dept_metrics['typical_pm']}")
        
        with col2:
            st.subheader("💎 Quality Premium (QP)")
            st.markdown("**Measures: How much more VALUABLE the outcomes are**")
            st.markdown("**Track these metrics:**")
            for metric in dept_metrics["qp_metrics"]:
                st.markdown(f"• {metric}")
            
            st.info(f"**Typical QP Range for {department}:** {dept_metrics['typical_qp']}")
        
        st.markdown("---")
        st.markdown(f"### 💡 Notes for {department}")
        st.markdown(dept_metrics["notes"])
        
        st.markdown("---")
        st.markdown("### 🎯 How to Use These Metrics")
        
        st.markdown("""
        **Step 1: Pick 2-3 PM metrics** that are easiest to track in your context
        - These should measure output volume (more work done per hour)
        - Track baseline for 1-2 months before AI implementation
        
        **Step 2: Pick 2-3 QP metrics** that reflect true business value
        - These should measure outcome quality (better results per action)
        - Focus on metrics that leadership cares about (revenue, cost, quality, risk)
        
        **Step 3: Set Conservative Phase Targets**
        - Phase 1 (Months 1-6): PM = 50% of typical range, QP = 30% of typical range
        - Phase 2 (Months 7-12): PM = 75% of typical range, QP = 70% of typical range  
        - Phase 3 (Months 13-18): PM = Full typical range, QP = Full typical range
        
        **Step 4: Track Monthly**
        - Compare actual metrics to baseline
        - Calculate actual PM and QP achieved
        - Adjust projections quarterly based on learnings
        
        **Step 5: Connect to Narrative**
        - "Our win rate improved 25% → 30% because reps now spend 60% more time on strategic accounts"
        - "We ship 40% more features because engineers focus on architecture, not bug fixes"
        - "Campaign ROI jumped 34% because marketers have time for deep audience research"
        """)
        
    else:
        st.markdown("### Define Your Own Metrics")
        
        st.markdown("""
        **For Productivity Multiplier (PM):**
        
        Think about **output volume metrics** that increase when people do higher-value work:
        - What gets produced more of? (reports, meetings, projects, analyses)
        - What throughput increases? (deals, cases, features, campaigns)
        - What strategic activities increase? (planning, research, innovation)
        
        **For Quality Premium (QP):**
        
        Think about **outcome quality metrics** that improve when work is more strategic:
        - What business results improve? (revenue, margin, retention, satisfaction)
        - What risks decrease? (errors, compliance issues, customer churn)
        - What speeds up? (cycle time, time to market, response time)
        - What efficiency gains occur? (cost reduction, resource optimization)
        
        **Example Calculation:**
        
        If your team currently completes 50 projects per quarter at an average value of $100K each:
        - After AI, they complete 70 projects (PM = +40%)
        - Projects now average $115K due to better quality (QP = +15%)
        - Combined effect: (1.40) × (1.15) = 1.61x or +61% total value multiplier
        """)
    
    st.markdown("---")
    st.markdown("### ⚠️ Calibration Warnings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🚫 Red Flags (Too Optimistic):**")
        st.markdown("""
        - PM above +80% (unprecedented)
        - QP above +60% (very rare)
        - RR above 85% (nearly impossible)
        - Claiming benefits in Phase 1 (unrealistic)
        - No consideration of coordination overhead
        """)
    
    with col2:
        st.markdown("**✅ Green Flags (Credible):**")
        st.markdown("""
        - PM in the +30-50% range
        - QP in the +20-40% range  
        - RR building from 40% → 70% over phases
        - Negative value in Phase 1 (honest)
        - Clear metrics tied to business outcomes
        """)
    
    st.markdown("---")
    st.markdown("### 📈 Benchmark Ranges by Function")
    
    benchmark_data = []
    for dept_name, metrics in metrics_library.items():
        benchmark_data.append({
            "Function": dept_name,
            "Typical PM Range": metrics["typical_pm"],
            "Typical QP Range": metrics["typical_qp"]
        })
    
    df_benchmarks = pd.DataFrame(benchmark_data)
    st.dataframe(df_benchmarks, width="stretch", hide_index=True)
    
    st.info("""
    💡 **Remember:** These are typical ranges based on work design quality. Your actual results depend on:
    - How well roles are redesigned for elevated work
    - Quality of governance and accountability structures
    - Team capability and readiness for new responsibilities
    - Strategic intent (efficiency vs. innovation focus)
    """)

with tab7:
    st.header("Task Deconstruction")

    st.markdown("""
    Break down your team's work into individual tasks and assess each one for AI redeployment potential.
    Rate each task across four dimensions to understand automation opportunity and the best AI approach.
    """)

    if "tasks" not in st.session_state:
        st.session_state.tasks = []

    with st.expander("➕ Add a Task", expanded=len(st.session_state.tasks) == 0):
        with st.form("add_task_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                task_name = st.text_input("Task Name", placeholder="e.g. Monthly expense report")
                primary_skill = st.text_input("Primary Skill", placeholder="e.g. Financial Analysis")
            with col2:
                time_pct = st.slider("% of Role Time", 1, 100, 10)

            st.markdown("**Rate this task on each dimension (0% = Low, 100% = High)**")
            col3, col4 = st.columns(2)
            with col3:
                repetitive = st.slider("Repetitive (vs. Variable)", 0, 100, 50,
                                       help="How repetitive and rule-based is this task?")
                physical = st.slider("Physical (vs. Mental)", 0, 100, 20,
                                     help="How physical vs. cognitive is the work?")
            with col4:
                independent = st.slider("Independent (vs. Interactive)", 0, 100, 50,
                                        help="How independently can this be done without human judgment?")
                deterministic = st.slider("Deterministic (vs. Probabilistic)", 0, 100, 50,
                                          help="How rule-based vs. judgment-based is this task?")

            submitted = st.form_submit_button("Add Task")
            if submitted and task_name:
                annual_cost = avg_compensation * (time_pct / 100) * team_size
                st.session_state.tasks.append({
                    "task": task_name,
                    "skill": primary_skill,
                    "time_pct": time_pct,
                    "annual_cost": annual_cost,
                    "repetitive": repetitive,
                    "physical": physical,
                    "independent": independent,
                    "deterministic": deterministic,
                })

    if st.session_state.tasks:
        tasks_df = pd.DataFrame(st.session_state.tasks)

        def get_redeployment_potential(row):
            score = (row["repetitive"] * 0.35 +
                     (100 - row["physical"]) * 0.15 +
                     row["independent"] * 0.25 +
                     row["deterministic"] * 0.25)
            if score >= 65:
                return "High"
            elif score >= 40:
                return "Medium"
            else:
                return "Low"

        def get_ai_type(row):
            if row["repetitive"] >= 70 and row["deterministic"] >= 70:
                return "RPA"
            elif row["independent"] >= 60 and row["deterministic"] >= 55:
                return "Machine Learning"
            else:
                return "GenAI"

        def get_objective(row):
            if row["repetitive"] >= 70:
                return "Reduce Variance"
            elif row["deterministic"] < 40:
                return "Enhance Precision"
            elif row["physical"] < 30:
                return "Improve Productivity"
            else:
                return "Increase Efficiency"

        tasks_df["potential"] = tasks_df.apply(get_redeployment_potential, axis=1)
        tasks_df["ai_type"] = tasks_df.apply(get_ai_type, axis=1)
        tasks_df["objective"] = tasks_df.apply(get_objective, axis=1)

        # Summary metrics
        st.markdown("### Project Status")
        col1, col2, col3, col4 = st.columns(4)
        high_count = len(tasks_df[tasks_df["potential"] == "High"])
        high_cost = tasks_df[tasks_df["potential"] == "High"]["annual_cost"].sum()
        hours_releasable = tasks_df[tasks_df["potential"] == "High"]["time_pct"].sum() * team_size * 2000 / 100
        total_cost = tasks_df["annual_cost"].sum()

        with col1:
            st.metric("Tasks Analyzed", len(tasks_df))
        with col2:
            st.metric("High Potential Tasks", high_count)
        with col3:
            st.metric("Cost in High-Potential Tasks", f"${high_cost:,.0f}")
        with col4:
            st.metric("Hours Releasable", f"{hours_releasable:,.0f}")

        st.markdown("---")

        # Task table
        st.subheader("Task Analysis")
        display_tasks = tasks_df[[
            "task", "skill", "time_pct", "annual_cost",
            "repetitive", "deterministic", "independent",
            "potential", "ai_type", "objective"
        ]].copy()
        display_tasks.columns = [
            "Task", "Primary Skill", "Time %", "Annual Cost",
            "Repetitive", "Deterministic", "Independent",
            "Potential", "AI Type", "Objective"
        ]
        display_tasks["Annual Cost"] = display_tasks["Annual Cost"].apply(lambda x: f"${x:,.0f}")
        st.dataframe(display_tasks, width="stretch", hide_index=True)

        # Charts
        col_left, col_right = st.columns(2)

        with col_left:
            potential_counts = tasks_df["potential"].value_counts().reindex(
                ["High", "Medium", "Low"], fill_value=0)
            fig_pot = go.Figure(go.Bar(
                x=potential_counts.index,
                y=potential_counts.values,
                marker_color=["#2ca02c", "#ff7f0e", "#d62728"],
                text=potential_counts.values,
                textposition="outside"
            ))
            fig_pot.update_layout(
                title="Tasks by Redeployment Potential",
                yaxis_title="Number of Tasks",
                height=350,
                showlegend=False
            )
            st.plotly_chart(fig_pot, width="stretch")

        with col_right:
            ai_counts = tasks_df["ai_type"].value_counts()
            fig_ai = go.Figure(go.Pie(
                labels=ai_counts.index,
                values=ai_counts.values,
                hole=0.4
            ))
            fig_ai.update_layout(
                title="Suggested AI Type for Tasks",
                height=350
            )
            st.plotly_chart(fig_ai, width="stretch")

        if st.button("🗑️ Clear All Tasks"):
            st.session_state.tasks = []
            st.rerun()

    else:
        st.info("Add tasks above to begin your task deconstruction analysis.")


with tab8:
    st.header("Redeployment Dashboard")

    st.markdown("""
    A headline view of redeployment opportunity across your organization, combining task-level
    analysis with your ROI model inputs.
    """)

    has_tasks = "tasks" in st.session_state and len(st.session_state.tasks) > 0

    if has_tasks:
        tasks_df_dash = pd.DataFrame(st.session_state.tasks)

        def get_potential_dash(row):
            score = (row["repetitive"] * 0.35 +
                     (100 - row["physical"]) * 0.15 +
                     row["independent"] * 0.25 +
                     row["deterministic"] * 0.25)
            if score >= 65:
                return "High"
            elif score >= 40:
                return "Medium"
            else:
                return "Low"

        def get_ai_type_dash(row):
            if row["repetitive"] >= 70 and row["deterministic"] >= 70:
                return "RPA"
            elif row["independent"] >= 60 and row["deterministic"] >= 55:
                return "Machine Learning"
            else:
                return "GenAI"

        tasks_df_dash["potential"] = tasks_df_dash.apply(get_potential_dash, axis=1)
        tasks_df_dash["ai_type"] = tasks_df_dash.apply(get_ai_type_dash, axis=1)

        tasks_analyzed = len(tasks_df_dash)
        high_potential = tasks_df_dash[tasks_df_dash["potential"] == "High"]
        medium_potential = tasks_df_dash[tasks_df_dash["potential"] == "Medium"]
        hours_released = high_potential["time_pct"].sum() * team_size * 2000 / 100
        headcount_to_redeploy = max(1, round(hours_released / 2000))
        cost_savings = high_potential["annual_cost"].sum()
        productivity_gain = params["pm"][2]

    else:
        # Fall back to main calculator estimates
        tasks_analyzed = 0
        hours_released = hours_savable * adoption_curve[2]
        headcount_to_redeploy = max(1, round(hours_released / 2000))
        cost_savings = total_18mo_value
        productivity_gain = params["pm"][2]

    # Headline metrics — styled like Mercer's project status bar
    st.markdown("### Project Status")
    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.metric("Tasks Analyzed", tasks_analyzed if has_tasks else "—")
    with c2:
        st.metric("Headcount to Redeploy", headcount_to_redeploy)
    with c3:
        st.metric("Working Hours Released", f"{hours_released:,.0f}")
    with c4:
        st.metric("Cost Savings", f"${cost_savings:,.0f}")
    with c5:
        st.metric("Avg Productivity Gain", f"{productivity_gain:.0%}")

    st.markdown("---")

    if has_tasks:
        col_left, col_right = st.columns(2)

        with col_left:
            potential_counts = tasks_df_dash["potential"].value_counts().reindex(
                ["High", "Medium", "Low"], fill_value=0)
            fig_redeploy = go.Figure(go.Bar(
                x=["High Potential", "Medium Potential", "Low Potential"],
                y=potential_counts.values,
                marker_color=["#2ca02c", "#ff7f0e", "#d62728"],
                text=[f"{v} tasks\n({v/len(tasks_df_dash)*100:.0f}%)" for v in potential_counts.values],
                textposition="outside"
            ))
            fig_redeploy.update_layout(
                title="Opportunities to Redeploy by Task",
                yaxis_title="Number of Tasks",
                height=380,
                showlegend=False
            )
            st.plotly_chart(fig_redeploy, width="stretch")

        with col_right:
            ai_counts = tasks_df_dash["ai_type"].value_counts()
            fig_ai_dash = go.Figure(go.Pie(
                labels=ai_counts.index,
                values=ai_counts.values,
                hole=0.4,
                marker_colors=["#1f77b4", "#ff7f0e", "#2ca02c"]
            ))
            fig_ai_dash.update_layout(
                title="Suggested Redeployment Type for High-Potential Tasks",
                height=380
            )
            st.plotly_chart(fig_ai_dash, width="stretch")

        # Task-level redeployment table
        st.subheader("Task Redeployment Summary")
        summary = tasks_df_dash[[
            "task", "skill", "time_pct", "annual_cost", "potential", "ai_type"
        ]].copy()
        summary.columns = ["Task", "Primary Skill", "Time %", "Annual Cost", "Potential", "AI Type"]
        summary["Annual Cost"] = summary["Annual Cost"].apply(lambda x: f"${x:,.0f}")
        summary = summary.sort_values("Potential", key=lambda x: x.map({"High": 0, "Medium": 1, "Low": 2}))
        st.dataframe(summary, width="stretch", hide_index=True)

    else:
        st.info("Complete the **Task Deconstruction** tab first to see task-level redeployment analysis. The metrics above are estimated from your ROI model inputs.")

        # Show a projection chart based on main calculator
        st.subheader("Projected Hours Released Over Time")
        fig_hrs = go.Figure(go.Bar(
            x=[f"Month {m}" for m in df["month"]],
            y=df["hours_saved"],
            marker_color="#1f77b4"
        ))
        fig_hrs.update_layout(
            xaxis_title="Month",
            yaxis_title="Hours Released",
            height=350
        )
        st.plotly_chart(fig_hrs, width="stretch")


with tab9:
    st.header("AI Type Recommender")
    st.markdown("""
    Describe a specific task and get a recommendation for the most appropriate AI approach,
    with a full explanation of the tradeoffs between RPA, GenAI, and Machine Learning.
    """)

    col_form, col_result = st.columns([1, 1])

    with col_form:
        st.subheader("Describe the Task")
        rec_task_name = st.text_input("Task Name", placeholder="e.g. Invoice processing")

        st.markdown("**Rate each dimension**")
        rec_repetitive = st.slider("Repetitive (vs. Variable)", 0, 100, 50,
                                   help="100 = same steps every time; 0 = different every time",
                                   key="rec_rep")
        rec_deterministic = st.slider("Deterministic (vs. Probabilistic)", 0, 100, 50,
                                      help="100 = clear rules; 0 = requires human judgment",
                                      key="rec_det")
        rec_volume = st.slider("Volume (transactions per month)", 0, 100, 50,
                               help="100 = very high volume; 0 = rare/one-off",
                               key="rec_vol")
        rec_data_richness = st.slider("Data Richness (historical data available)", 0, 100, 50,
                                      help="100 = lots of labeled historical data; 0 = little or none",
                                      key="rec_data")
        rec_language = st.slider("Language/Content Complexity", 0, 100, 50,
                                 help="100 = involves complex text, nuance, or creativity; 0 = structured data only",
                                 key="rec_lang")

    with col_result:
        st.subheader("Recommendation")

        # Scoring logic
        rpa_score = (rec_repetitive * 0.40 + rec_deterministic * 0.35 + rec_volume * 0.15 + (100 - rec_language) * 0.10)
        ml_score = (rec_data_richness * 0.40 + rec_volume * 0.25 + rec_deterministic * 0.20 + (100 - rec_language) * 0.15)
        genai_score = (rec_language * 0.40 + (100 - rec_deterministic) * 0.25 + rec_data_richness * 0.15 + rec_repetitive * 0.20)

        scores = {"RPA": rpa_score, "Machine Learning": ml_score, "GenAI": genai_score}
        recommended = max(scores, key=scores.get)

        color_map = {"RPA": "#1f77b4", "Machine Learning": "#2ca02c", "GenAI": "#ff7f0e"}
        descriptions = {
            "RPA": "Robotic Process Automation — best for high-volume, rule-based, repetitive tasks with structured data and clear steps. Executes the same process reliably at scale.",
            "Machine Learning": "Machine Learning — best when you have rich historical data and need the system to learn patterns, make predictions, or classify inputs. Improves over time.",
            "GenAI": "Generative AI — best for tasks involving language, content, nuance, or creativity. Handles variability well and can draft, summarize, analyze, and converse."
        }
        when_to_use = {
            "RPA": [
                "Data entry and form processing",
                "Invoice and expense processing",
                "Report generation from fixed sources",
                "System-to-system data transfer",
                "Compliance checks against fixed rules"
            ],
            "Machine Learning": [
                "Demand forecasting and planning",
                "Anomaly and fraud detection",
                "Employee attrition prediction",
                "Customer churn scoring",
                "Document classification at scale"
            ],
            "GenAI": [
                "Drafting emails, reports, proposals",
                "Summarizing documents and meetings",
                "Answering employee or customer questions",
                "Policy and procedure interpretation",
                "Performance review drafting"
            ]
        }
        watch_out = {
            "RPA": "Fragile when underlying systems change. Requires clean, structured inputs. High maintenance if processes evolve frequently.",
            "Machine Learning": "Requires substantial labeled historical data. Results degrade if underlying patterns shift. Needs ongoing monitoring.",
            "GenAI": "Can hallucinate or produce plausible-sounding errors. Requires human review for high-stakes outputs. Cost scales with usage."
        }

        # Primary recommendation
        rec_color = color_map[recommended]
        st.markdown(f"""
        <div style="background-color:{rec_color}22; border-left: 5px solid {rec_color};
             padding: 16px; border-radius: 8px; margin-bottom: 16px;">
            <h3 style="color:{rec_color}; margin:0;">Recommended: {recommended}</h3>
            <p style="margin-top:8px;">{descriptions[recommended]}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("**Best used for tasks like:**")
        for example in when_to_use[recommended]:
            st.markdown(f"• {example}")

        st.warning(f"**Watch out for:** {watch_out[recommended]}")

    st.markdown("---")
    st.subheader("How All Three Options Score for This Task")

    fig_scores = go.Figure(go.Bar(
        x=list(scores.keys()),
        y=list(scores.values()),
        marker_color=[color_map[k] for k in scores.keys()],
        text=[f"{v:.0f}" for v in scores.values()],
        textposition="outside"
    ))
    fig_scores.update_layout(
        yaxis_title="Fit Score (0-100)",
        height=350,
        showlegend=False,
        yaxis_range=[0, 110]
    )
    st.plotly_chart(fig_scores, width="stretch")

    st.markdown("---")
    st.subheader("Quick Reference: When to Use Each")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"#### 🔵 RPA")
        st.markdown("**Best when:** High volume, clear rules, structured data, no judgment needed")
        st.markdown("**Avoid when:** Processes change frequently or inputs are unstructured")
    with c2:
        st.markdown(f"#### 🟢 Machine Learning")
        st.markdown("**Best when:** Rich historical data exists and you need prediction or pattern recognition")
        st.markdown("**Avoid when:** Data is scarce, the outcome is purely rule-based, or explainability is critical")
    with c3:
        st.markdown(f"#### 🟠 GenAI")
        st.markdown("**Best when:** Task involves language, nuance, variability, or content generation")
        st.markdown("**Avoid when:** Accuracy is critical with no human review, or data is purely numerical")


# Footer
st.markdown("---")
st.markdown("""
### 📚 About This Model

This calculator implements the **Human × Machine ROI Framework**, which emphasizes that AI value 
comes from strategic reallocation of human capacity, not from technology alone.

**The Equation:**
```
Monthly Value = [HS × Rate × RR × (1 + PM) × (1 + QP)] + IV - (RC + CO)
```

**Critical Insight:** The variables that matter most (RR, PM, QP, IV) are all about **work design 
and governance**, not about which AI vendor you choose.

---
*Built to demonstrate that identical AI implementations deliver radically different results based on 
how organizations manage people, redesign work, and govern adoption.*
""")
