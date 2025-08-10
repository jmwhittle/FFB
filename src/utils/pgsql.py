"""
PostgreSQL helper utilities for the Fantasy Football Database project.
Provides convenient functions for executing queries and returning pandas DataFrames.
"""

import os
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
from typing import Optional, Dict, Any, List, Union
import warnings

# Load environment variables
load_dotenv()

class PostgreSQLHelper:
    """Helper class for PostgreSQL database operations."""
    
    def __init__(self):
        """Initialize the PostgreSQL helper with connection from environment variables."""
        self.engine = None
        self._create_engine()
    
    def _create_engine(self):
        """Create SQLAlchemy engine from environment variables."""
        try:
            # Get database configuration from environment
            db_config = {
                'host': os.getenv('DB_HOST', 'localhost'),
                'port': os.getenv('DB_PORT', '5432'),
                'database': os.getenv('DB_NAME', 'ffb_stats'),
                'user': os.getenv('DB_USER', 'postgres'),
                'password': os.getenv('DB_PASSWORD', '')
            }
            
            # Build connection string
            connection_string = (
                f"postgresql://{db_config['user']}:{db_config['password']}"
                f"@{db_config['host']}:{db_config['port']}/{db_config['database']}"
            )
            
            # Create engine
            self.engine = create_engine(
                connection_string,
                echo=False,
                pool_pre_ping=True,
                pool_recycle=300
            )
            
        except Exception as e:
            raise ConnectionError(f"Failed to create database engine: {e}")
    
    def test_connection(self) -> bool:
        """Test database connection."""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False
    
    def pg_df(self, query: str, params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        Execute a PostgreSQL query and return results as a pandas DataFrame.
        
        Args:
            query (str): SQL query string
            params (dict, optional): Parameters for parameterized queries
            
        Returns:
            pd.DataFrame: Query results as DataFrame
            
        Example:
            # Simple query
            df = helper.pg_df("SELECT * FROM players LIMIT 10")
            
            # Parameterized query
            df = helper.pg_df(
                "SELECT * FROM players WHERE position = :pos AND team = :team",
                {'pos': 'QB', 'team': 'BUF'}
            )
        """
        try:
            with self.engine.connect() as conn:
                if params:
                    result = pd.read_sql(text(query), conn, params=params)
                else:
                    result = pd.read_sql(text(query), conn)
                
                return result
                
        except SQLAlchemyError as e:
            raise RuntimeError(f"Database query failed: {e}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error executing query: {e}")
    
    def pg_execute(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Execute a PostgreSQL query that doesn't return data (INSERT, UPDATE, DELETE).
        
        Args:
            query (str): SQL query string
            params (dict, optional): Parameters for parameterized queries
            
        Returns:
            Any: Result of the execution (typically row count for DML operations)
        """
        try:
            with self.engine.connect() as conn:
                if params:
                    result = conn.execute(text(query), params)
                else:
                    result = conn.execute(text(query))
                
                conn.commit()
                return result.rowcount
                
        except SQLAlchemyError as e:
            raise RuntimeError(f"Database execution failed: {e}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error executing query: {e}")
    
    def get_table_info(self, table_name: str) -> pd.DataFrame:
        """
        Get column information for a specific table.
        
        Args:
            table_name (str): Name of the table
            
        Returns:
            pd.DataFrame: Table column information
        """
        query = """
        SELECT 
            column_name,
            data_type,
            is_nullable,
            column_default,
            character_maximum_length
        FROM information_schema.columns 
        WHERE table_name = :table_name
        ORDER BY ordinal_position
        """
        return self.pg_df(query, {'table_name': table_name})
    
    def list_tables(self) -> pd.DataFrame:
        """
        List all tables in the current database.
        
        Returns:
            pd.DataFrame: List of tables with row counts
        """
        query = """
        SELECT 
            schemaname,
            tablename,
            tableowner
        FROM pg_tables 
        WHERE schemaname = 'public'
        ORDER BY tablename
        """
        
        tables_df = self.pg_df(query)
        
        # Add row counts
        row_counts = []
        for _, row in tables_df.iterrows():
            try:
                count_query = f"SELECT COUNT(*) as row_count FROM {row['tablename']}"
                count_result = self.pg_df(count_query)
                row_counts.append(count_result.iloc[0]['row_count'])
            except:
                row_counts.append(0)
        
        tables_df['row_count'] = row_counts
        return tables_df
    
    def quick_stats(self, table_name: str, limit: int = 5) -> Dict[str, Any]:
        """
        Get quick statistics and sample data for a table.
        
        Args:
            table_name (str): Name of the table
            limit (int): Number of sample rows to return
            
        Returns:
            dict: Dictionary containing table stats and sample data
        """
        # Get row count
        count_query = f"SELECT COUNT(*) as total_rows FROM {table_name}"
        count_df = self.pg_df(count_query)
        total_rows = count_df.iloc[0]['total_rows']
        
        # Get sample data
        sample_query = f"SELECT * FROM {table_name} LIMIT {limit}"
        sample_df = self.pg_df(sample_query)
        
        # Get table info
        table_info = self.get_table_info(table_name)
        
        return {
            'table_name': table_name,
            'total_rows': total_rows,
            'total_columns': len(table_info),
            'columns': table_info['column_name'].tolist(),
            'sample_data': sample_df,
            'table_info': table_info
        }


# Global helper instance
_pg_helper = None

def get_pg_helper() -> PostgreSQLHelper:
    """Get or create the global PostgreSQL helper instance."""
    global _pg_helper
    if _pg_helper is None:
        _pg_helper = PostgreSQLHelper()
    return _pg_helper

def pg_df(query: str, params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
    """
    Convenience function to execute a PostgreSQL query and return a pandas DataFrame.
    
    Args:
        query (str): SQL query string
        params (dict, optional): Parameters for parameterized queries
        
    Returns:
        pd.DataFrame: Query results as DataFrame
        
    Example:
        from src.utils.pgsql import pg_df
        
        # Simple query
        df = pg_df("SELECT * FROM players WHERE position = 'QB' LIMIT 10")
        
        # Parameterized query  
        df = pg_df(
            "SELECT * FROM players WHERE position = :pos AND team = :team",
            {'pos': 'QB', 'team': 'BUF'}
        )
        
        # Multi-line query
        query = '''
        SELECT 
            p.full_name,
            p.position,
            p.team,
            COUNT(re.id) as roster_appearances
        FROM players p
        LEFT JOIN roster_entries re ON p.id = re.player_id
        WHERE p.active = true
        GROUP BY p.id, p.full_name, p.position, p.team
        ORDER BY roster_appearances DESC
        LIMIT 20
        '''
        df = pg_df(query)
    """
    helper = get_pg_helper()
    return helper.pg_df(query, params)

def pg_execute(query: str, params: Optional[Dict[str, Any]] = None) -> Any:
    """
    Convenience function to execute a PostgreSQL query that doesn't return data.
    
    Args:
        query (str): SQL query string
        params (dict, optional): Parameters for parameterized queries
        
    Returns:
        Any: Result of the execution (typically row count)
    """
    helper = get_pg_helper()
    return helper.pg_execute(query, params)

def pg_table_info(table_name: str) -> pd.DataFrame:
    """Get column information for a table."""
    helper = get_pg_helper()
    return helper.get_table_info(table_name)

def pg_list_tables() -> pd.DataFrame:
    """List all tables in the database."""
    helper = get_pg_helper()
    return helper.list_tables()

def pg_quick_stats(table_name: str, limit: int = 5) -> Dict[str, Any]:
    """Get quick statistics for a table."""
    helper = get_pg_helper()
    return helper.quick_stats(table_name, limit)

def pg_test_connection() -> bool:
    """Test database connection."""
    try:
        helper = get_pg_helper()
        return helper.test_connection()
    except:
        return False

# Common query templates
QUERY_TEMPLATES = {
    'top_players_by_position': """
        SELECT full_name, team, position, age, years_exp 
        FROM players 
        WHERE position = :position AND active = true
        ORDER BY years_exp DESC, age ASC
        LIMIT :limit
    """,
    
    'league_standings': """
        SELECT 
            u.display_name,
            r.wins,
            r.losses,
            r.ties,
            ROUND(r.wins::decimal / NULLIF(r.wins + r.losses + r.ties, 0), 3) as win_percentage
        FROM rosters r
        JOIN users u ON r.owner_id = u.id
        WHERE r.league_id = :league_id
        ORDER BY r.wins DESC, win_percentage DESC
    """,
    
    'player_ownership': """
        SELECT 
            p.full_name,
            p.position,
            p.team,
            COUNT(re.id) as times_rostered
        FROM players p
        LEFT JOIN roster_entries re ON p.id = re.player_id
        WHERE p.active = true
        GROUP BY p.id, p.full_name, p.position, p.team
        HAVING COUNT(re.id) > 0
        ORDER BY times_rostered DESC
        LIMIT :limit
    """
}

def pg_template(template_name: str, **kwargs) -> pd.DataFrame:
    """
    Execute a predefined query template.
    
    Args:
        template_name (str): Name of the template
        **kwargs: Parameters for the template
        
    Returns:
        pd.DataFrame: Query results
    """
    if template_name not in QUERY_TEMPLATES:
        raise ValueError(f"Template '{template_name}' not found. Available: {list(QUERY_TEMPLATES.keys())}")
    
    query = QUERY_TEMPLATES[template_name]
    return pg_df(query, kwargs)

# Export main functions
__all__ = [
    'pg_df',
    'pg_execute', 
    'pg_table_info',
    'pg_list_tables',
    'pg_quick_stats',
    'pg_test_connection',
    'pg_template',
    'PostgreSQLHelper',
    'QUERY_TEMPLATES'
]
