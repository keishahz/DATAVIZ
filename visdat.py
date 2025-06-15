import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os

st.set_page_config(page_title="Pacific Islands Renewable Capacity", layout="wide")

@st.cache_data
def load_data():
    file_path = 'Blue Pacific 2050_ Climate Change And Disasters (Thematic Area 5) data.csv'
    df = pd.read_csv(file_path)
    cols = ['Pacific Island Countries and territories', 'TIME_PERIOD', 'OBS_VALUE']
    df = df[cols]
    df = df.rename(columns={
        'Pacific Island Countries and territories': 'Country',
        'TIME_PERIOD': 'Year',
        'OBS_VALUE': 'Renewable Capacity (W/capita)'
    })
    df = df.dropna(subset=['Year', 'Renewable Capacity (W/capita)'])
    df['Year'] = df['Year'].astype(int)
    df['Renewable Capacity (W/capita)'] = df['Renewable Capacity (W/capita)'].astype(float)
    return df

df = load_data()
countries = sorted(df['Country'].unique())

# Load dan transformasi data emisi CO2
co2_filenames = [
    'API_EN.GHG.CO2.MT.CE.AR5_DS2_en_csv_v2_3349.csv',
    'API_EN.GHG.CO2.MT.CE.AR5_DS2_en_csv_v2_3349/API_EN.GHG.CO2.MT.CE.AR5_DS2_en_csv_v2_3349.csv',
    r'C:\Users\Lenovo\Downloads\API_EN.GHG.CO2.MT.CE.AR5_DS2_en_csv_v2_3349\API_EN.GHG.CO2.MT.CE.AR5_DS2_en_csv_v2_3349.csv'
]
co2_path = None
for fname in co2_filenames:
    if os.path.exists(fname):
        co2_path = fname
        break
try:
    if co2_path:
        df_co2 = pd.read_csv(co2_path, skiprows=4)
        df_co2_long = df_co2.melt(
            id_vars=['Country Name'],
            var_name='Year',
            value_name='CO2 Emissions (Mt CO2e)'
        )
        df_co2_long = df_co2_long.rename(columns={'Country Name': 'Country'})
        df_co2_long['Year'] = pd.to_numeric(df_co2_long['Year'], errors='coerce')
        df_co2_long = df_co2_long.dropna(subset=['Year'])
        # Gabungkan dengan data utama (df)
        df_merged = pd.merge(df, df_co2_long, on=['Country', 'Year'], how='left')
    else:
        st.warning("File data emisi CO₂ tidak ditemukan di folder project atau Downloads.")
except Exception as e:
    st.warning(f"Gagal memuat atau menggabungkan data emisi CO₂: {e}")

st.markdown("""
<h1 style='color:#fff; text-align:center; font-size:2.8rem; font-weight:700; margin-bottom:0.5em;'>Blue Pacific 2050: Climate Change & Disasters Data Explorer</h1>
<div style='background-color:#e3f2fd; padding:16px; border-radius:8px; margin-bottom:20px;'>
    <b style='color:#1976d2;'>Deskripsi Visualisasi:</b><br>
    <span style='color:#333;'>Grafik di bawah ini menampilkan perkembangan kapasitas terpasang listrik terbarukan (dalam watt per kapita) di negara-negara Pasifik dari tahun ke tahun.</span><br>
    <ul>
        <li style='color:#388e3c;'><b>Setiap garis</b> mewakili satu negara.</li>
        <li style='color:#f57c00;'>Hover</li> <span style='color:#333;'>pada garis untuk melihat detail nilai pada tahun tertentu.</span>
        <li style='color:#0288d1;'>Pilih negara</li> <span style='color:#333;'>di sidebar untuk membandingkan negara tertentu.</span>
        <li style='color:#7b1fa2;'>Data diambil dari <i>Blue Pacific 2050 - Climate Change And Disasters (Thematic Area 5)</i>.</li>
    </ul>
    <span style='color:#333;'>Visualisasi ini membantu memahami tren adopsi energi terbarukan di kawasan Pasifik dan membandingkan antar negara secara interaktif.</span>
</div>
""", unsafe_allow_html=True)

st.markdown(
    """
    <style>
    .stApp {
        background-color: #102542 !important;
    }
    section[data-testid="stSidebar"] {
        background-color: #061126 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# (Bagian narasi dan visualisasi story-telling di atas DIHAPUS, hanya visualisasi interaktif dengan filter per chart yang ditampilkan di bawah)

# --- Visualisasi 1: Tren Renewable Capacity ---
st.subheader("Tren Kapasitas Listrik Terbarukan per Negara")
st.markdown("Tren ini menunjukkan upaya transisi energi bersih di negara-negara Pasifik.")
vis1_countries = st.multiselect('Pilih negara (visualisasi 1)', countries, default=countries, key='v1-country')
vis1_year_min, vis1_year_max = int(df['Year'].min()), int(df['Year'].max())
vis1_years = st.slider('Pilih rentang tahun (visualisasi 1)', vis1_year_min, vis1_year_max, (vis1_year_min, vis1_year_max), key='v1-year')
vis1_filtered = df[(df['Country'].isin(vis1_countries)) & (df['Year'] >= vis1_years[0]) & (df['Year'] <= vis1_years[1])]
fig1 = px.line(
    vis1_filtered.groupby(['Year', 'Country'], as_index=False).mean(),
    x='Year',
    y='Renewable Capacity (W/capita)',
    color='Country',
    markers=True,
    labels={'Renewable Capacity (W/capita)': 'Watt per kapita', 'Year': 'Tahun'},
    title='Tren Kapasitas Terbarukan per Negara'
)
fig1.update_layout(legend_title_text='Negara', hovermode='x unified')
st.plotly_chart(fig1, use_container_width=True, key="line1-main")
st.markdown("""
Dari grafik di atas, kita dapat melihat negara mana yang paling aktif meningkatkan kapasitas listrik terbarukan. Selanjutnya, kita lihat apakah upaya ini berdampak pada penurunan emisi CO₂.
""")

# --- Visualisasi 2: Tren Emisi CO2 (jika data tersedia) ---
if 'df_merged' in locals():
    vis2_countries = st.multiselect('Pilih negara (visualisasi 2)', countries, default=countries, key='v2-country')
    vis2_year_min, vis2_year_max = int(df['Year'].min()), int(df['Year'].max())
    vis2_years = st.slider('Pilih rentang tahun (visualisasi 2)', vis2_year_min, vis2_year_max, (vis2_year_min, vis2_year_max), key='v2-year')
    filtered_merged = df_merged[(df_merged['Country'].isin(vis2_countries)) & (df_merged['Year'] >= vis2_years[0]) & (df_merged['Year'] <= vis2_years[1])]
    st.subheader("Tren Emisi CO₂ per Negara")
    st.markdown("Tren ini memperlihatkan perubahan emisi CO₂ seiring waktu. Penurunan emisi dapat menjadi indikasi keberhasilan transisi energi terbarukan.")
    fig2 = px.line(
        filtered_merged.groupby(['Year', 'Country'], as_index=False).mean(),
        x='Year',
        y='CO2 Emissions (Mt CO2e)',
        color='Country',
        markers=True,
        labels={'CO2 Emissions (Mt CO2e)': 'Emisi CO₂ (Mt)', 'Year': 'Tahun'},
        title='Tren Emisi CO₂ per Negara'
    )
    fig2.update_layout(legend_title_text='Negara', hovermode='x unified')
    st.plotly_chart(fig2, use_container_width=True, key="line2-main")
    st.markdown("""
Bandingkan tren kedua grafik di atas: apakah negara yang kapasitas terbarukannya naik, emisinya juga turun?
""")
else:
    st.warning("Data emisi CO₂ tidak tersedia. Silakan pastikan file CO₂ sudah ada di folder project.")

# --- Visualisasi 3: Scatter Plot Hubungan Renewable Capacity vs Emisi CO2 ---
if 'df_merged' in locals():
    vis3_countries = st.multiselect('Pilih negara (visualisasi 3)', countries, default=countries, key='v3-country')
    vis3_year_min, vis3_year_max = int(df['Year'].min()), int(df['Year'].max())
    vis3_years = st.slider('Pilih rentang tahun (visualisasi 3)', vis3_year_min, vis3_year_max, (vis3_year_min, vis3_year_max), key='v3-year')
    filtered_merged = df_merged[(df_merged['Country'].isin(vis3_countries)) & (df_merged['Year'] >= vis3_years[0]) & (df_merged['Year'] <= vis3_years[1])]
    st.subheader("Korelasi Kapasitas Terbarukan & Emisi CO₂")
    st.markdown("Scatter plot berikut memperlihatkan hubungan langsung antara kapasitas listrik terbarukan dan emisi CO₂. Titik-titik mewakili negara-tahun.")
    fig3_scatter = px.scatter(
        filtered_merged.dropna(subset=['CO2 Emissions (Mt CO2e)']),
        x='Renewable Capacity (W/capita)',
        y='CO2 Emissions (Mt CO2e)',
        color='Country',
        hover_data=['Year'],
        title='Renewable Capacity vs CO2 Emissions'
    )
    st.plotly_chart(fig3_scatter, use_container_width=True, key="scatter_co2-main")
    st.markdown("""
Jika terlihat pola menurun (semakin tinggi kapasitas terbarukan, emisi makin rendah), berarti transisi energi bersih efektif menurunkan emisi penyebab climate change.
""")
else:
    st.warning("Data emisi CO₂ tidak tersedia. Silakan pastikan file CO₂ sudah ada di folder project.")

# --- Visualisasi 4: Data Table ---
st.subheader("Tabel Data Eksplorasi Renewable Capacity per Negara & Tahun")
filtered_table = df.copy()
col1, col2, col3 = st.columns(3)
with col1:
    country_opt = ['(Semua)'] + sorted(filtered_table['Country'].unique().tolist())
    country_sel = st.selectbox('Filter Country', country_opt, key='table-country')
    if country_sel != '(Semua)':
        filtered_table = filtered_table[filtered_table['Country'] == country_sel]
with col2:
    year_opt = ['(Semua)'] + sorted(filtered_table['Year'].unique().tolist())
    year_sel = st.selectbox('Filter Year', year_opt, key='table-year')
    if year_sel != '(Semua)':
        filtered_table = filtered_table[filtered_table['Year'] == year_sel]
with col3:
    min_val, max_val = float(filtered_table['Renewable Capacity (W/capita)'].min()), float(filtered_table['Renewable Capacity (W/capita)'].max())
    value_range = st.slider('Filter Renewable Capacity (W/capita)', min_val, max_val, (min_val, max_val), key='table-value')
    filtered_table = filtered_table[(filtered_table['Renewable Capacity (W/capita)'] >= value_range[0]) & (filtered_table['Renewable Capacity (W/capita)'] <= value_range[1])]
st.dataframe(filtered_table)

# 7. Download Data
st.subheader("Download Data")
csv = df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download CSV",
    data=csv,
    file_name='blue_pacific_2050_data.csv',
    mime='text/csv',
)
