import pandas as pd
import glob
import os
import holidays

def prepare_ieso_data():
    raw_energy_dir = 'data/ieso/raw'
    output_dir = 'data/ieso'
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Load and aggregate IESO energy data
    print("Finding raw IESO energy files...")
    energy_files = sorted(glob.glob(os.path.join(raw_energy_dir, 'PUB_HourlyConsumptionByFSA_*.csv')))
    print(f"Found {len(energy_files)} raw files. Aggregating Toronto demand (FSA starting with 'M')...")
    
    df_energy_list = []
    for f in energy_files:
        basename = os.path.basename(f)
        print(f"Processing {basename}...")
        
        # Robustly find the header line index to skip server/database warnings
        header_line = 0
        with open(f, 'r', encoding='utf-8', errors='ignore') as file_ref:
            for idx, line in enumerate(file_ref):
                if 'FSA,DATE,HOUR' in line:
                    header_line = idx
                    break
                    
        df_month = pd.read_csv(f, skiprows=header_line)
        
        # Filter for FSAs starting with 'M' (Toronto region)
        df_toronto = df_month[df_month['FSA'].str.startswith('M', na=False)].copy()
        
        # Group by DATE and HOUR, sum TOTAL_CONSUMPTION
        df_grouped = df_toronto.groupby(['DATE', 'HOUR'])['TOTAL_CONSUMPTION'].sum().reset_index()
        
        # Convert HOUR (Hour Ending, 1-24) to Beginning of Hour (0-23)
        df_grouped['hour_beginning'] = df_grouped['HOUR'] - 1
        df_grouped['timestamp'] = pd.to_datetime(df_grouped['DATE']) + pd.to_timedelta(df_grouped['hour_beginning'], unit='h')
        
        df_clean = df_grouped[['timestamp', 'TOTAL_CONSUMPTION']].rename(columns={'TOTAL_CONSUMPTION': 'energy'})
        df_energy_list.append(df_clean)
        
    df_energy = pd.concat(df_energy_list, ignore_index=True)
    df_energy = df_energy.sort_values('timestamp').set_index('timestamp')
    
    # Resample to ensure hourly frequency continuity and interpolate gaps
    df_energy = df_energy.resample('h').mean().interpolate()
    df_energy = df_energy.reset_index()
    
    # Save univariate data
    univariate_path = os.path.join(output_dir, 'ieso_toronto_univariate_2023_2025.csv')
    df_energy.to_csv(univariate_path, index=False)
    print(f"Saved univariate energy data to {univariate_path} ({len(df_energy)} rows)")
    
    # 2. Load and process weather data
    weather_file = os.path.join(raw_energy_dir, 'open-meteo-toronto-2023-2025.csv')
    print(f"Loading weather data from {weather_file}...")
    df_weather = pd.read_csv(weather_file, skiprows=3)
    
    df_weather['timestamp'] = pd.to_datetime(df_weather['time'])
    df_weather = df_weather.rename(columns={
        'temperature_2m (°C)': 'temp',
        'relative_humidity_2m (%)': 'humidity',
        'dew_point_2m (°C)': 'dew_point',
        'apparent_temperature (°C)': 'apparent_temp',
        'wind_speed_10m (km/h)': 'wind_speed',
        'cloud_cover (%)': 'cloud_cover',
        'precipitation (mm)': 'precip',
        'shortwave_radiation (W/m²)': 'radiation'
    })
    
    cols = ['timestamp', 'temp', 'humidity', 'dew_point', 'apparent_temp', 'wind_speed', 'cloud_cover', 'precip', 'radiation']
    df_weather = df_weather[cols].set_index('timestamp')
    df_weather = df_weather.resample('h').mean().interpolate()
    df_weather = df_weather.reset_index()
    
    # 3. Merge datasets
    print("Merging energy and weather data...")
    df_covariate = pd.merge(df_energy, df_weather, on='timestamp', how='inner')
    
    # 4. Add Calendar Features (Ontario Holidays)
    print("Adding Ontario calendar features...")
    on_holidays = holidays.CA(prov='ON')
    
    df_covariate['day_of_week'] = df_covariate['timestamp'].dt.dayofweek  # 0=Monday, 6=Sunday
    df_covariate['is_holiday'] = df_covariate['timestamp'].apply(lambda x: 1 if x in on_holidays else 0)
    
    # Save covariate data
    covariate_path = os.path.join(output_dir, 'ieso_toronto_covariate_2023_2025.csv')
    df_covariate.to_csv(covariate_path, index=False)
    print(f"Saved covariate data to {covariate_path} ({len(df_covariate)} rows)")
    print("IESO Toronto data preparation complete!")

if __name__ == '__main__':
    prepare_ieso_data()
