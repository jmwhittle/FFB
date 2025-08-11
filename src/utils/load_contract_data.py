"""
Sample script for loading NFL contract data.
This demonstrates the structure for loading historical contract information.

Note: This script provides sample data structure. Real contract data would come from:
- Spotrac.com
- OverTheCap.com
- NFL Players Association
- Team salary cap databases
"""

import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from datetime import datetime
from sqlalchemy import text
from src.models import NFLContractInfo
from config.database import get_session_local
import pandas as pd

def load_sample_contract_data():
    """Load sample contract data to demonstrate the table structure."""
    SessionLocal = get_session_local()
    session = SessionLocal()
    
    try:
        print("Loading sample NFL contract data...")
        
        # Sample contract data for demonstration
        sample_contracts = [
            {
                'player_id': '00-0019596',  # Tom Brady
                'season': 2024,
                'player_name': 'T.Brady',
                'player_display_name': 'Tom Brady',
                'position': 'QB',
                'team': 'TB',
                'contract_value_total': 50000000.0,
                'contract_length_years': 1,
                'contract_year': 1,
                'contract_signed_date': datetime(2024, 3, 1),
                'base_salary': 15000000.0,
                'signing_bonus': 20000000.0,
                'roster_bonus': 5000000.0,
                'workout_bonus': 500000.0,
                'incentives_likely': 3000000.0,
                'incentives_unlikely': 6500000.0,
                'cap_hit': 43000000.0,
                'cap_percent': 15.2,
                'dead_money': 25000000.0,
                'contract_type': 'extension',
                'guaranteed_money': 40000000.0,
                'is_franchise_tag': False,
                'is_transition_tag': False,
                'has_performance_incentives': True,
                'has_playing_time_incentives': True,
                'has_statistical_incentives': True,
                'contract_notes': 'Historic contract for legendary QB',
                'source': 'sample_data'
            },
            {
                'player_id': '00-0026498',  # Matthew Stafford
                'season': 2024,
                'player_name': 'M.Stafford',
                'player_display_name': 'Matthew Stafford',
                'position': 'QB',
                'team': 'LA',
                'contract_value_total': 160000000.0,
                'contract_length_years': 4,
                'contract_year': 3,
                'contract_signed_date': datetime(2022, 3, 15),
                'base_salary': 31000000.0,
                'signing_bonus': 0.0,  # Already prorated
                'roster_bonus': 2500000.0,
                'workout_bonus': 750000.0,
                'incentives_likely': 1500000.0,
                'incentives_unlikely': 3250000.0,
                'cap_hit': 49500000.0,
                'cap_percent': 17.8,
                'dead_money': 47000000.0,
                'contract_type': 'extension',
                'guaranteed_money': 135000000.0,
                'is_franchise_tag': False,
                'is_transition_tag': False,
                'has_performance_incentives': True,
                'has_playing_time_incentives': False,
                'has_statistical_incentives': True,
                'contract_notes': 'Super Bowl winning QB contract',
                'source': 'sample_data'
            },
            {
                'player_id': '00-0031285',  # Devonta Freeman (example historical)
                'season': 2015,
                'player_name': 'D.Freeman',
                'player_display_name': 'Devonta Freeman',
                'position': 'RB',
                'team': 'ATL',
                'contract_value_total': 41250000.0,
                'contract_length_years': 5,
                'contract_year': 1,
                'contract_signed_date': datetime(2015, 8, 20),
                'base_salary': 8750000.0,
                'signing_bonus': 15000000.0,
                'roster_bonus': 1500000.0,
                'workout_bonus': 250000.0,
                'incentives_likely': 750000.0,
                'incentives_unlikely': 1500000.0,
                'cap_hit': 12500000.0,
                'cap_percent': 8.9,
                'dead_money': 30000000.0,
                'contract_type': 'extension',
                'guaranteed_money': 22000000.0,
                'is_franchise_tag': False,
                'is_transition_tag': False,
                'has_performance_incentives': True,
                'has_playing_time_incentives': True,
                'has_statistical_incentives': True,
                'contract_notes': 'Multi-year extension after breakout season',
                'source': 'sample_data'
            }
        ]
        
        # Insert sample data
        for contract_data in sample_contracts:
            contract = NFLContractInfo(**contract_data)
            session.add(contract)
        
        session.commit()
        
        print(f"✅ Successfully loaded {len(sample_contracts)} sample contract records!")
        
        # Verify the data
        result = session.execute(text("""
            SELECT player_display_name, position, team, season, 
                   contract_value_total, cap_hit, contract_type
            FROM nfl_contract_info 
            ORDER BY season DESC, cap_hit DESC;
        """)).fetchall()
        
        print(f"\n📊 Sample Contract Data:")
        for row in result:
            player, pos, team, season, total, cap_hit, c_type = row
            print(f"  {player} ({pos}, {team}) {season}: ${total/1e6:.1f}M total, ${cap_hit/1e6:.1f}M cap hit ({c_type})")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error loading sample contract data: {e}")
        raise
    finally:
        session.close()

def get_contract_data_sources():
    """Display information about potential contract data sources."""
    print("\n🔍 NFL Contract Data Sources:")
    print("=" * 50)
    print("1. Spotrac.com - Comprehensive contract database")
    print("   - Historical data back to 1999")
    print("   - Detailed breakdown of salaries, bonuses, incentives")
    print("   - Cap hit calculations and dead money")
    print()
    print("2. OverTheCap.com - Salary cap focused")
    print("   - Team salary cap management")
    print("   - Contract restructuring analysis")
    print("   - Free agency predictions")
    print()
    print("3. NFL Players Association (NFLPA)")
    print("   - Official salary data")
    print("   - Collective bargaining agreement details")
    print("   - Player benefits and pension info")
    print()
    print("4. Team Sources")
    print("   - Official team announcements")
    print("   - Local beat reporters")
    print("   - Front office leaks")
    print()
    print("📝 Implementation Notes:")
    print("- Web scraping would be needed for Spotrac/OverTheCap")
    print("- API access may be available for some sources")
    print("- Historical data may require backfilling from archives")
    print("- Contract details often have confidential elements")

if __name__ == "__main__":
    load_sample_contract_data()
    get_contract_data_sources()
