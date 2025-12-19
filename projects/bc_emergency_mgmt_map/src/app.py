import json
import requests
import numpy as np
import pandas as pd
import geopandas as gpd
import plotly.graph_objects as go

from dash import Dash, dcc, html, Input, Output, State, dash_table
from datetime import datetime, timedelta
from shapely.geometry import shape, Point, Polygon
from zoneinfo import ZoneInfo
from utils import *


# ============================================================================
# DASH APP
# ============================================================================

# Initialize data
# poly_geodf = bc_alerts_api()
# sites_df = retrieve_site_data()
# sites_with_events = check_sites_in_emergencies(sites_df, poly_geodf)

print("Fetching emergency data...")
poly_geodf = bc_alerts_api()
print(f"✓ Got {len(poly_geodf)} emergency events")

print("Fetching sites data...")
sites_df = retrieve_site_data()
print(f"✓ Got {len(sites_df)} sites")

print("Checking affected sites...")
sites_with_events = check_sites_in_emergencies(sites_df, poly_geodf)
print("✓ Initialization complete")

# Color mapping for event types
EVENT_LINE_COLORS = {
    'Fire': 'rgba(255, 80, 80, 0.4)',
    'Flood': 'rgba(80, 150, 255, 0.4)',
    'Landslide': 'rgba(200, 120, 60, 0.4)',
}

EVENT_COLORS = {
    'Alert': 'rgb(246, 200, 176)',
    'Order': 'rgb(251, 159, 157)',
}

# Initialize Dash app
app = Dash(__name__)

# App layout
app.layout = html.Div([
    # Header
    html.Div([
        html.H1('BC Emergency Evacuations Dashboard',
                style={'display': 'inline-block', 'margin-right': '20px'}),
        html.Div([
            html.Label('Show only affected sites: ',
                      style={'margin-right': '10px', 'font-weight': 'bold'}),
            dcc.Checklist(
                id='affected-toggle',
                options=[{'label': '', 'value': 'affected'}],
                value=[],
                style={'display': 'inline-block'}
            )
        ], style={'display': 'inline-block', 'float': 'right', 'margin-top': '20px'})
    ], style={'padding': '20px', 'background-color': '#f0f0f0', 'border-bottom': '2px solid #ccc'}),

    # Controls row
    html.Div([
        html.Div([
            html.Label('Filter by City:', style={'font-weight': 'bold'}),
            dcc.Dropdown(
                id='city-filter',
                options=[{'label': 'All Cities', 'value': 'all'}] +
                        [{'label': city, 'value': city} for city in sorted(sites_df['city'].unique())],
                value='all',
                clearable=False,
                style={'width': '200px'}
            )
        ], style={'display': 'inline-block', 'margin-right': '20px'}),

        html.Div([
            html.Label('Filter by Event Type:', style={'font-weight': 'bold'}),
            dcc.Dropdown(
                id='event-type-filter',
                options=[{'label': 'All Types', 'value': 'all'}],
                value='all',
                clearable=False,
                style={'width': '200px'}
            )
        ], style={'display': 'inline-block', 'margin-right': '20px'}),

        html.Div([
            html.Label('Filter by Event Name:', style={'font-weight': 'bold'}),
            dcc.Dropdown(
                id='event-name-filter',
                options=[{'label': 'All Events', 'value': 'all'}],
                value='all',
                clearable=False,
                style={'width': '250px'}
            )
        ], style={'display': 'inline-block', 'margin-right': '20px'}),

        html.Button('Refresh Emergency Data', id='refresh-button', n_clicks=0,
                   style={'padding': '10px 20px', 'background-color': '#4CAF50',
                         'color': 'white', 'border': 'none', 'cursor': 'pointer',
                         'margin-left': '20px'})
    ], style={'padding': '20px'}),

    # Map
    dcc.Graph(id='emergency-map', style={'height': '600px'}),

    # Data table
    html.Div([
        html.H3('Site Details'),
        dash_table.DataTable(
            id='sites-table',
            columns=[
                {'name': 'Site Name', 'id': 'site_name'},
                {'name': 'City', 'id': 'city'},
                # {'name': 'Contact Phone', 'id': 'phone'},
                {'name': 'Max Capacity', 'id': 'max_capacity'},
                {'name': 'Event Type', 'id': 'event_type'},
            ],
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left', 'padding': '10px'},
            style_header={'backgroundColor': '#f0f0f0', 'fontWeight': 'bold'},
            style_data_conditional=[
                {
                    'if': {'filter_query': '{event_type} != \"\"'},
                    'backgroundColor': '#fff3cd',
                }
            ],
            page_size=15
        )
    ], style={'padding': '20px'}),

    # Hidden div to store data
    html.Div(id='emergency-data-store', style={'display': 'none'}),
    html.Div(id='sites-data-store', style={'display': 'none'})
])


# ============================================================================
# CALLBACKS
# ============================================================================

@app.callback(
    [Output('emergency-data-store', 'children'),
     Output('sites-data-store', 'children')],
    Input('refresh-button', 'n_clicks')
)
def refresh_emergency_data(n_clicks):
    """Refresh emergency data from API"""
    # In real implementation, fetch from API here
    print("Fetching emergency data from function...")
    poly_geodf_new = bc_alerts_api()

    print("Fetching site data from function...")
    sites_with_events_new = check_sites_in_emergencies(sites_df, poly_geodf_new)

    # Store as JSON
    poly_json = poly_geodf_new.to_json()
    sites_json = sites_with_events_new.to_json(orient='records')

    return poly_json, sites_json


@app.callback(
    [Output('event-type-filter', 'options'),
     Output('event-name-filter', 'options')],
    [Input('city-filter', 'value'),
     Input('sites-data-store', 'children'),
     Input('emergency-data-store', 'children')]
)
def update_filter_options(selected_city, sites_json, poly_json):
    """Update filter options based on selected city"""

    # Load data -- CLAUDE FIX
    if sites_json and poly_json:
        import json
        sites_data = pd.read_json(sites_json)
        poly_data = gpd.GeoDataFrame.from_features(json.loads(poly_json))  # <-- BETTER FIX
    else:
        sites_data = sites_with_events
        poly_data = poly_geodf

    # Filter sites by city if selected
    if selected_city != 'all':
        filtered_sites = sites_data[sites_data['city'] == selected_city]
    else:
        filtered_sites = sites_data

    # Get unique event types and names from affected sites
    affected_sites = filtered_sites[filtered_sites['event_type'].notna()]

    # Event types
    if len(affected_sites) > 0:
        event_types = [{'label': 'All Types', 'value': 'all'}] + [{'label': et, 'value': et} for et in sorted(affected_sites['event_type'].unique())]
        event_names = [{'label': 'All Events', 'value': 'all'}] + [{'label': en, 'value': en} for en in sorted(affected_sites['event_name'].unique())]
    else:
        event_types = [{'label': 'All Types', 'value': 'all'}]
        event_names = [{'label': 'All Events', 'value': 'all'}]

    return event_types, event_names


@app.callback(
    [Output('emergency-map', 'figure'),
     Output('sites-table', 'data')],
    [Input('city-filter', 'value'),
     Input('event-type-filter', 'value'),
     Input('event-name-filter', 'value'),
     Input('affected-toggle', 'value'),
     Input('sites-data-store', 'children'),
     Input('emergency-data-store', 'children')]
)


def update_map_and_table(city_filter, event_type_filter, event_name_filter,
                        affected_toggle, sites_json, poly_json):
    """Update map and table based on filters"""

    # Load data
    if sites_json and poly_json:
        import json
        sites_data = pd.read_json(sites_json)
        poly_data = gpd.GeoDataFrame.from_features(json.loads(poly_json))  # <-- BETTER FIX
    else:
        sites_data = sites_with_events
        poly_data = poly_geodf

    # Apply filters
    filtered_sites = sites_data.copy()

    # City filter
    if city_filter != 'all':
        filtered_sites = filtered_sites[filtered_sites['city'] == city_filter]

    # Event type filter
    if event_type_filter != 'all':
        filtered_sites = filtered_sites[filtered_sites['event_type'] == event_type_filter]

    # Event name filter
    if event_name_filter != 'all':
        filtered_sites = filtered_sites[filtered_sites['event_name'] == event_name_filter]

    # Affected toggle
    if 'affected' in affected_toggle:
        filtered_sites = filtered_sites[filtered_sites['event_type'].notna()]

    # Create map figure
    fig = go.Figure()

    # Add emergency polygons
    for idx, row in poly_geodf.iterrows():
        # coords = list(row.geometry.exterior.coords)
        # lons, lats = zip(*coords)
        geometry = row.geometry

        # Check if the geometry is a MultiPolygon or a single Polygon
        if geometry.geom_type == 'MultiPolygon':
            geometries_to_plot = geometry.geoms  # Iterate over individual polygons within the MultiPolygon
        elif geometry.geom_type == 'Polygon':
            geometries_to_plot = [geometry]  # Wrap single Polygon in a list for consistent iteration
        else:
            # Handle other geometry types if necessary, or skip them
            # For example, Point or LineString don't have an exterior to plot as a filled area
            print(f"Skipping non-polygon geometry type in plotting: {geometry.geom_type}")
            continue

        for geom_part in geometries_to_plot:
            # Ensure the polygon part has an exterior to avoid errors on invalid polygons
            if geom_part.exterior:
                coords = list(geom_part.exterior.coords)
                lons, lats = zip(*coords)

                fig.add_trace(
                    go.Scattermapbox(
                      lon=list(lons),
                      lat=list(lats),
                      mode='lines',
                      fill='toself',
                      fillcolor=EVENT_COLORS.get(row['order_alert_status'], 'rgba(128, 128, 128, 0.3)'),
                      line=dict(
                          color=EVENT_LINE_COLORS.get(row['event_type'], 'gray'),
                          width=3
                      ),
                      name=f"ID: {row['event_id']} | {row['event_name']} ({row['event_type']})",
                      hoverinfo='text',
                      hovertext=f"<b>{row['event_name']}</b> (Part {row['part_num']} of {row['total_parts']})<br>Type: {row['event_type']}<br>ID: {row['event_id']}",
                      showlegend=True
                  )
                )

    # Separate affected and unaffected sites
    affected_sites = sites_with_events[sites_with_events['event_type'].notna()]
    unaffected_sites = sites_with_events[sites_with_events['event_type'].isna()]

    # Add affected sites (red markers)
    if len(affected_sites) > 0:
        fig.add_trace(go.Scattermapbox(
            lon=affected_sites['lon'],
            lat=affected_sites['lat'],
            mode='markers',
            marker=dict(size=14, color='#FF3333', opacity=0.9),
            name='Affected Sites',
            hoverinfo='text',
            hovertext=[
                f"<b>{row['site_name']}</b><br>"
                f"City: {row['city']}<br>"
                f"Capacity: {row['max_capacity']}<br>"
                f"<b>⚠️ Affected by: {row['event_type']}</b>"
                for _, row in affected_sites.iterrows()
            ],
            showlegend=True
        ))

    # Add unaffected sites (cyan markers)
    if len(unaffected_sites) > 0:
        fig.add_trace(go.Scattermapbox(
            lon=unaffected_sites['lon'],
            lat=unaffected_sites['lat'],
            mode='markers',
            marker=dict(size=14, color='#00FFFF', opacity=0.9),
            name='Unaffected Sites',
            hoverinfo='text',
            hovertext=[
                f"<b>{row['site_name']}</b><br>"
                f"City: {row['city']}<br>"
                f"Capacity: {row['max_capacity']}<br>"
                f"Status: Not affected"
                for _, row in unaffected_sites.iterrows()
            ],
            showlegend=True
        ))

    # Update layout with VISIBLE dark mode style
    fig.update_layout(
        mapbox=dict(
            style='open-street-map',   # 'carto-darkmatter',
            center=dict(lat=48.441776002871805, lon=-123.37745586330038),
            zoom=5
        ),
        modebar_add=['pan2d', 'zoom2d', 'zoomIn2d', 'zoomOut2d', 'resetScale2d'],
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor='rgba(30,30,30,0.9)',
            bordercolor='white',
            borderwidth=1,
            font=dict(color='white', size=10)
        ),
        margin=dict(l=0, r=0, t=40, b=0),
        height=800,
        hovermode='closest',
        paper_bgcolor='#1a1a1a',
        title=dict(
            text='BC Emergency Management Dashboard',
            font=dict(size=24, color='white'),
            x=0.5,
            xanchor='center'
        )
    )

    # Configure scroll zoom behavior
    fig.update_mapboxes(bearing=0, pitch=0)
    # fig.show(config={'scrollZoom': True, 'displayModeBar': True})

    # Prepare table data
    table_data = filtered_sites[['site_name', 'city', 'max_capacity', 'event_type']].fillna('').to_dict('records') # Removed 'phone', 

    return fig, table_data

if __name__ == '__main__':
    # For Google Colab, use mode='inline' or 'external'
    # For local Jupyter, use mode='inline' or mode='jupyterlab'
    # app.run(port=8050, debug=False, use_reloader=False)
    app.run(
        debug=True,
        dev_tools_hot_reload=True,
        use_reloader=False,  # Avoids Windows signal issues
        port=8050
    )