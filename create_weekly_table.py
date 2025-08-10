"""
Create NFLWeeklyStats table in the database.
"""

from config.database import get_engine, Base
from src.models import NFLWeeklyStats

def create_weekly_stats_table():
    """Create the NFLWeeklyStats table."""
    engine = get_engine()
    
    print("Creating NFLWeeklyStats table...")
    
    # Create the table
    NFLWeeklyStats.__table__.create(engine, checkfirst=True)
    
    print("NFLWeeklyStats table created successfully!")
    
    # Verify table exists
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    if 'nfl_weekly_stats' in tables:
        print("✓ Table 'nfl_weekly_stats' confirmed in database")
        
        # Show table columns
        columns = inspector.get_columns('nfl_weekly_stats')
        print(f"✓ Table has {len(columns)} columns")
        print("Sample columns:", [col['name'] for col in columns[:10]])
    else:
        print("✗ Table not found in database")

if __name__ == "__main__":
    create_weekly_stats_table()
