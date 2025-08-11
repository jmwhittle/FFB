"""
Create the NFL contract information table.
"""

import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from sqlalchemy import text
from src.models import NFLContractInfo
from config.database import get_engine, Base

def create_contract_table():
    """Create the NFL contract information table."""
    try:
        print("Creating NFL contract information table...")
        
        # Get engine and create table
        engine = get_engine()
        
        # Create the table
        NFLContractInfo.__table__.create(engine, checkfirst=True)
        
        print("✅ Successfully created nfl_contract_info table!")
        
        # Verify table creation
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'nfl_contract_info' 
                ORDER BY ordinal_position;
            """))
            
            columns = result.fetchall()
            print(f"\nTable created with {len(columns)} columns:")
            for col_name, data_type, nullable in columns:
                print(f"  {col_name}: {data_type} {'(nullable)' if nullable == 'YES' else '(not null)'}")
        
    except Exception as e:
        print(f"❌ Error creating contract table: {e}")
        raise

if __name__ == "__main__":
    create_contract_table()
