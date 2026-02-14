"""
SQLite Data Ingestion Tool
--------------------------
Robust, interactive tool to ingest CSV datasets into SQLite with validation and logging.
"""

import requests
import sqlite3
import pandas as pd
import logging
import re
from pathlib import Path
from datetime import datetime
from typing import Tuple, Dict, Optional, List
from urllib.parse import urlparse


# ============================================================================
# CONFIGURATION & LOGGING
# ============================================================================

# Create logs directory if it doesn't exist
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Configure logging
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = LOG_DIR / f"ingest_{timestamp}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()  # Also print to console
    ]
)
logger = logging.getLogger(__name__)

# Constants
MAX_FILE_SIZE_GB = 3
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_GB * 1024 * 1024 * 1024
NETWORK_TIMEOUT = 30  # seconds
MAX_URL_RETRIES = 3

# BC Boundaries for validation
BC_LAT_MIN, BC_LAT_MAX = 48.0, 60.0
BC_LON_MIN, BC_LON_MAX = -139.0, -114.0
MAX_REASONABLE_CAPACITY = 10000


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def clean_column_name(col_name: str) -> str:
    """
    Clean column names for SQLite compatibility.
    
    Rules:
    - Convert to lowercase
    - Replace spaces with underscores
    - Remove special characters (keep only alphanumeric and underscore)
    - Remove leading/trailing underscores
    
    Args:
        col_name: Original column name
        
    Returns:
        Cleaned column name
    """
    # Convert to lowercase
    cleaned = col_name.lower()
    
    # Replace spaces and hyphens with underscores
    cleaned = cleaned.replace(' ', '_').replace('-', '_')
    
    # Remove special characters (keep alphanumeric and underscore)
    cleaned = re.sub(r'[^a-z0-9_]', '', cleaned)
    
    # Remove leading/trailing underscores and collapse multiple underscores
    cleaned = re.sub(r'_+', '_', cleaned).strip('_')
    
    # Ensure doesn't start with number (SQLite requirement)
    if cleaned and cleaned[0].isdigit():
        cleaned = 'col_' + cleaned
    
    return cleaned


def validate_bc_coordinates(df: pd.DataFrame) -> Dict[str, any]:
    """
    Validate that lat/lon coordinates fall within BC boundaries.
    
    Args:
        df: DataFrame with potential 'lat'/'latitude' and 'lon'/'longitude' columns
        
    Returns:
        Dictionary with validation results including problematic row indices
    """
    # Find latitude column
    lat_cols = [col for col in df.columns if col.lower() in ['lat', 'latitude']]
    lon_cols = [col for col in df.columns if col.lower() in ['lon', 'long', 'longitude']]
    
    if not lat_cols or not lon_cols:
        return {'has_coords': False}
    
    lat_col = lat_cols[0]
    lon_col = lon_cols[0]
    
    # Convert to numeric
    lat_numeric = pd.to_numeric(df[lat_col], errors='coerce')
    lon_numeric = pd.to_numeric(df[lon_col], errors='coerce')
    
    # Identify problem types
    null_coords = df[lat_numeric.isna() | lon_numeric.isna()].index.tolist()
    
    # Check bounds (only for valid numeric values)
    valid_lat = (lat_numeric >= BC_LAT_MIN) & (lat_numeric <= BC_LAT_MAX)
    valid_lon = (lon_numeric >= BC_LON_MIN) & (lon_numeric <= BC_LON_MAX)
    outside_bc = df[~(valid_lat & valid_lon) & lat_numeric.notna() & lon_numeric.notna()].index.tolist()
    
    total_coords = (lat_numeric.notna() & lon_numeric.notna()).sum()
    total_problems = len(null_coords) + len(outside_bc)
    
    return {
        'has_coords': True,
        'lat_col': lat_col,
        'lon_col': lon_col,
        'total_rows': len(df),
        'total_with_coords': int(total_coords),
        'null_coords': null_coords,
        'outside_bc': outside_bc,
        'total_problems': total_problems,
        'valid_percentage': (int(total_coords) - len(outside_bc)) / int(total_coords) * 100 if total_coords > 0 else 0
    }


def validate_capacity(df: pd.DataFrame) -> Dict[str, any]:
    """
    Validate capacity values are reasonable.
    
    Args:
        df: DataFrame with potential capacity column
        
    Returns:
        Dictionary with validation results
    """
    # Find capacity column
    capacity_cols = [col for col in df.columns if 'capacity' in col.lower() or 'spaces' in col.lower()]
    
    if not capacity_cols:
        return {'has_capacity': False}
    
    capacity_col = capacity_cols[0]
    
    # Convert to numeric
    capacity_numeric = pd.to_numeric(df[capacity_col], errors='coerce')
    
    # Check reasonable bounds
    unreasonable = (capacity_numeric > MAX_REASONABLE_CAPACITY) | (capacity_numeric < 0)
    unreasonable_count = (unreasonable & capacity_numeric.notna()).sum()
    total_capacity = capacity_numeric.notna().sum()
    
    return {
        'has_capacity': True,
        'capacity_col': capacity_col,
        'total_with_capacity': int(total_capacity),
        'unreasonable_count': int(unreasonable_count),
        'max_capacity': int(capacity_numeric.max()) if total_capacity > 0 else 0,
        'min_capacity': int(capacity_numeric.min()) if total_capacity > 0 else 0
    }


def identify_missing_name_address(df: pd.DataFrame) -> List[int]:
    """
    Identify rows where BOTH name AND address are null.
    
    Args:
        df: DataFrame to check
        
    Returns:
        List of row indices with both name and address null
    """
    # Find name columns (flexible matching)
    name_cols = [col for col in df.columns if any(keyword in col.lower() 
                 for keyword in ['name', 'facility', 'school', 'site'])]
    
    # Find address columns
    address_cols = [col for col in df.columns if any(keyword in col.lower() 
                   for keyword in ['address', 'street', 'location'])]
    
    if not name_cols or not address_cols:
        logger.warning("Could not identify name or address columns for validation")
        return []
    
    name_col = name_cols[0]
    address_col = address_cols[0]
    
    # Find rows where BOTH are null
    both_null = df[(df[name_col].isna() | (df[name_col] == '')) & 
                   (df[address_col].isna() | (df[address_col] == ''))].index.tolist()
    
    return both_null


def map_dtype_to_sqlite(dtype) -> str:
    """Map Pandas dtype to SQLite data type."""
    dtype_str = str(dtype)
    
    if 'int' in dtype_str:
        return 'INTEGER'
    elif 'float' in dtype_str:
        return 'REAL'
    elif dtype_str == 'bool':
        return 'INTEGER'
    elif 'datetime' in dtype_str:
        return 'TEXT'
    else:
        return 'TEXT'


# ============================================================================
# CORE FUNCTIONS
# ============================================================================

def fetch_csv_from_url(url: str, retries: int = MAX_URL_RETRIES) -> pd.DataFrame:
    """
    Fetch CSV from URL with validation and error handling.
    
    Args:
        url: URL to CSV file
        retries: Number of retry attempts
        
    Returns:
        Pandas DataFrame
        
    Raises:
        ValueError: If URL is invalid or file too large
        requests.RequestException: If network error occurs
    """
    logger.info(f"Fetching data from: {url}")
    
    # Validate URL format
    parsed = urlparse(url)
    if not all([parsed.scheme, parsed.netloc]):
        raise ValueError(f"Invalid URL format: {url}")
    
    attempt = 0
    while attempt < retries:
        try:
            # Check file size first (HEAD request)
            logger.info(f"Checking file size... (Attempt {attempt + 1}/{retries})")
            head_response = requests.head(url, timeout=NETWORK_TIMEOUT, allow_redirects=True)
            
            if 'content-length' in head_response.headers:
                file_size = int(head_response.headers['content-length'])
                file_size_gb = file_size / (1024 ** 3)
                
                logger.info(f"File size: {file_size_gb:.2f} GB")
                
                if file_size > MAX_FILE_SIZE_BYTES:
                    raise ValueError(
                        f"File too large: {file_size_gb:.2f} GB. "
                        f"Maximum allowed: {MAX_FILE_SIZE_GB} GB"
                    )
                
                if file_size_gb > 1:
                    print(f"\n⚠️  WARNING: Large file detected ({file_size_gb:.2f} GB)")
                    response = input("Continue? (yes/no): ").strip().lower()
                    if response not in ['yes', 'y']:
                        raise ValueError("Download cancelled by user")
            
            # Fetch CSV
            logger.info("Downloading CSV...")
            df = pd.read_csv(url)
            
            logger.info(f"✓ Successfully loaded {len(df)} rows, {len(df.columns)} columns")
            return df
            
        except requests.Timeout:
            logger.error(f"Network timeout after {NETWORK_TIMEOUT} seconds")
            raise requests.RequestException(f"Network timeout - server took too long to respond")
        
        except requests.RequestException as e:
            attempt += 1
            if attempt < retries:
                logger.warning(f"Network error: {e}. Retrying...")
            else:
                logger.error(f"Failed after {retries} attempts")
                raise
        
        except pd.errors.ParserError as e:
            logger.error(f"CSV parsing error: {e}")
            raise ValueError(f"Malformed CSV file: {e}")


def preview_and_clean_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, str]]:
    """
    Preview data and clean column names.
    
    Args:
        df: Raw DataFrame
        
    Returns:
        Tuple of (cleaned DataFrame, column mapping dict)
    """
    print("\n" + "=" * 80)
    print("PREVIEW: Raw Data (First 5 rows)")
    print("=" * 80)
    print(df.head())
    
    print("\n" + "=" * 80)
    print("PREVIEW: Data Types")
    print("=" * 80)
    print(df.dtypes)
    
    print("\n" + "=" * 80)
    print("PREVIEW: Data Info")
    print("=" * 80)
    print(f"Total rows: {len(df)}")
    print(f"Total columns: {len(df.columns)}")
    print(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    
    # Null counts
    null_counts = df.isnull().sum()
    if null_counts.any():
        print("\nNull value counts:")
        print(null_counts[null_counts > 0])
    
    # Clean column names
    print("\n" + "=" * 80)
    print("COLUMN NAME CLEANING")
    print("=" * 80)
    
    column_mapping = {}
    for original in df.columns:
        cleaned = clean_column_name(original)
        column_mapping[original] = cleaned
        if original != cleaned:
            print(f"  '{original}' → '{cleaned}'")
    
    if not any(orig != clean for orig, clean in column_mapping.items()):
        print("  ✓ All column names are already clean")
    
    # Apply cleaning
    df_cleaned = df.rename(columns=column_mapping)
    logger.info(f"Cleaned {len(column_mapping)} column names")
    
    return df_cleaned, column_mapping


def validate_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Run BC-specific validations on the data and optionally remove problematic rows.
    
    Args:
        df: DataFrame to validate
        
    Returns:
        Cleaned DataFrame (may have fewer rows if user opts to remove problems)
    """
    print("\n" + "=" * 80)
    print("DATA VALIDATION")
    print("=" * 80)
    
    rows_to_remove = set()  # Track all problematic row indices
    
    # ========================================================================
    # AUTO-REMOVAL: Rows with BOTH name AND address null
    # ========================================================================
    missing_both = identify_missing_name_address(df)
    if missing_both:
        print(f"\n⚠️  AUTO-REMOVING: {len(missing_both)} rows with BOTH name AND address missing")
        logger.warning(f"Auto-removing {len(missing_both)} rows with missing name AND address")
        rows_to_remove.update(missing_both)
    
    # ========================================================================
    # Coordinate validation
    # ========================================================================
    coord_results = validate_bc_coordinates(df)
    if coord_results['has_coords']:
        print(f"\n✓ Found coordinate columns: '{coord_results['lat_col']}', '{coord_results['lon_col']}'")
        print(f"  Total rows with coordinates: {coord_results['total_with_coords']}")
        
        # Show problems
        total_problems = coord_results['total_problems']
        if total_problems > 0:
            print(f"\n  ⚠️  COORDINATE PROBLEMS DETECTED: {total_problems} rows")
            print(f"     - {len(coord_results['null_coords'])} with null/invalid coordinates")
            print(f"     - {len(coord_results['outside_bc'])} outside BC boundaries")
            print(f"     BC bounds: Lat [{BC_LAT_MIN}, {BC_LAT_MAX}], Lon [{BC_LON_MIN}, {BC_LON_MAX}]")
            
            # Find name column for display
            name_cols = [col for col in df.columns if any(keyword in col.lower() 
                         for keyword in ['name', 'facility', 'school', 'site'])]
            name_col = name_cols[0] if name_cols else df.columns[0]
            
            # Show problematic facilities
            problem_indices = coord_results['null_coords'] + coord_results['outside_bc']
            
            print(f"\n  Facilities with coordinate problems (showing up to 20):")
            print("  " + "-" * 76)
            for idx in problem_indices[:20]:
                facility_name = df.loc[idx, name_col]
                lat_val = df.loc[idx, coord_results['lat_col']]
                lon_val = df.loc[idx, coord_results['lon_col']]
                
                if pd.isna(lat_val) or pd.isna(lon_val):
                    issue = "NULL coordinates"
                else:
                    issue = f"Outside BC (lat={lat_val}, lon={lon_val})"
                
                print(f"  [{idx}] {facility_name} - {issue}")
            
            if len(problem_indices) > 20:
                print(f"  ... and {len(problem_indices) - 20} more")
            
            # Ask user if they want to remove
            print("\n" + "-" * 80)
            response = input(f"Remove these {total_problems} rows with coordinate problems? (yes/no): ").strip().lower()
            if response in ['yes', 'y']:
                rows_to_remove.update(problem_indices)
                logger.info(f"User opted to remove {total_problems} rows with coordinate problems")
                print(f"  ✓ Will remove {total_problems} rows")
            else:
                logger.info("User opted to keep rows with coordinate problems")
                print(f"  ℹ️  Keeping problematic rows")
        else:
            print(f"  ✓ All coordinates valid!")
    else:
        print("\n  ℹ️  No coordinate columns detected")
    
    # ========================================================================
    # Capacity validation
    # ========================================================================
    capacity_results = validate_capacity(df)
    if capacity_results['has_capacity']:
        print(f"\n✓ Found capacity column: '{capacity_results['capacity_col']}'")
        print(f"  Total rows with capacity: {capacity_results['total_with_capacity']}")
        print(f"  Range: {capacity_results['min_capacity']} - {capacity_results['max_capacity']}")
        
        if capacity_results['unreasonable_count'] > 0:
            print(f"\n  ⚠️  WARNING: {capacity_results['unreasonable_count']} unreasonable capacity values")
            print(f"     (negative or > {MAX_REASONABLE_CAPACITY})")
            
            # Show problematic facilities
            capacity_col = capacity_results['capacity_col']
            capacity_numeric = pd.to_numeric(df[capacity_col], errors='coerce')
            unreasonable = (capacity_numeric > MAX_REASONABLE_CAPACITY) | (capacity_numeric < 0)
            unreasonable_indices = df[unreasonable & capacity_numeric.notna()].index.tolist()
            
            # Find name column
            name_cols = [col for col in df.columns if any(keyword in col.lower() 
                         for keyword in ['name', 'facility', 'school', 'site'])]
            name_col = name_cols[0] if name_cols else df.columns[0]
            
            print(f"\n  Facilities with unreasonable capacity (showing up to 10):")
            print("  " + "-" * 76)
            for idx in unreasonable_indices[:10]:
                facility_name = df.loc[idx, name_col]
                capacity_val = df.loc[idx, capacity_col]
                print(f"  [{idx}] {facility_name} - Capacity: {capacity_val}")
            
            if len(unreasonable_indices) > 10:
                print(f"  ... and {len(unreasonable_indices) - 10} more")
            
            # Ask user if they want to remove
            print("\n" + "-" * 80)
            response = input(f"Remove these {capacity_results['unreasonable_count']} rows with unreasonable capacity? (yes/no): ").strip().lower()
            if response in ['yes', 'y']:
                rows_to_remove.update(unreasonable_indices)
                logger.info(f"User opted to remove {capacity_results['unreasonable_count']} rows with unreasonable capacity")
                print(f"  ✓ Will remove {capacity_results['unreasonable_count']} rows")
            else:
                logger.info("User opted to keep rows with unreasonable capacity")
                print(f"  ℹ️  Keeping problematic rows")
    else:
        print("\n  ℹ️  No capacity column detected")
    
    # ========================================================================
    # Apply removals
    # ========================================================================
    if rows_to_remove:
        original_count = len(df)
        df_cleaned = df.drop(index=list(rows_to_remove)).reset_index(drop=True)
        removed_count = original_count - len(df_cleaned)
        
        print("\n" + "=" * 80)
        print("DATA CLEANING SUMMARY")
        print("=" * 80)
        print(f"Original rows: {original_count}")
        print(f"Removed rows: {removed_count}")
        print(f"Final rows: {len(df_cleaned)}")
        
        logger.info(f"Removed {removed_count} problematic rows from dataset")
        
        return df_cleaned
    else:
        print("\n  ✓ No rows removed")
        return df


def get_type_overrides(df: pd.DataFrame) -> Dict[str, str]:
    """
    Interactively allow user to override data types.
    
    Args:
        df: DataFrame with detected types
        
    Returns:
        Dictionary mapping column names to SQLite types
    """
    print("\n" + "=" * 80)
    print("DATA TYPE REVIEW & OVERRIDES")
    print("=" * 80)
    print("\nDetected types for each column:")
    print("(Press Enter to keep detected type, or enter: TEXT, INTEGER, REAL)")
    print("-" * 80)
    
    overrides = {}
    
    for col_name, dtype in df.dtypes.items():
        sqlite_type = map_dtype_to_sqlite(dtype)
        print(f"\n'{col_name}'")
        print(f"  Pandas type: {dtype}")
        print(f"  SQLite type: {sqlite_type}")
        
        # Show sample values
        sample_vals = df[col_name].dropna().head(3).tolist()
        if sample_vals:
            print(f"  Sample values: {sample_vals}")
        
        override = input(f"  Override? [Enter=keep {sqlite_type}]: ").strip().upper()
        
        if override in ['TEXT', 'INTEGER', 'REAL']:
            overrides[col_name] = override
            logger.info(f"Type override: {col_name} → {override}")
        else:
            overrides[col_name] = sqlite_type
    
    return overrides


def generate_create_table_sql(df: pd.DataFrame, table_name: str, type_overrides: Dict[str, str]) -> str:
    """
    Generate CREATE TABLE SQL with type overrides.
    
    Args:
        df: DataFrame
        table_name: Table name
        type_overrides: Column name to SQLite type mapping
        
    Returns:
        CREATE TABLE SQL statement
    """
    columns = []
    for col_name in df.columns:
        sqlite_type = type_overrides.get(col_name, 'TEXT')
        columns.append(f"    {col_name} {sqlite_type}")
    
    columns_sql = ",\n".join(columns)
    create_sql = f"CREATE TABLE {table_name} (\n{columns_sql}\n);"
    
    return create_sql


def create_and_populate_table(
    df: pd.DataFrame,
    db_path: str,
    table_name: str,
    type_overrides: Dict[str, str]
) -> sqlite3.Connection:
    """
    Create SQLite table and insert data.
    
    Args:
        df: DataFrame to insert
        db_path: Database path
        table_name: Table name
        type_overrides: Type mapping
        
    Returns:
        Database connection
        
    Raises:
        ValueError: If table already exists
    """
    db_file = Path(db_path)
    
    # Check if database exists
    if db_file.exists():
        logger.info(f"Using existing database: {db_path}")
    else:
        logger.info(f"Creating new database: {db_path}")
    
    # Connect
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if table exists
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,)
    )
    
    if cursor.fetchone():
        conn.close()
        raise ValueError(
            f"Table '{table_name}' already exists in '{db_path}'. "
            f"Choose a different name or delete the existing table."
        )
    
    # Generate and execute CREATE TABLE
    create_sql = generate_create_table_sql(df, table_name, type_overrides)
    
    print("\n" + "=" * 80)
    print("CREATE TABLE SQL")
    print("=" * 80)
    print(create_sql)
    
    cursor.execute(create_sql)
    conn.commit()
    logger.info(f"✓ Table '{table_name}' created successfully")
    
    # Insert data
    print("\n" + "=" * 80)
    print("INSERTING DATA")
    print("=" * 80)
    
    df.to_sql(table_name, conn, if_exists='append', index=False)
    
    rows_inserted = len(df)
    logger.info(f"✓ Inserted {rows_inserted} rows")
    print(f"✓ Successfully inserted {rows_inserted} rows")
    
    return conn


def verify_insertion(conn: sqlite3.Connection, table_name: str):
    """
    Verify data was inserted correctly.
    
    Args:
        conn: Database connection
        table_name: Table to verify
    """
    print("\n" + "=" * 80)
    print("VERIFICATION: Database Contents")
    print("=" * 80)
    
    cursor = conn.cursor()
    
    # Row count
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"\nTotal rows in table: {count}")
    
    # First 3 rows
    cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
    rows = cursor.fetchall()
    
    # Get column names
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [col[1] for col in cursor.fetchall()]
    
    print("\nFirst 3 rows:")
    print("-" * 80)
    for row in rows:
        print(dict(zip(columns, row)))
    
    logger.info(f"✓ Verification complete: {count} rows in table '{table_name}'")


# ============================================================================
# MAIN ORCHESTRATION
# ============================================================================

def main():
    """Main execution flow."""
    print("\n" + "=" * 80)
    print("SQLite Data Ingestion Tool")
    print("=" * 80)
    print(f"Log file: {log_file}")
    logger.info("Starting data ingestion process")
    
    try:
        # Step 1: Get URL with retry
        url = None
        for attempt in range(MAX_URL_RETRIES):
            url = input("\nEnter dataset URL: ").strip()
            
            try:
                df = fetch_csv_from_url(url, retries=1)
                break
            except (ValueError, requests.RequestException) as e:
                logger.error(f"URL attempt {attempt + 1} failed: {e}")
                print(f"\n❌ Error: {e}")
                
                if attempt < MAX_URL_RETRIES - 1:
                    print(f"Retries remaining: {MAX_URL_RETRIES - attempt - 1}")
                else:
                    logger.error("Max URL retries exceeded")
                    print("\n❌ Maximum retries exceeded. Exiting.")
                    return
        
        # Step 2: Preview and clean
        df_cleaned, column_mapping = preview_and_clean_data(df)
        
        # Step 3: Validate
        df_cleaned = validate_data(df_cleaned)
        
        # Checkpoint: Continue?
        print("\n" + "=" * 80)
        response = input("\nContinue with this data? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            logger.info("User cancelled after preview")
            print("Operation cancelled.")
            return
        
        # Step 4: Type overrides
        type_overrides = get_type_overrides(df_cleaned)
        
        # Step 5: Get database and table names
        print("\n" + "=" * 80)
        print("DATABASE & TABLE NAMES")
        print("=" * 80)
        
        db_name = input("\nEnter database name (e.g., 'bc_facilities.db'): ").strip()
        if not db_name.endswith('.db'):
            db_name += '.db'
        
        table_name = input("Enter table name (e.g., 'schools'): ").strip()
        table_name = clean_column_name(table_name)  # Clean table name too
        
        logger.info(f"Target: {db_name} / {table_name}")
        
        # Step 6: Create table and insert
        conn = create_and_populate_table(df_cleaned, db_name, table_name, type_overrides)
        
        # Step 7: Verify
        verify_insertion(conn, table_name)
        
        # Cleanup
        conn.close()
        
        # Success summary
        print("\n" + "=" * 80)
        print("✓ SUCCESS")
        print("=" * 80)
        print(f"Database: {db_name}")
        print(f"Table: {table_name}")
        print(f"Rows: {len(df_cleaned)}")
        print(f"Log: {log_file}")
        
        logger.info("Data ingestion completed successfully")
        
    except KeyboardInterrupt:
        logger.info("User interrupted process")
        print("\n\n⚠️  Operation cancelled by user")
    
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        print(f"\n❌ Error: {e}")
    
    except requests.RequestException as e:
        logger.error(f"Network error: {e}")
        print(f"\n❌ Network Error: {e}")
        print("Please check your internet connection and try again.")
    
    except Exception as e:
        logger.exception("Unexpected error occurred")
        print(f"\n❌ Unexpected Error: {e}")
        print(f"See log file for details: {log_file}")


if __name__ == "__main__":
    main()

# # daycare = "https://catalogue.data.gov.bc.ca/dataset/4cc207cc-ff03-44f8-8c5f-415af5224646/resource/9a9f14e1-03ea-4a11-936a-6e77b15eeb39/download/childcare_locations.csv"
# schools = "https://catalogue.data.gov.bc.ca/dataset/95da1091-7e8c-4aa6-9c1b-5ab159ea7b42/resource/5832eff2-3380-435e-911b-5ada41c1d30b/download/bc_k12_schools_2024-10.csv"