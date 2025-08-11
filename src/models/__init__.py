"""
Database models for Fantasy Football data.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from config.database import Base


class User(Base):
    """Sleeper user model."""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)  # Sleeper user ID
    username = Column(String, unique=True, nullable=False)
    display_name = Column(String)
    avatar = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    roster_entries = relationship("RosterEntry", back_populates="user")


class League(Base):
    """Fantasy league model."""
    __tablename__ = "leagues"
    
    id = Column(String, primary_key=True)  # Sleeper league ID
    name = Column(String, nullable=False)
    season = Column(String, nullable=False)
    sport = Column(String, default="nfl")
    status = Column(String)  # pre_draft, drafting, in_season, complete
    season_type = Column(String)  # regular, playoff
    total_rosters = Column(Integer)
    scoring_settings = Column(JSON)
    roster_positions = Column(JSON)
    settings = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    rosters = relationship("Roster", back_populates="league")
    matchups = relationship("Matchup", back_populates="league")


class Player(Base):
    """NFL player model."""
    __tablename__ = "players"
    
    id = Column(String, primary_key=True)  # Sleeper player ID
    player_id = Column(String, unique=True)  # NFL player ID
    first_name = Column(String)
    last_name = Column(String)
    full_name = Column(String)
    position = Column(String)
    team = Column(String)
    college = Column(String)
    height = Column(String)
    weight = Column(String)
    age = Column(Integer)
    years_exp = Column(Integer)
    active = Column(Boolean, default=True)
    injury_status = Column(String)
    fantasy_data_id = Column(String)
    rotowire_id = Column(String)
    rotoworld_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    roster_entries = relationship("RosterEntry", back_populates="player")
    stats = relationship("PlayerStats", back_populates="player")


class Roster(Base):
    """Fantasy roster model."""
    __tablename__ = "rosters"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    roster_id = Column(Integer, nullable=False)  # Sleeper roster ID within league
    league_id = Column(String, ForeignKey("leagues.id"), nullable=False)
    owner_id = Column(String, ForeignKey("users.id"))
    co_owners = Column(JSON)  # Array of user IDs
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    ties = Column(Integer, default=0)
    waiver_position = Column(Integer)
    waiver_budget_used = Column(Integer, default=0)
    total_moves = Column(Integer, default=0)
    settings = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    league = relationship("League", back_populates="rosters")
    roster_entries = relationship("RosterEntry", back_populates="roster")
    matchups = relationship("Matchup", back_populates="roster")


class RosterEntry(Base):
    """Individual player on a roster."""
    __tablename__ = "roster_entries"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    roster_id = Column(Integer, ForeignKey("rosters.id"), nullable=False)
    player_id = Column(String, ForeignKey("players.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"))
    position = Column(String)  # Starting lineup position or bench
    week = Column(Integer)
    season = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    roster = relationship("Roster", back_populates="roster_entries")
    player = relationship("Player", back_populates="roster_entries")
    user = relationship("User", back_populates="roster_entries")


class Matchup(Base):
    """Weekly matchup model."""
    __tablename__ = "matchups"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    matchup_id = Column(Integer)  # Groups teams in same matchup
    league_id = Column(String, ForeignKey("leagues.id"), nullable=False)
    roster_id = Column(Integer, ForeignKey("rosters.id"), nullable=False)
    week = Column(Integer, nullable=False)
    points = Column(Float)
    points_against = Column(Float)
    starters = Column(JSON)  # Array of player IDs
    starters_points = Column(JSON)  # Array of points for each starter
    players = Column(JSON)  # All rostered players
    players_points = Column(JSON)  # Points for all players
    custom_points = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    league = relationship("League", back_populates="matchups")
    roster = relationship("Roster", back_populates="matchups")


class PlayerStats(Base):
    """Player statistics by week."""
    __tablename__ = "player_stats"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(String, ForeignKey("players.id"), nullable=False)
    week = Column(Integer, nullable=False)
    season = Column(String, nullable=False)
    season_type = Column(String, default="regular")  # regular, playoff
    
    # Passing stats
    pass_att = Column(Integer, default=0)
    pass_cmp = Column(Integer, default=0)
    pass_yds = Column(Integer, default=0)
    pass_td = Column(Integer, default=0)
    pass_int = Column(Integer, default=0)
    pass_2pt = Column(Integer, default=0)
    
    # Rushing stats
    rush_att = Column(Integer, default=0)
    rush_yds = Column(Integer, default=0)
    rush_td = Column(Integer, default=0)
    rush_2pt = Column(Integer, default=0)
    
    # Receiving stats
    rec = Column(Integer, default=0)
    rec_yds = Column(Integer, default=0)
    rec_td = Column(Integer, default=0)
    rec_2pt = Column(Integer, default=0)
    rec_tgt = Column(Integer, default=0)
    
    # Kicking stats
    fgm = Column(Integer, default=0)
    fga = Column(Integer, default=0)
    fgm_0_19 = Column(Integer, default=0)
    fgm_20_29 = Column(Integer, default=0)
    fgm_30_39 = Column(Integer, default=0)
    fgm_40_49 = Column(Integer, default=0)
    fgm_50p = Column(Integer, default=0)
    xpm = Column(Integer, default=0)
    xpa = Column(Integer, default=0)
    
    # Defense stats
    def_st_td = Column(Integer, default=0)
    def_st_ff = Column(Integer, default=0)
    def_st_fum_rec = Column(Integer, default=0)
    def_st_int = Column(Integer, default=0)
    def_st_safety = Column(Integer, default=0)
    def_st_sack = Column(Integer, default=0)
    def_st_blk_kick = Column(Integer, default=0)
    pts_allow = Column(Integer, default=0)
    
    # Fantasy points
    fantasy_points = Column(Float)
    fantasy_points_ppr = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    player = relationship("Player", back_populates="stats")


class Transaction(Base):
    """League transactions (trades, waivers, free agency)."""
    __tablename__ = "transactions"
    
    id = Column(String, primary_key=True)  # Sleeper transaction ID
    league_id = Column(String, ForeignKey("leagues.id"), nullable=False)
    type = Column(String, nullable=False)  # trade, waiver, free_agent
    status = Column(String)  # complete, failed, processing
    creator = Column(String, ForeignKey("users.id"))
    created = Column(DateTime)
    consenter_ids = Column(JSON)  # Array of user IDs who need to consent
    roster_ids = Column(JSON)  # Array of roster IDs involved
    adds = Column(JSON)  # Players added {player_id: roster_id}
    drops = Column(JSON)  # Players dropped {player_id: roster_id}
    draft_picks = Column(JSON)  # Draft picks involved
    waiver_budget = Column(JSON)  # FAAB bids
    settings = Column(JSON)
    transaction_metadata = Column(JSON)  # Renamed from metadata to avoid conflict
    created_at = Column(DateTime, default=datetime.utcnow)


class NFLWeeklyStats(Base):
    """NFL weekly player statistics from nfl_data_py."""
    __tablename__ = "nfl_weekly_stats"
    
    # Composite primary key
    player_id = Column(String, primary_key=True)
    season = Column(Integer, primary_key=True)
    week = Column(Integer, primary_key=True)
    
    # Player info
    player_name = Column(String)
    player_display_name = Column(String)
    position = Column(String)
    position_group = Column(String)
    recent_team = Column(String)
    headshot_url = Column(String)
    
    # Game info
    opponent_team = Column(String)
    season_type = Column(String)  # REG, POST
    
    # Passing stats
    completions = Column(Float)
    attempts = Column(Float)
    passing_yards = Column(Float)
    passing_tds = Column(Float)
    interceptions = Column(Float)
    sacks = Column(Float)
    sack_yards = Column(Float)
    sack_fumbles = Column(Float)
    sack_fumbles_lost = Column(Float)
    passing_air_yards = Column(Float)
    passing_yards_after_catch = Column(Float)
    passing_first_downs = Column(Float)
    passing_epa = Column(Float)
    passing_2pt_conversions = Column(Float)
    
    # Rushing stats
    carries = Column(Float)
    rushing_yards = Column(Float)
    rushing_tds = Column(Float)
    rushing_fumbles = Column(Float)
    rushing_fumbles_lost = Column(Float)
    rushing_first_downs = Column(Float)
    rushing_epa = Column(Float)
    rushing_2pt_conversions = Column(Float)
    
    # Receiving stats
    targets = Column(Float)
    receptions = Column(Float)
    receiving_yards = Column(Float)
    receiving_tds = Column(Float)
    receiving_fumbles = Column(Float)
    receiving_fumbles_lost = Column(Float)
    receiving_air_yards = Column(Float)
    receiving_yards_after_catch = Column(Float)
    receiving_first_downs = Column(Float)
    receiving_epa = Column(Float)
    receiving_2pt_conversions = Column(Float)
    
    # Special teams
    special_teams_tds = Column(Float)
    
    # Fantasy points
    fantasy_points = Column(Float)
    fantasy_points_ppr = Column(Float)
    
    # Target share and snap counts
    target_share = Column(Float)
    air_yards_share = Column(Float)
    wopr = Column(Float)  # Weighted Opportunity Rating
    pacr = Column(Float)  # Passer Air Conversion Ratio
    racr = Column(Float)  # Receiver Air Conversion Ratio
    dakota = Column(Float)  # Dakota completion percentage
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class NFLSeasonalStats(Base):
    """NFL seasonal (aggregated) player statistics from nfl_data_py."""
    __tablename__ = "nfl_seasonal_stats"
    
    # Composite primary key
    player_id = Column(String, primary_key=True)
    season = Column(Integer, primary_key=True)
    
    # Player info
    player_name = Column(String)
    player_display_name = Column(String)
    position = Column(String)
    position_group = Column(String)
    team = Column(String)  # Most recent team
    
    # Season summary
    games_played = Column(Integer)
    season_type = Column(String)  # REG, POST, or BOTH
    
    # Passing stats (season totals)
    completions = Column(Float)
    attempts = Column(Float)
    passing_yards = Column(Float)
    passing_tds = Column(Float)
    interceptions = Column(Float)
    sacks = Column(Float)
    sack_yards = Column(Float)
    sack_fumbles = Column(Float)
    sack_fumbles_lost = Column(Float)
    passing_air_yards = Column(Float)
    passing_yards_after_catch = Column(Float)
    passing_first_downs = Column(Float)
    passing_epa = Column(Float)
    passing_2pt_conversions = Column(Float)
    
    # Passing efficiency (calculated)
    completion_percentage = Column(Float)
    yards_per_attempt = Column(Float)
    yards_per_completion = Column(Float)
    passer_rating = Column(Float)
    
    # Rushing stats (season totals)
    carries = Column(Float)
    rushing_yards = Column(Float)
    rushing_tds = Column(Float)
    rushing_fumbles = Column(Float)
    rushing_fumbles_lost = Column(Float)
    rushing_first_downs = Column(Float)
    rushing_epa = Column(Float)
    rushing_2pt_conversions = Column(Float)
    
    # Rushing efficiency (calculated)
    yards_per_carry = Column(Float)
    
    # Receiving stats (season totals)
    targets = Column(Float)
    receptions = Column(Float)
    receiving_yards = Column(Float)
    receiving_tds = Column(Float)
    receiving_fumbles = Column(Float)
    receiving_fumbles_lost = Column(Float)
    receiving_air_yards = Column(Float)
    receiving_yards_after_catch = Column(Float)
    receiving_first_downs = Column(Float)
    receiving_epa = Column(Float)
    receiving_2pt_conversions = Column(Float)
    
    # Receiving efficiency (calculated)
    catch_percentage = Column(Float)
    yards_per_target = Column(Float)
    yards_per_reception = Column(Float)
    average_depth_of_target = Column(Float)
    
    # Special teams
    special_teams_tds = Column(Float)
    
    # Fantasy points (season totals)
    fantasy_points = Column(Float)
    fantasy_points_ppr = Column(Float)
    
    # Advanced metrics (season averages)
    target_share = Column(Float)
    air_yards_share = Column(Float)
    wopr = Column(Float)  # Weighted Opportunity Rating
    
    # Market share metrics
    team_pass_attempts = Column(Float)
    team_targets = Column(Float)
    team_carries = Column(Float)
    
    # Consistency metrics
    fantasy_points_per_game = Column(Float)
    fantasy_points_ppr_per_game = Column(Float)
    weeks_with_10plus_points = Column(Integer)
    weeks_with_20plus_points = Column(Integer)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class NFLContractInfo(Base):
    """NFL player contract information from 1999-present."""
    __tablename__ = "nfl_contract_info"
    
    # Composite primary key
    player_id = Column(String, primary_key=True)
    season = Column(Integer, primary_key=True)
    
    # Player info
    player_name = Column(String)
    player_display_name = Column(String)
    position = Column(String)
    team = Column(String)
    
    # Contract details
    contract_value_total = Column(Float)  # Total contract value
    contract_length_years = Column(Integer)  # Contract length in years
    contract_year = Column(Integer)  # Which year of contract (1st, 2nd, etc.)
    contract_signed_date = Column(DateTime)  # When contract was signed
    
    # Annual compensation
    base_salary = Column(Float)  # Base salary for the season
    signing_bonus = Column(Float)  # Signing bonus (prorated)
    roster_bonus = Column(Float)  # Roster bonus
    workout_bonus = Column(Float)  # Workout bonus
    incentives_likely = Column(Float)  # Likely to be earned incentives
    incentives_unlikely = Column(Float)  # Unlikely to be earned incentives
    
    # Cap impact
    cap_hit = Column(Float)  # Total cap hit for the season
    cap_percent = Column(Float)  # Percentage of team's total cap
    dead_money = Column(Float)  # Dead money if cut
    
    # Contract type and status
    contract_type = Column(String)  # 'rookie', 'extension', 'free_agent', 'franchise_tag', etc.
    guaranteed_money = Column(Float)  # Guaranteed money remaining
    is_franchise_tag = Column(Boolean, default=False)
    is_transition_tag = Column(Boolean, default=False)
    
    # Performance clauses
    has_performance_incentives = Column(Boolean, default=False)
    has_playing_time_incentives = Column(Boolean, default=False)
    has_statistical_incentives = Column(Boolean, default=False)
    
    # Contract notes
    contract_notes = Column(Text)  # Additional contract details
    source = Column(String)  # Data source (Spotrac, OverTheCap, etc.)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class NFLOfficials(Base):
    """NFL Officials and Officiating Crew model."""
    __tablename__ = "nfl_officials"
    
    # Composite primary key: game_id + official_id
    game_id = Column(String, primary_key=True)  # NFL game identifier
    official_id = Column(String, primary_key=True)  # Official identifier
    
    # Game information
    season = Column(Integer, nullable=False)
    week = Column(Integer, nullable=False)
    game_date = Column(String)
    home_team = Column(String)
    away_team = Column(String)
    
    # Official information
    official_name = Column(String, nullable=False)
    position = Column(String, nullable=False)  # Referee, Umpire, Line Judge, etc.
    jersey_number = Column(String)
    years_experience = Column(Integer)
    
    # Officiating statistics for this game
    total_penalties_called = Column(Integer, default=0)
    penalty_yards_assessed = Column(Integer, default=0)
    flags_thrown = Column(Integer, default=0)
    flags_picked_up = Column(Integer, default=0)
    
    # Penalty breakdown by type
    holding_penalties = Column(Integer, default=0)
    false_start_penalties = Column(Integer, default=0)
    pass_interference_penalties = Column(Integer, default=0)
    roughing_penalties = Column(Integer, default=0)
    unsportsmanlike_conduct = Column(Integer, default=0)
    delay_of_game = Column(Integer, default=0)
    offensive_penalties = Column(Integer, default=0)
    defensive_penalties = Column(Integer, default=0)
    
    # Game flow impact
    total_penalty_yards_home = Column(Integer, default=0)
    total_penalty_yards_away = Column(Integer, default=0)
    penalties_affecting_touchdowns = Column(Integer, default=0)
    penalties_affecting_turnovers = Column(Integer, default=0)
    
    # Challenge and review statistics
    challenges_total = Column(Integer, default=0)
    challenges_overturned = Column(Integer, default=0)
    automatic_reviews = Column(Integer, default=0)
    reviews_overturned = Column(Integer, default=0)
    
    # Crew information
    crew_id = Column(String)  # Identifies the officiating crew
    is_head_referee = Column(Boolean, default=False)
    is_playoff_eligible = Column(Boolean, default=False)
    
    # Performance metrics
    game_control_rating = Column(Float)  # 1-10 scale
    consistency_rating = Column(Float)  # 1-10 scale
    accuracy_rating = Column(Float)  # 1-10 scale
    
    # Career statistics (updated per official per season)
    career_games_officiated = Column(Integer, default=0)
    career_playoff_games = Column(Integer, default=0)
    career_super_bowls = Column(Integer, default=0)
    
    # Notes and additional information
    officiating_notes = Column(Text)  # Any special notes about officiating
    controversial_calls = Column(Text)  # Documentation of controversial calls
    
    # Data source and quality
    data_source = Column(String)  # Where the data came from
    data_quality = Column(String)  # Quality rating of the data
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Export all models for easy importing
__all__ = [
    "User", "League", "Player", "Roster", "RosterEntry", 
    "Matchup", "PlayerStats", "Transaction", "NFLWeeklyStats", "NFLSeasonalStats", "NFLContractInfo", "NFLOfficials"
]
