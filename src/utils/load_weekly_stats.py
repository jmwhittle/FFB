"""
Utility script to populate NFL weekly stats data.
"""

import pandas as pd
import nfl_data_py as nfl
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_
from config.database import get_engine
from src.models import NFLWeeklyStats
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create session factory
def get_session():
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()


def load_weekly_stats(seasons=None, force_reload=False):
    """
    Load NFL weekly stats for specified seasons.
    
    Args:
        seasons: List of seasons to load (default: last 10 years)
        force_reload: If True, delete existing data and reload
    """
    if seasons is None:
        current_year = datetime.now().year
        seasons = list(range(current_year - 9, current_year + 1))  # Last 10 years
    
    logger.info(f"Loading weekly stats for seasons: {seasons}")
    
    session = get_session()
    
    try:
        # Check if we should force reload
        if force_reload:
            logger.info("Force reload requested - deleting existing data")
            session.query(NFLWeeklyStats).filter(
                NFLWeeklyStats.season.in_(seasons)
            ).delete(synchronize_session=False)
            session.commit()
        
        for season in seasons:
            logger.info(f"Processing season {season}")
            
            # Check if data already exists for this season
            existing_count = session.query(NFLWeeklyStats).filter(
                NFLWeeklyStats.season == season
            ).count()
            
            if existing_count > 0 and not force_reload:
                logger.info(f"Season {season} already loaded ({existing_count} records), skipping")
                continue
            
            try:
                # Load weekly data from nfl_data_py
                logger.info(f"Downloading weekly data for {season}")
                weekly_data = nfl.import_weekly_data([season])
                
                if weekly_data.empty:
                    logger.warning(f"No data found for season {season}")
                    continue
                
                logger.info(f"Downloaded {len(weekly_data)} rows for season {season}")
                
                # Clean and prepare data
                weekly_data = clean_weekly_data(weekly_data)
                
                # Convert to database records
                records = []
                for _, row in weekly_data.iterrows():
                    record = NFLWeeklyStats(
                        player_id=str(row.get('player_id', '')),
                        season=int(row.get('season', season)),
                        week=int(row.get('week', 0)),
                        player_name=str(row.get('player_name', '')),
                        player_display_name=str(row.get('player_display_name', '')),
                        position=str(row.get('position', '')),
                        position_group=str(row.get('position_group', '')),
                        team=str(row.get('recent_team', row.get('team', ''))),
                        opponent_team=str(row.get('opponent_team', '')),
                        season_type=str(row.get('season_type', 'REG')),
                        
                        # Passing stats
                        completions=safe_float(row.get('completions')),
                        attempts=safe_float(row.get('attempts')),
                        passing_yards=safe_float(row.get('passing_yards')),
                        passing_tds=safe_float(row.get('passing_tds')),
                        interceptions=safe_float(row.get('interceptions')),
                        sacks=safe_float(row.get('sacks')),
                        sack_yards=safe_float(row.get('sack_yards')),
                        sack_fumbles=safe_float(row.get('sack_fumbles')),
                        sack_fumbles_lost=safe_float(row.get('sack_fumbles_lost')),
                        passing_air_yards=safe_float(row.get('passing_air_yards')),
                        passing_yards_after_catch=safe_float(row.get('passing_yards_after_catch')),
                        passing_first_downs=safe_float(row.get('passing_first_downs')),
                        passing_epa=safe_float(row.get('passing_epa')),
                        passing_2pt_conversions=safe_float(row.get('passing_2pt_conversions')),
                        
                        # Rushing stats
                        carries=safe_float(row.get('carries')),
                        rushing_yards=safe_float(row.get('rushing_yards')),
                        rushing_tds=safe_float(row.get('rushing_tds')),
                        rushing_fumbles=safe_float(row.get('rushing_fumbles')),
                        rushing_fumbles_lost=safe_float(row.get('rushing_fumbles_lost')),
                        rushing_first_downs=safe_float(row.get('rushing_first_downs')),
                        rushing_epa=safe_float(row.get('rushing_epa')),
                        rushing_2pt_conversions=safe_float(row.get('rushing_2pt_conversions')),
                        
                        # Receiving stats
                        targets=safe_float(row.get('targets')),
                        receptions=safe_float(row.get('receptions')),
                        receiving_yards=safe_float(row.get('receiving_yards')),
                        receiving_tds=safe_float(row.get('receiving_tds')),
                        receiving_fumbles=safe_float(row.get('receiving_fumbles')),
                        receiving_fumbles_lost=safe_float(row.get('receiving_fumbles_lost')),
                        receiving_air_yards=safe_float(row.get('receiving_air_yards')),
                        receiving_yards_after_catch=safe_float(row.get('receiving_yards_after_catch')),
                        receiving_first_downs=safe_float(row.get('receiving_first_downs')),
                        receiving_epa=safe_float(row.get('receiving_epa')),
                        receiving_2pt_conversions=safe_float(row.get('receiving_2pt_conversions')),
                        
                        # Special teams
                        special_teams_tds=safe_float(row.get('special_teams_tds')),
                        
                        # Fantasy points
                        fantasy_points=safe_float(row.get('fantasy_points')),
                        fantasy_points_ppr=safe_float(row.get('fantasy_points_ppr')),
                        
                        # Target share and advanced metrics
                        target_share=safe_float(row.get('target_share')),
                        air_yards_share=safe_float(row.get('air_yards_share')),
                        wopr=safe_float(row.get('wopr'))
                    )
                    records.append(record)
                
                # Bulk insert records
                if records:
                    logger.info(f"Inserting {len(records)} records for season {season}")
                    session.bulk_save_objects(records)
                    session.commit()
                    logger.info(f"Successfully inserted season {season} data")
                
            except Exception as e:
                logger.error(f"Error processing season {season}: {e}")
                session.rollback()
                continue
        
        logger.info("Weekly stats loading completed")
        
    except Exception as e:
        logger.error(f"Error in load_weekly_stats: {e}")
        session.rollback()
        raise
    finally:
        session.close()


def clean_weekly_data(df):
    """Clean and standardize weekly data."""
    # Handle missing values
    df = df.fillna(0)
    
    # Ensure required columns exist
    required_cols = ['player_id', 'season', 'week']
    for col in required_cols:
        if col not in df.columns:
            df[col] = ''
    
    # Remove rows with missing critical data
    df = df[df['player_id'].notna() & (df['player_id'] != '')]
    df = df[df['season'].notna()]
    df = df[df['week'].notna()]
    
    return df


def safe_float(value):
    """Safely convert value to float, returning None for invalid values."""
    if pd.isna(value) or value == '' or value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def get_weekly_stats_summary():
    """Get summary of loaded weekly stats data."""
    session = get_session()
    
    try:
        # Get total count
        total = session.query(NFLWeeklyStats).count()
        
        # Get count by season
        season_counts = session.query(
            NFLWeeklyStats.season,
            session.query(NFLWeeklyStats).filter(
                NFLWeeklyStats.season == NFLWeeklyStats.season
            ).count().label('count')
        ).group_by(NFLWeeklyStats.season).all()
        
        logger.info(f"Total weekly stats records: {total}")
        for season, count in season_counts:
            logger.info(f"Season {season}: {count} records")
            
        return total, dict(season_counts)
        
    except Exception as e:
        logger.error(f"Error getting summary: {e}")
        return 0, {}
    finally:
        session.close()


if __name__ == "__main__":
    # Load last 10 years of data
    load_weekly_stats()
    
    # Print summary
    get_weekly_stats_summary()
