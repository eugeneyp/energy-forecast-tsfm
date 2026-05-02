import pandas as pd
import os

def prepare_data():
    ercot_file = 'data/ercot/raw/ercot_2026_jan-mar.xlsx'
    weather_file = 'data/ercot/raw/open-meteo-dallas-2026-jan-apr.csv'
    
    # 1. Load ERCOT data
    print(f"Loading {ercot_file}...")
    df_ercot = pd.read_excel(ercot_file)
    
    # Extract timestamp and NCENT (Dallas)
    # ERCOT format is MM/DD/YYYY HH:MM for 'Hour Ending'
    # Special case: ERCOT uses 24:00 for the last hour of the day.
    def parse_ercot_datetime(s):
        if s.endswith('24:00'):
            # "01/01/2026 24:00" -> "01/01/2026 23:00" (Beginning of Hour)
            return pd.to_datetime(s.replace('24:00', '00:00')) + pd.Timedelta(days=1) - pd.Timedelta(hours=1)
        else:
            # "01/01/2026 01:00" -> "01/01/2026 00:00" (Beginning of Hour)
            return pd.to_datetime(s) - pd.Timedelta(hours=1)

    df_ercot['timestamp'] = df_ercot['Hour Ending'].apply(parse_ercot_datetime)
    
    # Prepare univariate dataframe
    df_univariate = df_ercot[['timestamp', 'NCENT']].copy()
    df_univariate.rename(columns={'NCENT': 'energy'}, inplace=True)
    
    # Save univariate
    univariate_output = 'data/ercot_dallas_univariate_2026.csv'
    df_univariate.to_csv(univariate_output, index=False)
    print(f"Saved univariate data to {univariate_output}")
    
    # 2. Load Weather data
    print(f"Loading {weather_file}...")
    # Skipping 3 lines based on observation: metadata line 1, metadata line 2, and blank line
    df_weather = pd.read_csv(weather_file, skiprows=3)
    
    # Convert 'time' to datetime
    df_weather['timestamp'] = pd.to_datetime(df_weather['time'])
    
    # 3. Merge data
    print("Merging data...")
    # Inner join to ensure we only have rows where both energy and weather data exist
    df_covariate = pd.merge(df_univariate, df_weather, on='timestamp', how='inner')
    
    # 4. Add Calendar Features (Categorical Covariates)
    print("Adding calendar features...")
    import holidays
    # Use Texas-specific holidays for Dallas energy load
    tx_holidays = holidays.US(state='TX')
    
    df_covariate['day_of_week'] = df_covariate['timestamp'].dt.dayofweek  # 0=Monday, 6=Sunday
    df_covariate['is_holiday'] = df_covariate['timestamp'].apply(lambda x: 1 if x in tx_holidays else 0)
    
    # Remove the extra 'time' column from weather file as we have 'timestamp'
    if 'time' in df_covariate.columns:
        df_covariate.drop(columns=['time'], inplace=True)
    
    # Save covariate
    covariate_output = 'data/ercot_dallas_covariate_2026.csv'
    df_covariate.to_csv(covariate_output, index=False)
    print(f"Saved covariate data to {covariate_output}")
    
    print("Data preparation complete.")

if __name__ == "__main__":
    prepare_data()
