# canada_immigration_dashboard.py
import dash
from dash import dcc, html
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ----------------------------
# 1. Load and clean data
# ----------------------------
df = pd.read_excel('data/Canada.xlsx', sheet_name='Canada by Citizenship (2)')

# Keep only relevant columns (years are INTs!)
cols = ['OdName', 'AreaName', 'RegName', 'DevName'] + list(range(1980, 2014))
df = df[cols].copy()
df.rename(columns={'OdName': 'Country'}, inplace=True)

# Remove 'Unknown' and 'World'
df = df[~df['Country'].isin(['Unknown', 'World'])]

# Melt into tidy format
df_tidy = df.melt(
    id_vars=['Country', 'AreaName', 'RegName', 'DevName'],
    value_vars=list(range(1980, 2014)),
    var_name='Year',
    value_name='Immigrants'
)
df_tidy['Year'] = df_tidy['Year'].astype(int)

# ----------------------------
# 2. Compute KPIs
# ----------------------------
total_immigrants = df_tidy['Immigrants'].sum()
top_country = df_tidy.groupby('Country')['Immigrants'].sum().idxmax()
top_country_total = df_tidy.groupby('Country')['Immigrants'].sum().max()
peak_year = df_tidy.groupby('Year')['Immigrants'].sum().idxmax()
peak_year_total = df_tidy.groupby('Year')['Immigrants'].sum().max()

# ----------------------------
# 3. Create individual plots
# ----------------------------

# Plot 1: Total Immigration Over Time
yearly_total = df_tidy.groupby('Year')['Immigrants'].sum().reset_index()
fig1 = px.line(
    yearly_total,
    x='Year',
    y='Immigrants',
    title='Total Immigration to Canada (1980–2013)',
    markers=True,
    height=450
).update_layout(plot_bgcolor='white')

# Plot 2: Top 10 Source Countries
top10 = df_tidy.groupby('Country')['Immigrants'].sum().nlargest(10).reset_index()
fig2 = px.bar(
    top10,
    x='Immigrants',
    y='Country',
    orientation='h',
    title='Top 10 Source Countries (1980–2013)',
    color='Immigrants',
    color_continuous_scale='Blues',
    height=450
).update_layout(yaxis={'categoryorder': 'total ascending'}, plot_bgcolor='white')

# Plot 3: Immigration by Region
region_totals = df_tidy.groupby('AreaName')['Immigrants'].sum().reset_index().sort_values('Immigrants')
fig3 = px.bar(
    region_totals,
    x='Immigrants',
    y='AreaName',
    orientation='h',
    title='Immigration by Region',
    color='Immigrants',
    color_continuous_scale='Viridis',
    height=450
).update_layout(plot_bgcolor='white')

# Plot 4: Developed vs. Developing
dev_totals = df_tidy.groupby('DevName')['Immigrants'].sum().reset_index()
fig4 = px.pie(
    dev_totals,
    values='Immigrants',
    names='DevName',
    title='Developed vs. Developing Regions',
    color_discrete_sequence=['#2E86AB', '#A23B72'],
    height=450
)

# Plot 5: Top 5 Countries Over Time
top5_countries = top10.head(5)['Country']
df_top5 = df_tidy[df_tidy['Country'].isin(top5_countries)]
fig5 = px.line(
    df_top5,
    x='Year',
    y='Immigrants',
    color='Country',
    title='Top 5 Countries Over Time',
    height=450
).update_layout(plot_bgcolor='white')

# Plot 6: Heatmap of Top 20 Countries
top20 = df_tidy.groupby('Country')['Immigrants'].sum().nlargest(20).index
heatmap_data = df_tidy[df_tidy['Country'].isin(top20)].pivot(index='Country', columns='Year', values='Immigrants').fillna(0)
fig6 = px.imshow(
    heatmap_data,
    labels=dict(x="Year", y="Country", color="Immigrants"),
    title="Heatmap: Top 20 Countries by Year",
    color_continuous_scale='YlGnBu',
    height=700
)

# Plot 7: Immigration by Sub-Region
subregion_totals = df_tidy.groupby('RegName')['Immigrants'].sum().reset_index().sort_values('Immigrants')
fig7 = px.bar(
    subregion_totals,
    x='Immigrants',
    y='RegName',
    orientation='h',
    title='Immigration by Sub-Region',
    color='Immigrants',
    color_continuous_scale='Plasma',
    height=600
).update_layout(plot_bgcolor='white')

# Plot 8: Stacked Area by Region
region_yearly = df_tidy.groupby(['AreaName', 'Year'])['Immigrants'].sum().reset_index()
fig8 = px.area(
    region_yearly,
    x='Year',
    y='Immigrants',
    color='AreaName',
    title='Immigration by Region Over Time (Stacked)',
    height=500
)

# Plot 9: Year-over-Year Growth (Top 5)
df_growth = df_top5.copy()
df_growth['Growth'] = df_growth.groupby('Country')['Immigrants'].pct_change() * 100
fig9 = px.line(
    df_growth.dropna(),
    x='Year',
    y='Growth',
    color='Country',
    title='Year-over-Year Growth Rate (%) – Top 5 Countries',
    height=450
).update_layout(yaxis_title='Growth Rate (%)', plot_bgcolor='white')

# Plot 10: Treemap of All Countries
fig10 = px.treemap(
    df_tidy.groupby('Country')['Immigrants'].sum().reset_index(),
    path=['Country'],
    values='Immigrants',
    title='Treemap: Immigration by Country',
    color='Immigrants',
    color_continuous_scale='RdBu',
    height=600
)

# ----------------------------
# 4. Initialize Dash app
# ----------------------------
app = dash.Dash(__name__)
app.title = "Canada Immigration Dashboard"

# ----------------------------
# 5. App Layout
# ----------------------------
app.layout = html.Div(style={'padding': '20px', 'fontFamily': 'Arial'}, children=[
    html.H1("🇨🇦 Canada Immigration Dashboard (1980–2013)", style={'textAlign': 'center'}),

    # KPI Summary
    html.Div([
        html.Div([
            html.H4("Total Immigrants"),
            html.H2(f"{total_immigrants:,.0f}")
        ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px', 'textAlign': 'center', 'flex': '1'}),
        html.Div([
            html.H4("Top Source Country"),
            html.H2(top_country)
        ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px', 'textAlign': 'center', 'flex': '1'}),
        html.Div([
            html.H4("Peak Year"),
            html.H2(f"{peak_year} ({peak_year_total:,.0f})")
        ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px', 'textAlign': 'center', 'flex': '1'}),
        html.Div([
            html.H4("Top Country Total"),
            html.H2(f"{top_country_total:,.0f}")
        ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px', 'textAlign': 'center', 'flex': '1'}),
    ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '30px', 'flexWrap': 'wrap'}),

    # Charts
    html.H2("📈 Key Trends"),
    dcc.Graph(figure=fig1),
    html.Div([dcc.Graph(figure=fig2), dcc.Graph(figure=fig3)], style={'display': 'flex', 'gap': '20px', 'marginBottom': '30px'}),
    html.Div([dcc.Graph(figure=fig4), dcc.Graph(figure=fig5)], style={'display': 'flex', 'gap': '20px', 'marginBottom': '30px'}),

    html.H2("🌍 Regional Analysis"),
    dcc.Graph(figure=fig8),
    dcc.Graph(figure=fig7),

    html.H2("🔥 Advanced Insights"),
    dcc.Graph(figure=fig6),
    html.Div([dcc.Graph(figure=fig9), dcc.Graph(figure=fig10)], style={'display': 'flex', 'gap': '20px'})
])

# ----------------------------
# 6. Run app
# ----------------------------
if __name__ == '__main__':
    app.run(debug=True)