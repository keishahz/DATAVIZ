import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

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

st.sidebar.header("Filter Negara")
selected_countries = st.sidebar.multiselect('Pilih negara', countries, default=countries)

filtered = df[df['Country'].isin(selected_countries)]

st.header("Line Chart: Renewable Capacity per Negara")
country_dropdown = st.selectbox('Pilih satu negara untuk ditampilkan pada line chart', countries)
filtered_dropdown = df[df['Country'] == country_dropdown]
# Gabungkan data per tahun (ambil rata-rata jika ada duplikat)
filtered_dropdown_grouped = filtered_dropdown.groupby('Year', as_index=False)['Renewable Capacity (W/capita)'].mean()
fig = px.line(
    filtered_dropdown_grouped,
    x='Year',
    y='Renewable Capacity (W/capita)',
    markers=True,
    labels={'Renewable Capacity (W/capita)': 'Watts per capita', 'Year': 'Tahun'},
    title=f'Installed Renewable Electricity-Generating Capacity: {country_dropdown}'
)
fig.update_layout(showlegend=False, hovermode='x unified')
st.plotly_chart(fig, use_container_width=True)

# Tambahan fitur visualisasi dan insight
st.markdown("## 📊 Visualisasi Lanjutan & Insight")

# 1. Bar chart perbandingan antar negara pada tahun tertentu
st.subheader("Perbandingan Kapasitas Antar Negara (Bar Chart)")
year_bar = st.slider('Pilih tahun untuk perbandingan antar negara', int(df['Year'].min()), int(df['Year'].max()), int(df['Year'].max()))
df_bar = df[df['Year'] == year_bar].sort_values('Renewable Capacity (W/capita)', ascending=False)
fig_bar = px.bar(df_bar, x='Country', y='Renewable Capacity (W/capita)', color='Country', labels={'Renewable Capacity (W/capita)': 'Watts per capita', 'Country': 'Negara'}, title=f'Kapasitas Terpasang per Negara ({year_bar})')
st.plotly_chart(fig_bar, use_container_width=True)

# 2. Growth rate line chart
st.subheader("Tren Pertumbuhan Kapasitas (Growth Rate)")
growth_df = df.copy()
growth_df['Growth'] = growth_df.groupby('Country')['Renewable Capacity (W/capita)'].pct_change() * 100
growth_filtered = growth_df[growth_df['Country'].isin(selected_countries)]
fig_growth = px.line(growth_filtered, x='Year', y='Growth', color='Country', markers=True, labels={'Growth': 'Growth Rate (%)', 'Year': 'Tahun'}, title='Persentase Pertumbuhan Kapasitas per Tahun')
st.plotly_chart(fig_growth, use_container_width=True)

# 3. Highlight negara dengan pertumbuhan tercepat/terlambat
# Abaikan inf, -inf, dan NaN
valid_growth = growth_df.replace([np.inf, -np.inf], np.nan)
growth_summary = valid_growth.groupby('Country')['Growth'].mean().reset_index()
growth_summary = growth_summary.dropna(subset=['Growth'])
if not growth_summary.empty:
    highest = growth_summary.loc[growth_summary['Growth'].idxmax()]
    lowest = growth_summary.loc[growth_summary['Growth'].idxmin()]
    st.info(f"Negara dengan rata-rata pertumbuhan tercepat: **{highest['Country']}** ({highest['Growth']:.2f}%)")
    st.warning(f"Negara dengan rata-rata pertumbuhan terlambat: **{lowest['Country']}** ({lowest['Growth']:.2f}%)")
else:
    st.info("Tidak ada data pertumbuhan yang valid untuk ditampilkan.")

# 4. Boxplot distribusi kapasitas per tahun
st.subheader("Distribusi Kapasitas per Tahun (Boxplot)")
fig_box = px.box(df, x='Year', y='Renewable Capacity (W/capita)', points='all', labels={'Renewable Capacity (W/capita)': 'Watts per capita', 'Year': 'Tahun'}, title='Sebaran Kapasitas Terpasang per Tahun')
st.plotly_chart(fig_box, use_container_width=True)

# 5. Statistik ringkas
desc = df['Renewable Capacity (W/capita)'].describe()
st.markdown(f"""
**Statistik Ringkas (Seluruh Data):**
- Rata-rata: `{desc['mean']:.2f}`
- Median: `{desc['50%']:.2f}`
- Maksimum: `{desc['max']:.2f}`
- Minimum: `{desc['min']:.2f}`
""")

# 6. Data Table dengan filter per kolom
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

st.markdown("---")
st.markdown("Data source: Blue Pacific 2050 - Climate Change And Disasters (Thematic Area 5)")
