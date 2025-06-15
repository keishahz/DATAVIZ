import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

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
years = sorted(df['Year'].unique())

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Line Chart", "Bar Chart (Latest Year)", "Heatmap", "Data Table", "Download Data"])

st.title("Blue Pacific 2050: Climate Change & Disasters Data Explorer")
st.markdown("Explore renewable electricity-generating capacity across Pacific Island countries.")

if page == "Line Chart":
    st.header("Line Chart: Capacity Over Time")
    selected_countries = st.multiselect('Select countries', countries, default=countries[:5])
    filtered = df[df['Country'].isin(selected_countries)]
    pivot_df = filtered.pivot_table(index='Year', columns='Country', values='Value')
    fig, ax = plt.subplots(figsize=(12, 7))
    for country in pivot_df.columns:
        ax.plot(pivot_df.index, pivot_df[country], label=country)
    ax.set_xlabel('Year')
    ax.set_ylabel('Watts per capita')
    ax.set_title('Installed Renewable Electricity-Generating Capacity')
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
    fig.tight_layout()
    st.pyplot(fig)

elif page == "Bar Chart (Latest Year)":
    st.header("Bar Chart: Latest Year by Country")
    latest_year = df['Year'].max()
    st.write(f"Showing data for year: {latest_year}")
    latest = df[df['Year'] == latest_year]
    latest = latest.sort_values('Value', ascending=False)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(latest['Country'], latest['Value'], color='skyblue')
    ax.set_xlabel('Watts per capita')
    ax.set_title(f'Renewable Capacity by Country ({latest_year})')
    st.pyplot(fig)

elif page == "Heatmap":
    st.header("Heatmap: Country vs Year")
    heatmap_df = df.pivot_table(index='Country', columns='Year', values='Value')
    fig, ax = plt.subplots(figsize=(16, 8))
    sns.heatmap(heatmap_df, cmap='YlGnBu', ax=ax, cbar_kws={'label': 'Watts per capita'})
    ax.set_title('Renewable Capacity Heatmap')
    st.pyplot(fig)

elif page == "Data Table":
    st.header("Data Table Preview")
    st.dataframe(df)
    st.markdown(f"**Total rows:** {len(df)}")

elif page == "Download Data":
    st.header("Download Data")
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name='blue_pacific_2050_data.csv',
        mime='text/csv',
    )
    st.write("You can use this data for your own analysis!")

st.markdown("---")
st.markdown("Data source: Blue Pacific 2050 - Climate Change And Disasters (Thematic Area 5)")
