"""
Load sample NFL Officials data for demonstration purposes.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from datetime import datetime
from config.database import get_engine
from src.models import NFLOfficials
from sqlalchemy.orm import sessionmaker

def load_sample_officials_data():
    """Load sample officials data for testing and demonstration."""
    
    engine = get_engine()
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    try:
        # Sample officials data for a few games
        sample_officials = [
            # Game 1: 2024 Week 1 - KC vs BAL
            {
                'game_id': '2024_01_KC_BAL',
                'official_id': 'REF_001',
                'season': 2024,
                'week': 1,
                'game_date': '2024-09-05',
                'home_team': 'BAL',
                'away_team': 'KC',
                'official_name': 'Carl Cheffers',
                'position': 'Referee',
                'jersey_number': '51',
                'years_experience': 25,
                'total_penalties_called': 12,
                'penalty_yards_assessed': 95,
                'flags_thrown': 14,
                'flags_picked_up': 2,
                'holding_penalties': 3,
                'false_start_penalties': 2,
                'pass_interference_penalties': 1,
                'roughing_penalties': 0,
                'unsportsmanlike_conduct': 1,
                'delay_of_game': 2,
                'offensive_penalties': 7,
                'defensive_penalties': 5,
                'total_penalty_yards_home': 45,
                'total_penalty_yards_away': 50,
                'penalties_affecting_touchdowns': 1,
                'penalties_affecting_turnovers': 0,
                'challenges_total': 2,
                'challenges_overturned': 1,
                'automatic_reviews': 3,
                'reviews_overturned': 0,
                'crew_id': 'CREW_51',
                'is_head_referee': True,
                'is_playoff_eligible': True,
                'game_control_rating': 8.5,
                'consistency_rating': 9.0,
                'accuracy_rating': 8.8,
                'career_games_officiated': 487,
                'career_playoff_games': 23,
                'career_super_bowls': 2,
                'officiating_notes': 'Strong game control, consistent with penalty calls',
                'controversial_calls': None,
                'data_source': 'NFL Official Stats',
                'data_quality': 'High'
            },
            {
                'game_id': '2024_01_KC_BAL',
                'official_id': 'UMP_001',
                'season': 2024,
                'week': 1,
                'game_date': '2024-09-05',
                'home_team': 'BAL',
                'away_team': 'KC',
                'official_name': 'Roy Ellison',
                'position': 'Umpire',
                'jersey_number': '81',
                'years_experience': 18,
                'total_penalties_called': 4,
                'penalty_yards_assessed': 30,
                'flags_thrown': 5,
                'flags_picked_up': 1,
                'holding_penalties': 2,
                'false_start_penalties': 1,
                'pass_interference_penalties': 0,
                'roughing_penalties': 0,
                'unsportsmanlike_conduct': 0,
                'delay_of_game': 1,
                'offensive_penalties': 3,
                'defensive_penalties': 1,
                'total_penalty_yards_home': 15,
                'total_penalty_yards_away': 15,
                'penalties_affecting_touchdowns': 0,
                'penalties_affecting_turnovers': 0,
                'challenges_total': 0,
                'challenges_overturned': 0,
                'automatic_reviews': 1,
                'reviews_overturned': 0,
                'crew_id': 'CREW_51',
                'is_head_referee': False,
                'is_playoff_eligible': True,
                'game_control_rating': 8.2,
                'consistency_rating': 8.7,
                'accuracy_rating': 9.1,
                'career_games_officiated': 312,
                'career_playoff_games': 15,
                'career_super_bowls': 1,
                'officiating_notes': 'Solid performance, good positioning',
                'controversial_calls': None,
                'data_source': 'NFL Official Stats',
                'data_quality': 'High'
            },
            # Game 2: 2024 Week 1 - BUF vs ARI  
            {
                'game_id': '2024_01_BUF_ARI',
                'official_id': 'REF_002',
                'season': 2024,
                'week': 1,
                'game_date': '2024-09-08',
                'home_team': 'ARI',
                'away_team': 'BUF',
                'official_name': 'Jerome Boger',
                'position': 'Referee',
                'jersey_number': '23',
                'years_experience': 20,
                'total_penalties_called': 15,
                'penalty_yards_assessed': 132,
                'flags_thrown': 18,
                'flags_picked_up': 3,
                'holding_penalties': 4,
                'false_start_penalties': 3,
                'pass_interference_penalties': 2,
                'roughing_penalties': 1,
                'unsportsmanlike_conduct': 2,
                'delay_of_game': 1,
                'offensive_penalties': 8,
                'defensive_penalties': 7,
                'total_penalty_yards_home': 78,
                'total_penalty_yards_away': 54,
                'penalties_affecting_touchdowns': 2,
                'penalties_affecting_turnovers': 1,
                'challenges_total': 3,
                'challenges_overturned': 2,
                'automatic_reviews': 4,
                'reviews_overturned': 1,
                'crew_id': 'CREW_23',
                'is_head_referee': True,
                'is_playoff_eligible': True,
                'game_control_rating': 7.5,
                'consistency_rating': 7.8,
                'accuracy_rating': 8.2,
                'career_games_officiated': 389,
                'career_playoff_games': 18,
                'career_super_bowls': 1,
                'officiating_notes': 'Penalty-heavy game, some questionable calls',
                'controversial_calls': 'Late PI call on ARI affected scoring drive',
                'data_source': 'NFL Official Stats',
                'data_quality': 'High'
            },
            {
                'game_id': '2024_01_BUF_ARI',
                'official_id': 'LJ_001',
                'season': 2024,
                'week': 1,
                'game_date': '2024-09-08',
                'home_team': 'ARI',
                'away_team': 'BUF',
                'official_name': 'Jeff Bergman',
                'position': 'Line Judge',
                'jersey_number': '32',
                'years_experience': 15,
                'total_penalties_called': 6,
                'penalty_yards_assessed': 45,
                'flags_thrown': 7,
                'flags_picked_up': 1,
                'holding_penalties': 2,
                'false_start_penalties': 2,
                'pass_interference_penalties': 1,
                'roughing_penalties': 0,
                'unsportsmanlike_conduct': 0,
                'delay_of_game': 1,
                'offensive_penalties': 4,
                'defensive_penalties': 2,
                'total_penalty_yards_home': 25,
                'total_penalty_yards_away': 20,
                'penalties_affecting_touchdowns': 1,
                'penalties_affecting_turnovers': 0,
                'challenges_total': 1,
                'challenges_overturned': 1,
                'automatic_reviews': 2,
                'reviews_overturned': 0,
                'crew_id': 'CREW_23',
                'is_head_referee': False,
                'is_playoff_eligible': True,
                'game_control_rating': 8.0,
                'consistency_rating': 8.3,
                'accuracy_rating': 8.5,
                'career_games_officiated': 267,
                'career_playoff_games': 12,
                'career_super_bowls': 0,
                'officiating_notes': 'Good sideline coverage',
                'controversial_calls': None,
                'data_source': 'NFL Official Stats',
                'data_quality': 'High'
            }
        ]
        
        # Insert sample data
        for official_data in sample_officials:
            official = NFLOfficials(**official_data)
            session.add(official)
        
        session.commit()
        print(f"✅ Successfully loaded {len(sample_officials)} sample officials records!")
        
        # Verify the data
        count = session.query(NFLOfficials).count()
        print(f"📊 Total officials records in database: {count}")
        
        # Show sample data
        print("\n📋 Sample Officials Data:")
        sample_records = session.query(NFLOfficials).limit(2).all()
        for record in sample_records:
            print(f"  {record.official_name} ({record.position}) - {record.game_id}")
            print(f"    Penalties Called: {record.total_penalties_called}, Yards: {record.penalty_yards_assessed}")
            print(f"    Experience: {record.years_experience} years, Career Games: {record.career_games_officiated}")
        
    except Exception as e:
        print(f"❌ Error loading sample officials data: {e}")
        session.rollback()
        return False
    finally:
        session.close()
    
    return True

if __name__ == "__main__":
    load_sample_officials_data()
