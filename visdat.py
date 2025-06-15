import streamlit as st
import pandas as pd
import plotly.express as px

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
        'OBS_VALUE': 'Value'
    })
    df = df.dropna(subset=['Year', 'Value'])
    df['Year'] = df['Year'].astype(int)
    df['Value'] = df['Value'].astype(float)
    return df

df = load_data()
countries = sorted(df['Country'].unique())

st.title("Blue Pacific 2050: Climate Change & Disasters Data Explorer")
st.markdown("Visualisasi interaktif seperti <a href='https://holtzy.github.io/pacific-challenge/' target='_blank'>Pacific Challenge</a>.", unsafe_allow_html=True)

st.markdown("""
<div style='background-color:#e3f2fd; padding:16px; border-radius:8px; margin-bottom:20px;'>
    <b>Deskripsi Visualisasi:</b><br>
    Grafik di bawah ini menampilkan perkembangan kapasitas terpasang listrik terbarukan (dalam watt per kapita) di negara-negara Pasifik dari tahun ke tahun.<br>
    <ul>
        <li><b>Setiap garis</b> mewakili satu negara.</li>
        <li><b>Hover</b> pada garis untuk melihat detail nilai pada tahun tertentu.</li>
        <li><b>Pilih negara</b> di sidebar untuk membandingkan negara tertentu.</li>
        <li>Data diambil dari <i>Blue Pacific 2050 - Climate Change And Disasters (Thematic Area 5)</i>.</li>
    </ul>
    Visualisasi ini membantu memahami tren adopsi energi terbarukan di kawasan Pasifik dan membandingkan antar negara secara interaktif.
</div>
""", unsafe_allow_html=True)

st.sidebar.header("Filter Negara")
selected_countries = st.sidebar.multiselect('Pilih negara', countries, default=countries[:5])

filtered = df[df['Country'].isin(selected_countries)]

st.header("Line Chart Interaktif: Renewable Capacity per Negara")
fig = px.line(
    filtered,
    x='Year',
    y='Value',
    color='Country',
    markers=True,
    labels={'Value': 'Watts per capita', 'Year': 'Tahun'},
    title='Installed Renewable Electricity-Generating Capacity (Interactive)'
)
fig.update_layout(legend_title_text='Negara', hovermode='x unified')
st.plotly_chart(fig, use_container_width=True)

# Tambahan fitur visualisasi dan insight
st.markdown("## 📊 Visualisasi Lanjutan & Insight")

# 1. Bar chart perbandingan antar negara pada tahun tertentu
st.subheader("Perbandingan Kapasitas Antar Negara (Bar Chart)")
year_bar = st.slider('Pilih tahun untuk perbandingan antar negara', int(df['Year'].min()), int(df['Year'].max()), int(df['Year'].max()))
df_bar = df[df['Year'] == year_bar].sort_values('Value', ascending=False)
fig_bar = px.bar(df_bar, x='Country', y='Value', color='Country', labels={'Value': 'Watts per capita', 'Country': 'Negara'}, title=f'Kapasitas Terpasang per Negara ({year_bar})')
st.plotly_chart(fig_bar, use_container_width=True)

# 2. Growth rate line chart
st.subheader("Tren Pertumbuhan Kapasitas (Growth Rate)")
growth_df = df.copy()
growth_df['Growth'] = growth_df.groupby('Country')['Value'].pct_change() * 100
growth_filtered = growth_df[growth_df['Country'].isin(selected_countries)]
fig_growth = px.line(growth_filtered, x='Year', y='Growth', color='Country', markers=True, labels={'Growth': 'Growth Rate (%)', 'Year': 'Tahun'}, title='Persentase Pertumbuhan Kapasitas per Tahun')
st.plotly_chart(fig_growth, use_container_width=True)

# 3. Highlight negara dengan pertumbuhan tercepat/terlambat
growth_summary = growth_df.groupby('Country')['Growth'].mean().reset_index()
highest = growth_summary.loc[growth_summary['Growth'].idxmax()]
lowest = growth_summary.loc[growth_summary['Growth'].idxmin()]
st.info(f"Negara dengan rata-rata pertumbuhan tercepat: **{highest['Country']}** ({highest['Growth']:.2f}%)")
st.warning(f"Negara dengan rata-rata pertumbuhan terlambat: **{lowest['Country']}** ({lowest['Growth']:.2f}%)")

# 4. Boxplot distribusi kapasitas per tahun
st.subheader("Distribusi Kapasitas per Tahun (Boxplot)")
fig_box = px.box(df, x='Year', y='Value', points='all', labels={'Value': 'Watts per capita', 'Year': 'Tahun'}, title='Sebaran Kapasitas Terpasang per Tahun')
st.plotly_chart(fig_box, use_container_width=True)

# 5. Statistik ringkas
desc = df['Value'].describe()
st.markdown(f"""
**Statistik Ringkas (Seluruh Data):**
- Rata-rata: `{desc['mean']:.2f}`
- Median: `{desc['50%']:.2f}`
- Maksimum: `{desc['max']:.2f}`
- Minimum: `{desc['min']:.2f}`
""")

# 6. Data Table
st.subheader("Data Tabel")
st.dataframe(df)

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
