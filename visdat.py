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
co2_path = r'C:\Users\Lenovo\Downloads\API_EN.GHG.CO2.MT.CE.AR5_DS2_en_csv_v2_3349\API_EN.GHG.CO2.MT.CE.AR5_DS2_en_csv_v2_3349.csv'
try:
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
    # Contoh visualisasi gabungan: Scatter plot Renewable Capacity vs CO2 Emissions
    st.subheader("Kapasitas Terbarukan vs Emisi CO₂")
    st.markdown("Visualisasi ini memperlihatkan hubungan antara kapasitas listrik terbarukan per kapita dan emisi CO₂ per negara per tahun.")
    fig_scatter = px.scatter(
        df_merged.dropna(subset=['CO2 Emissions (Mt CO2e)']),
        x='Renewable Capacity (W/capita)',
        y='CO2 Emissions (Mt CO2e)',
        color='Country',
        hover_data=['Year'],
        title='Renewable Capacity vs CO2 Emissions'
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
except Exception as e:
    st.warning(f"Gagal memuat atau menggabungkan data emisi CO₂: {e}")

st.markdown("""
<h1 style='color:#fff; text-align:center; font-size:2.8rem; font-weight:700; margin-bottom:0.5em;'>Blue Pacific 2050: Climate Change & Disasters Data Explorer</h1>
""", unsafe_allow_html=True)

st.markdown("""
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

# Sidebar filter global
st.sidebar.header("Filter Global")
selected_countries = st.sidebar.multiselect('Pilih negara', countries, default=countries)
year_min, year_max = int(df['Year'].min()), int(df['Year'].max())
selected_years = st.sidebar.slider('Pilih rentang tahun', year_min, year_max, (year_min, year_max))

# Filter data global
filtered = df[(df['Country'].isin(selected_countries)) & (df['Year'] >= selected_years[0]) & (df['Year'] <= selected_years[1])]

# --- Visualisasi 1: Line Chart ---
st.header("Line Chart Interaktif: Renewable Capacity per Negara")
st.markdown("""
Visualisasi ini memperlihatkan tren kapasitas listrik terbarukan per kapita di negara-negara Pasifik dari tahun ke tahun. Pilihan negara dan rentang tahun di sidebar akan mempengaruhi seluruh grafik di bawah.
""")
fig = px.line(
    filtered.groupby(['Year', 'Country'], as_index=False).mean(),
    x='Year',
    y='Renewable Capacity (W/capita)',
    color='Country',
    markers=True,
    labels={'Renewable Capacity (W/capita)': 'Watt per kapita', 'Year': 'Tahun'},
    title='Tren Kapasitas Terbarukan per Negara'
)
fig.update_layout(legend_title_text='Negara', hovermode='x unified')
st.plotly_chart(fig, use_container_width=True)

# --- Narasi penghubung ---
st.markdown("""
Dengan melihat tren di atas, kita dapat mengamati negara mana yang mengalami peningkatan signifikan dalam kapasitas listrik terbarukan. Selanjutnya, kita lihat distribusi dan perbandingan antar negara pada tahun-tahun yang dipilih.
""")

# --- Visualisasi 2: Bar Chart ---
st.subheader("Perbandingan Kapasitas Antar Negara (Bar Chart)")
latest_year = filtered['Year'].max()
st.write(f"Menampilkan data untuk tahun: {latest_year}")
df_bar = filtered[filtered['Year'] == latest_year].sort_values('Renewable Capacity (W/capita)', ascending=False)
fig_bar = px.bar(df_bar, x='Country', y='Renewable Capacity (W/capita)', color='Country', labels={'Renewable Capacity (W/capita)': 'Watt per kapita', 'Country': 'Negara'}, title=f'Kapasitas Terpasang per Negara ({latest_year})')
st.plotly_chart(fig_bar, use_container_width=True)

# --- Narasi penghubung ---
st.markdown("""
Bar chart di atas memperlihatkan perbandingan kapasitas antar negara pada tahun terakhir yang dipilih. Selanjutnya, kita lihat sebaran (distribusi) kapasitas di seluruh negara dan tahun.
""")

# --- Visualisasi 3: Boxplot ---
st.subheader("Distribusi Kapasitas per Tahun (Boxplot)")
fig_box = px.box(filtered, x='Year', y='Renewable Capacity (W/capita)', points='all', labels={'Renewable Capacity (W/capita)': 'Watt per kapita', 'Year': 'Tahun'}, title='Sebaran Kapasitas Terpasang per Tahun')
st.plotly_chart(fig_box, use_container_width=True)

# --- Narasi penghubung ---
st.markdown("""
Boxplot di atas membantu memahami variasi kapasitas antar negara di setiap tahun. Dengan filter global, Anda bisa fokus pada negara atau periode tertentu untuk analisis lebih dalam.
""")

# --- Visualisasi 4: Data Table ---
st.subheader("Tabel Data Eksplorasi Renewable Capacity per Negara & Tahun")
filtered_table = filtered.copy()

# Buat dropdown filter untuk setiap kolom
col1, col2, col3 = st.columns(3)
with col1:
    country_opt = ['(Semua)'] + sorted(filtered_table['Country'].unique().tolist())
    country_sel = st.selectbox('Filter Country', country_opt)
    if country_sel != '(Semua)':
        filtered_table = filtered_table[filtered_table['Country'] == country_sel]
with col2:
    year_opt = ['(Semua)'] + sorted(filtered_table['Year'].unique().tolist())
    year_sel = st.selectbox('Filter Year', year_opt)
    if year_sel != '(Semua)':
        filtered_table = filtered_table[filtered_table['Year'] == year_sel]
with col3:
    # Value biasanya numerik, bisa filter rentang jika mau
    min_val, max_val = float(filtered_table['Renewable Capacity (W/capita)'].min()), float(filtered_table['Renewable Capacity (W/capita)'].max())
    value_range = st.slider('Filter Renewable Capacity (W/capita)', min_val, max_val, (min_val, max_val))
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

