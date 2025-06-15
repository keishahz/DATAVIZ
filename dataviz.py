import streamlit as st
import plotly.express as px
import numpy as np
import os
import matplotlib.pyplot as plt

# --- LOAD DATA ---
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
co2_path = 'API_EN.GHG.CO2.MT.CE.AR5_DS2_en_csv_v2_3349.csv'
df_co2 = None
df_merged = None
if os.path.exists(co2_path):
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
    st.warning("File data emisi CO₂ tidak ditemukan di folder project.")

# --- VISUALISASI ---
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

# --- VISUALISASI ORANG TERDAMPAT BENCANA ---
st.title("Visualisasi Jumlah Orang Terdampak Bencana per Negara")

# Baca data
df = pd.read_csv(r'../Blue Pacific 2050_ Climate Change And Disasters (Thematic Area 5) data.csv')
df.columns = df.columns.str.strip()
if 'Pacific Island Countries and territories' in df.columns:
    df = df.rename(columns={'Pacific Island Countries and territories': 'Country'})

# Otomatis cari kolom value dan year yang benar
value_col = None
year_col = None
for col in ['Value', 'OBS_VALUE', 'Observation value']:
    if col in df.columns:
        value_col = col
        break
for col in ['Year', 'TIME_PERIOD', 'Time']:
    if col in df.columns:
        year_col = col
        break

if value_col is None or year_col is None:
    st.error('Kolom nilai (Value/OBS_VALUE/Observation value) atau tahun (Year/TIME_PERIOD/Time) tidak ditemukan di dataset.')
else:
    # Filter hanya indikator 'Number of people affected by disaster'
    disaster_indicator = 'Number of people affected by disaster'
    df_disaster = df[df['Indicator'] == disaster_indicator]

    if df_disaster.empty:
        st.warning('Tidak ada data orang terdampak bencana di dataset ini.')
    else:
        st.subheader('Grafik Jumlah Orang Terdampak Bencana per Negara (Total Seluruh Tahun)')
        # Hitung total orang terdampak per negara
        total_per_country = df_disaster.groupby('Country')[value_col].sum().sort_values(ascending=False).reset_index()
        fig = px.bar(
            total_per_country,
            x='Country',
            y=value_col,
            color='Country',
            labels={value_col: 'Total Orang Terdampak', 'Country': 'Negara'},
            title='Total Orang Terdampak Bencana per Negara (Akumulasi Seluruh Tahun)',
            hover_data={value_col: ':,', 'Country': True}
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

        # --- INSIGHT OTOMATIS & STATISTIK RINGKAS ---
        max_country = total_per_country.loc[total_per_country[value_col].idxmax(), 'Country']
        max_value = int(total_per_country[value_col].max())
        min_country = total_per_country.loc[total_per_country[value_col].idxmin(), 'Country']
        min_value = int(total_per_country[value_col].min())
        total_affected = int(df_disaster[value_col].sum())
        mean_affected = int(df_disaster[value_col].mean())
        median_affected = int(df_disaster[value_col].median())
        # Tahun dengan jumlah terdampak terbanyak
        total_per_year = df_disaster.groupby(year_col)[value_col].sum()
        max_year = int(total_per_year.idxmax())
        max_year_value = int(total_per_year.max())
        st.info(f"""
        **Insight Otomatis:**
        - Negara dengan jumlah orang terdampak bencana terbanyak: **{max_country}** ({max_value:,} orang)
        - Negara dengan jumlah terdampak paling sedikit: **{min_country}** ({min_value:,} orang)
        - Tahun paling parah (jumlah terdampak terbanyak): **{max_year}** ({max_year_value:,} orang di seluruh kawasan)
        - Total seluruh orang terdampak bencana: **{total_affected:,}**
        - Rata-rata per entri: **{mean_affected:,}**, Median: **{median_affected:,}**
        """)

        st.subheader('Grafik Jumlah Orang Terdampak Bencana per Negara per Tahun')
        # Pilih negara
        negara_pilih = st.selectbox('Pilih Negara', sorted(df_disaster['Country'].unique()))
        df_negara = df_disaster[df_disaster['Country'] == negara_pilih]
        fig2 = px.line(
            df_negara,
            x=year_col,
            y=value_col,
            markers=True,
            labels={year_col: 'Tahun', value_col: 'Jumlah Orang Terdampak'},
            title=f'Jumlah Orang Terdampak Bencana di {negara_pilih} per Tahun',
            hover_data={year_col: True, value_col: ':,'}
        )
        st.plotly_chart(fig2, use_container_width=True)
        # Narasi otomatis
        if not df_negara.empty:
            max_tahun_negara = df_negara.loc[df_negara[value_col].idxmax(), year_col]
            max_val_negara = int(df_negara[value_col].max())
            st.success(f"Tahun paling parah untuk {negara_pilih}: **{max_tahun_negara}** ({max_val_negara:,} orang terdampak)")

        # --- KESIMPULAN & NARASI OTOMATIS ---
        st.header('Kesimpulan & Insight Dampak Bencana dan Iklim di Kawasan Pasifik')
        st.markdown('''
        <div style='background-color:#e3f2fd; padding:18px; border-radius:8px; margin-bottom:20px;'>
        <b style='color:#1976d2;'>Deskripsi & Analisis:</b><br>
        <span style='color:#111; font-size:1.08em; font-weight:500;'>Kawasan Pasifik menghadapi tantangan besar terkait perubahan iklim dan bencana alam. Dari visualisasi di atas, dapat dilihat:</span>
        <ul style='color:#111; font-size:1.08em; font-weight:500;'>
        <li><b style='color:#1976d2;'>Kapasitas listrik terbarukan</b> di beberapa negara meningkat pesat, menandakan upaya transisi energi bersih.</li>
        <li><b style='color:#1976d2;'>Emisi CO₂</b> cenderung menurun di negara-negara dengan peningkatan energi terbarukan, namun tidak semua negara menunjukkan tren yang sama.</li>
        <li><b style='color:#1976d2;'>Jumlah orang terdampak bencana</b> masih sangat tinggi di beberapa negara, terutama di tahun-tahun tertentu yang didominasi bencana besar.</li>
        </ul>
        </div>
        ''', unsafe_allow_html=True)

        # Insight otomatis hubungan
        st.info('''
        **Insight Otomatis:**
        - Negara dengan transisi energi terbarukan yang konsisten cenderung mengalami penurunan emisi CO₂, namun dampak bencana tetap signifikan.
        - Tahun dengan jumlah orang terdampak bencana tertinggi seringkali tidak selalu berhubungan langsung dengan emisi karbon, menandakan faktor lain seperti intensitas bencana alam dan kerentanan sosial.
        - Upaya mitigasi perubahan iklim melalui energi terbarukan penting, namun adaptasi dan perlindungan masyarakat tetap krusial untuk mengurangi dampak bencana.
        ''')

        st.markdown('''
        <div style='background-color:#fffde7; padding:16px; border-radius:8px; margin-bottom:20px;'>
        <b style='color:#f57c00;'>Kesimpulan:</b><br>
        <span style='color:#222;'><i>Transisi energi terbarukan di kawasan Pasifik berpotensi menurunkan emisi karbon, namun belum sepenuhnya menurunkan jumlah orang terdampak bencana. Adaptasi kebijakan, penguatan kapasitas masyarakat, dan kolaborasi regional sangat penting untuk menghadapi tantangan perubahan iklim dan bencana di masa depan.</i></span>
        </div>
        ''', unsafe_allow_html=True)