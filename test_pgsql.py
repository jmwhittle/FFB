"""
Test script for the PostgreSQL helper utilities.
Demonstrates usage of pg_df() and other helper functions.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.utils.pgsql import pg_df, pg_list_tables, pg_quick_stats, pg_test_connection, pg_template

def main():
    """Test the PostgreSQL helper functions."""
    print("🏈 Testing PostgreSQL Helper Functions")
    print("=" * 50)
    
    # Test connection
    print("1. Testing database connection...")
    if pg_test_connection():
        print("✓ Database connection successful!")
    else:
        print("✗ Database connection failed!")
        return
    
    # List tables
    print("\n2. Listing database tables...")
    try:
        tables_df = pg_list_tables()
        print(f"Found {len(tables_df)} tables:")
        print(tables_df.to_string(index=False))
    except Exception as e:
        print(f"Error listing tables: {e}")
    
    # Test basic query
    print("\n3. Testing basic pg_df() query...")
    try:
        query = "SELECT COUNT(*) as total_players FROM players"
        df = pg_df(query)
        print(f"Total players in database: {df.iloc[0]['total_players']}")
    except Exception as e:
        print(f"Error executing query: {e}")
    
    # Test parameterized query
    print("\n4. Testing parameterized query...")
    try:
        query = """
        SELECT position, COUNT(*) as player_count 
        FROM players 
        WHERE active = :active
        GROUP BY position 
        ORDER BY player_count DESC
        """
        df = pg_df(query, {'active': True})
        print("Active players by position:")
        print(df.to_string(index=False))
    except Exception as e:
        print(f"Error with parameterized query: {e}")
    
    # Test multi-line query
    print("\n5. Testing multi-line query...")
    try:
        query = """
        SELECT 
            team,
            COUNT(*) as player_count,
            COUNT(CASE WHEN position = 'QB' THEN 1 END) as qb_count,
            COUNT(CASE WHEN position = 'RB' THEN 1 END) as rb_count,
            COUNT(CASE WHEN position = 'WR' THEN 1 END) as wr_count
        FROM players 
        WHERE active = true AND team IS NOT NULL
        GROUP BY team 
        ORDER BY player_count DESC
        LIMIT 10
        """
        df = pg_df(query)
        print("Top 10 teams by player count:")
        print(df.to_string(index=False))
    except Exception as e:
        print(f"Error with multi-line query: {e}")
    
    # Test quick stats
    print("\n6. Testing quick stats for players table...")
    try:
        stats = pg_quick_stats('players', limit=3)
        print(f"Table: {stats['table_name']}")
        print(f"Total rows: {stats['total_rows']}")
        print(f"Total columns: {stats['total_columns']}")
        print(f"Columns: {', '.join(stats['columns'][:5])}...")  # Show first 5 columns
        print("Sample data:")
        print(stats['sample_data'][['full_name', 'position', 'team']].to_string(index=False))
    except Exception as e:
        print(f"Error getting quick stats: {e}")
    
    print("\n🎉 PostgreSQL helper testing complete!")
    print("\nExample usage in your notebooks or scripts:")
    print("""
    from src.utils.pgsql import pg_df
    
    # Simple query
    df = pg_df("SELECT * FROM players WHERE position = 'QB' LIMIT 10")
    
    # Multi-line query with parameters
    query = '''
    SELECT 
        p.full_name,
        p.position, 
        p.team,
        p.age
    FROM players p
    WHERE p.position = :pos 
      AND p.active = :active
    ORDER BY p.age DESC
    LIMIT :limit
    '''
    df = pg_df(query, {'pos': 'QB', 'active': True, 'limit': 5})
    """)

if __name__ == "__main__":
    main()
