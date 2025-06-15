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

st.markdown("---")
st.markdown("Data source: Blue Pacific 2050 - Climate Change And Disasters (Thematic Area 5)")
