from app import create_app, db
import sqlite3
from pathlib import Path

app = create_app()

# Path to the SQLite database file
db_path = Path("medlife.db")

def check_table_schema(table_name):
    """Check the schema of a specific table"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    print(f"Current schema for {table_name}:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    conn.close()
    return columns

def update_allergies_table():
    """Update the allergies table to match the model"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if the table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='allergy'")
    if not cursor.fetchone():
        print("Allergy table doesn't exist. It will be created when the app starts.")
        conn.close()
        return
    
    # Check if the drug_name column exists
    cursor.execute("PRAGMA table_info(allergy)")
    columns = [col[1] for col in cursor.fetchall()]
    
    # If drug_name doesn't exist, add it
    if 'drug_name' not in columns:
        print("Adding drug_name column to allergy table...")
        try:
            cursor.execute("ALTER TABLE allergy ADD COLUMN drug_name VARCHAR(100) NOT NULL DEFAULT 'Unknown'")
            conn.commit()
            print("Column added successfully.")
        except sqlite3.Error as e:
            print(f"Error adding column: {e}")
            
    # If reaction doesn't exist, add it
    if 'reaction' not in columns:
        print("Adding reaction column to allergy table...")
        try:
            cursor.execute("ALTER TABLE allergy ADD COLUMN reaction VARCHAR(200)")
            conn.commit()
            print("Column added successfully.")
        except sqlite3.Error as e:
            print(f"Error adding column: {e}")
    
    conn.close()

def update_search_history_table():
    """Update the search_history table to use search_query column instead of query"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if the table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='search_history'")
    if not cursor.fetchone():
        print("Search history table doesn't exist. It will be created when the app starts.")
        conn.close()
        return
    
    # Check existing columns
    cursor.execute("PRAGMA table_info(search_history)")
    columns = [col[1] for col in cursor.fetchall()]
    
    # If old 'query' column exists but 'search_query' doesn't
    if 'query' in columns and 'search_query' not in columns:
        print("Migrating search_history table from 'query' to 'search_query'...")
        try:
            # SQLite doesn't support direct column renames, so we need to recreate the table
            # 1. Create a new temporary table with the new schema
            cursor.execute("CREATE TABLE search_history_new (id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, search_query VARCHAR(200) NOT NULL, timestamp DATETIME, FOREIGN KEY(user_id) REFERENCES user(id))")
            
            # 2. Copy data from old table to new table
            cursor.execute("INSERT INTO search_history_new (id, user_id, search_query, timestamp) SELECT id, user_id, query, timestamp FROM search_history")
            
            # 3. Drop the old table
            cursor.execute("DROP TABLE search_history")
            
            # 4. Rename the new table to the original name
            cursor.execute("ALTER TABLE search_history_new RENAME TO search_history")
            
            conn.commit()
            print("Search history table updated successfully.")
        except sqlite3.Error as e:
            print(f"Error updating search_history table: {e}")
            conn.rollback()
    conn.close()

if __name__ == "__main__":
    print("Checking database schema...")
    check_table_schema("allergy")
    check_table_schema("search_history")
    
    print("\nUpdating tables to match models...")
    update_allergies_table()
    update_search_history_table()  # Add the new function call
    
    print("\nAfter update:")
    check_table_schema("allergy")
    check_table_schema("search_history")
    
    print("\nRecreating all tables that don't exist...")
    with app.app_context():
        db.create_all()
        print("Database schema updated.")
