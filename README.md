# Fantasy Football Database Project

A comprehensive fantasy football statistics database with Sleeper API integration and data science capabilities.

## Features

- **PostgreSQL Database**: Robust storage for fantasy football statistics
- **Sleeper API Integration**: Real-time data from the Sleeper fantasy football platform
- **Data Science Ready**: Built-in support for pandas, numpy, and analytical tools
- **Extensible Architecture**: Modular design for easy feature additions

## Project Structure

```
ffb/
├── src/                    # Main application code
│   ├── models/            # Database models
│   ├── services/          # Business logic
│   └── utils/             # Utility functions
├── database/              # Database schema and migrations
├── api/                   # Sleeper API integration
├── config/                # Configuration files
├── tests/                 # Unit tests
├── notebooks/             # Jupyter notebooks for analysis
└── requirements.txt       # Python dependencies
```

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Database**
   - Install PostgreSQL
   - Create database: `ffb_stats`
   - Update connection settings in `config/database.py`

3. **Environment Variables**
   Create `.env` file with:
   ```
   DATABASE_URL=postgresql://username:password@localhost:5432/ffb_stats
   SLEEPER_API_BASE_URL=https://api.sleeper.app/v1
   ```

## Usage

### Database Setup
```python
from src.database.connection import setup_database
setup_database()
```

### Fetch Sleeper Data
```python
from api.sleeper_client import SleeperClient
client = SleeperClient()
leagues = client.get_user_leagues("username")
```

### Data Analysis
See example notebooks in `notebooks/` directory for data science workflows.

## Dependencies

- **Database**: PostgreSQL, SQLAlchemy, psycopg2
- **API**: requests, sleeper-py
- **Data Science**: pandas, numpy, matplotlib, seaborn, jupyter
- **Development**: pytest, black, flake8

## Contributing

1. Follow PEP 8 style guidelines
2. Add type hints to all functions
3. Write tests for new features
4. Update documentation

## parting instructions
🎉 Project Setup Complete!
✅ What's Been Built:
Project Structure: Clean, organized folder structure with separate modules for different concerns
Database Layer: PostgreSQL-ready models for users, leagues, players, rosters, matchups, and stats
API Integration: Sleeper API client with rate limiting and error handling
Data Sync Service: Automated data fetching and database population
Analysis Tools: Jupyter notebook ready for data science workflows
Utilities & Tests: Helper functions and basic test framework
🏗️ Architecture Overview:
✅ Core Features Ready:
PostgreSQL Integration: Full schema with relationships
Sleeper API: Tested and working (connected to 2025 season)
Data Models: Users, leagues, players, rosters, matchups, stats, transactions
Analysis Notebook: Complete setup guide with data visualization examples
📋 Next Steps:
Set up PostgreSQL:

Configure Environment:

Edit .env file with your PostgreSQL credentials
Set your Sleeper username for data collection
Initialize Database:

Start Data Collection:

Explore Analytics:

Open fantasy_football_setup.ipynb
Follow the guided setup and analysis examples
🏈 Why PostgreSQL is Perfect for This:
Robust Relationships: Handle complex fantasy football data relationships
JSON Support: Store flexible API responses and settings
Analytics Ready: Excellent integration with pandas and data science tools
Scalable: Handles growing datasets as your league history expands
Time Series: Perfect for tracking player performance over time
The foundation is solid and ready for your fantasy football analytics! The Sleeper API is already working, and you just need to configure PostgreSQL to start collecting and analyzing data.

## License

MIT License
