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


# Export all models for easy importing
__all__ = [
    "User", "League", "Player", "Roster", "RosterEntry", 
    "Matchup", "PlayerStats", "Transaction"
]
