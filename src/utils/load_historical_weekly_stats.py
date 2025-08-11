"""
Load historical NFL weekly stats from 1999 to current year.
This will significantly expand the database with 26+ years of data.
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

import nfl_data_py as nfl
from sqlalchemy import text
from src.models import NFLWeeklyStats
from config.database import get_session_local
import pandas as pd

def load_historical_weekly_stats(start_year=1999, end_year=2024):
    """
    Load NFL weekly stats for all years from start_year to end_year.
    
    Args:
        start_year (int): Starting year (default 1999)
        end_year (int): Ending year (default 2024)
    """
    SessionLocal = get_session_local()
    
    try:
        print(f"Loading NFL weekly stats from {start_year} to {end_year}...")
        
        # Create year range
        years = list(range(start_year, end_year + 1))
        print(f"Years to process: {len(years)} years")
        
        # Load data for all years at once (nfl_data_py can handle multiple years efficiently)
        print("Fetching data from nfl_data_py API...")
        weekly_data = nfl.import_weekly_data(years=years)
        
        print(f"Retrieved {len(weekly_data)} records total")
        print(f"Years in dataset: {sorted(weekly_data['season'].unique())}")
        
        # Clean and prepare data
        print("Cleaning and preparing data...")
        
        # Handle missing values
        weekly_data = weekly_data.fillna(0)
        
        # Convert object columns to appropriate types
        for col in weekly_data.columns:
            if weekly_data[col].dtype == 'object':
                try:
                    weekly_data[col] = pd.to_numeric(weekly_data[col], errors='ignore')
                except:
                    pass
        
        # Convert DataFrame to list of dictionaries for bulk insert
        records = weekly_data.to_dict('records')
        
        # Insert data in batches
        session = SessionLocal()
        try:
            batch_size = 1000
            total_batches = (len(records) + batch_size - 1) // batch_size
            
            print(f"Inserting data in {total_batches} batches of {batch_size} records each...")
            
            for i in range(0, len(records), batch_size):
                batch = records[i:i+batch_size]
                batch_num = (i // batch_size) + 1
                
                print(f"Processing batch {batch_num}/{total_batches} ({len(batch)} records)...")
                
                # Create NFLWeeklyStats objects
                stats_objects = []
                for record in batch:
                    stats_obj = NFLWeeklyStats(**record)
                    stats_objects.append(stats_obj)
                
                # Bulk insert
                session.bulk_save_objects(stats_objects)
                session.commit()
                
                print(f"Batch {batch_num} completed successfully")
            
            print(f"✅ Successfully loaded {len(records)} historical weekly stats records!")
            
            # Verify the data
            total_count = session.query(NFLWeeklyStats).count()
            year_counts = session.execute(text("""
                SELECT season, COUNT(*) as record_count 
                FROM nfl_weekly_stats 
                GROUP BY season 
                ORDER BY season
            """)).fetchall()
            
            print(f"\n📊 Database Summary:")
            print(f"Total records in nfl_weekly_stats: {total_count}")
            print(f"\nRecords by year:")
            for year, count in year_counts:
                print(f"  {year}: {count} records")
                
        except Exception as e:
            session.rollback()
            print(f"❌ Error during database insertion: {e}")
            raise
        finally:
            session.close()
            
    except Exception as e:
        print(f"❌ Error loading historical data: {e}")
        raise

def main():
    """Main function to load historical data."""
    print("🏈 NFL Historical Weekly Stats Loader")
    print("=====================================")
    
    # Load from 1999 to 2024 (26 years of data)
    load_historical_weekly_stats(start_year=1999, end_year=2024)
    
    print("\n🎉 Historical data loading complete!")
    print("Your database now contains comprehensive NFL weekly statistics from 1999-2024")

if __name__ == "__main__":
    main()
