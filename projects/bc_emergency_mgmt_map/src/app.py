<<<<<<< HEAD
import json
import os
=======
>>>>>>> 05a612ff867b612a7e92a4f61b7b0051891e20d1
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

<<<<<<< HEAD
# Initializing data with some diagnostics...
=======
# Initialize data
# poly_geodf = bc_alerts_api()
# sites_df = retrieve_site_data()
# sites_with_events = check_sites_in_emergencies(sites_df, poly_geodf)

>>>>>>> 05a612ff867b612a7e92a4f61b7b0051891e20d1
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

<<<<<<< HEAD
COLORS = {
    'dark_bg': '#00060e',
    'dark_text': '#e4e4e4',
    'dark_text_secondary': '#f5d5b5',
    'dark_border': '#333',
    'dark_header': '#00ff2b',
    'blue': '#00aeff',
    'green': '#00FF41',
    'darkgreen': '#36ba01',
}

# Font family
FONT_FAMILY = "'Helvetica Neue Bold', 'Helvetica Neue', Helvetica, Arial, sans-serif"
FONT_FAMILY_REGULAR = "'Helvetica Neue', Helvetica, Arial, sans-serif"

# Initialize Dash app
app = Dash(__name__)

# RECENT EDIT - Add custom CSS for hover effects and global styles
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                background-color: #00FF41;
                color: #e4e4e4;
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                margin: 0;
                padding: 0;
            }
            
            /* Button hover effect */
            button:hover {
                background-color: #00aeff !important;
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0, 174, 255, 0.3);
                transition: all 0.3s ease;
            }
            
            /* Dropdown styling */
            /* Dropdown text color fix */
            .custom-dropdown .Select-control,
            .custom-dropdown .Select-value-label,
            .custom-dropdown .Select-placeholder {
                color: #e4e4e4 !important;
            }

            .Select-control {
                background-color: #1a1a1a !important;
                border-color: #333 !important;
            }

            .Select-value-label {
                color: #e4e4e4 !important;
            }
            
            .Select-placeholder {
                color: #b0b0b0 !important;
            }

            .Select-menu-outer {
                background-color: #1a1a1a !important;
                border-color: #333 !important;
            }
            
            .Select-option {
                background-color: #1a1a1a !important;
                color: #e4e4e4 !important;
            }
            
            .Select-option:hover {
                background-color: #00aeff !important;
                color: #00060e !important;
            }
            
            /* Checkbox styling */
            input[type="checkbox"] {
                accent-color: #00FF41;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# App Layout
app.layout = html.Div([
    # Header
    html.Div(
        [
            html.H1(
                'BC Emergency Management Dashboard',
                style={
                    'display': 'inline-block',
                    'margin-right': '20px',
                    'color': COLORS['dark_header'],
                    'fontFamily': FONT_FAMILY,
                    'fontSize': '32px',
                    'fontWeight': 'bold'
                }
            ),

            html.Button(
                'Refresh Data',
                id='refresh-button',
                n_clicks=0,
                style={
                    'padding': '10px 20px',
                    'backgroundColor': COLORS['darkgreen'],
                    'color': 'white',
                    'border': 'none',
                    'cursor': 'pointer',
                    'marginLeft': '20px',
                    'fontFamily': FONT_FAMILY_REGULAR,
                    'fontSize': '14px',
                    'borderRadius': '4px',
                    'fontWeight': 'bold'
                }
            ),

            html.Div(
                [
                    html.Label(
                        'Show only affected sites: ',
                        style={
                            'margin-right': '10px',
                            'fontFamily': FONT_FAMILY,
                            'fontWeight': 'bold',
                            'color': COLORS['dark_text']
                        }
                    ),
                    dcc.Checklist(
                        id='affected-toggle',
                        options=[{'label': '', 'value': 'affected'}],
                        value=[],
                        style={'display': 'inline-block'}
                    )
                ], 
                style={'display': 'inline-block', 'float': 'right', 'margin-top': '20px'}
            )
        ], 
        style={
            'padding': '20px',
            'backgroundColor': COLORS['dark_bg'],
            'borderBottom': f'2px solid {COLORS["dark_border"]}'
        }
    ),
=======
# Initialize Dash app
app = Dash(__name__)

# App layout
app.layout = html.Div([
    # Header
    html.Div([
        html.H1('Emergency Sites Dashboard',
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
>>>>>>> 05a612ff867b612a7e92a4f61b7b0051891e20d1

    # Controls row
    html.Div([
        html.Div([
<<<<<<< HEAD
            html.Label(
                'City:',
                style={
                    'fontFamily': FONT_FAMILY,
                    'fontWeight': 'bold',
                    'color': COLORS['dark_text'],
                    'marginBottom': '5px',
                    'display': 'block'
                }
            ),

=======
            html.Label('Filter by City:', style={'font-weight': 'bold'}),
>>>>>>> 05a612ff867b612a7e92a4f61b7b0051891e20d1
            dcc.Dropdown(
                id='city-filter',
                options=[{'label': 'All Cities', 'value': 'all'}] +
                        [{'label': city, 'value': city} for city in sorted(sites_df['city'].unique())],
                value='all',
                clearable=False,
<<<<<<< HEAD
                style={
                    'width': '200px',
                    'fontFamily': FONT_FAMILY_REGULAR,
                    'color': COLORS['dark_text']
                },
                className='custom-dropdown'
            )
        ], style={'display': 'inline-block', 'margin-right': '20px', 'vertical-align': 'top'}),

        html.Div([
            html.Label(
                'Event Type:',
                style={
                    'fontFamily': FONT_FAMILY,
                    'fontWeight': 'bold',
                    'color': COLORS['dark_text'],
                    'marginBottom': '5px',
                    'display': 'block'
                }
            ),
=======
                style={'width': '200px'}
            )
        ], style={'display': 'inline-block', 'margin-right': '20px'}),

        html.Div([
            html.Label('Filter by Event Type:', style={'font-weight': 'bold'}),
>>>>>>> 05a612ff867b612a7e92a4f61b7b0051891e20d1
            dcc.Dropdown(
                id='event-type-filter',
                options=[{'label': 'All Types', 'value': 'all'}],
                value='all',
                clearable=False,
<<<<<<< HEAD
                style={
                    'width': '200px',
                    'fontFamily': FONT_FAMILY_REGULAR,
                    'color': COLORS['dark_text']
                },
                className='custom-dropdown'
            )
        ], style={'display': 'inline-block', 'margin-right': '20px', 'vertical-align': 'top'}),

        html.Div([
            html.Label(
                'Event Name:',
                style={
                    'fontFamily': FONT_FAMILY,
                    'fontWeight': 'bold',
                    'color': COLORS['dark_text'],
                    'marginBottom': '5px',
                    'display': 'block'
                }
            ),
=======
                style={'width': '200px'}
            )
        ], style={'display': 'inline-block', 'margin-right': '20px'}),

        html.Div([
            html.Label('Filter by Event Name:', style={'font-weight': 'bold'}),
>>>>>>> 05a612ff867b612a7e92a4f61b7b0051891e20d1
            dcc.Dropdown(
                id='event-name-filter',
                options=[{'label': 'All Events', 'value': 'all'}],
                value='all',
                clearable=False,
<<<<<<< HEAD
                style={
                    'width': '250px',
                    'fontFamily': FONT_FAMILY_REGULAR,
                    'color': COLORS['dark_text']
                },
                className='custom-dropdown'
            )

        ], style={'display': 'inline-block', 'margin-right': '20px', 'vertical-align': 'top'}),

        html.Button(
            'Reset Filters',
            id='reset-button',
            n_clicks=0,
            style={
                'padding': '10px 20px',
                'backgroundColor': COLORS['darkgreen'],
                'color': 'white',
                'border': 'none',
                'cursor': 'pointer',
                'marginLeft': '20px',
                'fontFamily': FONT_FAMILY_REGULAR,
                'fontSize': '14px',
                'borderRadius': '4px',
                'fontWeight': 'bold'
            }
        )

    ], style={
        'padding': '20px',
        'backgroundColor': COLORS['dark_bg'],
        'borderBottom': f'1px solid {COLORS["dark_border"]}'
    }),

    # Map
    dcc.Graph(
        id='emergency-map',
        style={'height': '600px', 'backgroundColor': COLORS['dark_bg']},
        config={
            'scrollZoom': True,
            'displayModeBar': True,
            'doubleClick': 'reset+autosize'
        }
    ),

    # Data table
    html.Div([
        html.H3(
            'Site Details',
            style={
                'fontFamily': FONT_FAMILY,
                'fontWeight': 'bold',
                'color': COLORS['dark_text'],
                'marginBottom': '15px'
            }
        ),
=======
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
>>>>>>> 05a612ff867b612a7e92a4f61b7b0051891e20d1
        dash_table.DataTable(
            id='sites-table',
            columns=[
                {'name': 'Site Name', 'id': 'site_name'},
                {'name': 'City', 'id': 'city'},
                {'name': 'Contact Phone', 'id': 'phone'},
                {'name': 'Max Capacity', 'id': 'max_capacity'},
                {'name': 'Event Type', 'id': 'event_type'},
            ],
<<<<<<< HEAD
            style_table={
                'overflowX': 'auto',
                'overflowY': 'auto',
                'maxHeight': '400px',
                'backgroundColor': COLORS['dark_bg']
            },
            style_cell={
                'textAlign': 'left',
                'padding': '10px',
                'backgroundColor': '#1a1a1a',
                'color': COLORS['dark_text'],
                'border': f'1px solid {COLORS["dark_border"]}',
                'fontFamily': FONT_FAMILY_REGULAR
            },
            style_header={
                'backgroundColor': '#2d2d2d',
                'fontWeight': 'bold',
                'color': COLORS['dark_text'],
                'border': f'1px solid {COLORS["dark_border"]}',
                'fontFamily': FONT_FAMILY,
                'fontSize': '14px'
            },
            style_data_conditional=[
                {
                    'if': {'filter_query': '{event_type} != ""'},
                    'backgroundColor': '#3d2a1f',
                    'color': COLORS['dark_text_secondary']
                },
                {
                    'if': {'state': 'active'},
                    'backgroundColor': '#0a2540',
                    'border': f'1px solid {COLORS["blue"]}'
=======
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left', 'padding': '10px'},
            style_header={'backgroundColor': '#f0f0f0', 'fontWeight': 'bold'},
            style_data_conditional=[
                {
                    'if': {'filter_query': '{event_type} != \"\"'},
                    'backgroundColor': '#fff3cd',
>>>>>>> 05a612ff867b612a7e92a4f61b7b0051891e20d1
                }
            ],
            page_size=15
        )
<<<<<<< HEAD
    ], style={
        'padding': '20px',
        'backgroundColor': COLORS['dark_bg']
    }),
=======
    ], style={'padding': '20px'}),
>>>>>>> 05a612ff867b612a7e92a4f61b7b0051891e20d1

    # Hidden div to store data
    html.Div(id='emergency-data-store', style={'display': 'none'}),
    html.Div(id='sites-data-store', style={'display': 'none'})
<<<<<<< HEAD
], 
style={
    'backgroundColor': COLORS['dark_bg'],
    'minHeight': '100vh',
    'fontFamily': FONT_FAMILY_REGULAR
})
=======
])
>>>>>>> 05a612ff867b612a7e92a4f61b7b0051891e20d1


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

<<<<<<< HEAD
    # Load data -- CLAUDE FIX
    if sites_json and poly_json:
        import json
        sites_data = pd.read_json(sites_json)
        poly_data = gpd.GeoDataFrame.from_features(json.loads(poly_json))  # <-- BETTER FIX
=======
    # Load data
    if sites_json and poly_json:
        sites_data = pd.read_json(sites_json)
        poly_data = gpd.read_file(poly_json)
>>>>>>> 05a612ff867b612a7e92a4f61b7b0051891e20d1
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
<<<<<<< HEAD
        import json
        sites_data = pd.read_json(sites_json)
        poly_data = gpd.GeoDataFrame.from_features(json.loads(poly_json))  # <-- BETTER FIX
    else:
        sites_data = sites_with_events
        poly_data = poly_geodf
=======
        sites_data = pd.read_json(sites_json)
        poly_data = gpd.read_file(poly_json)
    else:
        sites_data = sites_with_events.copy()
        poly_data = poly_geodf.copy()
>>>>>>> 05a612ff867b612a7e92a4f61b7b0051891e20d1

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
<<<<<<< HEAD
    for idx, row in poly_data.iterrows():
=======
    for idx, row in poly_geodf.iterrows():
>>>>>>> 05a612ff867b612a7e92a4f61b7b0051891e20d1
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
<<<<<<< HEAD
                      showlegend=False
=======
                      showlegend=True
>>>>>>> 05a612ff867b612a7e92a4f61b7b0051891e20d1
                  )
                )

    # Separate affected and unaffected sites
<<<<<<< HEAD
    # affected_sites = sites_with_events[sites_with_events['event_type'].notna()]
    # unaffected_sites = sites_with_events[sites_with_events['event_type'].isna()]

    # Separate affected and unaffected sites (use filtered_sites instead)
    affected_sites = filtered_sites[filtered_sites['event_type'].notna()]  # <-- CORRECT
    unaffected_sites = filtered_sites[filtered_sites['event_type'].isna()]  # <-- CORRECT

    # Add affected sites (red markers)
    if len(affected_sites) > 0:
        fig.add_trace(
            go.Scattermapbox(
                lon=affected_sites['lon'],
                lat=affected_sites['lat'],
                mode='markers',
                marker=dict(size=8, color='#FF3333', opacity=0.8), # Line border didn't work: , line=dict(color='black', width=2)
                name='Affected Sites',
                hoverinfo='text',
                hovertext=[
                    f"<b>{row['site_name']}</b><br>"
                    f"City: {row['city']}<br>"
                    f"Capacity: {row['max_capacity']}<br>"
                    f"<b>⚠️ Affected by: {row['event_type']}</b>"
                    for _, row in affected_sites.iterrows()
                ],
                showlegend=False
            )
        )

    # Add unaffected sites (cyan markers)
    if len(unaffected_sites) > 0:
        fig.add_trace(
            go.Scattermapbox(
                lon=unaffected_sites['lon'],
                lat=unaffected_sites['lat'],
                mode='markers',
                marker=dict(size=8, color='#00FFFF', opacity=0.8), # Line border didn't work: , line=dict(color='black', width=2)
                name='Unaffected Sites',
                hoverinfo='text',
                hovertext=[
                    f"<b>{row['site_name']}</b><br>"
                    f"City: {row['city']}<br>"
                    f"Capacity: {row['max_capacity']}<br>"
                    f"Status: Not affected"
                    for _, row in unaffected_sites.iterrows()
                ],
                showlegend=False
            )
        )

    # Adding automatic zoom calculations
    # Calculate map center and zoom based on filtered sites
    is_default_view = (city_filter == 'all' and 
                   event_type_filter == 'all' and 
                   event_name_filter == 'all' and 
                   'affected' not in affected_toggle)
    
    if is_default_view:
        # Reset view - use your default coordinates
        center_lat = 49.17486136570926
        center_lon = -123.15151571413801
        zoom_level = 8

    elif len(filtered_sites) > 0:
        # Get bounding box of filtered sites
        min_lat = filtered_sites['lat'].min()
        max_lat = filtered_sites['lat'].max()
        min_lon = filtered_sites['lon'].min()
        max_lon = filtered_sites['lon'].max()
        
        # Calculate center
        center_lat = (min_lat + max_lat) / 2
        center_lon = (min_lon + max_lon) / 2
        
        # Calculate zoom level based on bounding box size
        lat_range = max_lat - min_lat
        lon_range = max_lon - min_lon
        max_range = max(lat_range, lon_range)
        
        # Rough zoom calculation (you can adjust these values)
        if max_range > 10:
            zoom_level = 5
        elif max_range > 5:
            zoom_level = 6
        elif max_range > 2:
            zoom_level = 7
        elif max_range > 1:
            zoom_level = 8
        elif max_range > 0.5:
            zoom_level = 9
        elif max_range > 0.2:
            zoom_level = 10
        else:
            zoom_level = 11

    # Brand new update layout with dark mode
    fig.update_layout(
        mapbox=dict(
            style='open-street-map',
            center=dict(lat=center_lat, lon=center_lon),
            zoom=zoom_level
        ),
        dragmode='zoom',
        modebar_add=['pan2d', 'zoom2d', 'zoomIn2d', 'zoomOut2d', 'resetScale2d'],
        showlegend=False,
=======
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
>>>>>>> 05a612ff867b612a7e92a4f61b7b0051891e20d1
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
<<<<<<< HEAD
            bgcolor='rgba(0, 6, 14, 0.9)',  # Dark background
            bordercolor=COLORS['dark_border'],
            borderwidth=1,
            font=dict(
                color=COLORS['dark_text'],
                size=10,
                family=FONT_FAMILY_REGULAR
            )
=======
            bgcolor='rgba(30,30,30,0.9)',
            bordercolor='white',
            borderwidth=1,
            font=dict(color='white', size=10)
>>>>>>> 05a612ff867b612a7e92a4f61b7b0051891e20d1
        ),
        margin=dict(l=0, r=0, t=40, b=0),
        height=800,
        hovermode='closest',
<<<<<<< HEAD
        paper_bgcolor=COLORS['dark_bg'],
        plot_bgcolor=COLORS['dark_bg']
=======
        paper_bgcolor='#1a1a1a',
        title=dict(
            text='BC Emergency Management Dashboard',
            font=dict(size=24, color='white'),
            x=0.5,
            xanchor='center'
        )
>>>>>>> 05a612ff867b612a7e92a4f61b7b0051891e20d1
    )

    # Configure scroll zoom behavior
    fig.update_mapboxes(bearing=0, pitch=0)
    # fig.show(config={'scrollZoom': True, 'displayModeBar': True})

    # Prepare table data
<<<<<<< HEAD
    table_data = filtered_sites[['site_name', 'city', 'max_capacity', 'event_type']].fillna('').to_dict('records') # Removed 'phone', 

    return fig, table_data

@app.callback(
    [Output('city-filter', 'value'),
     Output('event-type-filter', 'value'),
     Output('event-name-filter', 'value'),
     Output('affected-toggle', 'value')],
    Input('reset-button', 'n_clicks'),
    prevent_initial_call=True
)
def reset_filters(n_clicks):
    """Reset all filters to default values"""
    return 'all', 'all', 'all', []

if __name__ == '__main__':
    # For Google Colab, use mode='inline' or 'external'
    # For local Jupyter, use mode='inline' or mode='jupyterlab'
    port = int(os.environ.get('PORT', 8050))
    app.run(host='0.0.0.0', port=port, debug=False)
    # app.run(
    #     debug=True,
    #     dev_tools_hot_reload=True,
    #     use_reloader=False,  # Avoids Windows signal issues
    #     port=8050
    # )
=======
    table_data = filtered_sites[['site_name', 'city', 'phone', 'max_capacity', 'event_type']].fillna('').to_dict('records')

    return fig, table_data

if __name__ == '__main__':
    # For Google Colab, use mode='inline' or 'external'
    # For local Jupyter, use mode='inline' or mode='jupyterlab'
    app.run(port=8050, debug=False, use_reloader=False)
>>>>>>> 05a612ff867b612a7e92a4f61b7b0051891e20d1
