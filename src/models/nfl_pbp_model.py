from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, Index, BigInteger
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class NFLPlayByPlay(Base):
    """NFL Play-by-Play data from nfl_data_py with detailed game context and player involvement."""
    
    __tablename__ = 'nfl_play_by_play'
    
    # Primary key - combination of game_id and play_id should be unique
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    
    # Game identification
    play_id = Column(Float)
    game_id = Column(String(20), nullable=False, index=True)
    old_game_id = Column(String(20))
    home_team = Column(String(3), index=True)
    away_team = Column(String(3), index=True)
    season_type = Column(String(10), index=True)
    week = Column(Integer, index=True)
    season = Column(Integer, nullable=False, index=True)
    game_date = Column(DateTime)
    
    # Game context
    qtr = Column(Integer)
    down = Column(Integer)
    ydstogo = Column(Integer)
    yardline_100 = Column(Integer)
    quarter_seconds_remaining = Column(Integer)
    half_seconds_remaining = Column(Integer)
    game_seconds_remaining = Column(Integer)
    game_half = Column(String(10))
    quarter_end = Column(Integer)
    drive = Column(Integer)
    sp = Column(Integer)
    
    # Team possession
    posteam = Column(String(3), index=True)
    posteam_type = Column(String(10))
    defteam = Column(String(3))
    side_of_field = Column(String(3))
    goal_to_go = Column(Integer)
    time = Column(String(10))
    yrdln = Column(String(10))
    desc = Column(Text)
    play_type = Column(String(20), index=True)
    
    # Play details
    yards_gained = Column(Integer)
    shotgun = Column(Integer)
    no_huddle = Column(Integer)
    qb_dropback = Column(Integer)
    qb_kneel = Column(Integer)
    qb_spike = Column(Integer)
    qb_scramble = Column(Integer)
    
    # Passing details
    pass_length = Column(String(10))
    pass_location = Column(String(10))
    air_yards = Column(Integer)
    yards_after_catch = Column(Integer)
    pass_attempt = Column(Integer)
    complete_pass = Column(Integer)
    incomplete_pass = Column(Integer)
    pass_touchdown = Column(Integer)
    passing_yards = Column(Integer)
    interception = Column(Integer)
    
    # Rushing details
    run_location = Column(String(10))
    run_gap = Column(String(10))
    rush_attempt = Column(Integer)
    rush_touchdown = Column(Integer)
    rushing_yards = Column(Integer)
    
    # Kicking
    field_goal_result = Column(String(20))
    kick_distance = Column(Integer)
    extra_point_result = Column(String(20))
    two_point_conv_result = Column(String(20))
    field_goal_attempt = Column(Integer)
    kickoff_attempt = Column(Integer)
    punt_attempt = Column(Integer)
    extra_point_attempt = Column(Integer)
    two_point_attempt = Column(Integer)
    
    # Scoring
    touchdown = Column(Integer)
    return_touchdown = Column(Integer)
    safety = Column(Integer)
    home_score = Column(Integer)
    away_score = Column(Integer)
    total_home_score = Column(Integer)
    total_away_score = Column(Integer)
    
    # Player involvement
    passer_player_id = Column(String(20), index=True)
    passer_player_name = Column(String(100))
    receiver_player_id = Column(String(20), index=True)
    receiver_player_name = Column(String(100))
    receiving_yards = Column(Integer)
    rusher_player_id = Column(String(20), index=True)
    rusher_player_name = Column(String(100))
    lateral_receiver_player_id = Column(String(20))
    lateral_receiver_player_name = Column(String(100))
    lateral_receiving_yards = Column(Integer)
    lateral_rusher_player_id = Column(String(20))
    lateral_rusher_player_name = Column(String(100))
    lateral_rushing_yards = Column(Integer)
    
    # Turnovers
    fumble = Column(Integer)
    fumble_lost = Column(Integer)
    fumble_out_of_bounds = Column(Integer)
    
    # Penalties
    penalty = Column(Integer)
    tackled_for_loss = Column(Integer)
    
    # Advanced metrics
    epa = Column(Float)
    wpa = Column(Float)
    wp = Column(Float)
    def_wp = Column(Float)
    home_wp = Column(Float)
    away_wp = Column(Float)
    cpoe = Column(Float)
    success = Column(Integer)
    air_epa = Column(Float)
    yac_epa = Column(Float)
    comp_air_epa = Column(Float)
    comp_yac_epa = Column(Float)
    total_home_epa = Column(Float)
    total_away_epa = Column(Float)
    qb_epa = Column(Float)
    xyac_epa = Column(Float)
    xyac_mean_yardage = Column(Float)
    xyac_median_yardage = Column(Float)
    xyac_success = Column(Integer)
    xyac_fd = Column(Integer)
    xpass = Column(Float)
    pass_oe = Column(Float)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_pbp_game_play', 'game_id', 'play_id'),
        Index('idx_pbp_season_week', 'season', 'week'),
        Index('idx_pbp_player_pass', 'passer_player_id', 'season'),
        Index('idx_pbp_player_rush', 'rusher_player_id', 'season'),
        Index('idx_pbp_player_rec', 'receiver_player_id', 'season'),
        Index('idx_pbp_team_season', 'posteam', 'season'),
    )
