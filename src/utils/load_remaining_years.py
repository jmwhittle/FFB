"""
Load remaining NFL weekly stats from 2009 to 2023.
"""

import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

import nfl_data_py as nfl
from sqlalchemy import text
from src.models import NFLWeeklyStats
from config.database import get_session_local
import pandas as pd

def load_remaining_years():
    """Load remaining years 2009-2023."""
    SessionLocal = get_session_local()
    session = SessionLocal()
    
    try:
        # Check what years we already have
        existing_years = session.execute(text("""
            SELECT DISTINCT season FROM nfl_weekly_stats ORDER BY season
        """)).fetchall()
        
        existing_years_set = {row[0] for row in existing_years}
        print(f"Existing years: {sorted(existing_years_set)}")
        
        # Years we need to load
        target_years = list(range(2009, 2024))  # 2009-2023
        missing_years = [year for year in target_years if year not in existing_years_set]
        
        print(f"Missing years to load: {missing_years}")
        
        if not missing_years:
            print("✅ All years already loaded!")
            return
        
        # Load in smaller chunks (5 years at a time)
        chunk_size = 5
        for i in range(0, len(missing_years), chunk_size):
            chunk_years = missing_years[i:i+chunk_size]
            print(f"\nLoading years: {chunk_years}")
            
            # Load data for this chunk
            weekly_data = nfl.import_weekly_data(years=chunk_years)
            print(f"Retrieved {len(weekly_data)} records for {chunk_years}")
            
            # Clean data
            weekly_data = weekly_data.fillna(0)
            
            # Convert to records
            records = weekly_data.to_dict('records')
            
            # Insert in smaller batches
            batch_size = 500  # Smaller batches for stability
            total_batches = (len(records) + batch_size - 1) // batch_size
            
            print(f"Inserting {len(records)} records in {total_batches} batches...")
            
            for j in range(0, len(records), batch_size):
                batch = records[j:j+batch_size]
                batch_num = (j // batch_size) + 1
                
                try:
                    # Create objects and insert
                    stats_objects = [NFLWeeklyStats(**record) for record in batch]
                    session.bulk_save_objects(stats_objects)
                    session.commit()
                    
                    print(f"  Batch {batch_num}/{total_batches} completed")
                    
                except Exception as e:
                    session.rollback()
                    print(f"  Error in batch {batch_num}: {e}")
                    # Continue with next batch
                    continue
            
            print(f"✅ Completed loading {chunk_years}")
        
        # Final verification
        final_years = session.execute(text("""
            SELECT season, COUNT(*) as record_count 
            FROM nfl_weekly_stats 
            GROUP BY season 
            ORDER BY season
        """)).fetchall()
        
        print(f"\n📊 Final Database Summary:")
        total_records = 0
        for year, count in final_years:
            print(f"  {year}: {count} records")
            total_records += count
        
        print(f"\nTotal records: {total_records}")
        print(f"Years covered: {len(final_years)} years")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    load_remaining_years()
