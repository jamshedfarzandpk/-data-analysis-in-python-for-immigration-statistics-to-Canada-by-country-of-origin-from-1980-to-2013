import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

# Set default theme
pio.templates.default = "plotly_white"

# ----------------------------
# 1. Load and clean data
# ----------------------------
df = pd.read_excel('data/Canada.xlsx', sheet_name='Canada by Citizenship (2)')

# Keep only relevant columns (years are INTs!)
cols_to_keep = ['OdName', 'AreaName', 'RegName', 'DevName'] + list(range(1980, 2014))
df = df[cols_to_keep].copy()
df.rename(columns={'OdName': 'Country'}, inplace=True)

# Melt into tidy format
df_tidy = df.melt(
    id_vars=['Country', 'AreaName', 'RegName', 'DevName'],
    value_vars=list(range(1980, 2014)),
    var_name='Year',
    value_name='Immigrants'
)
df_tidy['Year'] = df_tidy['Year'].astype(int)
df_tidy = df_tidy[~df_tidy['Country'].isin(['Unknown', 'World'])]

# Compute aggregates
country_totals = df_tidy.groupby('Country')['Immigrants'].sum().reset_index()
region_totals = df_tidy.groupby('AreaName')['Immigrants'].sum().reset_index()
dev_totals = df_tidy.groupby('DevName')['Immigrants'].sum().reset_index()
yearly_total = df_tidy.groupby('Year')['Immigrants'].sum().reset_index()

top10_countries = country_totals.nlargest(10, 'Immigrants')['Country'].tolist()
df_top10 = df_tidy[df_tidy['Country'].isin(top10_countries)]

# ----------------------------
# 2. Generate All Possible Plots
# ----------------------------

# Plot 1: Total Immigration Over Time
fig1 = px.line(
    yearly_total,
    x='Year',
    y='Immigrants',
    title='Total Immigration to Canada (1980–2013)',
    markers=True,
    height=500
)
fig1.update_traces(line=dict(width=3), marker=dict(size=6))

# Plot 2: Top 10 Source Countries (Bar)
fig2 = px.bar(
    country_totals.nlargest(10, 'Immigrants'),
    x='Immigrants',
    y='Country',
    orientation='h',
    title='Top 10 Source Countries (1980–2013)',
    color='Immigrants',
    color_continuous_scale='Blues',
    height=500
).update_layout(yaxis={'categoryorder': 'total ascending'})

# Plot 3: Immigration by Region (Bar)
fig3 = px.bar(
    region_totals.sort_values('Immigrants'),
    x='Immigrants',
    y='AreaName',
    orientation='h',
    title='Immigration by Region',
    color='Immigrants',
    color_continuous_scale='Viridis',
    height=500
)

# Plot 4: Developed vs. Developing (Pie)
fig4 = px.pie(
    dev_totals,
    values='Immigrants',
    names='DevName',
    title='Developed vs. Developing Regions',
    color_discrete_sequence=['#2E86AB', '#A23B72'],
    height=500
)

# Plot 5: Top 10 Countries Over Time (Line)
fig5 = px.line(
    df_top10,
    x='Year',
    y='Immigrants',
    color='Country',
    title='Immigration Trends: Top 10 Countries',
    height=600
)

# Plot 6: Heatmap of Top 20 Countries by Year
top20 = country_totals.nlargest(20, 'Immigrants')['Country']
heatmap_data = df_tidy[df_tidy['Country'].isin(top20)].pivot(index='Country', columns='Year', values='Immigrants').fillna(0)
fig6 = px.imshow(
    heatmap_data,
    labels=dict(x="Year", y="Country", color="Immigrants"),
    title="Heatmap: Top 20 Countries by Year",
    color_continuous_scale='YlGnBu',
    aspect="auto",
    height=800
)

# Plot 7: Immigration by Sub-Region (Bar)
subregion_totals = df_tidy.groupby('RegName')['Immigrants'].sum().reset_index().sort_values('Immigrants')
fig7 = px.bar(
    subregion_totals,
    x='Immigrants',
    y='RegName',
    orientation='h',
    title='Immigration by Sub-Region',
    color='Immigrants',
    color_continuous_scale='Plasma',
    height=700
)

# Plot 8: Year-over-Year Growth Rate (Top 5 Countries)
df_growth = df_tidy[df_tidy['Country'].isin(top10_countries[:5])].copy()
df_growth['Growth'] = df_growth.groupby('Country')['Immigrants'].pct_change() * 100
fig8 = px.line(
    df_growth.dropna(),
    x='Year',
    y='Growth',
    color='Country',
    title='Year-over-Year Growth Rate (%) – Top 5 Countries',
    height=500
)
fig8.update_layout(yaxis_title='Growth Rate (%)')

# Plot 9: Stacked Area Chart by Region
region_yearly = df_tidy.groupby(['AreaName', 'Year'])['Immigrants'].sum().reset_index()
fig9 = px.area(
    region_yearly,
    x='Year',
    y='Immigrants',
    color='AreaName',
    title='Immigration by Region Over Time (Stacked)',
    height=600
)

# Plot 10: Treemap of All Countries (Optional – requires plotly >= 4.5)
fig10 = px.treemap(
    df_tidy.groupby('Country')['Immigrants'].sum().reset_index(),
    path=['Country'],
    values='Immigrants',
    title='Treemap: Immigration by Country (All)',
    color='Immigrants',
    color_continuous_scale='RdBu',
    height=700
)

# ----------------------------
# 3. Save All Plots
# ----------------------------
plots = [
    (fig1, "1_total_immigration"),
    (fig2, "2_top10_countries"),
    (fig3, "3_by_region"),
    (fig4, "4_developed_vs_developing"),
    (fig5, "5_top10_trends"),
    (fig6, "6_heatmap_top20"),
    (fig7, "7_by_subregion"),
    (fig8, "8_growth_rate"),
    (fig9, "9_stacked_region"),
    (fig10, "10_treemap")
]

for fig, name in plots:
    fig.write_html(f"{name}.html")
    #fig.write_image(f"{name}.png", scale=2)  # Requires kaleido

print("✅ All 10 plots saved as HTML ")

# ----------------------------
# 4. Optional: Show one plot
# ----------------------------
 #fig.show()