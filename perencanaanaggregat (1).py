import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import io

# ==============================================================================
# 1. KONFIGURASI HALAMAN & STYLE DASHBOARD (MINIMALIS, PROFESIONAL & GRADASI)
# ==============================================================================
st.set_page_config(
    page_title="Interactive Aggregate Planning Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS Premium: Minimalis, Profesional, dengan Sentuhan Gradasi Halus
st.markdown("""
<style>
    :root {
        color-scheme: light !important;
        --st-background: #ffffff !important;
        --st-color: #1e293b !important;
    }
    
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"], .main {
        background-color: #ffffff !important;
        color: #1e293b !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    [data-testid="stSidebar"] {
        background-color: #f8fafc !important;
        border-right: 1px solid #e2e8f0 !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #0f172a !important;
        font-weight: 600 !important;
    }

    div[data-testid="stDataFrame"], div[data-testid="stDataEditor"], [data-testid="stTable"] {
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05) !important;
    }

    div[data-testid="stGridCanvas"] canvas {
        filter: invert(0) !important;
    }
    
    div[data-baseweb="table"] {
        background-color: #ffffff !important;
        color: #1e293b !important;
    }
    
    div[data-baseweb="input"], div[data-baseweb="select"], select, input {
        background-color: #ffffff !important;
        color: #1e293b !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 6px !important;
    }
    
    button[title="Increment"], button[title="Decrement"], 
    [data-testid="stNumberInputStepDown"], [data-testid="stNumberInputStepUp"] {
        background-color: #f1f5f9 !important;
        color: #475569 !important;
        border: 1px solid #cbd5e1 !important;
        opacity: 1 !important;
    }

    .kpi-card {
        background-color: #ffffff !important;
        border-radius: 10px;
        padding: 22px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        border: 1px solid #e2e8f0;
        position: relative;
        overflow: hidden;
    }
    .kpi-card::before {
        content: "";
        position: absolute;
        top: 0; left: 0; bottom: 0;
        width: 4px;
        background: linear-gradient(180deg, #3b82f6 0%, #6366f1 100%);
    }
    .kpi-title { font-size: 13px; color: #64748b !important; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
    .kpi-value { font-size: 24px; color: #0f172a !important; font-weight: 700; margin-top: 6px; }
    .kpi-card small { color: #475569 !important; font-weight: 500; }
    
    .recommendation-box {
        background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%) !important;
        border: 1px solid #bbf7d0;
        border-radius: 10px;
        padding: 25px;
        position: relative;
    }
    .recommendation-box::before {
        content: "";
        position: absolute;
        top: 0; left: 0; bottom: 0;
        width: 5px;
        background: linear-gradient(180deg, #22c55e 0%, #10b981 100%);
    }
    .recommendation-box h4 { color: #166534 !important; font-weight: 700; margin-top: 0; }
    .recommendation-box li, .recommendation-box p { color: #1e293b !important; font-weight: 500; line-height: 1.6; }

    hr {
        border: 0;
        height: 1px;
        background: #e2e8f0 !important;
        margin: 24px 0;
    }

    .upload-box {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%) !important;
        border: 1px solid #cbd5e1;
        border-radius: 10px;
        padding: 22px;
        position: relative;
        margin-bottom: 20px;
    }
    .upload-box::before {
        content: "";
        position: absolute;
        top: 0; left: 0; bottom: 0;
        width: 5px;
        background: linear-gradient(180deg, #3b82f6 0%, #6366f1 100%);
    }
    .upload-box h4 { color: #0f172a !important; font-weight: 700; margin-top: 0; margin-bottom: 8px;}
    .upload-box p { color: #334155 !important; font-size: 14px; margin-bottom: 12px; line-height: 1.5; }
    .table-template { width: 100%; border-collapse: collapse; margin: 10px 0; background-color: #ffffff; }
    .table-template th { background-color: #e2e8f0; color: #0f172a; padding: 6px 12px; border: 1px solid #cbd5e1; font-size: 13px; font-weight: 600; text-align: left; }
    .table-template td { padding: 6px 12px; border: 1px solid #cbd5e1; color: #475569; font-size: 13px; font-family: monospace; }
</style>
""", unsafe_allow_html=True)

st.title("📊 Sistem Pendukung Keputusan: Perencanaan Agregat Interaktif (12 Periode)")
st.markdown("Aplikasi analisis strategi produksi komprehensif dengan pendekatan *Robust Planning* berbasis skenario.")
st.markdown("---")

# ==============================================================================
# MANAJEMEN STATE & INTEGRASI EXCEL LENGKAP (5 KOLOM)
# ==============================================================================
num_periods = 12

# Inisialisasi awal Master Data jika belum ada di session state
if "master_data" not in st.session_state:
    st.session_state.master_data = pd.DataFrame({
        "Periode": [f"Bulan {i+1}" for i in range(num_periods)],
        "Demand": [1200, 1300, 1500, 1700, 1800, 1600, 1400, 1300, 1100, 1400, 1600, 1900],
        "Kapasitas per Pekerja": [70] * num_periods,
        "Tenaga Kerja": [20] * num_periods,
        "Inventory Awal": [200] + [0] * (num_periods - 1)  # Default awal di bulan pertama
    })

if "editor_trigger" not in st.session_state:
    st.session_state.editor_trigger = 0

# Tampilan Panduan Baru dengan Struktur Kepala Tabel Lengkap
st.markdown("""
<div class="upload-box">
    <h4>📅 Integrasi Data Operasional Massal via Excel Template</h4>
    <p>Sekarang Anda dapat mengunggah target permintaan beserta batasan kapasitas dan parameter awal sekaligus. Pastikan file Excel Anda menggunakan struktur <b>Kepala Tabel (Header Column)</b> tepat seperti di bawah ini:</p>
    <table class="table-template">
        <tr>
            <th>Periode</th>
            <th>Demand</th>
            <th>Kapasitas per Pekerja</th>
            <th>Tenaga Kerja</th>
            <th>Inventory Awal</th>
        </tr>
        <tr>
            <td>Bulan 1</td>
            <td>1200</td>
            <td>70</td>
            <td>20</td>
            <td>200</td>
        </tr>
        <tr>
            <td>Bulan 2</td>
            <td>1300</td>
            <td>70</td>
            <td>20</td>
            <td>0</td>
        </tr>
    </table>
    <small style="color: #64748b; font-weight: 500;">*Catatan: Nilai 'Tenaga Kerja' dan 'Inventory Awal' pada baris Bulan 1 akan otomatis dijadikan sebagai baseline acuan awal sistem.</small>
</div>
""", unsafe_allow_html=True)

# Generate File Excel Template secara Real-Time
template_io = io.BytesIO()
with pd.ExcelWriter(template_io, engine='openpyxl') as writer:
    st.session_state.master_data.to_excel(writer, index=False, sheet_name='Planning_Template')
template_io.seek(0)

col_dl, col_up = st.columns([1, 2])
with col_dl:
    st.write("") 
    st.write("") 
    st.download_button(
        label="📥 Unduh Template Excel Lengkap",
        data=template_io,
        file_name="template_master_operasional.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

with col_up:
    uploaded_file = st.file_uploader("Seret atau pilih file Excel Anda di sini:", type=["xlsx", "xls"], label_visibility="collapsed")

# Logika Pemrosesan Ungguhan Excel untuk 5 Kolom
required_cols = ["Periode", "Demand", "Kapasitas per Pekerja", "Tenaga Kerja", "Inventory Awal"]
if uploaded_file is not None:
    try:
        excel_data = pd.read_excel(uploaded_file)
        if all(col in excel_data.columns for col in required_cols):
            parsed_df = excel_data[required_cols].head(num_periods).copy()
            
            # Validasi dan konversi tipe data numerik
            for col in required_cols[1:]:
                parsed_df[col] = pd.to_numeric(parsed_df[col], errors='coerce').fillna(0).astype(int)
            
            # Jika baris kurang dari 12, lengkapi sisanya
            if len(parsed_df) < num_periods:
                extra_rows = pd.DataFrame({
                    "Periode": [f"Bulan {i+1}" for i in range(len(parsed_df), num_periods)],
                    "Demand": [0] * (num_periods - len(parsed_df)),
                    "Kapasitas per Pekerja": [70] * (num_periods - len(parsed_df)),
                    "Tenaga Kerja": [20] * (num_periods - len(parsed_df)),
                    "Inventory Awal": [0] * (num_periods - len(parsed_df))
                })
                parsed_df = pd.concat([parsed_df, extra_rows], ignore_index=True)
                
            st.session_state.master_data = parsed_df
            st.session_state.editor_trigger += 1
            st.success("✅ Seluruh data master operasional dari Excel berhasil diselaraskan ke dalam sistem!")
        else:
            st.error(f"❌ Format Kepala Tabel Salah! Pastikan kolom berlabel persis: {', '.join(required_cols)}")
    except Exception as e:
        st.error(f"❌ Gagal membaca file: {str(e)}")

st.markdown("---")

# ==============================================================================
# TABEL EDITOR UTAMA (MAIN PANEL - LUXURIOUS & SPACIUS UX)
# ==============================================================================
st.subheader("📝 Master Table Input Parameter Operasional")
st.markdown("Anda bisa langsung mengubah angka Demand, Kapasitas, Tenaga Kerja Baseline, maupun Inventory Awal langsung pada tabel interaktif di bawah ini:")

active_master_df = st.data_editor(
    st.session_state.master_data,
    hide_index=True,
    key=f"master_editor_{st.session_state.editor_trigger}",
    use_container_width=True
)
# Simpan perubahan kembali ke session state agar persisten
st.session_state.master_data = active_master_df

# Ekstraksi Variabel Baseline dari baris pertama tabel editor
init_inv = int(active_master_df.iloc[0]["Inventory Awal"])
init_workforce = int(active_master_df.iloc[0]["Tenaga Kerja"])

st.markdown("---")

# ==============================================================================
# SIDEBAR - BIAYA & SKENARIO KETIDAKPASTIAN
# ==============================================================================
st.sidebar.header("💰 Struktur Biaya (IDR)")
c_material = st.sidebar.number_input("Biaya Bahan Baku (/Unit)", value=150000, step=5000, min_value=0)
c_regular = st.sidebar.number_input("Biaya Produksi Reguler (/Unit)", value=50000, step=1000, min_value=0)
c_overtime = st.sidebar.number_input("Biaya Overtime (/Unit)", value=75000, step=1000, min_value=0)
c_subcontract = st.sidebar.number_input("Biaya Subcontracting (/Unit)", value=90000, step=1000, min_value=0)
c_inventory = st.sidebar.number_input("Biaya Simpan (/Unit/Bulan)", value=10000, step=500, min_value=0)
c_stockout = st.sidebar.number_input("Biaya Shortage (/Unit/Bulan)", value=15000, step=500, min_value=0)
c_hiring = st.sidebar.number_input("Biaya Rekrutmen (/Pekerja)", value=2000000, step=50000, min_value=0)
c_firing = st.sidebar.number_input("Biaya PHK (/Pekerja)", value=3500000, step=50000, min_value=0)

st.sidebar.subheader("🛡️ Batasan Kapasitas Tambahan")
safety_stock = st.sidebar.number_input("Safety Stock Target (Unit)", value=100, min_value=0)
max_ot_cap = st.sidebar.number_input("Batas Maksimum Overtime (Unit/Bulan)", value=300, min_value=0)
min_sub_cap = st.sidebar.number_input("Batas Minimum Subkontrak (Unit)", value=50, min_value=0)
max_sub_cap = st.sidebar.number_input("Batas Maksimum Subkontrak (Unit)", value=500, min_value=0)

st.sidebar.header("🎲 Skenario Ketidakpastian")
p_normal = st.sidebar.slider("Probabilitas Normal", 0.0, 1.0, 0.6, step=0.05)
p_optimistic = st.sidebar.slider("Probabilitas Optimis (+25%)", 0.0, 1.0 - p_normal, 0.2, step=0.05)
p_pessimistic = round(1.0 - p_normal - p_optimistic, 2)
st.sidebar.text(f"Probabilitas Pesimis (-25%): {p_pessimistic}")

selected_scenario = st.selectbox("Pilih Skenario Tampilan Utama Dashboard:", ["Normal", "Optimis", "Pesimis"])

# ==============================================================================
# 3. PERBAIKAN LOGIKA ENGINE PERHITUNGAN AGREGAT (MENDUKUNG KANVAS DINAMIS)
# ==============================================================================
def calculate_aggregate_planning(strategy, master_df, scenario_demand_list):
    inv_prev = init_inv
    wf_prev = init_workforce
    records = []
    
    # Pre-kalkulasi untuk Strategi Level berdasarkan kapasitas per pekerja bulanan yang dinamis
    if strategy == "Level":
        total_demand = sum(scenario_demand_list)
        total_production_needed = max(0, total_demand + safety_stock - init_inv)
        total_capacity_per_worker = master_df["Kapasitas per Pekerja"].sum()
        constant_wf = int(np.ceil(total_production_needed / (total_capacity_per_worker / num_periods))) if total_capacity_per_worker > 0 else 0
    else:
        constant_wf = init_workforce

    for t in range(num_periods):
        row = master_df.iloc[t]
        b_d = int(row["Demand"])
        d_t = scenario_demand_list[t]
        worker_cap_t = int(row["Kapasitas per Pekerja"])
        net_demand = d_t + safety_stock
        
        # 1. Logika Penyesuaian Tenaga Kerja & Produksi Reguler
        if strategy == "Chase":
            prod_needed = max(0, d_t + safety_stock - inv_prev)
            wf_needed = int(np.ceil(prod_needed / worker_cap_t)) if worker_cap_t > 0 else 0
            hiring = max(0, wf_needed - wf_prev)
            firing = max(0, wf_prev - wf_needed)
            wf_current = wf_needed
            rt_prod = wf_current * worker_cap_t
        elif strategy == "Level":
            wf_current = constant_wf
            hiring = max(0, wf_current - wf_prev) if t == 0 else 0
            firing = max(0, wf_prev - wf_current) if t == 0 else 0
            rt_prod = wf_current * worker_cap_t
        elif strategy == "Mixed":
            wf_current = int(row["Tenaga Kerja"]) if t > 0 else init_workforce
            hiring = max(0, wf_current - wf_prev)
            firing = max(0, wf_prev - wf_current)
            rt_prod = wf_current * worker_cap_t

        # 2. Logika Alokasi Lembur & Subkontrak
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

        # 3. Neraca Inventori Akhir vs Stockout Riil
        total_supply = inv_prev + rt_prod + ot_prod + sub_prod
        if total_supply >= d_t:
            inv_end = total_supply - d_t
            stockout = 0
        else:
            inv_end = 0
            stockout = d_t - total_supply
            
        # 4. Penghitungan Cost Matrix Komprehensif
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
            "Periode": row["Periode"],
            "Base Demand": b_d,
            "Demand": d_t,
            "Kapasitas/Pekerja": worker_cap_t,
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

# Integrasi Skenario Multiplier
base_demands = active_master_df["Demand"].tolist()
demand_scenarios = {
    "Normal": base_demands,
    "Optimis": [int(d * 1.25) for d in base_demands],
    "Pesimis": [int(d * 0.75) for d in base_demands]
}

# Pemrosesan Seluruh Kombinasi
results = {}
for strat in ["Chase", "Level", "Mixed"]:
    results[strat] = {}
    for scen, d_list in demand_scenarios.items():
        results[strat][scen] = calculate_aggregate_planning(strat, active_master_df, d_list)

# ==============================================================================
# 4. EVALUASI KPI & EXPECTED VALUE STRATEGIS
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
    
    service_level = max(0.0, ((total_demand - total_shortage) / total_demand) * 100) if total_demand > 0 else 100
    actual_production = df_active["RT Production"].sum() + df_active["OT Production"].sum()
    max_capacity = (df_active["Workforce"] * df_active["Kapasitas/Pekerja"]).sum() + (max_ot_cap * num_periods)
    capacity_util = (actual_production / max_capacity) * 100 if max_capacity > 0 else 0
    
    summary_metrics.append({
        "Strategi": strat,
        "Total Cost (Active)": df_active["Total Cost"].sum(),
        "Expected Cost": expected_cost,
        "Service Level": service_level,
        "Capacity Utilization": capacity_util
    })

summary_df = pd.DataFrame(summary_metrics)

# ==============================================================================
# 5. LAYOUT TABS INTERAKTIF
# ==============================================================================
tab1, tab2, tab3 = st.tabs([
    "📈 Ringkasan Eksekutif & Rekomendasi", 
    "🔍 Detail Analisis Operasional per Strategi", 
    "🎲 Analisis Risiko Skenario (Robust Planning)"
])

def apply_forced_light_theme(fig):
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#0f172a", family="'Inter', sans-serif"),
        title_font=dict(color="#0f172a", size=14, family="'Inter', sans-serif"),
        xaxis=dict(gridcolor="#f1f5f9", tickfont=dict(color="#475569")),
        yaxis=dict(gridcolor="#f1f5f9", tickfont=dict(color="#475569")),
        legend=dict(font=dict(color="#475569"))
    )
    return fig

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
                <small>Expected Cost: IDR {row['Expected Cost']:,.0f}</small><br>
                <small>Service Level: {row['Service Level']:.2f}%</small><br>
                <small>Cap. Util: {row['Capacity Utilization']:.1f}%</small>
            </div>
            """, unsafe_allow_html=True)
            
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        fig_cost = px.bar(summary_df, x="Strategi", y="Total Cost (Active)", title="Perbandingan Total Biaya Operasional", color="Strategi", text_auto=',.0f', color_discrete_sequence=px.colors.qualitative.Safe)
        st.plotly_chart(apply_forced_light_theme(fig_cost), use_container_width=True)
    with c2:
        fig_sl = px.bar(summary_df, x="Strategi", y="Service Level", title="Service Level (%)", color="Strategi", text_auto='.2f', range_y=[0, 105], color_discrete_sequence=px.colors.qualitative.Safe)
        st.plotly_chart(apply_forced_light_theme(fig_sl), use_container_width=True)

# --- TAB 2 ---
with tab2:
    selected_strategy = st.radio("Pilih Strategi untuk Analisis Mendalam:", ["Chase", "Level", "Mixed"], horizontal=True)
    df_selected = results[selected_strategy][selected_scenario]
    
    st.subheader(f"📋 Master Table Perencanaan Terpilih: {selected_strategy} ({selected_scenario})")
    master_display = df_selected[["Periode", "Base Demand", "Demand", "Kapasitas/Pekerja", "Workforce", "Hiring", "Firing", "RT Production", "OT Production", "Subcontracting", "Total Supply", "Inventory", "Stockout"]]
    st.dataframe(master_display.style.format(precision=0), use_container_width=True)
    
    st.subheader("💸 Detail Komponen Finansial")
    cost_cols = ["Periode", "Material Cost", "Production Cost", "Labor Cost", "Hiring Cost", "Firing Cost", "Inventory Holding Cost", "Overtime Cost", "Subcontract Cost", "Shortage Cost", "Total Cost"]
    st.dataframe(df_selected[cost_cols].style.format(precision=0), use_container_width=True)

    st.markdown("### 📊 Tren Grafis Operasional")
    v1, v2 = st.columns(2)
    with v1:
        fig_dp = go.Figure()
        fig_dp.add_trace(go.Scatter(x=df_selected["Periode"], y=df_selected["Demand"], name="Demand Riil", line=dict(color='#ef4444', width=2, dash='dash')))
        fig_dp.add_trace(go.Bar(x=df_selected["Periode"], y=df_selected["RT Production"] + df_selected["OT Production"] + df_selected["Subcontracting"], name="Total Realisasi Produksi", marker_color='#3b82f6'))
        fig_dp.update_layout(barmode='group')
        st.plotly_chart(apply_forced_light_theme(fig_dp), use_container_width=True)
    with v2:
        fig_cb = px.bar(df_selected, x="Periode", y=["Material Cost", "Production Cost", "Inventory Holding Cost", "Overtime Cost", "Subcontract Cost", "Shortage Cost"], title="Struktur Pembebanan Biaya", color_discrete_sequence=px.colors.qualitative.Safe)
        st.plotly_chart(apply_forced_light_theme(fig_cb), use_container_width=True)

# --- TAB 3 ---
with tab3:
    st.subheader("🎲 Matriks Analisis Ketangguhan Skenario (Robust Planning)")
    robust_records = []
    for strat in ["Chase", "Level", "Mixed"]:
        robust_records.append({
            "Strategi": strat,
            "Skenario Pesimis (Cost)": results[strat]["Pesimis"]["Total Cost"].sum(),
            "Skenario Normal (Cost)": results[strat]["Normal"]["Total Cost"].sum(),
            "Skenario Optimis (Cost)": results[strat]["Optimis"]["Total Cost"].sum(),
            "Expected Robust Cost": (results[strat]["Normal"]["Total Cost"].sum() * p_normal) + (results[strat]["Optimis"]["Total Cost"].sum() * p_optimistic) + (results[strat]["Pesimis"]["Total Cost"].sum() * p_pessimistic)
        })
    st.dataframe(pd.DataFrame(robust_records).style.format({c: "IDR {:,.0f}" for c in ["Skenario Pesimis (Cost)", "Skenario Normal (Cost)", "Skenario Optimis (Cost)", "Expected Robust Cost"]}), use_container_width=True)
