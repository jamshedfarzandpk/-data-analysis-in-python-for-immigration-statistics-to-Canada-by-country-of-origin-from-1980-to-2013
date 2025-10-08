import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Load data
df = pd.read_excel('data/Canada.xlsx', sheet_name='Canada by Citizenship (2)')

# Keep only relevant columns — YEARS ARE INTEGERS!
cols_to_keep = ['OdName', 'AreaName', 'RegName', 'DevName'] + list(range(1980, 2014))
df = df[cols_to_keep].copy()

# Rename for clarity
df.rename(columns={'OdName': 'Country'}, inplace=True)

# Melt year columns into rows
df_tidy = df.melt(
    id_vars=['Country', 'AreaName', 'RegName', 'DevName'],
    value_vars=list(range(1980, 2014)),  # ← also integers here
    var_name='Year',
    value_name='Immigrants'
)

# Convert Year to integer (it already is, but ensure)
df_tidy['Year'] = df_tidy['Year'].astype(int)

# Remove 'Unknown' and 'World' entries
df_tidy = df_tidy[~df_tidy['Country'].isin(['Unknown', 'World'])]

# Compute total immigrants per country
country_totals = df_tidy.groupby('Country')['Immigrants'].sum().reset_index()

# Key metrics
total_immigrants = df_tidy['Immigrants'].sum()
top_10_countries = country_totals.nlargest(10, 'Immigrants')

print(f"✅ Total immigrants to Canada (1980–2013): {total_immigrants:,.0f}")
print("\nTop 10 Source Countries:")
print(top_10_countries.to_string(index=False))

# --- Visualizations ---
yearly_total = df_tidy.groupby('Year')['Immigrants'].sum().reset_index()
fig1 = px.line(yearly_total, x='Year', y='Immigrants', title='Total Immigration to Canada (1980–2013)', markers=True)

top10_fig = px.bar(
    top_10_countries,
    x='Immigrants', y='Country',
    orientation='h',
    title='Top 10 Source Countries',
    color='Immigrants',
    color_continuous_scale='Blues'
).update_layout(yaxis={'categoryorder': 'total ascending'})

# Show a simple chart
fig1.show()
top10_fig.show()