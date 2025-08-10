"""
Simple database connection test and setup for FFB project.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def test_postgres_connection():
    """Test basic PostgreSQL connection."""
    load_dotenv()
    
    # Connection parameters
    conn_params = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'postgres'),
        'database': 'postgres'  # Connect to default database first
    }
    
    print("Testing PostgreSQL connection...")
    print(f"Host: {conn_params['host']}:{conn_params['port']}")
    print(f"User: {conn_params['user']}")
    
    try:
        # Test connection
        conn = psycopg2.connect(**conn_params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Test query
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        print(f"✓ Connected successfully!")
        print(f"  PostgreSQL version: {version[:50]}...")
        
        # Check if FFB database exists
        db_name = os.getenv('DB_NAME', 'ffb_stats')
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        db_exists = cursor.fetchone()
        
        if not db_exists:
            print(f"Creating database '{db_name}'...")
            cursor.execute(f"CREATE DATABASE {db_name}")
            print(f"✓ Database '{db_name}' created successfully")
        else:
            print(f"✓ Database '{db_name}' already exists")
        
        cursor.close()
        conn.close()
        
        return True
        
    except psycopg2.Error as e:
        print(f"✗ PostgreSQL connection failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def test_sqlalchemy_connection():
    """Test SQLAlchemy connection."""
    from sqlalchemy import create_engine, text
    
    load_dotenv()
    
    # Build connection string
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD', 'postgres')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'ffb_stats')
    
    connection_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    print(f"\nTesting SQLAlchemy connection...")
    print(f"Connection string: postgresql://{db_user}:***@{db_host}:{db_port}/{db_name}")
    
    try:
        engine = create_engine(connection_string, echo=False)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT current_database(), current_user"))
            db, user = result.fetchone()
            print(f"✓ SQLAlchemy connection successful!")
            print(f"  Connected to database: {db}")
            print(f"  Connected as user: {user}")
        
        return True
        
    except Exception as e:
        print(f"✗ SQLAlchemy connection failed: {e}")
        return False

def main():
    """Main test function."""
    print("FFB Database Connection Test")
    print("=" * 40)
    
    # Test 1: Basic PostgreSQL connection
    postgres_ok = test_postgres_connection()
    
    if postgres_ok:
        # Test 2: SQLAlchemy connection
        sqlalchemy_ok = test_sqlalchemy_connection()
        
        if sqlalchemy_ok:
            print(f"\n✅ All database tests passed!")
            print(f"You can now run 'python main.py' to set up the application.")
        else:
            print(f"\n❌ SQLAlchemy connection failed.")
    else:
        print(f"\n❌ PostgreSQL connection failed.")
        print(f"\nTroubleshooting:")
        print(f"1. Check if PostgreSQL service is running")
        print(f"2. Verify the password in your .env file")
        print(f"3. Try connecting manually: psql -h localhost -U postgres")

if __name__ == "__main__":
    main()
