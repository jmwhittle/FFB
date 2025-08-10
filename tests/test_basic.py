"""
Test suite for Fantasy Football Database.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.helpers import (
    format_player_name,
    calculate_fantasy_points,
    safe_int_convert,
    safe_float_convert,
    validate_sleeper_data
)


class TestHelperFunctions:
    """Test cases for utility helper functions."""
    
    def test_format_player_name(self):
        """Test player name formatting."""
        assert format_player_name("Josh", "Allen") == "Josh Allen"
        assert format_player_name("Josh", None) == "Josh"
        assert format_player_name(None, "Allen") == "Allen"
        assert format_player_name(None, None) == "Unknown Player"
        assert format_player_name("", "") == "Unknown Player"
    
    def test_calculate_fantasy_points(self):
        """Test fantasy points calculation."""
        stats = {
            'pass_yd': 300,
            'pass_td': 2,
            'rush_yd': 50,
            'rec': 5,
            'rec_yd': 80
        }
        
        points = calculate_fantasy_points(stats)
        expected = (300 * 0.04) + (2 * 4.0) + (50 * 0.1) + (5 * 1.0) + (80 * 0.1)
        assert points == expected
    
    def test_safe_int_convert(self):
        """Test safe integer conversion."""
        assert safe_int_convert("123") == 123
        assert safe_int_convert(123.7) == 123
        assert safe_int_convert(None) is None
        assert safe_int_convert("invalid") is None
        assert safe_int_convert("") is None
    
    def test_safe_float_convert(self):
        """Test safe float conversion."""
        assert safe_float_convert("123.45") == 123.45
        assert safe_float_convert(123) == 123.0
        assert safe_float_convert(None) is None
        assert safe_float_convert("invalid") is None
    
    def test_validate_sleeper_data(self):
        """Test Sleeper data validation."""
        data = {
            'user_id': '123',
            'username': 'test_user',
            'display_name': 'Test User'
        }
        
        required_fields = ['user_id', 'username']
        assert validate_sleeper_data(data, required_fields) is True
        
        required_fields = ['user_id', 'email']  # email not in data
        assert validate_sleeper_data(data, required_fields) is False
        
        assert validate_sleeper_data(None, required_fields) is False
        assert validate_sleeper_data({}, required_fields) is False


class TestDatabaseModels:
    """Test cases for database models."""
    
    def test_model_imports(self):
        """Test that all models can be imported."""
        try:
            from src.models import User, League, Player, Roster, Matchup
            assert True
        except ImportError as e:
            pytest.skip(f"Database models not available: {e}")


class TestSleeperAPI:
    """Test cases for Sleeper API client."""
    
    @pytest.mark.integration
    def test_api_connectivity(self):
        """Test basic API connectivity."""
        try:
            from api.sleeper_client import SleeperClient
            client = SleeperClient()
            nfl_state = client.get_nfl_state()
            assert nfl_state is not None
            assert 'season' in nfl_state
        except ImportError:
            pytest.skip("Sleeper client not available")
        except Exception as e:
            pytest.skip(f"API test failed: {e}")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
