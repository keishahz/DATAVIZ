import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Pacific Islands Renewable Capacity", layout="wide")

st.title("Installed Renewable Electricity-Generating Capacity in Pacific Islands")

# Load the dataset
file_path = 'Blue Pacific 2050_ Climate Change And Disasters (Thematic Area 5) data.csv'
df = pd.read_csv(file_path)

# Select relevant columns and rename for convenience
cols = ['Pacific Island Countries and territories', 'TIME_PERIOD', 'OBS_VALUE']
df = df[cols]
df = df.rename(columns={
    'Pacific Island Countries and territories': 'Country',
    'TIME_PERIOD': 'Year',
    'OBS_VALUE': 'Value'
})

# Drop rows with missing values in Year or Value
plot_df = df.dropna(subset=['Year', 'Value'])

# Convert Year to int and Value to float
plot_df['Year'] = plot_df['Year'].astype(int)
plot_df['Value'] = plot_df['Value'].astype(float)

# Sidebar for country selection
countries = sorted(plot_df['Country'].unique())
selected_countries = st.sidebar.multiselect(
    'Select countries to display', countries, default=countries
)

# Filter data based on selection
filtered_df = plot_df[plot_df['Country'].isin(selected_countries)]

# Pivot the data for plotting
pivot_df = filtered_df.pivot_table(index='Year', columns='Country', values='Value')

# Plot
fig, ax = plt.subplots(figsize=(12, 7))
for country in pivot_df.columns:
    ax.plot(pivot_df.index, pivot_df[country], label=country)
ax.set_xlabel('Year')
ax.set_ylabel('Installed renewable electricity-generating capacity (watts per capita)')
ax.set_title('Installed Renewable Electricity-Generating Capacity in Pacific Islands')
ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
fig.tight_layout()
st.pyplot(fig)

st.markdown("Data source: Blue Pacific 2050 - Climate Change And Disasters (Thematic Area 5)")
