import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# ==============================================================================
# 1. KONFIGURASI HALAMAN & STYLE DASHBOARD
# ==============================================================================

st.set_page_config(
    page_title="Interactive Aggregate Planning Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# CUSTOM CSS - WHITE & SOFT PINK MODERN THEME
# ==============================================================================

st.markdown("""
<style>

/* =========================
BACKGROUND UTAMA
========================= */
.stApp {
    background: linear-gradient(to bottom right, #fffafb, #fff5f8);
    color: #222222;
}

/* =========================
CONTAINER
========================= */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* =========================
SIDEBAR
========================= */
section[data-testid="stSidebar"] {
    background-color: #fff0f5;
    border-right: 2px solid #ffd6e7;
}

/* =========================
HEADINGS
========================= */
h1, h2, h3, h4 {
    color: #c2185b;
    font-weight: 700;
}

/* =========================
TEXT
========================= */
p, label, div {
    color: #333333;
}

/* =========================
KPI CARD
========================= */
.kpi-card {
    background: white;
    border-radius: 20px;
    padding: 22px;
    box-shadow: 0 4px 18px rgba(255, 182, 193, 0.25);
    border: 2px solid #ffd6e7;
    margin-bottom: 18px;
    transition: 0.3s ease;
    color: #222222;
}

.kpi-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 28px rgba(255, 182, 193, 0.35);
}

.kpi-title {
    font-size: 14px;
    color: #ad1457;
    font-weight: bold;
    text-transform: uppercase;
}

.kpi-value {
    font-size: 30px;
    color: #d81b60;
    font-weight: 800;
    margin-top: 8px;
}

.kpi-card small {
    color: #444444;
    font-weight: 500;
}

/* =========================
RECOMMENDATION BOX
========================= */
.recommendation-box {
    background: linear-gradient(to right, #fff0f5, #ffe4ec);
    border-radius: 20px;
    padding: 28px;
    border-left: 8px solid #ec407a;
    margin-top: 25px;
    color: #222222;
    box-shadow: 0 4px 18px rgba(255, 182, 193, 0.25);
}

.recommendation-box h4 {
    color: #c2185b;
    font-weight: 800;
}

.recommendation-box li {
    margin-bottom: 10px;
    line-height: 1.6;
}

/* =========================
DATAFRAME
========================= */
[data-testid="stDataFrame"] {
    border-radius: 15px;
    overflow: hidden;
    border: 1px solid #ffd6e7;
    background-color: white;
}

/* =========================
TABS
========================= */
button[data-baseweb="tab"] {
    background-color: #fff0f5;
    color: #c2185b;
    border-radius: 12px 12px 0px 0px;
    margin-right: 4px;
    border: 1px solid #ffd6e7;
    font-weight: 600;
}

button[data-baseweb="tab"][aria-selected="true"] {
    background-color: #f8bbd0;
    color: white;
}

/* =========================
INPUT
========================= */
.stNumberInput input,
.stTextInput input {
    border-radius: 10px !important;
    border: 1px solid #f8bbd0 !important;
    background-color: white !important;
}

/* =========================
SELECT BOX
========================= */
.stSelectbox div[data-baseweb="select"] {
    border-radius: 10px;
    border: 1px solid #f8bbd0;
}

/* =========================
SLIDER
========================= */
.stSlider > div > div {
    color: #ec407a !important;
}

/* =========================
BUTTON
========================= */
.stButton button {
    background-color: #f48fb1;
    color: white;
    border-radius: 12px;
    border: none;
    padding: 8px 18px;
    font-weight: bold;
}

.stButton button:hover {
    background-color: #ec407a;
    color: white;
}

/* =========================
RADIO BUTTON
========================= */
.stRadio label {
    color: #ad1457 !important;
    font-weight: 600;
}

/* =========================
TABLE HEADER
========================= */
thead tr th {
    background-color: #ffe4ec !important;
    color: #ad1457 !important;
}

/* =========================
SCROLLBAR
========================= */
::-webkit-scrollbar {
    width: 10px;
}

::-webkit-scrollbar-thumb {
    background: #f8bbd0;
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

# ==============================================================================
# TITLE
# ==============================================================================

st.title("📊 Sistem Pendukung Keputusan: Perencanaan Agregat Interaktif (12 Periode)")
st.markdown("Aplikasi analisis strategi produksi komprehensif dengan pendekatan *Robust Planning* berbasis skenario.")
st.markdown("---")

# ==============================================================================
# SIDEBAR
# ==============================================================================

st.sidebar.header("🛠️ Parameter Operasional")

num_periods = 12

st.sidebar.subheader("Permintaan (Demand) per Periode")

default_demand = [1200, 1300, 1500, 1700, 1800, 1600, 1400, 1300, 1100, 1400, 1600, 1900]

demand_df = st.sidebar.data_editor(
    pd.DataFrame({
        "Periode": [f"Bulan {i+1}" for i in range(num_periods)],
        "Demand": default_demand
    }),
    hide_index=True
)

base_demand = demand_df["Demand"].tolist()

st.sidebar.subheader("Kapasitas & Tenaga Kerja")

init_workforce = st.sidebar.number_input("Tenaga Kerja Awal (Pekerja)", value=20, min_value=0)
worker_cap = st.sidebar.number_input("Kapasitas per Tenaga Kerja (Unit/Bulan)", value=70, min_value=1)
init_inv = st.sidebar.number_input("Inventori Awal (Unit)", value=200, min_value=0)
safety_stock = st.sidebar.number_input("Safety Stock (Unit)", value=100, min_value=0)

max_ot_cap = st.sidebar.number_input("Batas Maksimum Overtime (Unit/Bulan)", value=300, min_value=0)
min_sub_cap = st.sidebar.number_input("Batas Minimum Subcontracting (Unit/Bulan)", value=50, min_value=0)
max_sub_cap = st.sidebar.number_input("Batas Maksimum Subcontracting (Unit/Bulan)", value=500, min_value=0)

if min_sub_cap > max_sub_cap:
    st.sidebar.error("⚠️ Batas minimum subkontrak tidak boleh lebih besar dari batas maksimum!")

st.sidebar.header("💰 Struktur Biaya (IDR / Unit / Pekerja)")

c_material = st.sidebar.number_input("Biaya Bahan Baku / Material Cost (/Unit)", value=150000)
c_regular = st.sidebar.number_input("Biaya Produksi Reguler (/Unit)", value=50000)
c_overtime = st.sidebar.number_input("Biaya Overtime (/Unit)", value=75000)
c_subcontract = st.sidebar.number_input("Biaya Subcontracting (/Unit)", value=90000)
c_inventory = st.sidebar.number_input("Biaya Simpan / Inventory (/Unit/Bulan)", value=10000)
c_stockout = st.sidebar.number_input("Biaya Stockout / Shortage (/Unit/Bulan)", value=15000)
c_hiring = st.sidebar.number_input("Biaya Rekrutmen / Hiring (/Pekerja)", value=2000000)
c_firing = st.sidebar.number_input("Biaya PHK / Firing (/Pekerja)", value=3500000)

st.sidebar.header("🎲 Skenario Ketidakpastian")

p_normal = st.sidebar.slider("Probabilitas Normal", 0.0, 1.0, 0.6, step=0.05)
p_optimistic = st.sidebar.slider("Probabilitas Optimis (Demand +25%)", 0.0, 1.0 - p_normal, 0.2, step=0.05)
p_pessimistic = round(1.0 - p_normal - p_optimistic, 2)

st.sidebar.text(f"Probabilitas Pesimis (Demand -25%): {p_pessimistic}")

selected_scenario = st.selectbox(
    "Pilih Skenario Tampilan Utama Dashboard:",
    ["Normal", "Optimis", "Pesimis"]
)

# ==============================================================================
# FUNCTION
# ==============================================================================

def calculate_aggregate_planning(strategy, demand_list):

    inv_prev = init_inv
    wf_prev = init_workforce

    records = []

    if strategy == "Level":
        total_net_demand = sum([d + safety_stock for d in demand_list])
        avg_production_needed = total_net_demand / num_periods
        constant_wf = int(np.ceil(avg_production_needed / worker_cap))
    else:
        constant_wf = init_workforce

    for t in range(num_periods):

        d_t = demand_list[t]
        net_demand = d_t + safety_stock

        if strategy == "Chase":

            wf_needed = int(np.ceil(net_demand / worker_cap))

            hiring = max(0, wf_needed - wf_prev)
            firing = max(0, wf_prev - wf_needed)

            wf_current = wf_needed

            rt_prod = wf_current * worker_cap

        elif strategy == "Level":

            wf_current = constant_wf

            hiring = max(0, wf_current - wf_prev) if t == 0 else 0
            firing = max(0, wf_prev - wf_current) if t == 0 else 0

            rt_prod = wf_current * worker_cap

        else:

            wf_current = init_workforce
            hiring = 0
            firing = 0

            rt_prod = wf_current * worker_cap

        deficit = max(0, net_demand - rt_prod - inv_prev)

        ot_prod = 0
        sub_prod = 0

        if strategy == "Mixed" and deficit > 0:

            ot_prod = min(max_ot_cap, deficit)

            deficit -= ot_prod

            if deficit > 0:

                sub_needed = max(min_sub_cap, deficit)

                sub_prod = min(max_sub_cap, sub_needed)

                deficit = max(0, deficit - sub_prod)

        total_supply = inv_prev + rt_prod + ot_prod + sub_prod

        balance = total_supply - net_demand

        if balance >= 0:
            inv_end = balance
            stockout = 0
        else:
            inv_end = 0
            stockout = abs(balance)

        cost_mat = (rt_prod + ot_prod) * c_material
        cost_rep = rt_prod * c_regular
        cost_labor = wf_current * 3000000
        cost_hire = hiring * c_hiring
        cost_fire = firing * c_firing
        cost_hold = inv_end * c_inventory
        cost_ot = ot_prod * c_overtime
        cost_sub = sub_prod * c_subcontract
        cost_short = stockout * c_stockout

        total_cost = (
            cost_mat + cost_rep + cost_labor +
            cost_hire + cost_fire + cost_hold +
            cost_ot + cost_sub + cost_short
        )

        records.append({
            "Periode": f"Bulan {t+1}",
            "Demand": d_t,
            "Inventory": inv_end,
            "Stockout": stockout,
            "RT Production": rt_prod,
            "OT Production": ot_prod,
            "Subcontracting": sub_prod,
            "Total Cost": total_cost
        })

        inv_prev = inv_end
        wf_prev = wf_current

    return pd.DataFrame(records)

# ==============================================================================
# SCENARIOS
# ==============================================================================

demand_scenarios = {
    "Normal": base_demand,
    "Optimis": [int(d * 1.25) for d in base_demand],
    "Pesimis": [int(d * 0.75) for d in base_demand]
}

results = {}

for strat in ["Chase", "Level", "Mixed"]:

    results[strat] = {}

    for scen, d_list in demand_scenarios.items():

        results[strat][scen] = calculate_aggregate_planning(strat, d_list)

# ==============================================================================
# KPI SUMMARY
# ==============================================================================

summary_metrics = []

for strat in ["Chase", "Level", "Mixed"]:

    df_active = results[strat][selected_scenario]

    total_cost = df_active["Total Cost"].sum()

    total_demand = df_active["Demand"].sum()

    total_shortage = df_active["Stockout"].sum()

    service_level = (
        ((total_demand - total_shortage) / total_demand) * 100
    )

    summary_metrics.append({
        "Strategi": strat,
        "Total Cost": total_cost,
        "Service Level": service_level
    })

summary_df = pd.DataFrame(summary_metrics)

# ==============================================================================
# TABS
# ==============================================================================

tab1, tab2, tab3 = st.tabs([
    "📈 Ringkasan Eksekutif",
    "🔍 Detail Strategi",
    "🎲 Analisis Risiko"
])

# ==============================================================================
# TAB 1
# ==============================================================================

with tab1:

    st.subheader(f"KPI Dashboard ({selected_scenario})")

    cols = st.columns(3)

    for idx, row in summary_df.iterrows():

        with cols[idx]:

            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">{row['Strategi']}</div>
                <div class="kpi-value">
                    IDR {row['Total Cost']:,.0f}
                </div>
                <small>
                    Service Level:
                    {row['Service Level']:.2f}%
                </small>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    fig_cost = px.bar(
        summary_df,
        x="Strategi",
        y="Total Cost",
        color="Strategi",
        text_auto=',.0f',
        color_discrete_sequence=[
            "#f8bbd0",
            "#f48fb1",
            "#ce93d8"
        ]
    )

    fig_cost.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='#444444')
    )

    st.plotly_chart(fig_cost, use_container_width=True)

# ==============================================================================
# TAB 2
# ==============================================================================

with tab2:

    selected_strategy = st.radio(
        "Pilih Strategi:",
        ["Chase", "Level", "Mixed"],
        horizontal=True
    )

    df_selected = results[selected_strategy][selected_scenario]

    st.dataframe(df_selected, use_container_width=True)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_selected["Periode"],
        y=df_selected["Demand"],
        name="Demand",
        line=dict(color='#ec407a', width=3, dash='dash')
    ))

    fig.add_trace(go.Bar(
        x=df_selected["Periode"],
        y=df_selected["RT Production"] +
          df_selected["OT Production"] +
          df_selected["Subcontracting"],
        name="Total Produksi",
        marker_color='#f8bbd0'
    ))

    fig.update_layout(
        title="Demand vs Supply",
        barmode='group',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='#444444')
    )

    st.plotly_chart(fig, use_container_width=True)

# ==============================================================================
# TAB 3
# ==============================================================================

with tab3:

    robust_records = []

    for strat in ["Chase", "Level", "Mixed"]:

        c_norm = results[strat]["Normal"]["Total Cost"].sum()
        c_opt = results[strat]["Optimis"]["Total Cost"].sum()
        c_pess = results[strat]["Pesimis"]["Total Cost"].sum()

        robust_records.append({
            "Strategi": strat,
            "Pesimis": c_pess,
            "Normal": c_norm,
            "Optimis": c_opt
        })

    robust_df = pd.DataFrame(robust_records)

    st.dataframe(robust_df, use_container_width=True)

    fig_robust = go.Figure()

    colors = {
        "Chase": "#ec407a",
        "Level": "#f48fb1",
        "Mixed": "#ce93d8"
    }

    for strat in ["Chase", "Level", "Mixed"]:

        row = robust_df[
            robust_df["Strategi"] == strat
        ].iloc[0]

        fig_robust.add_trace(go.Scatter(
            x=["Pesimis", "Normal", "Optimis"],
            y=[row["Pesimis"], row["Normal"], row["Optimis"]],
            mode='lines+markers',
            name=strat,
            line=dict(color=colors[strat], width=4)
        ))

    fig_robust.update_layout(
        title="Analisis Sensitivitas Biaya",
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='#444444')
    )

    st.plotly_chart(fig_robust, use_container_width=True)
