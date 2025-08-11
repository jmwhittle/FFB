"""
Check what columns are in the nfl_data_py weekly data to update our model.
"""

import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

import nfl_data_py as nfl
import pandas as pd

# Get a sample of the data to see all columns
print("Fetching sample data to check columns...")
sample_data = nfl.import_weekly_data(years=[2024])

print(f"Total columns: {len(sample_data.columns)}")
print(f"Column names:")
for col in sorted(sample_data.columns):
    print(f"  {col}")

print("\nColumn data types:")
print(sample_data.dtypes)

print("\nSample data shape:", sample_data.shape)
print("\nFirst few rows:")
print(sample_data.head())
