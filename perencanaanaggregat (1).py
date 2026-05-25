import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from io import BytesIO

# ==============================================================================
# 1. KONFIGURASI HALAMAN & INJEKSI CUSTOM CSS FULL LIGHT MODE (AKSEN PINK)
# ==============================================================================
st.set_page_config(
    page_title="Interactive Aggregate Planning & MRP Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Injeksi CSS Radikal untuk mengunci Light Mode dan mewarnai ulang seluruh komponen Streamlit
st.markdown("""
<style>
    /* 1. Global Light Mode Locking & Main Background */
    :root {
        color-scheme: light !important;
    }
    html, body, [data-testid="stAppViewContainer"], .main {
        background-color: #ffffff !important;
        color: #111111 !important;
    }
    
    /* 2. Judul, Subheader, dan Teks Global */
    h1, h2, h3, h4, h5, h6, p, span, label, li {
        color: #111111 !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* 3. Sidebar Styling Total */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 2px solid #ff1493 !important; /* Garis pembatas pink tegas */
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] label {
        color: #111111 !important;
        font-weight: 600 !important;
    }
    
    /* 4. Overwrite Input Box, Data Editor, & Dropdown (Background Putih, Teks Hitam) */
    div[data-baseweb="input"] {
        background-color: #ffffff !important;
        border: 1px solid #ff69b4 !important;
        border-radius: 6px !important;
    }
    div[data-baseweb="input"] input {
        color: #111111 !important;
        background-color: #ffffff !important;
    }
    div[data-baseweb="select"] {
        background-color: #ffffff !important;
        border: 1px solid #ff69b4 !important;
    }
    div[data-baseweb="select"] span {
        color: #111111 !important;
    }
    
    /* Tombol plus/minus (+ / -) pada Number Input */
    button[title="Increment/Decrement values"], 
    [data-testid="stNumberInputStepUp"], 
    [data-testid="stNumberInputStepDown"] {
        background-color: #ff69b4 !important;
        color: #ffffff !important;
        border-radius: 4px !important;
        opacity: 1 !important;
    }
    button[title="Increment/Decrement values"]:hover {
        background-color: #ff1493 !important;
    }

    /* 5. Rekayasa Gaya Tabel Bawaan & Data Editor (Paksa Putih & Garis Bagus) */
    [data-testid="stDataFrame"], [data-testid="stDataEditor"] {
        background-color: #ffffff !important;
        border: 1px solid #ff69b4 !important;
        border-radius: 8px !important;
        padding: 5px;
    }
    /* Memaksa sel di dalam canvas data editor/dataframe agar tidak gelap */
    div[class*="glideDataEditor"] {
        background-color: #ffffff !important;
    }
    
    /* 6. Tabs Custom Styling (Aksen Pink) */
    button[data-baseweb="tab"] {
        color: #495057 !important;
        background-color: #f8f9fa !important;
        border: 1px solid #dee2e6 !important;
        border-bottom: none !important;
        margin-right: 4px !important;
        padding: 10px 20px !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #ffffff !important;
        color: #ff1493 !important;
        border-top: 3px solid #ff1493 !important;
        font-weight: bold !important;
    }
    
    /* 7. Custom KPI Card & Box Informasi Terpadu */
    .kpi-card {
        background-color: #ffffff !important;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #f0f0f0;
        border-left: 6px solid #ff1493 !important; /* Batas kiri tebal warna pink */
        margin-bottom: 15px;
    }
    .kpi-title { font-size: 14px; color: #6c757d !important; font-weight: bold; text-transform: uppercase; }
    .kpi-value { font-size: 24px; color: #111111 !important; font-weight: bold; margin-top: 5px; }
    .kpi-card small { color: #495057 !important; font-weight: 500; }
    
    .recommendation-box {
        background-color: #fff0f5 !important; /* Warna latar lavender blush/pink sangat muda */
        border-radius: 8px;
        padding: 25px;
        border: 1px solid #ffb6c1;
        border-left: 6px solid #ff1493 !important;
        margin-top: 20px;
    }
    .recommendation-box h4 { color: #ff1493 !important; font-weight: bold; }
    
    /* Horizontal Rule Custom */
    hr {
        border: 0;
        height: 1px;
        background: linear-gradient(to right, #ff1493, #ff69b4, #ffffff) !important;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

st.title("📊 Sistem Pendukung Keputusan: Perencanaan Agregat Interaktif (12 Periode)")
st.markdown("Aplikasi analisis strategi produksi komprehensif dengan pendekatan *Robust Planning* berbasis skenario.")
st.markdown("---")

# ==============================================================================
# 2. SIDEBAR - INPUT PARAMETER OPERASIONAL & BIAYA
# ==============================================================================
st.sidebar.header("🛠️ Parameter Operasional")
num_periods = 12

# Input Demand Base via UI Dataframe
st.sidebar.subheader("Permintaan (Demand) per Periode")
default_demand = [1200, 1300, 1500, 1700, 1800, 1600, 1400, 1300, 1100, 1400, 1600, 1900]
demand_df = st.sidebar.data_editor(
    pd.DataFrame({"Periode": [f"Bulan {i+1}" for i in range(num_periods)], "Demand": default_demand}),
    hide_index=True
)
base_demand = demand_df["Demand"].tolist()

# Kapasitas & Tenaga Kerja
st.sidebar.subheader("Kapasitas & Tenaga Kerja")
init_workforce = st.sidebar.number_input("Tenaga Kerja Awal (Pekerja)", value=20, min_value=0)
worker_cap = st.sidebar.number_input("Kapasitas per Tenaga Kerja (Unit/Bulan)", value=70, min_value=1)
init_inv = st.sidebar.number_input("Inventori Awal (Unit)", value=200, min_value=0)
safety_stock = st.sidebar.number_input("Safety Stock (Unit)", value=100, min_value=0)

# Batasan Kapasitas Tambahan
max_ot_cap = st.sidebar.number_input("Batas Maksimum Overtime (Unit/Bulan)", value=300, min_value=0)
min_sub_cap = st.sidebar.number_input("Batas Minimum Subcontracting (Unit/Bulan)", value=50, min_value=0)
max_sub_cap = st.sidebar.number_input("Batas Maksimum Subcontracting (Unit/Bulan)", value=500, min_value=0)

if min_sub_cap > max_sub_cap:
    st.sidebar.error("⚠️ Batas minimum subkontrak tidak boleh lebih besar dari batas maksimum!")

# Struktur Biaya
st.sidebar.header("💰 Struktur Biaya (IDR / Unit / Pekerja)")
c_material = st.sidebar.number_input("Biaya Bahan Baku / Material Cost (/Unit)", value=150000, step=5000, min_value=0)
c_regular = st.sidebar.number_input("Biaya Produksi Reguler (/Unit)", value=50000, step=1000, min_value=0)
c_overtime = st.sidebar.number_input("Biaya Overtime (/Unit)", value=75000, step=1000, min_value=0)
c_subcontract = st.sidebar.number_input("Biaya Subcontracting (/Unit)", value=90000, step=1000, min_value=0)
c_inventory = st.sidebar.number_input("Biaya Simpan / Inventory (/Unit/Bulan)", value=10000, step=500, min_value=0)
c_stockout = st.sidebar.number_input("Biaya Stockout / Shortage (/Unit/Bulan)", value=15000, step=500, min_value=0)
c_hiring = st.sidebar.number_input("Biaya Rekrutmen / Hiring (/Pekerja)", value=2000000, step=50000, min_value=0)
c_firing = st.sidebar.number_input("Biaya PHK / Firing (/Pekerja)", value=3500000, step=50000, min_value=0)

# Skenario Ketidakpastian (Robust Planning)
st.sidebar.header("🎲 Skenario Ketidakpastian")
p_normal = st.sidebar.slider("Probabilitas Normal", 0.0, 1.0, 0.6, step=0.05)
p_optimistic = st.sidebar.slider("Probabilitas Optimis (Demand +25%)", 0.0, 1.0 - p_normal, 0.2, step=0.05)
p_pessimistic = round(1.0 - p_normal - p_optimistic, 2)
st.sidebar.text(f"Probabilitas Pesimis (Demand -25%): {p_pessimistic}")

if not np.isclose(p_normal + p_optimistic + p_pessimistic, 1.0):
    st.sidebar.error("⚠️ Total probabilitas skenario harus sama dengan 1.0")

# Pilih Skenario Aktif untuk Tampilan Detail Utama
selected_scenario = st.selectbox("Pilih Skenario Tampilan Utama Dashboard:", ["Normal", "Optimis", "Pesimis"])

# ==============================================================================
# 3. LOGIKA MESIN PERHITUNGAN STRATEGI AGREGAT
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
        
        # 1. Workforce & Regular Time Production Planning Based on Strategy
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
        elif strategy == "Mixed":
            wf_current = init_workforce
            hiring = 0
            firing = 0
            rt_prod = wf_current * worker_cap

        # 2. Perhitungan Overtime & Subcontracting dengan Kebijakan Minimum
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
                
        elif strategy in ["Chase", "Level"] and deficit > 0:
            pass

        # 3. Logika Inventori & Stockout Balance Sheet
        total_supply = inv_prev + rt_prod + ot_prod + sub_prod
        balance = total_supply - net_demand
        
        if balance >= 0:
            inv_end = balance
            stockout = 0
        else:
            inv_end = 0
            stockout = abs(balance)
            
        # 4. Kalkulasi Struktur Biaya Detail per Periode
        cost_mat = (rt_prod + ot_prod) * c_material 
        cost_rep = rt_prod * c_regular
        cost_labor = wf_current * 3000000
        cost_hire = hiring * c_hiring
        cost_fire = firing * c_firing
        cost_hold = inv_end * c_inventory
        cost_ot = ot_prod * c_overtime
        cost_sub = sub_prod * c_subcontract
        cost_short = stockout * c_stockout
        total_cost = cost_mat + cost_rep + cost_hire + cost_fire + cost_hold + cost_ot + cost_sub + cost_short

        records.append({
            "Periode": f"Bulan {t+1}",
            "Demand": d_t,
            "Net Demand": net_demand,
            "Workforce": wf_current,
            "Hiring": hiring,
            "Firing": firing,
            "RT Production": rt_prod,
            "OT Production": ot_prod,
            "Subcontracting": sub_prod,
            "Inventory": inv_end,
            "Stockout": stockout,
            "Total Supply": total_supply,
            "Material Cost": cost_mat,
            "Production Cost": cost_rep,
            "Labor Cost": cost_labor,
            "Hiring Cost": cost_hire,
            "Firing Cost": cost_fire,
            "Inventory Holding Cost": cost_hold,
            "Overtime Cost": cost_ot,
            "Subcontract Cost": cost_sub,
            "Shortage Cost": cost_short,
            "Total Cost": total_cost
        })
        
        inv_prev = inv_end
        wf_prev = wf_current
        
    return pd.DataFrame(records)

# Penyesuaian Multiplier Skenario Demand Uncertainty
demand_scenarios = {
    "Normal": base_demand,
    "Optimis": [int(d * 1.25) for d in base_demand],
    "Pesimis": [int(d * 0.75) for d in base_demand]
}

# Generate Data untuk Seluruh Kombinasi Strategi & Skenario
results = {}
for strat in ["Chase", "Level", "Mixed"]:
    results[strat] = {}
    for scen, d_list in demand_scenarios.items():
        results[strat][scen] = calculate_aggregate_planning(strat, d_list)

# ==============================================================================
# 4. EVALUASI METRIK KPI UTAMA VIA EXPECTED VALUE
# ==============================================================================
summary_metrics = []
for strat in ["Chase", "Level", "Mixed"]:
    c_norm = results[strat]["Normal"]["Total Cost"].sum()
    c_opt = results[strat]["Optimis"]["Total Cost"].sum()
    c_pess = results[strat]["Pesimis"]["Total Cost"].sum()
    
    expected_cost = (c_norm * p_normal) + (c_opt * p_optimistic) + (c_pess * p_pessimistic)
    
    df_active = results[strat][selected_scenario]
    total_demand = df_active["Demand"].sum()
    total_shortage = df_active["Stockout"].sum()
    
    service_level = max(0.0, ((total_demand - total_shortage) / total_demand) * 100)
    
    actual_production = df_active["RT Production"].sum() + df_active["OT Production"].sum()
    max_capacity = (df_active["Workforce"] * worker_cap).sum() + (max_ot_cap * num_periods)
    capacity_util = (actual_production / max_capacity) * 100 if max_capacity > 0 else 0
    wf_util = (df_active["RT Production"].sum() / (df_active["Workforce"] * worker_cap).sum()) * 100
    
    summary_metrics.append({
        "Strategi": strat,
        "Total Cost (Active)": df_active["Total Cost"].sum(),
        "Expected Cost": expected_cost,
        "Total Inventory": df_active["Inventory"].sum(),
        "Total Stockout": df_active["Stockout"].sum(),
        "Total Overtime": df_active["OT Production"].sum(),
        "Total Subcontracting": df_active["Subcontracting"].sum(),
        "Service Level": service_level,
        "Workforce Utilization": wf_util,
        "Capacity Utilization": capacity_util
    })

summary_df = pd.DataFrame(summary_metrics)

# ==============================================================================
# 5. LAYOUT UTAMA: TABS INTERAKTIF
# ==============================================================================
# Menambahkan Tab MRP dari kode kedua Anda ke struktur utama secara seamless
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Ringkasan Eksekutif Agregat", 
    "🔍 Detail Analisis Operasional", 
    "🎲 Analisis Risiko (Robust Planning)",
    "📦 MRP - MCP Cumulative",
    "🎯 MRP - Least Unit Cost (LUC)"
])

# ------------------------------------------------------------------------------
# TAB 1: EXECUTIVE SUMMARY & STRATEGIC RECOMMENDATION
# ------------------------------------------------------------------------------
with tab1:
    st.subheader(f"Key Performance Indicator (KPI) - Skenario: {selected_scenario}")
    
    cols = st.columns(3)
    for idx, row in summary_df.iterrows():
        with cols[idx]:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Strategi {row['Strategi']}</div>
                <div class="kpi-value">IDR {row['Total Cost (Active)']:,.0f}</div>
                <small>Expected Cost: IDR {row['Expected Cost']:,.0f}</small><br>
                <small>Service Level: {row['Service Level']:.2f}%</small><br>
                <small>Cap. Util: {row['Capacity Utilization']:.1f}%</small>
            </div>
            """, unsafe_allow_html=True)
            
    st.markdown("---")
    
    c1, c2 = st.columns(2)
    with c1:
        fig_cost = px.bar(summary_df, x="Strategi", y="Total Cost (Active)", 
                          title=f"Perbandingan Total Biaya Operasional Horison 12 Bulan ({selected_scenario})",
                          color="Strategi", text_auto=',.0f', template="plotly_white")
        st.plotly_chart(fig_cost, use_container_width=True)
    with c2:
        fig_sl = px.bar(summary_df, x="Strategi", y="Service Level", 
                        title="Tingkat Layanan Pemenuhan Permintaan (Service Level %)",
                        color="Strategi", text_auto='.2f', range_y=[0, 105], template="plotly_white")
        st.plotly_chart(fig_sl, use_container_width=True)

    st.markdown("### 🤖 Rekomendasi Strategi Optimal")
    best_cost_strat = summary_df.loc[summary_df["Expected Cost"].idxmin()]["Strategi"]
    best_sl_strat = summary_df.loc[summary_df["Service Level"].idxmax()]["Strategi"]
    best_util_strat = summary_df.loc[summary_df["Capacity Utilization"].idxmax()]["Strategi"]
    
    st.markdown(f"""
    <div class="recommendation-box">
        <h4>🎯 Keputusan Strategis Berdasarkan Aturan Optimasi Terpadu:</h4>
        <ul>
            <li><b>Efisiensi Biaya Terbaik (Robust):</b> Strategi <b>{best_cost_strat}</b> memberikan nilai ekonomis paling tangguh (Expected Cost terendah lintas skenario).</li>
            <li><b>Keterandalan Layanan (Service Level):</b> Strategi <b>{best_sl_strat}</b> paling optimal meminimalisir risiko stockout di pasar.</li>
            <li><b>Efisiensi Fasilitas (Utilisasi Kapasitas):</b> Strategi <b>{best_util_strat}</b> mencatatkan penggunaan infrastruktur produksi paling produktif.</li>
        </ul>
        <p><b>Rekomendasi Final:</b> Disarankan menggunakan pendekatan <b>{best_cost_strat} Strategy</b> untuk mengamankan struktur finansial perusahaan dari fluktuasi ketidakpastian pasar jangka panjang.</p>
    </div>
    """, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# TAB 2: DETAILED STRATEGY DEEP-DIVE
# ------------------------------------------------------------------------------
with tab2:
    selected_strategy = st.radio("Pilih Strategi untuk Analisis Mendalam:", ["Chase", "Level", "Mixed"], horizontal=True)
    df_selected = results[selected_strategy][selected_scenario]
    
    st.subheader(f"📋 Master Table Aggregate Production Planning: {selected_strategy} ({selected_scenario})")
    master_display = df_selected[["Periode", "Demand", "Net Demand", "RT Production", "OT Production", "Subcontracting", "Total Supply", "Inventory", "Stockout"]]
    st.dataframe(master_display.style.format(precision=0), use_container_width=True)
    
    if selected_strategy == "Chase":
        st.subheader("👨‍🏭 Workforce & Capacity Adjustment Sheet (Chase Focus)")
        st.dataframe(df_selected[["Periode", "Workforce", "Hiring", "Firing", "RT Production"]].style.format(precision=0), use_container_width=True)
        
    elif selected_strategy == "Level":
        st.subheader("📦 Inventory Buffer & Capacity Efficiency Sheet (Level Focus)")
        df_level_spec = df_selected[["Periode", "Inventory", "Stockout", "RT Production"]].copy()
        df_level_spec["Capacity Efficiency (%)"] = (df_level_spec["RT Production"] / (df_selected["Workforce"] * worker_cap)) * 100
        st.dataframe(df_level_spec.style.format(precision=1), use_container_width=True)
        
    elif selected_strategy == "Mixed":
        st.subheader("🔄 Sourcing Optimization & Make-or-Buy Analysis (Mixed Focus)")
        mob_df = df_selected[["Periode", "RT Production", "OT Production", "Subcontracting"]].copy()
        total_p = mob_df["RT Production"] + mob_df["OT Production"] + mob_df["Subcontracting"]
        mob_df["Internal Content (%)"] = np.where(total_p > 0, ((mob_df["RT Production"] + mob_df["OT Production"]) / total_p) * 100, 0)
        st.dataframe(mob_df.style.format(precision=1), use_container_width=True)
        
        st.subheader("🪵 Raw Material Requirements Planning (BOM Explode Proxy)")
        raw_mat_df = pd.DataFrame({
            "Periode": df_selected["Periode"],
            "Incoming Material (Unit)": (df_selected["RT Production"] + df_selected["OT Production"]) * 1.05,
            "Usage Material (Unit)": (df_selected["RT Production"] + df_selected["OT Production"]),
            "Ending Inventory Material": np.maximum(0, 100 + ((df_selected["RT Production"] + df_selected["OT Production"]) * 0.05)),
            "Material Shortage": 0
        })
        st.dataframe(raw_mat_df.style.format(precision=0), use_container_width=True)

    st.subheader("💸 Analisis Finansial & Struktur Biaya Berjalan")
    cost_cols = ["Periode", "Material Cost", "Production Cost", "Labor Cost", "Hiring Cost", "Firing Cost", "Inventory Holding Cost", "Overtime Cost", "Subcontract Cost", "Shortage Cost", "Total Cost"]
    st.dataframe(df_selected[cost_cols].style.format(precision=0), use_container_width=True)
    
    st.markdown("---")
    st.subheader("📊 Visualisasi Performa Berkala (12 Periode)")
    v1, v2 = st.columns(2)
    with v1:
        fig_dp = go.Figure()
        fig_dp.add_trace(go.Scatter(x=df_selected["Periode"], y=df_selected["Demand"], name="Demand Real", line=dict(color='red', width=2, dash='dash')))
        fig_dp.add_trace(go.Bar(x=df_selected["Periode"], y=df_selected["RT Production"] + df_selected["OT Production"] + df_selected["Subcontracting"], name="Total Produksi", marker_color='royalblue'))
        fig_dp.update_layout(title="Perbandingan Tren Permintaan vs Realisasi Pasokan (12 Bulan)", barmode='group', template="plotly_white")
        st.plotly_chart(fig_dp, use_container_width=True)
    with v2:
        fig_cb = px.bar(df_selected, x="Periode", y=["Material Cost", "Production Cost", "Inventory Holding Cost", "Overtime Cost", "Subcontract Cost", "Shortage Cost"],
                        title="Dinamika Komponen Biaya per Periode", template="plotly_white")
        st.plotly_chart(fig_cb, use_container_width=True)

    v3, v4 = st.columns(2)
    with v3:
        fig_inv = px.line(df_selected, x="Periode", y="Inventory", title="Fluktuasi Tingkat Inventori Akhir", markers=True, template="plotly_white")
        st.plotly_chart(fig_inv, use_container_width=True)
    with v4:
        fig_os = go.Figure()
        fig_os.add_trace(go.Bar(x=df_selected["Periode"], y=df_selected["OT Production"], name="Overtime Vol", marker_color='orange'))
        fig_os.add_trace(go.Bar(x=df_selected["Periode"], y=df_selected["Subcontracting"], name="Subcontract Vol", marker_color='purple'))
        fig_os.update_layout(title="Alokasi Kapasitas Tambahan: Lembur vs Pihak Ketiga", barmode='stack', template="plotly_white")
        st.plotly_chart(fig_os, use_container_width=True)

# ------------------------------------------------------------------------------
# TAB 3: ROBUST SCENARIO & RISK ANALYSIS
# ------------------------------------------------------------------------------
with tab3:
    st.subheader("🎲 Matriks Analisis Risiko & Robust Planning")
    st.markdown("Tabel di bawah menyajikan komparasi performa finansial di seluruh spektrum kemungkinan permintaan untuk menguji ketangguhan model.")
    
    robust_records = []
    for strat in ["Chase", "Level", "Mixed"]:
        c_norm = results[strat]["Normal"]["Total Cost"].sum()
        c_opt = results[strat]["Optimis"]["Total Cost"].sum()
        c_pess = results[strat]["Pesimis"]["Total Cost"].sum()
        exp_c = (c_norm * p_normal) + (c_opt * p_optimistic) + (c_pess * p_pessimistic)
        
        robust_records.append({
            "Strategi": strat,
            "Skenario Pesimis (Cost)": c_pess,
            "Skenario Normal (Cost)": c_norm,
            "Skenario Optimis (Cost)": c_opt,
            "Expected Robust Cost": exp_c
        })
        
    robust_df = pd.DataFrame(robust_records)
    st.dataframe(robust_df.style.format({
        "Skenario Pesimis (Cost)": "IDR {:,.0f}",
        "Skenario Normal (Cost)": "IDR {:,.0f}",
        "Skenario Optimis (Cost)": "IDR {:,.0f}",
        "Expected Robust Cost": "IDR {:,.0f}"
    }), use_container_width=True)
    
    fig_robust = go.Figure()
    for strat in ["Chase", "Level", "Mixed"]:
        row = robust_df[robust_df["Strategi"] == strat].iloc[0]
        fig_robust.add_trace(go.Scatter(
            x=["Pesimis", "Normal", "Optimis"], 
            y=[row["Skenario Pesimis (Cost)"], row["Skenario Normal (Cost)"], row["Skenario Optimis (Cost)"]],
            mode='lines+markers', name=f"Profil Risiko {strat}"
        ))
    fig_robust.update_layout(title="Analisis Sensitivitas Struktur Biaya Lintas Skenario Permintaan", yaxis_title="Total Biaya (IDR)", template="plotly_white")
    st.plotly_chart(fig_robust, use_container_width=True)

# ==============================================================================
# INTEGRASI LOGIKA MRP (DARI KODE KEDUA) DENGAN SEAMLESS & AMAN
# ==============================================================================

# Pembuatan parameter tambahan di sidebar khusus MRP (Melanjutkan parameter Anda)
st.sidebar.markdown("---")
st.sidebar.header("📋 Parameter Tambahan MRP")
setup_cost = st.sidebar.number_input("Setup Cost per Order (S)", value=500)
holding_cost = st.sidebar.number_input("Holding Cost per Unit (H)", value=5)
initial_inventory = st.sidebar.number_input("Initial Inventory", value=30)
lead_time = st.sidebar.number_input("Lead Time (periods)", value=1)
# Variabel safety_stock di-rename khusus MRP agar tidak bertabrakan dengan safety stock perencanaan agregat
mrp_safety_stock = st.sidebar.number_input("MRP Safety Stock", value=0)

# ---------------- TAB 4: MCP Tab ----------------
with tab4:
    st.subheader("MCP Cumulative Iteration")
    uploaded_csv = st.file_uploader("Upload CSV (Period, GR, Scheduled_Receipts) for MCP", type=["csv"], key="mcp_tab")
    if uploaded_csv:
        df_input = pd.read_csv(uploaded_csv)
        periods = len(df_input)
        periods_label = [f"P{i+1}" for i in range(periods)]
        gross_req = df_input['GR'].tolist()
        scheduled_rec = df_input['Scheduled_Receipts'].tolist()

        all_iterations = []
        optimal_combinations = []
        i = 0
        current_inventory = initial_inventory
        prev_cost_per_period = None

        while i < periods:
            best_combo = None
            combos_tried = []

            for j in range(i, periods):
                temp_inventory = current_inventory
                nr_list = []
                for k in range(i, j+1):
                    nr = max(0, gross_req[k] + mrp_safety_stock - (temp_inventory + scheduled_rec[k]))
                    nr_list.append(nr)
                    temp_inventory += nr + scheduled_rec[k] - gross_req[k]

                net_demand = sum(nr_list)
                planned_receipt = [0]*(j-i+1)
                planned_receipt[0] = net_demand

                temp_inv2 = current_inventory
                cumulative_holding = 0
                for k, nr in zip(range(j-i+1), nr_list):
                    temp_inv2 += planned_receipt[k] + scheduled_rec[i+k] - gross_req[i+k]
                    cumulative_holding += max(temp_inv2,0)
                    temp_inv2 -= gross_req[i+k]

                total_cost = setup_cost + holding_cost * cumulative_holding
                cost_per_period = total_cost / (j-i+1)

                combos_tried.append({
                    "Period Combination": f"{periods_label[i]}-{periods_label[j]}" if i!=j else periods_label[i],
                    "Net Requirement": net_demand,
                    "Lot Size": net_demand,
                    "Total Cost": total_cost,
                    "Cost per Period": cost_per_period
                })

                if prev_cost_per_period is not None and cost_per_period > prev_cost_per_period:
                    break
                else:
                    best_combo = (i,j,net_demand,total_cost,cost_per_period)
                    prev_cost_per_period = cost_per_period

            if best_combo is None:
                best_combo = (i,i,nr_list[0], setup_cost + holding_cost*nr_list[0], setup_cost + holding_cost*nr_list[0])

            all_iterations.extend(combos_tried)
            start,end,lot_size,total_cost,cost_per_period = best_combo
            optimal_combinations.append({
                "Period Combination": f"{periods_label[start]}-{periods_label[end]}" if start!=end else periods_label[start],
                "Lot Size": lot_size,
                "Total Cost": total_cost,
                "Cost per Period": cost_per_period
            })

            for k in range(start,end+1):
                current_inventory += lot_size if k==start else 0
                current_inventory += scheduled_rec[k] - gross_req[k]

            i = end+1

        st.markdown("### All Iterations Tested (MCP)")
        st.dataframe(pd.DataFrame(all_iterations), use_container_width=True)
        st.markdown("### Optimal Combination per Step (MCP)")
        st.dataframe(pd.DataFrame(optimal_combinations), use_container_width=True)

        csv_buffer = BytesIO()
        combined = pd.concat([pd.DataFrame(all_iterations), pd.DataFrame(optimal_combinations)],
                             keys=["All Iterations","Optimal"])
        combined.to_csv(csv_buffer)
        st.download_button("Download MCP CSV", data=csv_buffer,
                           file_name="mcp_final_multitab.csv", mime="text/csv")

# ---------------- TAB 5: LUC Tab ----------------
with tab5:
    st.subheader("Least Unit Cost (LUC) Iteration")
    uploaded_csv = st.file_uploader("Upload CSV (Period, GR, Scheduled_Receipts) for LUC", type=["csv"], key="luc_tab")
    if uploaded_csv:
        df_input = pd.read_csv(uploaded_csv)
        periods = len(df_input)
        periods_label = [f"P{i+1}" for i in range(periods)]
        gross_req = df_input['GR'].tolist()
        scheduled_rec = df_input['Scheduled_Receipts'].tolist()

        all_iterations = []
        optimal_combinations = []
        i = 0
        current_inventory = initial_inventory

        while i < periods:
            best_combo = None
            combos_tried = []

            for j in range(i, periods):
                temp_inventory = current_inventory
                nr_list = []
                for k in range(i,j+1):
                    nr = max(0, gross_req[k] + mrp_safety_stock - (temp_inventory + scheduled_rec[k]))
                    nr_list.append(nr)
                    temp_inventory += nr + scheduled_rec[k] - gross_req[k]

                net_demand = sum(nr_list)
                planned_receipt = [0]*(j-i+1)
                planned_receipt[0] = net_demand

                temp_inv2 = current_inventory
                cumulative_holding = 0
                for k, nr in zip(range(j-i+1), nr_list):
                    temp_inv2 += planned_receipt[k] + scheduled_rec[i+k] - gross_req[i+k]
                    cumulative_holding += max(temp_inv2,0)
                    temp_inv2 -= gross_req[i+k]

                total_cost = setup_cost + holding_cost * cumulative_holding
                unit_cost = total_cost / max(net_demand,1)

                combos_tried.append({
                    "Period Combination": f"{periods_label[i]}-{periods_label[j]}" if i!=j else periods_label[i],
                    "Net Requirement": net_demand,
                    "Lot Size": net_demand,
                    "Total Cost": total_cost,
                    "Unit Cost": unit_cost
                })

                if best_combo is not None and unit_cost > best_combo[4]:
                    break
                else:
                    best_combo = (i,j,net_demand,total_cost,unit_cost)

            if best_combo is None:
                best_combo = (i,i,nr_list[0], setup_cost + holding_cost*nr_list[0], setup_cost + holding_cost*nr_list[0])

            all_iterations.extend(combos_tried)
            start,end,lot_size,total_cost,unit_cost = best_combo
            optimal_combinations.append({
                "Period Combination": f"{periods_label[start]}-{periods_label[end]}" if start!=end else periods_label[start],
                "Lot Size": lot_size,
                "Total Cost": total_cost,
                "Unit Cost": unit_cost
            })

            for k in range(start,end+1):
                current_inventory += lot_size if k==start else 0
                current_inventory += scheduled_rec[k] - gross_req[k]

            i = end+1

        st.markdown("### All Iterations Tested (LUC)")
        df_all = pd.DataFrame(all_iterations)
        st.dataframe(df_all, use_container_width=True)
        st.markdown("### Optimal Combination per Step (LUC)")
        df_optimal = pd.DataFrame(optimal_combinations)
        st.dataframe(df_optimal, use_container_width=True)

        csv_buffer = BytesIO()
        combined = pd.concat([pd.DataFrame(all_iterations), pd.DataFrame(optimal_combinations)],
                             keys=["All Iterations","Optimal"])
        combined.to_csv(csv_buffer)
        st.download_button("Download LUC CSV", data=csv_buffer,
                           file_name="luc_final_multitab.csv", mime="text/csv")
