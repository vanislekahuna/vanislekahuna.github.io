
# BC Emergency Management Dashboard

A real-time interactive dashboard for monitoring emergency events and evacuation sites across British Columbia. Built with Python Dash, this tool helps emergency managers and the public visualize active emergency orders/alerts and identify affected evacuation sites.

![Dashboard Status](https://img.shields.io/badge/status-active-success)
![Python](https://img.shields.io/badge/python-3.11-blue)
![License](https://img.shields.io/badge/license-MIT-green)


View the product at: [vanislekahuna-github-io.onrender.com](https://vanislekahuna-github-io.onrender.com/)

## Features

- **Real-Time Emergency Data**: Fetches live evacuation orders and alerts from BC Emergency Management
- **Interactive Map**: OpenStreetMap-based visualization with zoom, pan, and hover interactions
- **Smart Filtering**: Filter sites by city, event type, event name, or affected status
- **Dynamic Metrics**: Real-time cards showing total sites and capacity
- **Spatial Analysis**: Point-in-polygon detection to identify sites within emergency boundaries
- **Responsive Design**: Dark mode interface optimized for desktop and mobile
- **Auto-Zoom**: Map automatically centers on filtered results


## Tech Stack

- **Backend**: Python 3.11, Dash 3.3.0
- **Geospatial**: GeoPandas, Shapely
- **Visualization**: Plotly, Dash DataTable
- **Data Sources**: 
  - BC Emergency Management API (real-time)
  - GitHub-hosted site data (CSV)
- **Deployment**: Render (eu-central-1)


## Quick Start

### Prerequisites
- Python 3.11+
- pip
- Git Bash

### Installation

```bash
# Clone the repository
git clone https://github.com/vanislekahuna/vanislekahuna.github.io.git
cd vanislekahuna.github.io/projects/bc_emergency_mgmt_map

# Install dependencies
pip install -r requirements.txt

# Run the app
python src/app.py
```

Open your browser to `http://localhost:8050`


## Project Structure

```
bc_emergency_mgmt_map/
│
├── src/
│   ├── app.py              # Main Dash application
│   └── utils.py            # Helper functions (API calls, spatial analysis)
│
├── requirements.txt        # Python dependencies
├── runtime.txt            # Python version for deployment
├── render.yaml            # Render deployment configuration
└── README.md              # This file
```

### Key Files

**`src/app.py`**
- Defines dashboard layout (header, filters, map, table, footer)
- Contains all Dash callbacks for interactivity
- Manages color schemes and styling
- Handles data flow between components

**`src/utils.py`**
- `bc_alerts_api()`: Fetches emergency events from BC API
- `retrieve_site_data()`: Loads evacuation site data from CSV
- `check_sites_in_emergencies()`: Performs spatial join to identify affected sites

--

## Architecture Overview

### Data Flow

```
1. Initial Load:
   bc_alerts_api() → Emergency polygons (GeoDataFrame)
   retrieve_site_data() → Site coordinates (DataFrame)
   check_sites_in_emergencies() → Merge data (spatial join)

2. User Interaction:
   Filter change → Callback triggered
   → Filter data
   → Update map (polygons + markers)
   → Update table (filtered rows)
   → Update metric cards (counts/sums)

3. Map Rendering:
   Filtered sites → Calculate bounding box
   → Determine center/zoom
   → Add polygons (emergency boundaries)
   → Add markers (affected/unaffected sites)
   → Return Plotly figure
```

### Callback Architecture

The app uses Dash callbacks to create interactivity. Key callbacks:

1. **`refresh_emergency_data`**: Fetches fresh API data on button click
2. **`update_filter_options`**: Dynamically updates filter dropdowns based on city selection
3. **`update_map_and_table`**: Main callback that filters data and updates map + table
4. **`update_metric_cards`**: Calculates and displays total sites/capacity
5. **`reset_filters`**: Clears all filters to default state


## Customization Guide

### Adding a New Filter

**Example: Add a "School District" filter**

1. **Update Layout** (`app.py`):
```python
html.Div([
    html.Label('Filter by School District:', style={'fontWeight': 'bold', ...}),
    dcc.Dropdown(
        id='district-filter',
        options=[{'label': 'All School Districts', 'value': 'all'}] + 
                [{'label': r, 'value': r} for r in sorted(sites_df['school_districts'].unique())],
        value='all',
        clearable=False,
        style={'width': '200px'}
    )
], style={'display': 'inline-block', 'margin-right': '20px'})
```

2. **Add to Callback Inputs** (`update_map_and_table`):
```python
@app.callback(
    [Output('emergency-map', 'figure'), Output('sites-table', 'data')],
    [Input('city-filter', 'value'),
     Input('district-filter', 'value'),  # ADD THIS
     # ... other inputs
    ]
)
def update_map_and_table(city_filter, district_filter, ...):  # ADD PARAMETER
    # Apply filter
    if district_filter != 'all':
        filtered_sites = filtered_sites[filtered_sites['school_districts'] == district_filter]
```

3. **Update Reset Callback**:
```python
@app.callback(
    [Output('city-filter', 'value'),
     Output('district-filter', 'value'),  # ADD THIS
     # ...
    ],
    Input('reset-button', 'n_clicks')
)
def reset_filters(n_clicks):
    return 'all', 'all', ...  # Add 'all' for new filter
```


### Adding a New Metric Card

**Example: Add "Affected Sites" card**

1. **Add Card Component** (in Controls Row):
```python
html.Div([
    html.Div(id='affected-sites-number', style={
        'fontSize': '36px',
        'fontWeight': 'bold',
        'color': COLORS['green'],
        'fontFamily': FONT_FAMILY
    }),
    html.Div('Affected Sites', style={
        'fontSize': '12px',
        'color': COLORS['green'],
        'fontFamily': FONT_FAMILY_REGULAR
    })
], style={
    'display': 'inline-block',
    'padding': '12px 20px',
    'backgroundColor': '#1a1a2e',
    'border': f'2px solid {COLORS["dark_text_secondary"]}',
    'borderRadius': '4px',
    'marginLeft': '20px',
    'minWidth': '120px',
    'textAlign': 'center'
})
```

2. **Update Metric Cards Callback**:
```python
@app.callback(
    [Output('total-sites-number', 'children'),
     Output('total-spaces-number', 'children'),
     Output('affected-sites-number', 'children')],  # ADD THIS
    [Input('city-filter', 'value'), ...]
)
def update_metric_cards(...):
    # Calculate metric
    affected_count = len(filtered_sites[filtered_sites['event_type'].notna()])
    affected_formatted = f"{affected_count:,}"
    
    return total_sites_formatted, total_spaces_formatted, affected_formatted
```


### Adding a New Table Column

**Example: Add "Distance to Event" column**

1. **Calculate the Value** (in data processing):
```python
# In utils.py or app.py processing logic
filtered_sites['distance_to_event'] = filtered_sites.apply(
    lambda row: calculate_distance(row) if pd.notna(row['event_type']) else '',
    axis=1
)
```

2. **Add Column to Table** (`app.py` layout):
```python
dash_table.DataTable(
    id='sites-table',
    columns=[
        {'name': 'Site Name', 'id': 'site_name'},
        {'name': 'City', 'id': 'city'},
        {'name': 'Contact Phone', 'id': 'phone'},
        {'name': 'Max Capacity', 'id': 'max_capacity'},
        {'name': 'Event Type', 'id': 'event_type'},
        {'name': 'Distance (km)', 'id': 'distance_to_event'},  # ADD THIS
    ],
    # ... rest of config
)
```

3. **Include in Table Data** (`update_map_and_table`):
```python
table_columns = ['site_name', 'city', 'phone', 'max_capacity', 'event_type', 'distance_to_event']
table_data = filtered_sites[table_columns].fillna('').to_dict('records')
```


### Changing Color Scheme

**Location:** `app.py` (top of file, after imports)

```python
COLORS = {
    'dark_bg': '#00060e',              # Main background
    'dark_text': '#e4e4e4',            # Primary text
    'dark_text_secondary': '#f5d5b5',  # Secondary text (cards, links)
    'dark_border': '#333',             # Borders
    'dark_header': '#00ff2b',          # Main header text
    'blue': '#00aeff',                 # Accent (hover, active states)
    'green': '#00FF41',                # Success/metrics
    'darkgreen': '#36ba01',            # Buttons
}
```

**To change colors:**
1. Update hex codes in `COLORS` dictionary
2. Changes apply globally across all components
3. For event-specific colors, update `EVENT_COLORS` and `EVENT_LINE_COLORS`:

```python
EVENT_LINE_COLORS = {
    'Fire': 'rgba(255, 80, 80, 0.4)',
    'Flood': 'rgba(80, 150, 255, 0.4)',
    'Landslide': 'rgba(200, 120, 60, 0.4)',
}

EVENT_COLORS = {
    'Alert': 'rgb(246, 200, 176)',
    'Order': 'rgb(251, 159, 157)',
}
```


### Changing Map Style

**Location:** `update_map_and_table` callback in `app.py`

```python
fig.update_layout(
    mapbox=dict(
        style='open-street-map',  # CHANGE THIS
        center=dict(lat=center_lat, lon=center_lon),
        zoom=zoom_level
    ),
    # ...
)
```

**Available Styles:**
- `'open-street-map'` - Default, detailed street view
- `'carto-darkmatter'` - Dark theme (good for dark mode)
- `'carto-positron'` - Light theme
- `'stamen-terrain'` - Topographic
- `'stamen-toner'` - High contrast B&W

**For custom Mapbox styles:**
1. Get free API key from [mapbox.com](https://mapbox.com)
2. Use: `style='mapbox://styles/mapbox/dark-v10'`
3. Add: `accesstoken='YOUR_MAPBOX_TOKEN'`


### Changing Fonts

**Location:** `app.py` (after COLORS definition)

```python
FONT_FAMILY = "'Helvetica Neue Bold', 'Helvetica Neue', Helvetica, Arial, sans-serif"  # Headers
FONT_FAMILY_REGULAR = "'Helvetica Neue', Helvetica, Arial, sans-serif"  # Body text
```

**To change:**
1. Replace font names with your preferred fonts
2. Ensure fonts are web-safe or include web font imports in `app.index_string`
3. Headers use `FONT_FAMILY` (bold)
4. Regular text uses `FONT_FAMILY_REGULAR`

**Example - Using Google Fonts:**
```python
# Add to app.index_string <head> section:
<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">

# Update font variables:
FONT_FAMILY = "'Roboto', sans-serif"
FONT_FAMILY_REGULAR = "'Roboto', sans-serif"
```


### Understanding Callbacks

Dash callbacks create interactivity by linking inputs (user actions) to outputs (component updates).

**Basic Structure:**
```python
@app.callback(
    Output('component-id', 'property'),  # What to update
    Input('trigger-id', 'property')      # What triggers the update
)
def callback_function(input_value):
    # Process input
    result = do_something(input_value)
    # Return value updates the output
    return result
```

**Multiple Inputs/Outputs:**
```python
@app.callback(
    [Output('map', 'figure'), Output('table', 'data')],  # Update 2 things
    [Input('filter1', 'value'), Input('filter2', 'value')]  # Triggered by 2 inputs
)
def update_both(filter1_val, filter2_val):
    # Process both inputs
    fig = create_figure(filter1_val, filter2_val)
    table = create_table(filter1_val, filter2_val)
    return fig, table  # Must match number of Outputs
```

**State (access without triggering):**
```python
@app.callback(
    Output('result', 'children'),
    Input('submit-button', 'n_clicks'),
    State('input-box', 'value')  # Read value but don't trigger on change
)
def submit_form(n_clicks, input_value):
    # Only triggered by button click, but can read input value
    return f"You submitted: {input_value}"
```

**Callback Chain in This App:**

```
User clicks filter
    ↓
update_map_and_table triggered
    ↓
Filters data → Creates figure + table
    ↓
update_metric_cards triggered (by same input)
    ↓
Calculates metrics
    ↓
Both callbacks return → UI updates
```


## Data Sources

### BC Emergency API
- **Endpoint**: `https://services6.arcgis.com/ubm4tcTYICKBpist/ArcGIS/rest/services/Evacuation_Orders_and_Alerts/FeatureServer/0/query`
- **Format**: GeoJSON
- **Refresh**: On-demand (Refresh button) or page reload
- **Fields Used**: 
  - `EVENT_NAME`: Name of emergency event
  - `EVENT_TYPE`: Fire, Flood, Landslide, etc.
  - `ORDER_ALERT_STATUS`: Order or Alert
  - `geometry`: Polygon boundaries
  - `event_id`, `issuing_agency`, `date_modified`, etc.

### Site Data
- **Source**: `https://raw.githubusercontent.com/vanislekahuna/bc-cc-maps/refs/heads/main/data/synth_data.csv`
- **Format**: CSV
- **Fields Used**:
  - `facility_name` → `site_name`
  - `latitude` → `lat`
  - `longitude` → `lon`
  - `total_spaces` → `max_capacity`
  - `city`, `phone`

**To update site data:**
1. Edit CSV in GitHub repository
2. Push changes
3. Dashboard automatically uses updated data on next load


## Deployment

### Deploy to Render

1. **Push code to GitHub** (if not already)

2. **Sign up at [render.com](https://render.com)** and connect GitHub

3. **Create New Web Service:**
   - Repository: `vanislekahuna/vanislekahuna.github.io`
   - Branch: `master`
   - Root Directory: `projects/bc_emergency_mgmt_map`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python src/app.py`

4. **Configure:**
   - Region: `eu-central-1` (AWS European data centre in Frankfurt, Germany)
   - Instance Type: Free

5. **Deploy** - Takes 5-10 minutes

6. **Access** at your Render URL

### Auto-Deploy
Every `git push origin master` command automatically triggers redeployment (~5 min)


## Common Issues

### Map Not Loading
- **Cause**: Network issue or API timeout
- **Fix**: Check browser console for errors, refresh page

### Filters Not Working
- **Cause**: Data type mismatch or missing values
- **Fix**: Check that filter columns exist in data, ensure proper data types

### Slow Performance
- **Cause**: Too many polygons/sites rendering
- **Fix**: Consider implementing pagination or reducing polygon complexity

### Deployment Fails on Render
- **Cause**: Missing dependencies or wrong Python version
- **Fix**: Verify `requirements.txt` and `runtime.txt` are correct


## Future Enhancements

- [ ] Address search with radius filtering
- [ ] Email/SMS alerts for new events
- [ ] Mobile app version
- [ ] Multi-language support
- [ ] Accessibility improvements (WCAG compliance)
- [ ] Export map as PDF/image
- [ ] Admin panel for site management


## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


## Acknowledgments

- BC Emergency Management for providing open data
- OpenStreetMap contributors for map tiles
- Plotly/Dash community for excellent documentation
- All emergency responders and volunteers keeping BC safe


## License

This project is licensed under the [MIT License](https://mit-license.org/).

```
Copyright (c) 2025 Ruiz Rivera
```


## Contact

**Project Maintainer**: Ruiz Rivera  
**Website**: [vanislekahuna.github.io](https://vanislekahuna.github.io)  
**Dashboard**: [vanislekahuna-github-io.onrender.com](https://vanislekahuna-github-io.onrender.com/)

---

*Built with ❤️ for British Columbia*
```