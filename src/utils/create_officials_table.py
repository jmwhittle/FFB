"""
Create NFLOfficials table in the database.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from config.database import get_engine
from src.models import NFLOfficials

def create_officials_table():
    """Create the NFLOfficials table."""
    try:
        engine = get_engine()
        
        # Create the table
        NFLOfficials.__table__.create(engine, checkfirst=True)
        print("✅ NFLOfficials table created successfully!")
        
        # Show table structure
        print("\n📋 Table structure:")
        print("nfl_officials:")
        for column in NFLOfficials.__table__.columns:
            print(f"  - {column.name}: {column.type}")
            
    except Exception as e:
        print(f"❌ Error creating NFLOfficials table: {e}")
        return False
    
    return True

if __name__ == "__main__":
    create_officials_table()
