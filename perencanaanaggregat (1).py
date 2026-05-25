import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# ==============================================================================
# 1. KONFIGURASI HALAMAN & TEMA GLOBAL (MEMAKSA LIGHT MODE VIA CONFIG)
# ==============================================================================
st.set_page_config(
    page_title="Interactive Aggregate Planning Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Menyuntikkan konfigurasi tema bawaan Streamlit secara paksa agar Full Light Mode
# Ini akan menyelesaikan masalah teks putih yang hilang di latar belakang putih.
st.markdown("""
<style>
    /* Mengunci skema warna global browser ke light mode */
    :root {
        color-scheme: light !important;
    }
    
    /* --- Latar Belakang & Teks Utama --- */
    .stApp {
        background-color: #ffffff !important;
        color: #111111 !important;
    }
    
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    
    /* --- Perbaikan Sidebar (Full Putih & Teks Hitam Pekat) --- */
    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 3px solid #ff69b4 !important; /* Garis pembatas pink tebal */
    }
    section[data-testid="stSidebar"] *, 
    section[data-testid="stSidebar"] label, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] p {
        color: #111111 !important; /* Memaksa semua teks di sidebar menjadi hitam */
    }

    /* --- Perbaikan Input Box & Tombol Plus Minus (+ / -) --- */
    div[data-baseweb="input"] {
        background-color: #ffffff !important;
        border: 2px solid #ff69b4 !important;
        border-radius: 6px !important;
    }
    div[data-baseweb="input"] input {
        color: #111111 !important;
        background-color: #ffffff !important;
    }
    
    /* Tombol tambah kurang pada input angka */
    button[title="Increment"], button[title="Decrement"] {
        background-color: #ffffff !important;
        color: #ff1493 !important; /* Warna pink kontras untuk tombol */
        border: 1px solid #ff69b4 !important;
    }
    button[title="Increment"]:hover, button[title="Decrement"]:hover {
        background-color: #ffe4e1 !important;
    }

    /* --- Perbaikan Total Tabel / Dataframe (Anti-Hitam) --- */
    div[data-testid="stDataFrame"], div[data-testid="stDataEditor"], div[data-testid="stTable"] {
        background-color: #ffffff !important;
        border: 2px solid #ff69b4 !important;
        border-radius: 8px !important;
    }
    /* Memaksa isi sel di dalam tabel berlatar putih pekat dengan teks hitam */
    div[data-testid="stDataFrame"] *, div[data-testid="stDataEditor"] * {
        background-color: #ffffff !important;
        color: #111111 !important;
    }
    /* Mengubah warna border antar baris/kolom tabel menjadi pink tipis */
    div[data-testid="stDataFrame"] [role="gridcell"], 
    div[data-testid="stDataEditor"] [role="gridcell"] {
        border-color: #ffe4e1 !important;
    }

    /* --- Custom Card Metrik KPI & Rekomendasi --- */
    .kpi-card {
        background-color: #ffffff !important;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(255, 105, 180, 0.25);
        border: 1px solid #ffe4e1;
        border-left: 7px solid #ff1493; /* Garis pink tegas di sisi kiri */
        margin-bottom: 15px;
        color: #111111 !important;
    }
    .kpi-title { font-size: 14px; color: #ff1493; font-weight: bold; text-transform: uppercase; }
    .kpi-value { font-size: 24px; color: #000000; font-weight: bold; margin-top: 5px; }
    
    .recommendation-box {
        background-color: #fffafb; /* Warna latar pink putih pastel */
        border-radius: 8px;
        padding: 25px;
        border: 1px solid #ffe4e1;
        border-left: 7px solid #ff1493;
        margin-top: 20px;
        color: #111111 !important;
    }
    .recommendation-box h4 { color: #d81b60; font-weight: bold; }

    /* Garis pemisah horizontal (hr) */
    hr {
        border-top: 2px solid #ffe4e1 !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("📊 Sistem Pendukung Keputusan: Perencanaan Agregat Interaktif (12 Periode)")
st.markdown("Aplikasi analisis strategi produksi komprehensif dengan pendekatan *Robust Planning* berbasis skenario.")
st.markdown("---")

# ==============================================================================
# 2. SIDEBAR - INPUT PARAMETER OPERASIONAL & BIAYA (LOGIKA TETAP UTUH)
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
# 3. LOGIKA MESIN PERHITUNGAN STRATEGI AGREGAT (TETAP UTUH)
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
        elif strategy == "Mixed":
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
                
        elif strategy in ["Chase", "Level"] and deficit > 0:
            pass

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
# 4. EVALUASI METRIK KPI UTAMA (EXPECTED VALUE)
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
# 5. LAYOUT TABS UTAMA
# ==============================================================================
tab1, tab2, tab3 = st.tabs([
    "📈 Ringkasan Eksekutif & Rekomendasi", 
    "🔍 Detail Analisis Operasional per Strategi", 
    "🎲 Analisis Risiko Skenario (Robust Planning)"
])

# --- TAB 1 ---
with tab1:
    st.subheader(f"Key Performance Indicator (KPI) - Skenario: {selected_scenario}")
    
    cols = st.columns(3)
    for idx, row in summary_df.iterrows():
        with cols[idx]:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Strategi {row['Strategi']}</div>
                <div class="kpi-value">IDR {row['Total Cost (Active)']:,.0f}</div>
                <small style="color: #495057;">Expected Cost: IDR {row['Expected Cost']:,.0f}</small><br>
                <small style="color: #495057;">Service Level: {row['Service Level']:.2f}%</small><br>
                <small style="color: #495057;">Cap. Util: {row['Capacity Utilization']:.1f}%</small>
            </div>
            """, unsafe_allow_html=True)
            
    st.markdown("---")
    
    c1, c2 = st.columns(2)
    with c1:
        fig_cost = px.bar(summary_df, x="Strategi", y="Total Cost (Active)", 
                          title=f"Perbandingan Total Biaya Operasional ({selected_scenario})",
                          color="Strategi", text_auto=',.0f',
                          color_discrete_sequence=["#ff69b4", "#db7093", "#ffb6c1"])
        fig_cost.update_layout(template="plotly_white", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#111111"))
        st.plotly_chart(fig_cost, use_container_width=True)
    with c2:
        fig_sl = px.bar(summary_df, x="Strategi", y="Service Level", 
                        title="Tingkat Layanan Pemenuhan Permintaan (Service Level %)",
                        color="Strategi", text_auto='.2f', range_y=[0, 105],
                        color_discrete_sequence=["#ff69b4", "#db7093", "#ffb6c1"])
        fig_sl.update_layout(template="plotly_white", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#111111"))
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

# --- TAB 2 ---
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
        
        st.subheader("🪵 Raw Material Requirements Planning")
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

    st.markdown("### 📊 Visualisasi Performa Berkala (12 Periode)")
    v1, v2 = st.columns(2)
    with v1:
        fig_dp = go.Figure()
        fig_dp.add_trace(go.Scatter(x=df_selected["Periode"], y=df_selected["Demand"], name="Demand Real", line=dict(color='red', width=2, dash='dash')))
        fig_dp.add_trace(go.Bar(x=df_selected["Periode"], y=df_selected["RT Production"] + df_selected["OT Production"] + df_selected["Subcontracting"], name="Total Produksi", marker_color='royalblue'))
        fig_dp.update_layout(title="Perbandingan Tren Permintaan vs Pasokan", barmode='group', template="plotly_white", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#111111"))
        st.plotly_chart(fig_dp, use_container_width=True)
    with v2:
        fig_cb = px.bar(df_selected, x="Periode", y=["Material Cost", "Production Cost", "Inventory Holding Cost", "Overtime Cost", "Subcontract Cost", "Shortage Cost"], title="Komponen Biaya per Periode")
        fig_cb.update_layout(template="plotly_white", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#111111"))
        st.plotly_chart(fig_cb, use_container_width=True)

# --- TAB 3 ---
with tab3:
    st.subheader("🎲 Matriks Analisis Risiko & Robust Planning")
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
    line_colors = {"Chase": "#ff1493", "Level": "#d81b60", "Mixed": "#4169e1"}
    for strat in ["Chase", "Level", "Mixed"]:
        row = robust_df[robust_df["Strategi"] == strat].iloc[0]
        fig_robust.add_trace(go.Scatter(
            x=["Pesimis", "Normal", "Optimis"], 
            y=[row["Skenario Pesimis (Cost)"], row["Skenario Normal (Cost)"], row["Skenario Optimis (Cost)"]],
            mode='lines+markers', name=f"Profil Risiko {strat}", line=dict(color=line_colors[strat], width=4)
        ))
    fig_robust.update_layout(title="Analisis Sensitivitas Struktur Biaya Lintas Skenario", yaxis_title="Total Biaya (IDR)", template="plotly_white", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#111111"))
    st.plotly_chart(fig_robust, use_container_width=True)
