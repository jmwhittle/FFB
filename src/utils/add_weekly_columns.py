"""
Add missing columns to NFLWeeklyStats table for nfl_data_py compatibility.
"""

import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from sqlalchemy import text
from config.database import get_session_local

def add_missing_columns():
    """Add missing columns to nfl_weekly_stats table."""
    SessionLocal = get_session_local()
    session = SessionLocal()
    
    try:
        print("Adding missing columns to nfl_weekly_stats table...")
        
        # Add new columns
        migration_sql = """
        -- Add missing player info columns
        ALTER TABLE nfl_weekly_stats 
        ADD COLUMN IF NOT EXISTS headshot_url VARCHAR,
        ADD COLUMN IF NOT EXISTS recent_team VARCHAR;
        
        -- Update team column name to recent_team if it exists
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name = 'nfl_weekly_stats' AND column_name = 'team') THEN
                ALTER TABLE nfl_weekly_stats RENAME COLUMN team TO recent_team_old;
            END IF;
        END $$;
        
        -- Add missing advanced stats columns
        ALTER TABLE nfl_weekly_stats 
        ADD COLUMN IF NOT EXISTS pacr FLOAT,
        ADD COLUMN IF NOT EXISTS racr FLOAT,
        ADD COLUMN IF NOT EXISTS dakota FLOAT;
        """
        
        session.execute(text(migration_sql))
        session.commit()
        
        print("✅ Successfully added missing columns!")
        
        # Verify columns exist
        columns_query = """
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'nfl_weekly_stats' 
        ORDER BY column_name;
        """
        
        result = session.execute(text(columns_query)).fetchall()
        print(f"\nCurrent table has {len(result)} columns:")
        for col_name, data_type in result:
            print(f"  {col_name}: {data_type}")
            
    except Exception as e:
        session.rollback()
        print(f"❌ Error adding columns: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    add_missing_columns()
