import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

st.set_page_config(page_title="Blue Pacific 2050: Climate Change & Disasters Data Explorer", layout="wide")

st.markdown('''
<div style="background-color:#e3f2fd; padding:10px 18px; border-radius:8px; margin-bottom:10px;">
<b style='color:#222;'>Dibuat Oleh:</b><br>
<b style='color:#222;'>- Dyan Maharani Az Zahra (103052300081)<br>
<b style='color:#222;'>- Felicia Cyntia Febriani (103052300086)<br>
<b style='color:#222;'>- Keisha Hernantya Zahra (103052330063)
</div>
''', unsafe_allow_html=True)

# --- LOAD DATA ---
@st.cache_data
def load_data():
    file_path = 'Blue Pacific 2050_ Climate Change And Disasters (Thematic Area 5) data.csv'
    df = pd.read_csv(file_path)
    cols = ['Pacific Island Countries and territories', 'TIME_PERIOD', 'OBS_VALUE', 'Indicator'] if 'Indicator' in df.columns else ['Pacific Island Countries and territories', 'TIME_PERIOD', 'OBS_VALUE']
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

# --- LOAD CO2 DATA ---
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
        df_merged = pd.merge(df, df_co2_long, on=['Country', 'Year'], how='left')
    else:
        st.warning("File data emisi CO₂ tidak ditemukan di folder project atau Downloads.")
except Exception as e:
    st.warning(f"Gagal memuat atau menggabungkan data emisi CO₂: {e}")

# --- HEADER & DESKRIPSI ---
st.markdown("""
<h1 style='color:#fff; text-align:center; font-size:2.8rem; font-weight:700; margin-bottom:0.5em;'>Blue Pacific 2050: Climate Change & Disasters Data Explorer</h1>
<div style='background-color:#e3f2fd; padding:16px; border-radius:8px; margin-bottom:20px;'>
    <b style='color:#1976d2;'>Deskripsi Visualisasi:</b><br>
    <span style='color:#333;'>Grafik di bawah ini menampilkan perkembangan kapasitas terpasang listrik terbarukan (dalam watt per kapita) di negara-negara Pasifik dari tahun ke tahun.</span><br>
    <ul>
        <li style='color:#388e3c;'><b>Setiap garis</b> mewakili satu negara.</li>
        <li style='color:#f57c00;'>Arahkan kursor (hover)</li> <span style='color:#333;'>Pada garis untuk melihat detail nilai pada tahun tertentu.</span>
        <li style='color:#0288d1;'>Gunakan dropdown</li> <span style='color:#333;'>Untuk memilih dan membandingkan negara tertentu.</span>
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

# --- VISUALISASI 1: Tren Renewable Capacity ---
st.subheader("Tren Kapasitas Listrik Terbarukan per Negara")
st.markdown("Tren ini menunjukkan upaya transisi energi bersih di negara-negara Pasifik.")
vis1_countries = st.multiselect('Pilih negara (visualisasi 1)', countries, default=countries, key='v1-country')
vis1_year_min, vis1_year_max = int(df['Year'].min()), int(df['Year'].max())
vis1_years = st.slider('Pilih rentang tahun (visualisasi 1)', vis1_year_min, vis1_year_max, (vis1_year_min, vis1_year_max), key='v1-year')
vis1_filtered = df[(df['Country'].isin(vis1_countries)) & (df['Year'] >= vis1_years[0]) & (df['Year'] <= vis1_years[1])]
grouped = vis1_filtered.groupby(['Year', 'Country'], as_index=False)[['Renewable Capacity (W/capita)']].mean()
# Tooltip lebih informatif
fig1 = px.line(
    grouped,
    x='Year',
    y='Renewable Capacity (W/capita)',
    color='Country',
    markers=True,
    labels={'Renewable Capacity (W/capita)': 'Watt per kapita', 'Year': 'Tahun'},
    title='Tren Kapasitas Terbarukan per Negara',
    hover_data={'Country': True, 'Year': True, 'Renewable Capacity (W/capita)': ':.2f'}
)
fig1.update_layout(legend_title_text='Negara', hovermode='x unified', transition={'duration': 500, 'easing': 'cubic-in-out'})
# Prediksi sederhana (linear regression)
if len(vis1_countries) == 1 and len(grouped) > 2:
    negara = vis1_countries[0]
    data_pred = grouped[grouped['Country'] == negara]
    X = data_pred['Year'].values.reshape(-1, 1)
    y = data_pred['Renewable Capacity (W/capita)'].values
    model = LinearRegression().fit(X, y)
    tahun_pred = np.arange(X.max()+1, X.max()+4).reshape(-1, 1)
    pred = model.predict(tahun_pred)
    fig1.add_scatter(x=tahun_pred.flatten(), y=pred, mode='lines+markers', name='Prediksi', line=dict(dash='dash', color='orange'))
    st.info(f"Prediksi kapasitas {negara} tahun {int(tahun_pred[0][0])}-{int(tahun_pred[-1][0])}: {pred[0]:.2f} - {pred[-1]:.2f} W/capita")
st.plotly_chart(fig1, use_container_width=True, key="line1-main")
# Highlight insight otomatis
if len(vis1_countries) > 1:
    delta = grouped.groupby('Country')['Renewable Capacity (W/capita)'].apply(lambda x: x.iloc[-1] - x.iloc[0])
    negara_terbesar = delta.idxmax()
    st.success(f"Negara dengan peningkatan kapasitas terbarukan terbesar: {negara_terbesar} (+{delta.max():.2f} W/capita)")

# Insight otomatis tren kapasitas terbarukan
desc = ""
if len(vis1_countries) == 1:
    negara = vis1_countries[0]
    max_val = vis1_filtered['Renewable Capacity (W/capita)'].max()
    min_val = vis1_filtered['Renewable Capacity (W/capita)'].min()
    if max_val > min_val:
        desc = f"Kapasitas listrik terbarukan di {negara} meningkat dari {min_val:.2f} ke {max_val:.2f} W/capita pada periode yang dipilih."
    else:
        desc = f"Kapasitas listrik terbarukan di {negara} relatif stabil pada periode yang dipilih."
elif len(vis1_countries) > 1:
    tertinggi = vis1_filtered.groupby('Country')[['Renewable Capacity (W/capita)']].max().idxmax()[0]
    desc = f"Negara dengan kapasitas terbarukan tertinggi pada periode ini: {tertinggi}."
else:
    desc = "Silakan pilih negara untuk melihat insight."
st.info(f"Insight: {desc}")

# --- VISUALISASI 2: Tren Emisi CO2 (jika data tersedia) ---
if 'df_merged' in locals():
    st.subheader("Tren Emisi CO₂ per Negara")
    st.markdown("Tren ini memperlihatkan perubahan emisi CO₂ seiring waktu. Penurunan emisi dapat menjadi indikasi keberhasilan transisi energi terbarukan.")
    vis2_countries = st.multiselect('Pilih negara (visualisasi 2)', countries, default=countries, key='v2-country')
    vis2_year_min, vis2_year_max = int(df['Year'].min()), int(df['Year'].max())
    vis2_years = st.slider('Pilih rentang tahun (visualisasi 2)', vis2_year_min, vis2_year_max, (vis2_year_min, vis2_year_max), key='v2-year')
    filtered_merged = df_merged[(df_merged['Country'].isin(vis2_countries)) & (df_merged['Year'] >= vis2_years[0]) & (df_merged['Year'] <= vis2_years[1])]
    grouped2 = filtered_merged.groupby(['Year', 'Country'], as_index=False)[['CO2 Emissions (Mt CO2e)']].mean()
    fig2 = px.line(
        grouped2,
        x='Year',
        y='CO2 Emissions (Mt CO2e)',
        color='Country',
        markers=True,
        labels={'CO2 Emissions (Mt CO2e)': 'Emisi CO₂ (Mt)', 'Year': 'Tahun'},
        title='Tren Emisi CO₂ per Negara'
    )
    fig2.update_layout(legend_title_text='Negara', hovermode='x unified', transition={'duration': 500, 'easing': 'cubic-in-out'})
    st.plotly_chart(fig2, use_container_width=True, key="line2-main")
    # Insight otomatis tren emisi CO2
    desc2 = ""
    if len(vis2_countries) == 1:
        negara = vis2_countries[0]
        max_val = filtered_merged['CO2 Emissions (Mt CO2e)'].max()
        min_val = filtered_merged['CO2 Emissions (Mt CO2e)'].min()
        if max_val > min_val:
            desc2 = f"Emisi CO₂ di {negara} tertinggi {max_val:.2f} Mt dan terendah {min_val:.2f} Mt pada periode yang dipilih."
        else:
            desc2 = f"Emisi CO₂ di {negara} relatif stabil pada periode yang dipilih."
    elif len(vis2_countries) > 1:
        terendah = filtered_merged.groupby('Country')[['CO2 Emissions (Mt CO2e)']].mean().idxmin()[0]
        desc2 = f"Negara dengan rata-rata emisi CO₂ terendah pada periode ini: {terendah}."
    else:
        desc2 = "Silakan pilih negara untuk melihat insight."
    st.info(f"Insight: {desc2}")

# --- VISUALISASI 3: Scatter Plot Hubungan Renewable Capacity vs Emisi CO2 ---
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
    fig3_scatter.update_layout(transition={'duration': 500, 'easing': 'cubic-in-out'})
    st.plotly_chart(fig3_scatter, use_container_width=True, key="scatter_co2-main")
    st.markdown("""
Jika terlihat pola menurun (semakin tinggi kapasitas terbarukan, emisi makin rendah), berarti transisi energi bersih efektif menurunkan emisi penyebab climate change.
""")
else:
    st.warning("Data emisi CO₂ tidak tersedia. Silakan pastikan file CO₂ sudah ada di folder project.")

# --- VISUALISASI 4: Data Table ---
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
try:
    df_disaster = pd.read_csv(r'Blue Pacific 2050_ Climate Change And Disasters (Thematic Area 5) data.csv')
    df_disaster.columns = df_disaster.columns.str.strip()
    if 'Pacific Island Countries and territories' in df_disaster.columns:
        df_disaster = df_disaster.rename(columns={'Pacific Island Countries and territories': 'Country'})
    value_col = None
    year_col = None
    for col in ['Value', 'OBS_VALUE', 'Observation value']:
        if col in df_disaster.columns:
            value_col = col
            break
    for col in ['Year', 'TIME_PERIOD', 'Time']:
        if col in df_disaster.columns:
            year_col = col
            break
    if value_col is None or year_col is None:
        st.error('Kolom nilai (Value/OBS_VALUE/Observation value) atau tahun (Year/TIME_PERIOD/Time) tidak ditemukan di dataset.')
    else:
        disaster_indicator = 'Number of people affected by disaster'
        df_disaster = df_disaster[df_disaster['Indicator'] == disaster_indicator]
        if df_disaster.empty:
            st.warning('Tidak ada data orang terdampak bencana di dataset ini.')
        else:
            st.subheader('Grafik Jumlah Orang Terdampak Bencana per Negara (Total Seluruh Tahun)')
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
            max_country = total_per_country.loc[total_per_country[value_col].idxmax(), 'Country']
            max_value = int(total_per_country[value_col].max())
            min_country = total_per_country.loc[total_per_country[value_col].idxmin(), 'Country']
            min_value = int(total_per_country[value_col].min())
            total_affected = int(df_disaster[value_col].sum())
            mean_affected = int(df_disaster[value_col].mean())
            total_per_year = df_disaster.groupby(year_col)[value_col].sum()
            max_year = int(total_per_year.idxmax())
            max_year_value = int(total_per_year.max())
            st.info(f"""
            **Insight:**
            - Negara dengan jumlah orang terdampak bencana terbanyak: **{max_country}** ({max_value:,} orang)
            - Negara dengan jumlah terdampak paling sedikit: **{min_country}** ({min_value:,} orang)
            - Tahun paling parah (jumlah terdampak terbanyak): **{max_year}** ({max_year_value:,} orang di seluruh kawasan)
            - Total seluruh orang terdampak bencana: **{total_affected:,}**
            - Rata-rata per entri: **{mean_affected:,}**, Median: **{int(df_disaster[value_col].median()):,}**
            """)
            st.subheader('Grafik Jumlah Orang Terdampak Bencana per Negara per Tahun')
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
            if not df_negara.empty:
                max_tahun_negara = df_negara.loc[df_negara[value_col].idxmax(), year_col]
                max_val_negara = int(df_negara[value_col].max())
                st.success(f"Tahun paling parah untuk {negara_pilih}: **{max_tahun_negara}** ({max_val_negara:,} orang terdampak)")
            # Insight otomatis orang terdampak bencana
            if len(df_negara) > 0:
                total = int(df_negara[value_col].sum())
                tahun_terbanyak = df_negara.loc[df_negara[value_col].idxmax(), year_col]
                st.info(f"Insight: Total orang terdampak di {negara_pilih} pada periode yang dipilih: {total:,}. Tahun paling parah: {tahun_terbanyak}.")

    # =====================
    # PERBANDINGAN EMISI KARBON VS ORANG TERDAMPAK BENCANA (PER NEGARA & TAHUN) DENGAN ANIMASI
    # =====================
    st.header("Perbandingan Emisi Karbon vs Jumlah Orang Terdampak Bencana")

    if 'df_bencana' not in globals():
        df_bencana = pd.read_csv('Blue Pacific 2050_ Climate Change And Disasters (Thematic Area 5) data.csv')
        df_bencana.columns = df_bencana.columns.str.strip()
        if 'Pacific Island Countries and territories' in df_bencana.columns:
            df_bencana = df_bencana.rename(columns={'Pacific Island Countries and territories': 'Country'})

    bencana_value_col = None
    bencana_year_col = None
    if 'Observation value' in df_bencana.columns and df_bencana['Observation value'].notna().any():
        bencana_value_col = 'Observation value'
    elif 'OBS_VALUE' in df_bencana.columns and df_bencana['OBS_VALUE'].notna().any():
        bencana_value_col = 'OBS_VALUE'
    for col in ['Year', 'TIME_PERIOD', 'Time']:
        if col in df_bencana.columns:
            bencana_year_col = col
            break

    if bencana_value_col and bencana_year_col and 'Indicator' in df_bencana.columns:
        df_disaster = df_bencana[df_bencana['Indicator'] == 'Number of people affected by disaster']
        if 'df_co2_long' in locals():
            df_disaster['Country'] = df_disaster['Country'].str.strip()
            df_co2_long['Country'] = df_co2_long['Country'].str.strip()
            df_disaster['Year'] = pd.to_numeric(df_disaster[bencana_year_col], errors='coerce')
            df_impact_emisi = pd.merge(
                df_disaster,
                df_co2_long,
                on=['Country', 'Year'],
                how='inner'
            )
            # Default negara animasi: French Polynesia & Marshall Islands
            default_negara = [n for n in ['French Polynesia', 'Marshall Islands'] if n in df_impact_emisi['Country'].unique()]
            negara_animasi = st.multiselect('Pilih Negara untuk Animasi', sorted(df_impact_emisi['Country'].unique()), default=default_negara, key='animasi-impact-country')
            df_animasi = df_impact_emisi[df_impact_emisi['Country'].isin(negara_animasi)]
            import plotly.graph_objects as go
            fig = go.Figure()
            for country in negara_animasi:
                df_c = df_animasi[df_animasi['Country'] == country]
                fig.add_trace(go.Scatter(
                    x=df_c['Year'],
                    y=df_c[bencana_value_col],
                    mode='lines+markers',
                    name=f'Orang Terdampak - {country}',
                    yaxis='y1',
                    line=dict(width=2),
                    marker=dict(symbol='circle')
                ))
                fig.add_trace(go.Scatter(
                    x=df_c['Year'],
                    y=df_c['CO2 Emissions (Mt CO2e)'],
                    mode='lines+markers',
                    name=f'Emisi CO₂ - {country}',
                    yaxis='y2',
                    line=dict(dash='dot', width=2),
                    marker=dict(symbol='square')
                ))
            fig.update_layout(
                title='Animasi Perbandingan Emisi CO₂ vs Orang Terdampak Bencana per Negara',
                xaxis=dict(title='Tahun'),
                yaxis=dict(title='Orang Terdampak', showgrid=False, color='royalblue'),
                yaxis2=dict(title='Emisi CO₂ (Mt)', overlaying='y', side='right', color='firebrick'),
                legend=dict(x=0.01, y=0.99, bgcolor='rgba(255,255,255,0.7)'),
                hovermode='x unified',
                margin=dict(l=40, r=40, t=60, b=40),
                updatemenus=[
                    dict(
                        type='buttons',
                        showactive=False,
                        y=1.15,
                        x=1.05,
                        xanchor='right',
                        yanchor='top',
                        buttons=[
                            dict(label='Play', method='animate', args=[None, {'frame': {'duration': 700, 'redraw': True}, 'fromcurrent': True}]),
                            dict(label='Pause', method='animate', args=[[None], {'frame': {'duration': 0, 'redraw': False}, 'mode': 'immediate', 'transition': {'duration': 0}}])
                        ]
                    )
                ]
            )
            # Buat frame per tahun
            years = sorted(df_animasi['Year'].unique())
            frames = []
            for year in years:
                data = []
                for country in negara_animasi:
                    df_c = df_animasi[(df_animasi['Country'] == country) & (df_animasi['Year'] <= year)]
                    data.append(go.Scatter(
                        x=df_c['Year'],
                        y=df_c[bencana_value_col],
                        mode='lines+markers',
                        name=f'Orang Terdampak - {country}',
                        yaxis='y1',
                        line=dict(width=2),
                        marker=dict(symbol='circle')
                    ))
                    data.append(go.Scatter(
                        x=df_c['Year'],
                        y=df_c['CO2 Emissions (Mt CO2e)'],
                        mode='lines+markers',
                        name=f'Emisi CO₂ - {country}',
                        yaxis='y2',
                        line=dict(dash='dot', width=2),
                        marker=dict(symbol='square')
                    ))
                frames.append(go.Frame(data=data, name=str(year)))
            fig.frames = frames
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("""
Gunakan tombol Play/Pause di kanan atas grafik untuk melihat animasi perubahan emisi CO₂ dan orang terdampak bencana dari tahun ke tahun.
""")
            # Penjelasan otomatis dari hasil grafik animasi
            if not df_animasi.empty:
                tahun_terakhir = int(df_animasi['Year'].max())
                insight_negara = []
                for country in negara_animasi:
                    df_c = df_animasi[df_animasi['Country'] == country]
                    if not df_c.empty:
                        orang_akhir = int(df_c[df_c['Year'] == tahun_terakhir][bencana_value_col].values[-1]) if tahun_terakhir in df_c['Year'].values else int(df_c[bencana_value_col].iloc[-1])
                        emisi_akhir = float(df_c[df_c['Year'] == tahun_terakhir]['CO2 Emissions (Mt CO2e)'].values[-1]) if tahun_terakhir in df_c['Year'].values else float(df_c['CO2 Emissions (Mt CO2e)'].iloc[-1])
                        insight_negara.append(f"<b>{country}</b>: Orang terdampak {orang_akhir:,}, Emisi CO₂ {emisi_akhir:.2f} Mt pada tahun terakhir.")
                st.markdown(f"""
<div style='background-color:#e3f2fd; padding:12px; border-radius:8px; margin-bottom:16px;'>
<b style='color:#222;'>Penjelasan Grafik:</b><br>
<span style='color:#222;'>
{'<br>'.join(insight_negara)}<br>
Grafik animasi ini memperlihatkan bahwa tren jumlah orang terdampak bencana tidak selalu sejalan dengan emisi karbon negara tersebut. Negara Pasifik bisa mengalami bencana besar meski emisinya sangat kecil, menegaskan isu ketidakadilan iklim global.
</span>
</div>
""", unsafe_allow_html=True)
        else:
            st.info('Data emisi CO₂ tidak tersedia atau gagal diproses.')
    else:
        st.info('Data bencana tidak tersedia atau gagal\u00a0diproses.')
except Exception as e:
    st.warning(f"Gagal memuat atau memproses data orang terdampak bencana: {e}")

# --- KESIMPULAN ---
st.header('Kesimpulan & Insight Dampak Bencana dan Iklim di Kawasan Pasifik')

# Otomatisasi kesimpulan berdasarkan hasil visualisasi
summary = []
if 'grouped' in locals() and not grouped.empty:
    negara_tertinggi = grouped.groupby('Country')['Renewable Capacity (W/capita)'].max().idxmax()
    summary.append(f"Negara dengan kapasitas listrik terbarukan tertinggi: <b>{negara_tertinggi}</b>.")
if 'grouped2' in locals() and not grouped2.empty:
    negara_terendah_emisi = grouped2.groupby('Country')['CO2 Emissions (Mt CO2e)'].mean().idxmin()
    summary.append(f"Negara dengan rata-rata emisi CO₂ terendah: <b>{negara_terendah_emisi}</b>.")
if 'total_per_country' in locals() and not total_per_country.empty:
    negara_terdampak_terbanyak = total_per_country.loc[total_per_country[value_col].idxmax(), 'Country']
    summary.append(f"Negara dengan jumlah orang terdampak bencana terbanyak: <b>{negara_terdampak_terbanyak}</b>.")

st.markdown(f"""
<div style='background-color:#e3f2fd; padding:18px; border-radius:8px; margin-bottom:20px;'>
<b style='color:#1976d2;'>Deskripsi & Analisis Otomatis:</b><br>
<span style='color:#111; font-size:1.08em; font-weight:500;'>
{'<br>'.join(summary) if summary else 'Data tidak tersedia untuk analisis otomatis.'}
</span>
</div>
""", unsafe_allow_html=True)

st.info('''
Insight:
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
