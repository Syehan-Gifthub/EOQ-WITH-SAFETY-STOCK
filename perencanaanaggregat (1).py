import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import io  # Penambahan modul input/output untuk pengelolaan file Excel instan

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
    /* 1. Reset Global ke Light Mode Total & Bebas Tabrakan Warna */
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
    
    /* 2. Desain Sidebar Minimalis & Bersih */
    [data-testid="stSidebar"] {
        background-color: #f8fafc !important; /* Abu-abu ultra light profesional */
        border-right: 1px solid #e2e8f0 !important; /* Garis pembatas sangat tipis & ringan */
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

    /* 3. Membongkar Paksa Tabel st.dataframe & st.data_editor Agar Full Putih & Teks Hitam */
    div[data-testid="stDataFrame"], div[data-testid="stDataEditor"], [data-testid="stTable"] {
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05) !important;
    }

    /* Override paksa komponen internal canvas/glide-data-grid milik Streamlit */
    div[data-testid="stGridCanvas"] canvas {
        filter: invert(0) !important; /* Mencegah inversi warna otomatis oleh browser/server */
    }
    
    /* Menargetkan background dan teks kontainer internal data editor */
    div[data-baseweb="table"] {
        background-color: #ffffff !important;
        color: #1e293b !important;
    }
    
    /* 4. Perbaikan Kotak Input & Tombol (+ / -) di Sidebar */
    div[data-baseweb="input"], div[data-baseweb="select"], select, input {
        background-color: #ffffff !important;
        color: #1e293b !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 6px !important;
    }
    
    /* Desain tombol step penambah/pengurang angka agar tampak profesional */
    button[title="Increment"], button[title="Decrement"], 
    [data-testid="stNumberInputStepDown"], [data-testid="stNumberInputStepUp"] {
        background-color: #f1f5f9 !important;
        color: #475569 !important;
        border: 1px solid #cbd5e1 !important;
        opacity: 1 !important;
    }
    
    button[title="Increment"]:hover, button[title="Decrement"]:hover {
        background-color: #e2e8f0 !important;
        color: #0f172a !important;
    }

    /* 5. Komponen Card KPI & Rekomendasi Dengan Aksen Gradasi Elegan */
    .kpi-card {
        background-color: #ffffff !important;
        border-radius: 10px;
        padding: 22px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        border: 1px solid #e2e8f0;
        position: relative;
        overflow: hidden;
    }
    /* Memberikan indikator bar gradasi tipis di sisi kiri card */
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
    
    /* Box Rekomendasi dengan latar gradasi linear tipis */
    .recommendation-box {
        background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%) !important; /* Gradasi hijau muda sukses yang sangat soft */
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

    /* 6. Garis Pembatas (HR) & Desain Tab Minimalis */
    hr {
        border: 0;
        height: 1px;
        background: #e2e8f0 !important;
        margin: 24px 0;
    }

    .stTabs [data-baseweb="tab-list"] { 
        gap: 4px; 
        border-bottom: 1px solid #e2e8f0;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent !important;
        border: none !important;
        color: #64748b !important;
        padding: 10px 16px;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        color: #3b82f6 !important;
        border-bottom: 2px solid #3b82f6 !important;
        font-weight: 600 !important;
    }

    /* 7. Box Panduan Upload Excel Premium (BARU) */
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
# INTEGRASI TEMPLATE & KOTAK UPLOAD EXCEL OTOMATIS (BARU)
# ==============================================================================
num_periods = 12
default_demand = [1200, 1300, 1500, 1700, 1800, 1600, 1400, 1300, 1100, 1400, 1600, 1900]

# Inisialisasi basis data demand ke dalam Session State agar tersinkronisasi lintas komponen
if "df_demand_state" not in st.session_state:
    st.session_state.df_demand_state = pd.DataFrame({
        "Periode": [f"Bulan {i+1}" for i in range(num_periods)],
        "Demand": default_demand
    })

# Desain Banner Instruksi Upload yang Menarik & Informatif
st.markdown("""
<div class="upload-box">
    <h4>📅 Integrasi Data Massal via Excel Template</h4>
    <p>Gunakan panel ini untuk mengunggah target permintaan (demand) secara sekaligus. Untuk memastikan integrasi berjalan lancar tanpa galat, file Excel wajib menggunakan struktur <b>Kepala Tabel (Header Column)</b> berikut:</p>
    <table class="table-template">
        <tr>
            <th>Periode (Kolom 1)</th>
            <th>Demand (Kolom 2)</th>
        </tr>
        <tr>
            <td>Bulan 1</td>
            <td>1200</td>
        </tr>
        <tr>
            <td>Bulan 2</td>
            <td>1300</td>
        </tr>
    </table>
    <small style="color: #64748b; font-weight: 500;">*Sistem secara otomatis menyesuaikan nilai di sidebar dan melakukan kalkulasi ulang pada seluruh grafik model.</small>
</div>
""", unsafe_allow_html=True)

# Generate File Excel Template secara Real-Time dalam Memory (Buffer)
template_io = io.BytesIO()
with pd.ExcelWriter(template_io, engine='openpyxl') as writer:
    st.session_state.df_demand_state.to_excel(writer, index=False, sheet_name='Demand_Template')
template_io.seek(0)

# Layout Interaktif Tombol Unduh & Unggah Excel
col_dl, col_up = st.columns([1, 2])

with col_dl:
    st.write("") # Spacer keselarasan vertikal
    st.write("") 
    st.download_button(
        label="📥 Unduh Template Excel Resmi",
        data=template_io,
        file_name="template_kepala_tabel_demand.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

with col_up:
    uploaded_file = st.file_uploader("Seret atau pilih file Excel Anda di sini:", type=["xlsx", "xls"], label_visibility="collapsed")

# Logika Pemrosesan Otomatis jika User mengupload file Excel
if uploaded_file is not None:
    try:
        excel_data = pd.read_excel(uploaded_file)
        # Validasi struktur kepala tabel agar sesuai prasyarat mesin hitung
        if "Periode" in excel_data.columns and "Demand" in excel_data.columns:
            # Ambil 12 periode teratas & konversi nilai ke tipe numerik integer beralur aman
            parsed_df = excel_data[["Periode", "Demand"]].head(num_periods).copy()
            parsed_df["Demand"] = pd.to_numeric(parsed_df["Demand"], errors='coerce').fillna(0).astype(int)
            
            # Perbarui state global aplikasi
            st.session_state.df_demand_state = parsed_df
            
            # Hancurkan session state internal widget editor lama agar dipaksa memuat data baru dari Excel
            if "demand_editor_key" in st.session_state:
                del st.session_state["demand_editor_key"]
                
            st.success("✅ File Excel berhasil diverifikasi! Seluruh data tabel utama dan sidebar otomatis diselaraskan.")
        else:
            st.error("❌ Format Kepala Tabel Salah! Pastikan kolom berlabel persis 'Periode' dan 'Demand'.")
    except Exception as e:
        st.error(f"❌ Gagal membaca file: {str(e)}")

st.markdown("---")

# ==============================================================================
# 2. SIDEBAR - INPUT PARAMETER OPERASIONAL & BIAYA
# ==============================================================================
st.sidebar.header("🛠️ Parameter Operasional")

# Input Demand Base via UI Dataframe (Sekarang Otomatis ter-update jika mengunggah Excel)
st.sidebar.subheader("Permintaan (Demand) per Periode")
demand_df = st.sidebar.data_editor(
    st.session_state.df_demand_state,
    hide_index=True,
    key="demand_editor_key"
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
tab1, tab2, tab3 = st.tabs([
    "📈 Ringkasan Eksekutif & Rekomendasi", 
    "🔍 Detail Analisis Operasional per Strategi", 
    "🎲 Analisis Risiko Skenario (Robust Planning)"
])

# Fungsi helper premium untuk grafik Plotly (Background Transparan & Grid Halus & Teks Gelap Pekat)
def apply_forced_light_theme(fig):
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#0f172a", family="'Inter', sans-serif"),
        title_font=dict(color="#0f172a", size=14, family="'Inter', sans-serif"),
        xaxis=dict(gridcolor="#f1f5f9", tickfont=dict(color="#475569"), title_font=dict(color="#0f172a")),
        yaxis=dict(gridcolor="#f1f5f9", tickfont=dict(color="#475569"), title_font=dict(color="#0f172a")),
        legend=dict(font=dict(color="#475569"))
    )
    return fig

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
                          color="Strategi", text_auto=',.0f', color_discrete_sequence=px.colors.qualitative.Safe)
        fig_cost = apply_forced_light_theme(fig_cost)
        st.plotly_chart(fig_cost, use_container_width=True)
    with c2:
        fig_sl = px.bar(summary_df, x="Strategi", y="Service Level", 
                        title="Tingkat Layanan Pemenuhan Permintaan (Service Level %)",
                        color="Strategi", text_auto='.2f', range_y=[0, 105], color_discrete_sequence=px.colors.qualitative.Safe)
        fig_sl = apply_forced_light_theme(fig_sl)
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
    
    st.markdown("### 📊 Visualisasi Performa Berkala (12 Periode)")
    v1, v2 = st.columns(2)
    with v1:
        fig_dp = go.Figure()
        fig_dp.add_trace(go.Scatter(x=df_selected["Periode"], y=df_selected["Demand"], name="Demand Real", line=dict(color='#ef4444', width=2, dash='dash')))
        fig_dp.add_trace(go.Bar(x=df_selected["Periode"], y=df_selected["RT Production"] + df_selected["OT Production"] + df_selected["Subcontracting"], name="Total Produksi", marker_color='#3b82f6'))
        fig_dp.update_layout(title="Perbandingan Tren Permintaan vs Realisasi Pasokan (12 Bulan)", barmode='group')
        fig_dp = apply_forced_light_theme(fig_dp)
        st.plotly_chart(fig_dp, use_container_width=True)
    with v2:
        fig_cb = px.bar(df_selected, x="Periode", y=["Material Cost", "Production Cost", "Inventory Holding Cost", "Overtime Cost", "Subcontract Cost", "Shortage Cost"],
                        title="Dinamika Komponen Biaya per Periode", color_discrete_sequence=px.colors.qualitative.Safe)
        fig_cb = apply_forced_light_theme(fig_cb)
        st.plotly_chart(fig_cb, use_container_width=True)

    v3, v4 = st.columns(2)
    with v3:
        fig_inv = px.line(df_selected, x="Periode", y="Inventory", title="Fluktuasi Tingkat Inventori Akhir", markers=True, line_shape="linear")
        fig_inv.update_traces(line=dict(color='#10b981'))
        fig_inv = apply_forced_light_theme(fig_inv)
        st.plotly_chart(fig_inv, use_container_width=True)
    with v4:
        fig_os = go.Figure()
        fig_os.add_trace(go.Bar(x=df_selected["Periode"], y=df_selected["OT Production"], name="Overtime Vol", marker_color='#f59e0b'))
        fig_os.add_trace(go.Bar(x=df_selected["Periode"], y=df_selected["Subcontracting"], name="Subcontract Vol", marker_color='#8b5cf6'))
        fig_os.update_layout(title="Alokasi Kapasitas Tambahan: Lembur vs Pihak Ketiga", barmode='stack')
        fig_os = apply_forced_light_theme(fig_os)
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
    fig_robust.update_layout(title="Analisis Sensitivitas Struktur Biaya Lintas Skenario Permintaan", yaxis_title="Total Biaya (IDR)")
    fig_robust = apply_forced_light_theme(fig_robust)
    st.plotly_chart(fig_robust, use_container_width=True)
