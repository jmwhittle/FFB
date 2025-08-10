#!/usr/bin/env python3
"""
Setup script for Fantasy Football Database project.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True


def check_postgresql():
    """Check if PostgreSQL is available."""
    try:
        result = subprocess.run("psql --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ PostgreSQL detected: {result.stdout.strip()}")
            return True
        else:
            print("⚠️  PostgreSQL not detected in PATH")
            print("Please install PostgreSQL manually")
            return False
    except Exception:
        print("⚠️  PostgreSQL not detected")
        print("Please install PostgreSQL manually")
        return False


def create_env_file():
    """Create .env file from template."""
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if env_example.exists() and not env_file.exists():
        with open(env_example, 'r') as src, open(env_file, 'w') as dst:
            dst.write(src.read())
        print("✅ Created .env file from template")
        print("📝 Please update .env with your database credentials")
        return True
    elif env_file.exists():
        print("✅ .env file already exists")
        return True
    else:
        print("❌ Could not create .env file")
        return False


def main():
    """Main setup function."""
    print("🏈 Fantasy Football Database Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check PostgreSQL
    check_postgresql()
    
    # Install dependencies
    print(f"\n📦 Installing Python dependencies...")
    success = run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing dependencies"
    )
    
    if not success:
        print("⚠️  Some dependencies failed to install")
        print("You may need to install PostgreSQL development headers:")
        print("  - Ubuntu/Debian: sudo apt-get install libpq-dev")
        print("  - CentOS/RHEL: sudo yum install postgresql-devel")
        print("  - macOS: brew install postgresql")
        print("  - Windows: Install PostgreSQL from postgresql.org")
    
    # Create .env file
    create_env_file()
    
    # Test imports
    print(f"\n🧪 Testing imports...")
    try:
        import pandas
        import sqlalchemy
        import requests
        print("✅ Core dependencies imported successfully")
    except ImportError as e:
        print(f"❌ Import test failed: {e}")
    
    print(f"\n🎉 Setup completed!")
    print(f"\nNext steps:")
    print(f"1. Update .env file with your PostgreSQL credentials")
    print(f"2. Create a PostgreSQL database named 'ffb_stats'")
    print(f"3. Run: python main.py")
    print(f"4. Explore the Jupyter notebook: notebooks/fantasy_football_setup.ipynb")
    
    print(f"\n📚 Project structure:")
    print(f"  src/          - Main application code")
    print(f"  api/          - Sleeper API integration")
    print(f"  config/       - Configuration files")
    print(f"  database/     - Database schemas and migrations")
    print(f"  notebooks/    - Jupyter notebooks for analysis")
    print(f"  tests/        - Unit tests")


if __name__ == "__main__":
    main()
