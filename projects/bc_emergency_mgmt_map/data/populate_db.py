import sqlite3
import os

def infer_data_type(value):
    """Infer SQLite data type from the value."""
    try:
        int(value)
        return "INTEGER"
    except ValueError:
        pass
    
    try:
        float(value)
        return "REAL"
    except ValueError:
        pass
    
    return "TEXT"

def get_tables(cursor):
    """Get list of all tables in the database."""
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    return [table[0] for table in cursor.fetchall()]

def column_exists(cursor, table_name, column_name):
    """Check if a column exists in the table."""
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = [col[1] for col in cursor.fetchall()]
    return column_name in columns

def main():
    # Get database name
    db_name = input("Enter the database filename (i.e 'bc_wildfires.db'): ").strip()
    
    if not os.path.exists(db_name):
        print(f"Warning: Database '{db_name}' does not exist. It will be created.")
        proceed = input("Do you want to continue? (yes/no): ").strip().lower()
        if proceed not in ['yes', 'y']:
            print("Operation cancelled.")
            return
    
    # Connect to database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Get table name with retry logic
    attempts = 0
    max_attempts = 2
    table_name = None
    
    while attempts < max_attempts:
        table_name = input("Enter the table name (i.e. 'schools'): ").strip()
        
        # Check if table exists
        tables = get_tables(cursor)
        
        if not tables:
            print("Error: No tables found in the database.")
            conn.close()
            return
        
        if table_name in tables:
            break
        else:
            print(f"\nError: Table '{table_name}' does not exist.")
            print(f"Available tables in the database: {', '.join(tables)}")
            attempts += 1
            
            if attempts < max_attempts:
                print(f"\nYou have {max_attempts - attempts} more attempt(s).")
            else:
                print("\nMaximum attempts reached. Operation cancelled.")
                conn.close()
                return
    
    # Get column name
    column_name = input("Enter the column name: ").strip()
    
    # Check if column exists
    col_exists = column_exists(cursor, table_name, column_name)
    
    if not col_exists:
        print(f"\n⚠️  WARNING: Column '{column_name}' does not exist in table '{table_name}'.")
        print("A new column will be created if you proceed.")
        
        proceed = input("Do you want to create this new column? (yes/no): ").strip().lower()
        if proceed not in ['yes', 'y']:
            print("Operation cancelled.")
            conn.close()
            return
    
    # Get value to populate
    value = input(f"Enter the value to populate in column '{column_name}': ").strip()
    
    # Infer data type
    data_type = infer_data_type(value)
    
    # Get row count
    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
    row_count = cursor.fetchone()[0]
    
    # Show summary and ask for confirmation
    print("\n" + "="*50)
    print("SUMMARY:")
    print("="*50)
    print(f"Database: {db_name}")
    print(f"Table: {table_name}")
    print(f"Column: {column_name} {'(NEW - will be created)' if not col_exists else '(existing)'}")
    if not col_exists:
        print(f"Data type: {data_type}")
    print(f"Value: {value}")
    print(f"Rows to update: {row_count}")
    print("="*50)
    
    confirm = input("\nProceed with this operation? (yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print("Operation cancelled.")
        conn.close()
        return
    
    try:
        # Create column if it doesn't exist
        if not col_exists:
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {data_type};")
            print(f"✓ Column '{column_name}' created successfully.")
        
        # Update all rows
        cursor.execute(f"UPDATE {table_name} SET {column_name} = ?;", (value,))
        conn.commit()
        
        print(f"✓ Updated {cursor.rowcount} row(s) successfully.")
        print("\nOperation completed successfully!")
        
    except sqlite3.Error as e:
        print(f"\n✗ Error occurred: {e}")
        conn.rollback()
    
    finally:
        conn.close()

if __name__ == "__main__":
    main()