import json
import os
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

# Initializing data with some diagnostics...
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

COLORS = {
    'dark_bg': '#00060e',
    'dark_text': '#e4e4e4',
    'dark_border': '#333',
    'dark_header': '#00ff2b',
    'blue': '#00aeff',
    'green': '#00FF41',
    'darkgreen': '#36ba01',
    'lycanroc': '#f5d5b5'
}

# Font family
FONT_FAMILY = "'Helvetica Neue Bold', 'Helvetica Neue', Helvetica, Arial, sans-serif"
FONT_FAMILY_REGULAR = "'Helvetica Neue', Helvetica, Arial, sans-serif"
MONOSPACE = "'Courier New', 'Courier', monospace"

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

            /* Eraser button hover effect */
            #reset-button:hover {
                background-color: #00aeff !important;
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0, 174, 255, 0.3);
                transition: all 0.3s ease;
            }

            /* Footer link hover effect */
            a:hover {
                color: #00aeff !important;
                text-decoration: underline;
                transition: color 0.3s ease;
            }

            #reset-button:hover img {
                transform: scale(1.1);
                transition: transform 0.3s ease;
            }

            /* Search button hover */
            #search-button:hover {
                background-color: #0088cc !important;
                transform: scale(1.05);
                transition: all 0.3s ease;
            }

            /* Radius button hover */
            button[id^="radius-"]:hover {
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

    # Controls row
    html.Div([
        html.Div([
            html.Label(
                'City:',
                style={
                    'fontFamily': FONT_FAMILY,
                    'fontWeight': 'bold',
                    'color': COLORS['lycanroc'],
                    'marginBottom': '5px',
                    'display': 'block'
                }
            ),

            dcc.Dropdown(
                id='city-filter',
                options=[{'label': 'All Cities', 'value': 'all'}] +
                        [{'label': city, 'value': city} for city in sorted(sites_df['city'].unique())],
                value='all',
                clearable=False,
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
                    'color': COLORS['lycanroc'],
                    'marginBottom': '5px',
                    'display': 'block'
                }
            ),
            dcc.Dropdown(
                id='event-type-filter',
                options=[{'label': 'All Types', 'value': 'all'}],
                value='all',
                clearable=False,
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
                    'color': COLORS['lycanroc'],
                    'marginBottom': '5px',
                    'display': 'block'
                }
            ),
            dcc.Dropdown(
                id='event-name-filter',
                options=[{'label': 'All Events', 'value': 'all'}],
                value='all',
                clearable=False,
                style={
                    'width': '250px',
                    'fontFamily': FONT_FAMILY_REGULAR,
                    'color': COLORS['dark_text']
                },
                className='custom-dropdown'
            )
        ], style={'display': 'inline-block', 'margin-right': '20px', 'vertical-align': 'top'}),

        html.Button(
            html.Img(
                src='https://raw.githubusercontent.com/vanislekahuna/vanislekahuna.github.io/test/images/assets/eraser.png',
                style={
                    'height': '34px',
                    'width': '34px',
                    'filter': 'brightness(0) saturate(100%) invert(70%) sepia(85%) saturate(445%) hue-rotate(61deg) brightness(101%) contrast(101%)'
                    # 'filter': 'invert(1)'  # Makes it white if the icon is black
                }
            ),
            id='reset-button',
            n_clicks=0,
            style={
                'backgroundColor': '#00060e',
                'color': 'white',
                'border': 'none',
                'cursor': 'pointer',
                'marginLeft': '5px',
                'borderRadius': '4px',
                'display': 'inline-flex',
                'alignItems': 'center',
                'justifyContent': 'center',
                'height': '44px',  
                'width': '44px',
                'verticalAlign': 'bottom'
            }
        ),

        # Total Spaces Card
        html.Div([
            html.Div(
                id='total-spaces-number',
                style={
                    'fontSize': '24px',
                    'fontWeight': 'bold',
                    'color': COLORS['green'],
                    'fontFamily': FONT_FAMILY,
                    'marginBottom': '5px'
                }
            ),
            html.Div(
                'Total Spaces',
                style={
                    'fontSize': '12px',
                    'color': COLORS['dark_text'],
                    'fontFamily': FONT_FAMILY_REGULAR
                }
            )
        ], style={
            'display': 'inline-block',
            'padding': '12px 20px',
            'border': f'2px solid {COLORS["dark_border"]}',
            'borderRadius': '4px',
            'marginLeft': '20px',
            'minWidth': '120px',
            'textAlign': 'center',
            'verticalAlign': 'middle',
            'height': '74px',
            'boxSizing': 'border-box',
            'float': 'right'
        }),

        # Total Sites Card
        html.Div([
            html.Div(
                id='total-sites-number',
                style={
                    'fontSize': '24px',
                    'fontWeight': 'bold',
                    'color': COLORS['green'],
                    'fontFamily': FONT_FAMILY,
                    'marginBottom': '5px'
                }
            ),
            html.Div(
                'Total Sites',
                style={
                    'fontSize': '12px',
                    'color': COLORS['dark_text'],
                    'fontFamily': FONT_FAMILY_REGULAR
                }
            )
        ], style={
            'display': 'inline-block',
            'padding': '12px 20px',
            'border': f'2px solid {COLORS["dark_border"]}',
            'borderRadius': '4px',
            'marginLeft': '20px',
            'minWidth': '120px',
            'textAlign': 'center',
            'verticalAlign': 'middle',
            'height': '74px',  # Match filter height
            'boxSizing': 'border-box',
            'float': 'right'
        }),

    ], style={
        'padding': '20px',
        'backgroundColor': COLORS['dark_bg']
        # 'borderBottom': f'1px solid {COLORS["dark_border"]}'
    }),

    # Map
    html.Div([
        dcc.Graph(
            id='emergency-map',
            style={
                'height': '500px', 
                'backgroundColor': 
                COLORS['dark_bg'],
                'marginLeft': '20px',
                'marginRight': '20px',
            },
            config={
                'scrollZoom': True,
                'displayModeBar': True,
                'responsive': True,  # Add this
                'doubleClick': 'reset+autosize'
            }
        ),
    ], style={
        'backgroundColor': COLORS['dark_bg'],
        'height': '540px',  # Fixed container height (map + padding)
        'overflow': 'hidden'  # Prevent overflow
        }
    ),

    # Location Search Section
    html.Div([
        # Search input and button
        html.Div([
            dcc.Input(
                id='address-search',
                type='text',
                placeholder='Enter an address here...',
                style={
                    'width': '300px',
                    'padding': '10px',
                    'backgroundColor': '#1a1a1a',
                    'color': COLORS['dark_text'],
                    'border': f'1px solid {COLORS["dark_border"]}',
                    'borderRadius': '4px 0 0 4px',
                    'fontFamily': FONT_FAMILY_REGULAR,
                    'fontSize': '14px'
                }
            ),
            html.Button(
                '🔍',
                id='search-button',
                n_clicks=0,
                style={
                    'padding': '8px 12px',
                    'backgroundColor': '#1a1a1a',
                    'color': 'white',
                    'border': 'none',
                    'cursor': 'pointer',
                    'borderRadius': '0 4px 4px 0',
                    'fontSize': '16px',
                    'marginLeft': '-1px',
                    'height': '38px',               # ADD - matches dropdown height
                    'verticalAlign': 'top'          # ADD - aligns with dropdown
                }
            ),
            html.Div(
                id='search-error-message',
                style={
                    'marginTop': '5px',
                    'color': '#ff4444',
                    'fontSize': '12px',
                    'fontFamily': FONT_FAMILY_REGULAR,
                    'display': 'none'  # Hidden by default
                }
            )
        ], style={'display': 'inline-block', 'verticalAlign': 'top'}),
        
        # Radius buttons
        html.Div([
            html.Button(
                '2 km',
                id='radius-2km',
                n_clicks=0,
                style={
                    'padding': '10px 20px',
                    'backgroundColor': '#555',
                    'color': 'white',
                    'border': 'none',
                    'cursor': 'pointer',
                    'marginLeft': '10px',
                    'borderRadius': '4px',
                    'fontFamily': FONT_FAMILY_REGULAR,
                    'fontSize': '14px'
                }
            ),
            html.Button(
                '5 km',
                id='radius-5km',
                n_clicks=0,
                style={
                    'padding': '10px 20px',
                    'backgroundColor': '#555',
                    'color': 'white',
                    'border': 'none',
                    'cursor': 'pointer',
                    'marginLeft': '15px',
                    'borderRadius': '4px',
                    'fontFamily': FONT_FAMILY_REGULAR,
                    'fontSize': '14px'
                }
            ),
            html.Button(
                '10 km',
                id='radius-10km',
                n_clicks=0,
                style={
                    'padding': '10px 20px',
                    'backgroundColor': '#555',
                    'color': 'white',
                    'border': 'none',
                    'cursor': 'pointer',
                    'marginLeft': '10px',
                    'borderRadius': '4px',
                    'fontFamily': FONT_FAMILY_REGULAR,
                    'fontSize': '14px'
                }
            )
        ], id='radius-buttons-container', style={'display': 'inline-block', 'marginLeft': '15px'}),
        
    ], style={
        'padding': '20px',
        'paddingTop': '0',
        'backgroundColor': COLORS['dark_bg']
    }),

    # Hidden divs to store search data
    html.Div(id='user-location-store', style={'display': 'none'}),
    html.Div(id='selected-radius-store', style={'display': 'none'}, children='10'),

    # Data table
    html.Div([
        html.H3(
            'Site Details',
            style={
                'fontFamily': FONT_FAMILY,
                'fontWeight': 'bold',
                'paddingTop': '10px',
                'color': COLORS['lycanroc'],
                'marginBottom': '15px'
            }
        ),
        dash_table.DataTable(
            id='sites-table',
            columns=[
                {'name': 'Site Name', 'id': 'site_name'},
                {'name': 'City', 'id': 'city'},
                {'name': 'Contact Phone', 'id': 'phone'},
                {'name': 'Max Capacity', 'id': 'max_capacity'},
                {'name': 'Event Type', 'id': 'event_type'},
            ],
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
                    'color': COLORS['lycanroc']
                },
                {
                    'if': {'state': 'active'},
                    'backgroundColor': '#0a2540',
                    'border': f'1px solid {COLORS["blue"]}'
                }
            ],
            page_size=15
        )
    ], style={
        'padding': '20px',
        'backgroundColor': COLORS['dark_bg']
    }),


    # Adding footer with a link back to main website
    html.Div([
        html.A(
            'C/O VANISLE_KAHUNA',
            href='https://vanislekahuna.github.io/',
            target='_self',  # Opens in same tab
            style={
                'color': COLORS['lycanroc'],
                'fontFamily': FONT_FAMILY_REGULAR,
                # 'fontSize': '12px',
                'textDecoration': 'none',
                'fontWeight': 'normal'
            }
        )
    ], style={
        'padding': '20px',
        'paddingTop': '10px',
        'backgroundColor': COLORS['dark_bg'],
        'textAlign': 'left'
    }),

    # Hidden div to store data
    html.Div(id='emergency-data-store', style={'display': 'none'}),
    html.Div(id='sites-data-store', style={'display': 'none'})
], 
style={
    'backgroundColor': COLORS['dark_bg'],
    'minHeight': '100vh',
    'fontFamily': FONT_FAMILY_REGULAR
})


# ============================================================================
# CALLBACKS
# ============================================================================

# Refresh Data button callback
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


# Slicers affecting one another callback
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


# Filter affecting map and table callback
@app.callback(
    [Output('emergency-map', 'figure'),
     Output('sites-table', 'data')],
    [Input('city-filter', 'value'),
     Input('event-type-filter', 'value'),
     Input('event-name-filter', 'value'),
     Input('affected-toggle', 'value'),
     Input('sites-data-store', 'children'),
     Input('emergency-data-store', 'children'),
     Input('user-location-store', 'children'),  # NEW
     Input('selected-radius-store', 'children')]  # NEW
)

def update_map_and_table(city_filter, event_type_filter, event_name_filter,
                        affected_toggle, sites_json, poly_json, user_location_json, selected_radius):
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

    # Parse user location
    user_lat, user_lon = None, None
    if user_location_json:
        try:
            location_data = json.loads(user_location_json)
            user_lat = location_data['lat']
            user_lon = location_data['lon']
        except:
            pass
    
    # Apply radius filter if location exists
    if user_lat and user_lon:
        radius_km = float(selected_radius) if selected_radius else 10
        
        # Calculate distances
        filtered_sites['distance_km'] = filtered_sites.apply(
            lambda row: haversine_distance(user_lat, user_lon, row['lat'], row['lon']),
            axis=1
        )
        
        # Filter by radius
        filtered_sites = filtered_sites[filtered_sites['distance_km'] <= radius_km]

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
    for idx, row in poly_data.iterrows():
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
                      showlegend=False
                  )
                )

    # Add radius circle if user location exists
    if user_lat and user_lon:
        radius_km = float(selected_radius) if selected_radius else 10
        
        # Create circle points (approximate)
        import numpy as np
        circle_lats = []
        circle_lons = []
        
        for angle in np.linspace(0, 360, 100):
            # Approximate circle (not perfect for large radii, but good enough)
            angle_rad = np.radians(angle)
            dx = radius_km / 111.32  # 1 degree latitude ≈ 111.32 km
            dy = radius_km / (111.32 * np.cos(np.radians(user_lat)))
            
            circle_lat = user_lat + dx * np.cos(angle_rad)
            circle_lon = user_lon + dy * np.sin(angle_rad)
            
            circle_lats.append(circle_lat)
            circle_lons.append(circle_lon)
        
        # Add circle
        fig.add_trace(go.Scattermapbox(
            lon=circle_lons,
            lat=circle_lats,
            mode='lines',
            fill='toself',
            fillcolor='rgba(0, 174, 255, 0.1)',
            line=dict(color=COLORS['blue'], width=2),
            name=f'{radius_km} km radius',
            hoverinfo='text',
            hovertext=f'{radius_km} km radius from your location',
            showlegend=False
        ))
        
        # Add user location pin
        fig.add_trace(go.Scattermapbox(
            lon=[user_lon],
            lat=[user_lat],
            mode='markers',
            marker=dict(
                size=15,
                color=COLORS['blue'],
                opacity=0.8
                # symbol='marker'  # Pin shape
            ),
            name='Your Location',
            hoverinfo='text',
            hovertext='<b>Your Location</b>',
            showlegend=True
        ))

    # Separate affected and unaffected sites (use filtered_sites instead)
    affected_sites = filtered_sites[filtered_sites['event_type'].notna()]
    unaffected_sites = filtered_sites[filtered_sites['event_type'].isna()]

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
                marker=dict(size=8, color=COLORS['darkgreen'], opacity=0.8), # Line border didn't work: , line=dict(color='black', width=2)
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

    # Priority 1: User searched an address - zoom to that location
    if user_lat and user_lon:
        center_lat = user_lat
        center_lon = user_lon
        zoom_level = 11  # Close zoom for user location
    
    # Priority 2: All filters at default - show BC overview
    elif is_default_view:
        # Reset view - use your default coordinates
        center_lat = 49.17486136570926
        center_lon = -123.15151571413801
        zoom_level = 8

    # Priority 3: Filters applied - auto-zoom to filtered sites
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

    # Priority 4: No sites match filters - default view
    else:
        center_lat = 49.17486136570926
        center_lon = -123.15151571413801
        zoom_level = 8

    # Brand new update layout with dark mode
    fig.update_layout(
        mapbox=dict(
            style='open-street-map',
            center=dict(lat=center_lat, lon=center_lon),
            zoom=zoom_level
        ),
        uirevision='constant',  # Add this line - forces stable state
        autosize=True,
        dragmode='zoom',
        modebar_add=['pan2d', 'zoom2d', 'zoomIn2d', 'zoomOut2d', 'resetScale2d'],
        showlegend=False,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor='rgba(0, 6, 14, 0.9)',  # Dark background
            bordercolor=COLORS['dark_border'],
            borderwidth=1,
            font=dict(
                color=COLORS['dark_text'],
                size=10,
                family=FONT_FAMILY_REGULAR
            )
        ),
        margin=dict(l=0, r=0, t=40, b=0),
        height=800,
        hovermode='closest',
        paper_bgcolor=COLORS['dark_bg'],
        plot_bgcolor=COLORS['dark_bg']
    )

    # Configure scroll zoom behavior
    fig.update_mapboxes(bearing=0, pitch=0)

    # Prepare table data
    table_data = filtered_sites[['site_name', 'city', 'max_capacity', 'event_type']].fillna('').to_dict('records') # Removed 'phone', 

    return fig, table_data


# Reset Filters Callback
@app.callback(
    [Output('city-filter', 'value'),
     Output('event-type-filter', 'value'),
     Output('event-name-filter', 'value'),
     Output('affected-toggle', 'value'),
     Output('address-search', 'value')],  # NEW - clear search box
    Input('reset-button', 'n_clicks'),
    prevent_initial_call=True
)
def reset_filters(n_clicks):
    """Reset all filters to default values"""
    return 'all', 'all', 'all', [], ''


# Update metric cards callback
@app.callback(
    [Output('total-sites-number', 'children'),
     Output('total-spaces-number', 'children')],
    [Input('city-filter', 'value'),
     Input('event-type-filter', 'value'),
     Input('event-name-filter', 'value'),
     Input('affected-toggle', 'value'),
     Input('sites-data-store', 'children'),
     Input('emergency-data-store', 'children')]
)
def update_metric_cards(city_filter, event_type_filter, event_name_filter,
                       affected_toggle, sites_json, poly_json):
    """Update the metric cards based on filters"""
    
    # Load data (same logic as update_map_and_table)
    if sites_json and poly_json:
        import json
        sites_data = pd.read_json(sites_json)
    else:
        sites_data = sites_with_events.copy()
    
    # Apply filters (same logic as update_map_and_table)
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
    
    # Calculate metrics
    total_sites = len(filtered_sites)
    total_spaces = int(filtered_sites['max_capacity'].sum())
    
    # Format with commas
    total_sites_formatted = f"{total_sites:,}"
    total_spaces_formatted = f"{total_spaces:,}"
    
    return total_sites_formatted, total_spaces_formatted


###############################
### NEW Search bar callback ###
###############################
@app.callback(
    [Output('user-location-store', 'children'),
     Output('address-search', 'style'),        # ADD - for red border
     Output('search-error-message', 'children'),  # ADD - error text
     Output('search-error-message', 'style')],    # ADD - show/hide error
    [Input('search-button', 'n_clicks'),
     Input('reset-button', 'n_clicks')],
    [State('address-search', 'value')],
    prevent_initial_call=True
)
def handle_location_search(search_clicks, reset_clicks, address):
    """Handle address search with error feedback"""
    from dash import callback_context
    import json
    
    # Default styles
    default_input_style = {
        'width': '300px',
        'padding': '10px',
        'backgroundColor': '#1a1a1a',
        'color': COLORS['dark_text'],
        'border': f'1px solid {COLORS["dark_border"]}',
        'borderRadius': '4px 0 0 4px',
        'fontFamily': FONT_FAMILY_REGULAR,
        'fontSize': '14px'
    }
    
    error_input_style = default_input_style.copy()
    error_input_style['border'] = '2px solid #ff4444'  # Red border
    
    hidden_error_style = {
        'marginTop': '5px',
        'color': '#ff4444',
        'fontSize': '12px',
        'fontFamily': FONT_FAMILY_REGULAR,
        'display': 'none'
    }
    
    visible_error_style = hidden_error_style.copy()
    visible_error_style['display'] = 'block'
    
    if not callback_context.triggered:
        return None, default_input_style, '', hidden_error_style
    
    button_id = callback_context.triggered[0]['prop_id'].split('.')[0]
    
    # Reset button clicked
    if button_id == 'reset-button':
        return None, default_input_style, '', hidden_error_style
    
    # Search button clicked
    if button_id == 'search-button':
        if not address or address.strip() == '':
            # Empty search
            error_msg = '⚠️ Please enter an address to search.'
            return None, error_input_style, error_msg, visible_error_style
        
        from utils import geocode_address
        lat, lon = geocode_address(address)
        
        if lat and lon:
            # Success!
            location_data = json.dumps({'lat': lat, 'lon': lon})
            return location_data, default_input_style, '', hidden_error_style
        else:
            # Geocoding failed - generate helpful suggestion
            error_msg = generate_search_suggestion(address)
            return None, error_input_style, error_msg, visible_error_style
    
    return None, default_input_style, '', hidden_error_style

###############################
### OLD Search bar callback ###
###############################
# @app.callback(
#     [Output('user-location-store', 'children'),
#      Output('radius-buttons-container', 'style')]
#     [Input('search-button', 'n_clicks'),
#      Input('reset-button', 'n_clicks')],
#     [State('address-search', 'value')],
#     prevent_initial_call=True
# )
# def handle_location_search(search_clicks, reset_clicks, address):
#     """Handle address search and show/hide radius buttons"""
#     from dash import callback_context
    
#     # Check which button was clicked
#     if not callback_context.triggered:
#         return None
    
#     button_id = callback_context.triggered[0]['prop_id'].split('.')[0]
    
#     # Reset button clicked
#     if button_id == 'reset-button':
#         return None
    
#     # Search button clicked
#     if button_id == 'search-button' and address:
#         from utils import geocode_address
#         lat, lon = geocode_address(address)
        
#         if lat and lon:
#             # Store location as JSON
#             import json
#             location_data = json.dumps({'lat': lat, 'lon': lon})
#             # Show radius buttons
#             return location_data, {'display': 'inline-block', 'marginLeft': '15px'}
#         else:
#             print(f"Address not found: {address}")
#             return None
    
#     return None #, {'display': 'none'}
###############################
###############################
###############################


# Search radius selection for search bar
@app.callback(
    [Output('selected-radius-store', 'children'),
     Output('radius-2km', 'style'),
     Output('radius-5km', 'style'),
     Output('radius-10km', 'style')],
    [Input('radius-2km', 'n_clicks'),
     Input('radius-5km', 'n_clicks'),
     Input('radius-10km', 'n_clicks'),
     Input('reset-button', 'n_clicks')],
    prevent_initial_call=True
)
def update_selected_radius(clicks_2, clicks_5, clicks_10, reset_clicks):
    """Update selected radius and button styles"""
    from dash import callback_context
    
    if not callback_context.triggered:
        return '10', *[base_style]*3
    
    button_id = callback_context.triggered[0]['prop_id'].split('.')[0]
    
    # Base style for buttons
    base_style = {
        'padding': '10px 20px',
        'backgroundColor': '#555',
        'color': 'white',
        'border': 'none',
        'cursor': 'pointer',
        'marginLeft': '10px',
        'borderRadius': '4px',
        'fontFamily': FONT_FAMILY_REGULAR,
        'fontSize': '14px'
    }
    
    # Active style
    active_style = base_style.copy()
    active_style['backgroundColor'] = COLORS['blue']
    
    # Reset clicked
    if button_id == 'reset-button':
        return '10', base_style, base_style, base_style
    
    # Radius buttons clicked
    if button_id == 'radius-2km':
        return '2', active_style, base_style, base_style
    elif button_id == 'radius-5km':
        return '5', base_style, active_style, base_style
    elif button_id == 'radius-10km':
        return '10', base_style, base_style, active_style

    
    return '10', base_style, base_style, active_style


@app.callback(
    [Output('address-search', 'style', allow_duplicate=True),
     Output('search-error-message', 'style', allow_duplicate=True)],
    Input('address-search', 'value'),
    prevent_initial_call=True
)
def clear_error_on_typing(value):
    """Clear error styling when user starts typing"""
    default_style = {
        'width': '300px',
        'padding': '10px',
        'backgroundColor': '#1a1a1a',
        'color': COLORS['dark_text'],
        'border': f'1px solid {COLORS["dark_border"]}',
        'borderRadius': '4px 0 0 4px',
        'fontFamily': FONT_FAMILY_REGULAR,
        'fontSize': '14px'
    }
    
    hidden_error_style = {
        'marginTop': '5px',
        'color': '#ff4444',
        'fontSize': '12px',
        'fontFamily': FONT_FAMILY_REGULAR,
        'display': 'none'
    }
    
    return default_style, hidden_error_style


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
