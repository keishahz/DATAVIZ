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
<b style='color:#222;'>Created By:</b><br>
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
        st.warning("CO₂ emissions data file not found in the project or Downloads folder.")
except Exception as e:
    st.warning(f"Failed to load or merge CO₂ emissions data: {e}")

# --- HEADER & DESCRIPTION ---
st.markdown("""
<h1 style='color:#fff; text-align:center; font-size:2.8rem; font-weight:700; margin-bottom:0.5em;'>Blue Pacific 2050: Climate Change & Disasters Data Explorer</h1>
<div style='background-color:#e3f2fd; padding:16px; border-radius:8px; margin-bottom:20px;'>
    <b style='color:#1976d2;'>Visualization Description:</b><br>
    <span style='color:#333;'>The chart below shows the development of installed renewable electricity capacity (in watts per capita) in Pacific countries over the years.</span><br>
    <ul>
        <li style='color:#388e3c;'><b>Each line</b> represents a country.</li>
        <li style='color:#f57c00;'>Hover</li> <span style='color:#333;'>over the lines to see detailed values for a specific year.</span>
        <li style='color:#0288d1;'>Use the dropdown</li> <span style='color:#333;'>to select and compare specific countries.</span>
        <li style='color:#7b1fa2;'>Data sourced from <i>Blue Pacific 2050 - Climate Change And Disasters (Thematic Area 5)</i>.</li>
    </ul>
    <span style='color:#333;'>This visualization helps to understand the trend of renewable energy adoption in the Pacific region and compare countries interactively.</span>
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

# --- VISUALIZATION 1: Renewable Capacity Trend ---
st.header("Renewable Electricity Capacity Trend per Country")
st.markdown("This trend shows the clean energy transition efforts in Pacific countries.")
vis1_countries = st.multiselect('Select countries (visualization 1)', countries, default=countries, key='v1-country')
vis1_year_min, vis1_year_max = int(df['Year'].min()), int(df['Year'].max())
vis1_years = st.slider('Select year range (visualization 1)', vis1_year_min, vis1_year_max, (vis1_year_min, vis1_year_max), key='v1-year')
vis1_filtered = df[(df['Country'].isin(vis1_countries)) & (df['Year'] >= vis1_years[0]) & (df['Year'] <= vis1_years[1])]
grouped = vis1_filtered.groupby(['Year', 'Country'], as_index=False)[['Renewable Capacity (W/capita)']].mean()
# More informative tooltip
fig1 = px.line(
    grouped,
    x='Year',
    y='Renewable Capacity (W/capita)',
    color='Country',
    markers=True,
    labels={'Renewable Capacity (W/capita)': 'Watt per capita', 'Year': 'Year'},
    title='Renewable Capacity Trend per Country',
    hover_data={'Country': True, 'Year': True, 'Renewable Capacity (W/capita)': ':.2f'}
)
fig1.update_layout(legend_title_text='Country', hovermode='x unified', transition={'duration': 500, 'easing': 'cubic-in-out'})
# Simple prediction (linear regression)
if len(vis1_countries) == 1 and len(grouped) > 2:
    country = vis1_countries[0]
    data_pred = grouped[grouped['Country'] == country]
    X = data_pred['Year'].values.reshape(-1, 1)
    y = data_pred['Renewable Capacity (W/capita)'].values
    model = LinearRegression().fit(X, y)
    year_pred = np.arange(X.max()+1, X.max()+4).reshape(-1, 1)
    pred = model.predict(year_pred)
    fig1.add_scatter(x=year_pred.flatten(), y=pred, mode='lines+markers', name='Prediction', line=dict(dash='dash', color='orange'))
    st.info(f"{country} capacity prediction for {int(year_pred[0][0])}-{int(year_pred[-1][0])}: {pred[0]:.2f} - {pred[-1]:.2f} W/capita")
st.plotly_chart(fig1, use_container_width=True, key="line1-main")
# Highlight automatic insight
if len(vis1_countries) > 1:
    delta = grouped.groupby('Country')['Renewable Capacity (W/capita)'].apply(lambda x: x.iloc[-1] - x.iloc[0])
    top_country = delta.idxmax()
    st.success(f"Country with the largest increase in renewable capacity: {top_country} (+{delta.max():.2f} W/capita)")

# Automatic insight for renewable capacity trend
desc = ""
if len(vis1_countries) == 1:
    country = vis1_countries[0]
    max_val = vis1_filtered['Renewable Capacity (W/capita)'].max()
    min_val = vis1_filtered['Renewable Capacity (W/capita)'].min()
    if max_val > min_val:
        desc = f"Renewable electricity capacity in {country} increased from {min_val:.2f} to {max_val:.2f} W/capita in the selected period."
    else:
        desc = f"Renewable electricity capacity in {country} was relatively stable in the selected period."
elif len(vis1_countries) > 1:
    highest = vis1_filtered.groupby('Country')[['Renewable Capacity (W/capita)']].max().idxmax()[0]
    desc = f"Country with the highest renewable capacity in this period: {highest}."
else:
    desc = "Please select a country to see the insight."
st.info(f"Insight: {desc}")

# --- VISUALIZATION 2: CO2 Emissions Trend (if data available) ---
if 'df_merged' in locals():
    st.header("CO₂ Emissions Trend per Country")
    st.markdown("This trend shows the change in CO₂ emissions over time. A decrease in emissions can indicate a successful renewable energy transition.")
    vis2_countries = st.multiselect('Select countries (visualization 2)', countries, default=countries, key='v2-country')
    vis2_year_min, vis2_year_max = int(df['Year'].min()), int(df['Year'].max())
    vis2_years = st.slider('Select year range (visualization 2)', vis2_year_min, vis2_year_max, (vis2_year_min, vis2_year_max), key='v2-year')
    filtered_merged = df_merged[(df_merged['Country'].isin(vis2_countries)) & (df_merged['Year'] >= vis2_years[0]) & (df_merged['Year'] <= vis2_years[1])]
    grouped2 = filtered_merged.groupby(['Year', 'Country'], as_index=False)[['CO2 Emissions (Mt CO2e)']].mean()
    fig2 = px.line(
        grouped2,
        x='Year',
        y='CO2 Emissions (Mt CO2e)',
        color='Country',
        markers=True,
        labels={'CO2 Emissions (Mt CO2e)': 'CO₂ Emissions (Mt)', 'Year': 'Year'},
        title='CO₂ Emissions Trend per Country'
    )
    fig2.update_layout(legend_title_text='Country', hovermode='x unified', transition={'duration': 500, 'easing': 'cubic-in-out'})
    st.plotly_chart(fig2, use_container_width=True, key="line2-main")
    # Automatic insight for CO2 emissions trend
    desc2 = ""
    if len(vis2_countries) == 1:
        country = vis2_countries[0]
        max_val = filtered_merged['CO2 Emissions (Mt CO2e)'].max()
        min_val = filtered_merged['CO2 Emissions (Mt CO2e)'].min()
        if max_val > min_val:
            desc2 = f"CO₂ emissions in {country} highest {max_val:.2f} Mt and lowest {min_val:.2f} Mt in the selected period."
        else:
            desc2 = f"CO₂ emissions in {country} were relatively stable in the selected period."
    elif len(vis2_countries) > 1:
        lowest = filtered_merged.groupby('Country')[['CO2 Emissions (Mt CO2e)']].mean().idxmin()[0]
        desc2 = f"Country with the lowest average CO₂ emissions in this period: {lowest}."
    else:
        desc2 = "Please select a country to see the insight."
    st.info(f"Insight: {desc2}")

# --- VISUALIZATION 3: Scatter Plot Renewable Capacity vs CO2 Emissions ---
if 'df_merged' in locals():
    st.header("Correlation of Renewable Capacity & CO₂ Emissions")
    st.markdown("The following scatter plot shows the direct relationship between renewable electricity capacity and CO₂ emissions. Each point represents a country-year.")
    vis3_countries = st.multiselect('Select countries (visualization 3)', countries, default=countries, key='v3-country')
    vis3_year_min, vis3_year_max = int(df['Year'].min()), int(df['Year'].max())
    vis3_years = st.slider('Select year range (visualization 3)', vis3_year_min, vis3_year_max, (vis3_year_min, vis3_year_max), key='v3-year')
    filtered_merged = df_merged[(df_merged['Country'].isin(vis3_countries)) & (df_merged['Year'] >= vis3_years[0]) & (df_merged['Year'] <= vis3_years[1])]
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
If a downward pattern is visible (the higher the renewable capacity, the lower the emissions), it means the clean energy transition is effective in reducing climate change-causing emissions.
""")
else:
    st.warning("CO₂ emissions data not available. Please ensure the CO₂ file is present in the project folder.")

# --- VISUALIZATION 4: Data Table ---
st.header("Data Table: Renewable Capacity per Country & Year")
filtered_table = df.copy()
col1, col2, col3 = st.columns(3)
with col1:
    country_opt = ['(All)'] + sorted(filtered_table['Country'].unique().tolist())
    country_sel = st.selectbox('Filter Country', country_opt, key='table-country')
    if country_sel != '(All)':
        filtered_table = filtered_table[filtered_table['Country'] == country_sel]
with col2:
    year_opt = ['(All)'] + sorted(filtered_table['Year'].unique().tolist())
    year_sel = st.selectbox('Filter Year', year_opt, key='table-year')
    if year_sel != '(All)':
        filtered_table = filtered_table[filtered_table['Year'] == year_sel]
with col3:
    min_val, max_val = float(filtered_table['Renewable Capacity (W/capita)'].min()), float(filtered_table['Renewable Capacity (W/capita)'].max())
    value_range = st.slider('Filter Renewable Capacity (W/capita)', min_val, max_val, (min_val, max_val), key='table-value')
    filtered_table = filtered_table[(filtered_table['Renewable Capacity (W/capita)'] >= value_range[0]) & (filtered_table['Renewable Capacity (W/capita)'] <= value_range[1])]
# Show only one row for each unique Renewable Capacity (W/capita), but keep country and year columns
filtered_table = filtered_table.drop_duplicates(subset=['Renewable Capacity (W/capita)'])
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

# --- VISUALIZATION OF PEOPLE AFFECTED BY DISASTER ---
st.title("Visualization of Number of People Affected by Disaster per Country")

# Read data
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
        st.error('Value (Value/OBS_VALUE/Observation value) or year (Year/TIME_PERIOD/Time) column not found in the dataset.')
    else:
        disaster_indicator = 'Number of people affected by disaster'
        df_disaster = df_disaster[df_disaster['Indicator'] == disaster_indicator]
        if df_disaster.empty:
            st.warning('No data on people affected by disaster in this dataset.')
        else:
            st.subheader('Chart of Number of People Affected by Disaster per Country (Total All Years)')
            total_per_country = df_disaster.groupby('Country')[value_col].sum().sort_values(ascending=False).reset_index()
            fig = px.bar(
                total_per_country,
                x='Country',
                y=value_col,
                color='Country',
                labels={value_col: 'Total People Affected', 'Country': 'Country'},
                title='Total People Affected by Disaster per Country (All Years Accumulated)',
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
            - Country with the highest number of people affected by disaster: **{max_country}** ({max_value:,} people)
            - Country with the lowest number affected: **{min_country}** ({min_value:,} people)
            - Worst year (most affected): **{max_year}** ({max_year_value:,} people across the region)
            - Total people affected by disaster: **{total_affected:,}**
            - Average per entry: **{mean_affected:,}**, Median: **{int(df_disaster[value_col].median()):,}**
            """)
            st.subheader('Chart of Number of People Affected by Disaster per Country per Year')
            selected_country = st.selectbox('Select Country', sorted(df_disaster['Country'].unique()))
            df_country = df_disaster[df_disaster['Country'] == selected_country]
            fig2 = px.line(
                df_country,
                x=year_col,
                y=value_col,
                markers=True,
                labels={year_col: 'Year', value_col: 'Number of People Affected'},
                title=f'Number of People Affected by Disaster in {selected_country} per Year',
                hover_data={year_col: True, value_col: ':,'}
            )
            st.plotly_chart(fig2, use_container_width=True)
            if not df_country.empty:
                max_year_country = df_country.loc[df_country[value_col].idxmax(), year_col]
                max_val_country = int(df_country[value_col].max())
                st.success(f"Worst year for {selected_country}: **{max_year_country}** ({max_val_country:,} people affected)")
            # Automatic insight for people affected by disaster
            if len(df_country) > 0:
                total = int(df_country[value_col].sum())
                worst_year = df_country.loc[df_country[value_col].idxmax(), year_col]
                st.info(f"Insight: Total people affected in {selected_country} in the selected period: {total:,}. Worst year: {worst_year}.")

    # =====================
    # COMPARISON OF CARBON EMISSIONS VS PEOPLE AFFECTED BY DISASTER (PER COUNTRY & YEAR) WITH ANIMATION
    # =====================
    st.header("Comparison of Carbon Emissions vs Number of People Affected by Disaster")

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
            # Default animation countries: French Polynesia & Marshall Islands
            default_countries = [n for n in ['French Polynesia', 'Marshall Islands'] if n in df_impact_emisi['Country'].unique()]
            animation_countries = st.multiselect('Select Countries for Animation', sorted(df_impact_emisi['Country'].unique()), default=default_countries, key='animasi-impact-country')
            df_animation = df_impact_emisi[df_impact_emisi['Country'].isin(animation_countries)]
            import plotly.graph_objects as go
            fig = go.Figure()
            for country in animation_countries:
                df_c = df_animation[df_animation['Country'] == country]
                fig.add_trace(go.Scatter(
                    x=df_c['Year'],
                    y=df_c[bencana_value_col],
                    mode='lines+markers',
                    name=f'People Affected - {country}',
                    yaxis='y1',
                    line=dict(width=2),
                    marker=dict(symbol='circle')
                ))
                fig.add_trace(go.Scatter(
                    x=df_c['Year'],
                    y=df_c['CO2 Emissions (Mt CO2e)'],
                    mode='lines+markers',
                    name=f'CO₂ Emissions - {country}',
                    yaxis='y2',
                    line=dict(dash='dot', width=2),
                    marker=dict(symbol='square')
                ))
            fig.update_layout(
                title='Animation: Comparison of CO₂ Emissions vs People Affected by Disaster per Country',
                xaxis=dict(title='Year'),
                yaxis=dict(title='People Affected', showgrid=False, color='royalblue'),
                yaxis2=dict(title='CO₂ Emissions (Mt)', overlaying='y', side='right', color='firebrick'),
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
            # Create frame per year
            years = sorted(df_animation['Year'].unique())
            frames = []
            for year in years:
                data = []
                for country in animation_countries:
                    df_c = df_animation[(df_animation['Country'] == country) & (df_animation['Year'] <= year)]
                    data.append(go.Scatter(
                        x=df_c['Year'],
                        y=df_c[bencana_value_col],
                        mode='lines+markers',
                        name=f'People Affected - {country}',
                        yaxis='y1',
                        line=dict(width=2),
                        marker=dict(symbol='circle')
                    ))
                    data.append(go.Scatter(
                        x=df_c['Year'],
                        y=df_c['CO2 Emissions (Mt CO2e)'],
                        mode='lines+markers',
                        name=f'CO₂ Emissions - {country}',
                        yaxis='y2',
                        line=dict(dash='dot', width=2),
                        marker=dict(symbol='square')
                    ))
                frames.append(go.Frame(data=data, name=str(year)))
            fig.frames = frames
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("""
Use the Play/Pause button at the top right of the chart to see the animation of changes in CO₂ emissions and people affected by disaster year by year.
""")
            # Automatic explanation from animation chart result
            if not df_animation.empty:
                last_year = int(df_animation['Year'].max())
                insight_countries = []
                for country in animation_countries:
                    df_c = df_animation[df_animation['Country'] == country]
                    if not df_c.empty:
                        people_last = int(df_c[df_c['Year'] == last_year][bencana_value_col].values[-1]) if last_year in df_c['Year'].values else int(df_c[bencana_value_col].iloc[-1])
                        emissions_last = float(df_c[df_c['Year'] == last_year]['CO2 Emissions (Mt CO2e)'].values[-1]) if last_year in df_c['Year'].values else float(df_c['CO2 Emissions (Mt CO2e)'].iloc[-1])
                        insight_countries.append(f"<b>{country}</b>: People affected {people_last:,}, CO₂ Emissions {emissions_last:.2f} Mt in the last year.")
                st.markdown(f"""
<div style='background-color:#e3f2fd; padding:12px; border-radius:8px; margin-bottom:16px;'>
<b style='color:#222;'>Chart Explanation:</b><br>
<span style='color:#222;'>
{'<br>'.join(insight_countries)}<br>
This animation chart shows that the trend of people affected by disaster does not always align with the country's carbon emissions. Pacific countries can experience major disasters even with very low emissions, highlighting the issue of global climate injustice.
</span>
</div>
""", unsafe_allow_html=True)
        else:
            st.info('CO₂ emissions data not available or failed to process.')
    else:
        st.info('Disaster data not available or failed to process.')
except Exception as e:
    st.warning(f"Failed to load or process people affected by disaster data: {e}")

# --- CONCLUSION ---
st.header('Conclusion & Insights on Disaster and Climate Impact in the Pacific Region')

# Automated conclusion based on visualization results
summary = []
if 'grouped' in locals() and not grouped.empty:
    highest_country = grouped.groupby('Country')['Renewable Capacity (W/capita)'].max().idxmax()
    summary.append(f"Country with the highest renewable electricity capacity: <b>{highest_country}</b>.")
if 'grouped2' in locals() and not grouped2.empty:
    lowest_emission_country = grouped2.groupby('Country')['CO2 Emissions (Mt CO2e)'].mean().idxmin()
    summary.append(f"Country with the lowest average CO₂ emissions: <b>{lowest_emission_country}</b>.")
if 'total_per_country' in locals() and not total_per_country.empty:
    most_affected_country = total_per_country.loc[total_per_country[value_col].idxmax(), 'Country']
    summary.append(f"Country with the highest number of people affected by disaster: <b>{most_affected_country}</b>.")

st.markdown(f"""
<div style='background-color:#e3f2fd; padding:18px; border-radius:8px; margin-bottom:20px;'>
<b style='color:#1976d2;'>Description & Automated Analysis:</b><br>
<span style='color:#111; font-size:1.08em; font-weight:500;'>
{'<br>'.join(summary) if summary else 'Data not available for automated analysis.'}
</span>
</div>
""", unsafe_allow_html=True)

st.info('''
Insights:
- Countries with consistent renewable energy transition tend to experience a decrease in CO₂ emissions, but disaster impacts remain significant.
- Years with the highest number of people affected by disaster are often not directly related to carbon emissions, indicating other factors such as disaster intensity and social vulnerability.
- Efforts to mitigate climate change through renewable energy are important, but adaptation and community protection remain crucial to reduce disaster impacts.
''')

st.markdown('''
<div style='background-color:#fffde7; padding:16px; border-radius:8px; margin-bottom:20px;'>
<b style='color:#f57c00;'>Conclusion:</b><br>
<span style='color:#222;'><i>The transition to renewable energy in the Pacific region has the potential to reduce carbon emissions, but has not yet fully reduced the number of people affected by disasters. Policy adaptation, community capacity building, and regional collaboration are essential to face the challenges of climate change and disasters in the future.</i></span>
</div>
''', unsafe_allow_html=True)
