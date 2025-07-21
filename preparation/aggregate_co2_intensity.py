import pandas as pd
import glob
from pathlib import Path
from collections import defaultdict

# Define the path to the directory containing the CSV files
base_path = Path(__file__).parent.parent
raw_path = base_path / 'extra_data' / 'co2_emissions' / 'raw_data'
all_files = list(raw_path.glob('*_hourly.csv'))
print(f"Found {len(list(all_files))} files in {raw_path}")

# 2. prepare a container to collect per‑year series
series_by_year = defaultdict(list)

for file in all_files:
    # 2a. parse country code and year from filename, e.g. "AL_2021_hourly.csv
    country, year, _ = file.stem.split('_')
    print(f"Processing {file} for country {country} in year {year}")
    
    # 2b. read CSV with the UTC datetime column as index
    df = pd.read_csv(
        file,
        index_col=0,
        parse_dates=True,
    )
    
    # 2c. pull out the Carbon intensity (direct) series and rename
    column = df['Carbon intensity gCO₂eq/kWh (direct)'].rename(country)
    
    # 2d. store it under its year
    series_by_year[year].append(column)

# 3. for each year, concat all country‑series side by side and export
out_path = base_path / 'extra_data' / 'co2_emissions' / 'aggregated_data'
out_path.mkdir(parents=True, exist_ok=True)

for year, series_list in series_by_year.items():
    # align on the union of all timestamps
    year_df = pd.concat(series_list, axis=1)
    
    # optional: sort the index and columns
    year_df = year_df.sort_index().sort_index(axis=1)
    
    # 4. write to CSV
    out_file =out_path / f'co2_intensity_{year}.csv'
    year_df.to_csv(out_file, index_label='DateTime (UTC)')
    print(f"Written {out_file} with shape {year_df.shape}")