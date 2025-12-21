import requests
import numpy as np
import pandas as pd
import geopandas as gpd
# import plotly.graph_objects as go

# from dash import Dash, dcc, html, Input, Output, State, dash_table
# from datetime import datetime, timedelta
from shapely.geometry import shape, Point, Polygon
# from zoneinfo import ZoneInfo



<<<<<<< HEAD

=======
>>>>>>> 05a612ff867b612a7e92a4f61b7b0051891e20d1
def bc_alerts_api():
    """Retrieves the data from fake the B.C. Emergency Orders and Alerts API"""

    alerts_api = "https://services6.arcgis.com/ubm4tcTYICKBpist/ArcGIS/rest/services/Evacuation_Orders_and_Alerts/FeatureServer/0/query?where=1%3D1&objectIds=&time=&geometry=&geometryType=esriGeometryEnvelope&inSR=&spatialRel=esriSpatialRelIntersects&resultType=none&distance=0.0&units=esriSRUnit_Meter&returnGeodetic=false&outFields=*&returnGeometry=true&returnCentroid=false&featureEncoding=esriDefault&multipatchOption=xyFootprint&maxAllowableOffset=&geometryPrecision=&outSR=&datumTransformation=&applyVCSProjection=false&returnIdsOnly=false&returnUniqueIdsOnly=false&returnCountOnly=false&returnExtentOnly=false&returnQueryGeometry=false&returnDistinctValues=false&cacheHint=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&having=&resultOffset=&resultRecordCount=0&returnZ=false&returnM=false&returnExceededLimitFeatures=true&quantizationParameters=&sqlFormat=none&f=pgeojson&token="

    try:
        print("Now calling the B.C. Emergency Orders and Alerts API...")

        # Call the API
        response = requests.get(alerts_api)
        print(f"API response code: {response.status_code}")

        if response.status_code != 200:
            print(f"ERROR: API returned status code {response.status_code}")
            return gpd.GeoDataFrame()

        # Parse JSON response
        js = response.json()

        # Check if we have features
        if 'features' not in js or len(js['features']) == 0:
            print("WARNING: GeoDataFrame is empty - no emergency events found")
            return gpd.GeoDataFrame()

        print(f"Successfully retrieved {len(js['features'])} emergency events\n")

        # Extract data from features
        event_data = []
        for feature in js["features"]:
            props = feature["properties"]

            # Get geometry
            geom = shape(feature["geometry"])

            if geom.geom_type == "MultiPolygon":
                print(f"Event: {props.get('EVENT_NAME', 'Unknown')} | ID: {feature.get('id', 'N/A')} | Type: {geom.geom_type}")

                for geom_part in geom.geoms:
                  event_data.append({
                    'event_id': feature.get('id'),
                    'event_name': props.get('EVENT_NAME'),
                    'event_type': props.get('EVENT_TYPE'),
                    'order_alert_status': props.get('ORDER_ALERT_STATUS'),
                    'issuing_agency': props.get('ISSUING_AGENCY'),
                    'preoc_code': props.get('PREOC_CODE'),
                    'order_alert_name': props.get('ORDER_ALERT_NAME'),
                    'event_number': props.get('EVENT_NUMBER'),
                    'date_modified': props.get('DATE_MODIFIED'),
                    'feature_area_sqm': props.get('FEATURE_AREA_SQM'),
                    'feature_length_m': props.get('FEATURE_LENGTH_M'),
                    'geometry': geom_part  # Corrected from 'geometry': geom
                  })

            # Check if this is a Polygon with multiple rings (coordinate arrays)
            elif geom.geom_type == 'Polygon' and len(geom.exterior.coords) > 0:
                # Get all coordinate rings from the geometry
                coords = feature["geometry"]["coordinates"]
                num_parts = len(coords)

                print(f"Event: {props.get('EVENT_NAME', 'Unknown')} | ID: {feature.get('id', 'N/A')} | Parts: {num_parts}")

                # Create a separate entry for each coordinate ring
                for part_num, ring_coords in enumerate(coords, start=1):
                    polygon_geom = Polygon(ring_coords)

                    event_data.append({
                        'event_id': feature.get('id'),
                        'event_name': props.get('EVENT_NAME'),
                        'event_type': props.get('EVENT_TYPE'),
                        'order_alert_status': props.get('ORDER_ALERT_STATUS'),
                        'issuing_agency': props.get('ISSUING_AGENCY'),
                        'preoc_code': props.get('PREOC_CODE'),
                        'order_alert_name': props.get('ORDER_ALERT_NAME'),
                        'event_number': props.get('EVENT_NUMBER'),
                        'date_modified': props.get('DATE_MODIFIED'),
                        'feature_area_sqm': props.get('FEATURE_AREA_SQM'),
                        'feature_length_m': props.get('FEATURE_LENGTH_M'),
                        'geometry': polygon_geom,
                        'part_num': part_num,
                        'total_parts': num_parts
                    })

            else:
                # Single polygon or other geometry type
                print(f"Event: {props.get('EVENT_NAME', 'Unknown')} | ID: {feature.get('id', 'N/A')} | Type: {geom.geom_type}")

                event_data.append({
                    'event_id': feature.get('id'),
                    'event_name': props.get('EVENT_NAME'),
                    'event_type': props.get('EVENT_TYPE'),
                    'order_alert_status': props.get('ORDER_ALERT_STATUS'),
                    'issuing_agency': props.get('ISSUING_AGENCY'),
                    'preoc_code': props.get('PREOC_CODE'),
                    'order_alert_name': props.get('ORDER_ALERT_NAME'),
                    'event_number': props.get('EVENT_NUMBER'),
                    'date_modified': props.get('DATE_MODIFIED'),
                    'feature_area_sqm': props.get('FEATURE_AREA_SQM'),
                    'feature_length_m': props.get('FEATURE_LENGTH_M'),
                    'geometry': geom,
                    'part_num': 1,
                    'total_parts': 1
                })


        # Create GeoDataFrame
        gdf = gpd.GeoDataFrame(event_data, crs='EPSG:4326')

        print(f"\nSuccessfully created GeoDataFrame with {len(gdf)} emergency events")
        return gdf

    except requests.exceptions.RequestException as e:
        print(f"ERROR: Failed to fetch data from API - {str(e)}")
        return gpd.GeoDataFrame()

    except Exception as e:
        print(f"ERROR: An unexpected error occurred - {str(e)}")
        return gpd.GeoDataFrame()


def retrieve_site_data():
    """Retrieve the geocoordinates of our sites assets"""

    synth_link = "https://raw.githubusercontent.com/vanislekahuna/bc-cc-maps/refs/heads/main/data/synth_data.csv"
    col_renames = {
        "facility_name": "site_name",
        "latitude": "lat",
        "longitude": "lon",
        "total_spaces": "max_capacity"
    }
    sites = pd.read_csv(synth_link)
    sites = sites.rename(columns=col_renames)

    # Convert lat/lon to float, replacing invalid values with NaN
    sites['lat'] = pd.to_numeric(sites['lat'], errors='coerce')
    sites['lon'] = pd.to_numeric(sites['lon'], errors='coerce')

    # Count rows with invalid coordinates before dropping
    invalid_coords = sites[sites['lat'].isna() | sites['lon'].isna()]
    if len(invalid_coords) > 0:
        print(f"WARNING: Dropped {len(invalid_coords)} sites with invalid coordinates")

    # Drop rows with invalid coordinates
    sites = sites.dropna(subset=['lat', 'lon'])

    print(f"Successfully loaded {len(sites)} sites with valid coordinates")

    return sites


def check_sites_in_emergencies(sites_df, poly_geodf):
    """Check which sites fall within emergency polygons"""


    sites_gdf = gpd.GeoDataFrame(
        sites_df,
        geometry=gpd.points_from_xy(sites_df.lon, sites_df.lat),
        crs='EPSG:4326'
    )

    sites_in_emergency = gpd.sjoin(
        sites_gdf,
        poly_geodf[['event_name', 'event_type', 'geometry']],
        how='left',
        predicate='within'
    )

    sites_in_emergency = sites_in_emergency.drop(columns=['geometry', 'index_right'], errors='ignore')

    return sites_in_emergency