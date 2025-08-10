"""
Create NFLSeasonalStats table in the database.
"""

from config.database import get_engine, Base
from src.models import NFLSeasonalStats

def create_seasonal_stats_table():
    """Create the NFLSeasonalStats table."""
    engine = get_engine()
    
    print("Creating NFLSeasonalStats table...")
    
    # Create the table
    NFLSeasonalStats.__table__.create(engine, checkfirst=True)
    
    print("NFLSeasonalStats table created successfully!")
    
    # Verify table exists
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    if 'nfl_seasonal_stats' in tables:
        print("✓ Table 'nfl_seasonal_stats' confirmed in database")
        
        # Show table columns
        columns = inspector.get_columns('nfl_seasonal_stats')
        print(f"✓ Table has {len(columns)} columns")
        print("Sample columns:", [col['name'] for col in columns[:15]])
    else:
        print("✗ Table not found in database")

if __name__ == "__main__":
    create_seasonal_stats_table()
