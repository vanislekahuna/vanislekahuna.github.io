import sqlite3
import pandas as pd
from pathlib import Path

def check_null_columns(df):
    """Check for columns that are entirely NULL and alert the user."""
    null_columns = []
    for column in df.columns:
        if df[column].isna().all():
            null_columns.append(column)
    
    if null_columns:
        print("\n⚠️  WARNING: The following columns are entirely NULL:")
        for col in null_columns:
            print(f"   - {col}")
    
    return null_columns

def combine_schools_daycares(db_path, output_csv=None):
    """
    Combine schools and daycares tables into a single DataFrame.
    
    Parameters:
    -----------
    db_path : str
        Path to the bc_assets.db database
    output_csv : str, optional
        Path to save the CSV file. If None, prompts user.
    
    Returns:
    --------
    pd.DataFrame
        Combined DataFrame with unified column names
    """
    
    # SQL query to union both tables with column renaming
    query = """
    SELECT 
        school_name AS facility_name,
        school_latitude AS lat,
        school_longitude AS lon,
        CAST(district_number AS INTEGER) AS max_capacity,
        TRIM(street_address) || ', ' || TRIM(physical_address_city) || ', BC' AS full_address,
        property_type
    FROM schools
    
    UNION
    
    SELECT 
        facility_name,
        latitude AS lat,
        longitude AS lon,
        CAST(total_spaces AS INTEGER) AS max_capacity,
        TRIM(address) || ', ' || TRIM(city) || ', BC' AS full_address,
        property_type
    FROM daycares;
    """
    
    try:
        # Connect to database
        print(f"Connecting to database: {db_path}")
        conn = sqlite3.connect(db_path)
        
        # Execute query and load into DataFrame
        print("Executing query and combining tables...")
        df = pd.read_sql_query(query, conn)
        
        # Close connection
        conn.close()
        
        print(f"\n✓ Successfully combined tables")
        print(f"  Total rows: {len(df)}")
        print(f"  Total columns: {len(df.columns)}")
        print(f"\nColumns: {', '.join(df.columns.tolist())}")
        
        # Check for entirely NULL columns
        check_null_columns(df)
        
        # Display sample data
        print("\n" + "="*60)
        print("SAMPLE DATA (first 5 rows):")
        print("="*60)
        print(df.head().to_string(index=False))
        
        # Display data info
        print("\n" + "="*60)
        print("DATA SUMMARY:")
        print("="*60)
        print(df.info())
        
        # Prompt to save CSV
        if output_csv is None:
            save_choice = input("\nDo you want to save this data to a CSV file? (yes/no): ").strip().lower()
            
            if save_choice in ['yes', 'y']:
                # Default filename
                default_filename = "combined_facilities.csv"
                filename = input(f"Enter filename (press Enter for '{default_filename}'): ").strip()
                
                if not filename:
                    filename = default_filename
                
                # Add .csv extension if not present
                if not filename.endswith('.csv'):
                    filename += '.csv'
                
                # Save to Downloads folder
                downloads_path = Path.home() / "Downloads"
                output_csv = downloads_path / filename
        
        # Save to CSV if path is provided
        if output_csv:
            df.to_csv(output_csv, index=False)
            print(f"\n✓ Data saved to: {output_csv}")
        
        return df
        
    except sqlite3.Error as e:
        print(f"\n✗ Database error: {e}")
        return None
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return None

def main():
    print("="*60)
    print("Schools & Daycares Data Combiner")
    print("="*60)
    
    # Database path
    db_path = "bc_assets.db"
    
    # Check if database exists
    if not Path(db_path).exists():
        print(f"\n✗ Error: Database file '{db_path}' not found.")
        return
    
    # Combine tables
    df = combine_schools_daycares(db_path)
    
    if df is not None:
        print("\n✓ Operation completed successfully!")
    else:
        print("\n✗ Operation failed.")



if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nScript interrupted by user. Exiting...")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")