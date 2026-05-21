import streamlit as st
import pandas as pd
import plotly.express as px

# 1. SETTING HALAMAN
st.set_page_config(page_title="Digital HoQ - UKM Tahu", layout="wide")

st.markdown("""
    <style>
    .main-header { font-size: 28px; font-weight: bold; color: #1E3A8A; margin-bottom: 10px; }
    .sub-header { font-size: 18px; color: #64748b; margin-bottom: 20px; }
    .section-box { padding: 20px; border-radius: 10px; background-color: #f8fafc; border: 1px solid #e2e8f0; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="main-header">🏠 Digital House of Quality (HoQ)</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Optimalisasi Spesifikasi Teknis berdasarkan Voice of Customer (UKM Tahu Endang)</p>', unsafe_allow_html=True)

# 2. INISIALISASI DATA (Session State)
if 'whats' not in st.session_state:
    st.session_state.whats = pd.DataFrame({
        "Customer Requirement (WHATs)": ["Tahu tidak mudah hancur", "Rasa kedelai terasa", "Warna kuning cerah", "Harga terjangkau"],
        "Importance (1-5)": [5, 4, 3, 5]
    })

if 'hows' not in st.session_state:
    st.session_state.hows = pd.DataFrame({
        "Technical Requirement (HOWs)": ["Tekanan Mesin Pres", "Kualitas Kedelai", "Lama Perebusan", "Takaran Kunyit"],
        "Direction": ["Max", "Max", "Target", "Max"]
    })

# --- TABS STRUKTUR ---
t1, t2, t3, t4, t5 = st.tabs(["1. WHATs", "2. HOWs", "3. Correlation", "4. Matrix", "5. 🏆 FINAL HOUSE"])

# TAB 1 & 2 (Input Data)
with t1:
    st.session_state.whats = st.data_editor(st.session_state.whats, num_rows="dynamic", use_container_width=True, key="ed_whats")
with t2:
    st.session_state.hows = st.data_editor(st.session_state.hows, num_rows="dynamic", use_container_width=True, key="ed_hows")

# TAB 3 (Correlation - The Roof)
with t3:
    hows_list = st.session_state.hows["Technical Requirement (HOWs)"].tolist()
    if 'roof_matrix' not in st.session_state or list(st.session_state.roof_matrix.columns) != hows_list:
        st.session_state.roof_matrix = pd.DataFrame("", index=hows_list, columns=hows_list)
    st.session_state.roof_matrix = st.data_editor(st.session_state.roof_matrix, use_container_width=True, key="ed_roof")

# TAB 4 (Relationship Matrix)
with t4:
    whats_list = st.session_state.whats["Customer Requirement (WHATs)"].tolist()
    if 'rel_matrix' not in st.session_state or list(st.session_state.rel_matrix.columns) != hows_list:
        st.session_state.rel_matrix = pd.DataFrame(0, index=whats_list, columns=hows_list)
    st.session_state.rel_matrix = st.data_editor(st.session_state.rel_matrix, use_container_width=True, key="ed_rel")

# --- TAB 5: THE FINAL HOUSE ---
with t5:
    try:
        # LOGIKA HITUNG
        weights = st.session_state.whats["Importance (1-5)"].values
        matrix_values = st.session_state.rel_matrix.values.astype(float)
        abs_importance = (matrix_values.T * weights).T.sum(axis=0)
        total = abs_importance.sum()
        rel_importance = (abs_importance / total * 100) if total > 0 else abs_importance * 0

        # --- LAYOUT RUMAH ---
        
        # 1. ATAP (Correlation)
        st.info("🛖 **Bagian Atap:** Korelasi Antar Persyaratan Teknis (Trade-offs)")
        st.dataframe(st.session_state.roof_matrix, use_container_width=True)

        st.write("")

        # 2. BADAN RUMAH (Relationship)
        st.success("🏢 **Bagian Utama:** Hubungan WHATs vs HOWs")
        col_voc, col_mat = st.columns([1, 2.5])
        with col_voc:
            st.write("**Customer Requirements**")
            st.dataframe(st.session_state.whats, hide_index=True, use_container_width=True)
        with col_mat:
            st.write("**Relationship Matrix (Scores)**")
            st.dataframe(st.session_state.rel_matrix, use_container_width=True)

        st.write("")

        # 3. FONDASI (Scores & Pareto)
        st.warning("⚓ **Bagian Fondasi:** Prioritas Spesifikasi Teknis")
        
        res_df = pd.DataFrame({
            "Requirement": hows_list,
            "Score": abs_importance,
            "Weight %": rel_importance.round(1)
        }).sort_values(by="Score", ascending=False)

        f1, f2 = st.columns([1, 1.5])
        with f1:
            st.write("**Peringkat Prioritas**")
            st.dataframe(res_df, hide_index=True, use_container_width=True)
        with f2:
            fig = px.bar(res_df, x="Requirement", y="Score", text="Weight %", 
                         color="Score", color_continuous_scale="Viridis")
            fig.update_layout(height=300, margin=dict(t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error("Silakan lengkapi data di tab-tab sebelumnya agar rumah bisa dibangun!")
