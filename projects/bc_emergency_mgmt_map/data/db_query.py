import sqlite3
import pandas as pd
import os
from pathlib import Path

# db_name = "bc_assets.db"
# conn = sqlite3.connect(db_name)
# cursor = conn.cursor()
# cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
# tables = cursor.fetchall()

# print(tables)

def is_read_only_query(query):
    """Check if the query is read-only (SELECT or PRAGMA)."""
    # Remove comments and normalize
    query_upper = query.strip().upper()
    
    # Remove SQL comments
    lines = [line.split('--')[0] for line in query_upper.split('\n')]
    query_clean = ' '.join(lines).strip()
    
    # Check for write operations
    write_keywords = ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER', 'CREATE', 
                      'REPLACE', 'TRUNCATE', 'ATTACH', 'DETACH']
    
    for keyword in write_keywords:
        if keyword in query_clean:
            return False
    
    # Allow SELECT and PRAGMA
    if query_clean.startswith('SELECT') or query_clean.startswith('PRAGMA'):
        return True
    
    return False

def get_multiline_query():
    """Get multi-line SQL query from user. Executes when `;` is followed by Enter."""
    print("\nEnter your SQL query (type `;` and press Enter to execute):")
    query_lines = []
    
    while True:
        line = input()
        query_lines.append(line)
        
        # Check if line ends with semicolon
        if line.rstrip().endswith(';'):
            break
    
    return '\n'.join(query_lines)

def execute_query(conn, query):
    """Execute the query and return results as a pandas DataFrame."""
    try:
        df = pd.read_sql_query(query, conn)
        return df, None
    except Exception as e:
        return None, str(e)

def save_results(df, db_name):
    """Save results to Downloads folder as CSV."""
    downloads_path = Path.home() / "Downloads"
    
    # Create a filename based on timestamp
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"query_results_{timestamp}.csv"
    filepath = downloads_path / filename
    
    try:
        df.to_csv(filepath, index=False)
        print(f"\n✓ Results saved to: {filepath}")
        return True
    except Exception as e:
        print(f"\n✗ Error saving file: {e}")
        return False

def main():
    print("="*60)
    print("SQLite Read-Only Query Tool")
    print("="*60)
    
    # Get database path
    db_path = input("\nEnter the database filename or path: ").strip()
    
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"\n✗ Error: Database file '{db_path}' does not exist.")
        return
    
    # Connect to database
    try:
        conn = sqlite3.connect(db_path)
        print(f"✓ Connected to database: {db_path}")
    except sqlite3.Error as e:
        print(f"\n✗ Error connecting to database: {e}")
        return
    
    # Query loop
    while True:
        print("\n" + "-"*60)
        print("⚠️  READ-ONLY MODE: Only SELECT and PRAGMA queries allowed")
        print("-"*60)
        
        # Get query
        query = get_multiline_query()
        
        # Validate read-only
        if not is_read_only_query(query):
            print("\n✗ ERROR: Write operations are not allowed.")
            print("Script terminated for safety.")
            conn.close()
            return
        
        # Execute query
        print("\nExecuting query...")
        df, error = execute_query(conn, query)
        
        if error:
            print(f"\n✗ Query error: {error}")
        else:
            # Display results
            print("\n" + "="*60)
            print("QUERY RESULTS:")
            print("="*60)
            
            if df.empty:
                print("(No results)")
            else:
                print(df.to_string(index=False))
                print(f"\nRows returned: {len(df)}")
            
            # Prompt to save results
            if not df.empty:
                save_choice = input("\nDo you want to save these results to your Downloads folder? (yes/no): ").strip().lower()
                if save_choice in ['yes', 'y']:
                    save_results(df, os.path.basename(db_path))
        
        # Prompt to continue
        print("\n" + "="*60)
        continue_choice = input("Do you want to run another query? (yes/no): ").strip().lower()
        
        if continue_choice not in ['yes', 'y']:
            print("\nClosing connection. Goodbye!")
            break
    
    conn.close()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nScript interrupted by user. Exiting...")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")