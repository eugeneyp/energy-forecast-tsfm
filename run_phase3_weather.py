import pandas as pd
import numpy as np
import glob
import xgboost as xgb
import holidays
from sklearn.metrics import mean_absolute_error, mean_squared_error

def load_ercot_data():
    files = sorted(glob.glob('data/ercot/raw/ercot_20*.xlsx'))
    dfs = []
    for f in files:
        df = pd.read_excel(f)
        dfs.append(df)
    df = pd.concat(dfs, ignore_index=True)
    
    def parse_ercot_datetime(s):
        s = str(s).replace(' DST', '')
        if s.endswith('24:00'):
            return pd.to_datetime(s.replace('24:00', '00:00')) + pd.Timedelta(days=1) - pd.Timedelta(hours=1)
        else:
            return pd.to_datetime(s) - pd.Timedelta(hours=1)

    df['timestamp'] = df['Hour Ending'].apply(parse_ercot_datetime)
    df = df[['timestamp', 'NCENT']].copy()
    df.rename(columns={'NCENT': 'target'}, inplace=True)
    df = df.sort_values('timestamp').set_index('timestamp')
    df = df.resample('h').mean()
    df['target'] = df['target'].interpolate()
    return df

def load_weather_data():
    files = sorted(glob.glob('data/ercot/raw/open-meteo-dallas-*.csv'))
    dfs = []
    for f in files:
        df_w = pd.read_csv(f, skiprows=3)
        dfs.append(df_w)
    df_w = pd.concat(dfs, ignore_index=True)
    df_w['timestamp'] = pd.to_datetime(df_w['time'])
    df_w = df_w.rename(columns={
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
    df_w = df_w[cols].set_index('timestamp')
    # Force unique index just in case
    df_w = df_w.resample('h').mean().interpolate()
    return df_w

tx_holidays = holidays.US(state='TX')

def get_calendar_features(dt_index):
    features = pd.DataFrame(index=dt_index)
    features['hour'] = dt_index.hour
    features['dayofweek'] = dt_index.dayofweek
    features['is_weekend'] = (dt_index.dayofweek >= 5).astype(int)
    features['month'] = dt_index.month
    features['is_holiday'] = pd.Series(dt_index).apply(lambda x: x in tx_holidays).values.astype(int)
    return features

def calculate_metrics(y_true, y_pred, y_train):
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    smape = 100 * np.mean(2 * np.abs(y_pred - y_true) / (np.abs(y_pred) + np.abs(y_true)))
    mae_naive = mean_absolute_error(y_train[168:], y_train[:-168])
    mase = mae / mae_naive
    return {'MAE': mae, 'RMSE': rmse, 'sMAPE': smape, 'MASE': mase}

def run_phase3():
    df_load = load_ercot_data()
    df_weather = load_weather_data()
    # Join and ensure unique indices
    df = df_load.join(df_weather, how='inner')
    df = df.groupby(level=0).mean() 
    
    train_end = '2025-07-31 23:00:00'
    train_df = df[:train_end].copy()
    
    print("Training Phase 3 (Weather Aware)...")
    models_direct = {}
    lag_cols = ['feat_origin', 'feat_origin_m1', 'feat_origin_m2', 
                'feat_24h_aligned', 'feat_48h_aligned', 'feat_168h_aligned']
    cal_cols = ['target_hour', 'target_dayofweek', 'target_is_weekend', 'target_month', 'target_is_holiday']
    weather_cols = ['target_temp', 'target_humidity', 'target_dew_point', 'target_apparent_temp', 
                    'target_wind_speed', 'target_cloud_cover', 'target_precip', 'target_radiation']
    feature_cols = lag_cols + cal_cols + weather_cols
    
    for h in range(1, 25):
        df_h = df.copy()
        df_h['target_h'] = df_h['target'].shift(-h)
        
        # Lags
        df_h['feat_origin'] = df_h['target']
        df_h['feat_origin_m1'] = df_h['target'].shift(1)
        df_h['feat_origin_m2'] = df_h['target'].shift(2)
        df_h['feat_24h_aligned'] = df_h['target'].shift(24 - h)
        df_h['feat_48h_aligned'] = df_h['target'].shift(48 - h)
        df_h['feat_168h_aligned'] = df_h['target'].shift(168 - h)
        
        # Calendar (Target T+h)
        target_times = df_h.index + pd.Timedelta(hours=h)
        cal_feats = get_calendar_features(target_times)
        df_h['target_hour'] = cal_feats['hour'].values
        df_h['target_dayofweek'] = cal_feats['dayofweek'].values
        df_h['target_is_weekend'] = cal_feats['is_weekend'].values
        df_h['target_month'] = cal_feats['month'].values
        df_h['target_is_holiday'] = cal_feats['is_holiday'].values
        
        # Weather (Target T+h)
        df_h['target_temp'] = df_h['temp'].shift(-h)
        df_h['target_humidity'] = df_h['humidity'].shift(-h)
        df_h['target_dew_point'] = df_h['dew_point'].shift(-h)
        df_h['target_apparent_temp'] = df_h['apparent_temp'].shift(-h)
        df_h['target_wind_speed'] = df_h['wind_speed'].shift(-h)
        df_h['target_cloud_cover'] = df_h['cloud_cover'].shift(-h)
        df_h['target_precip'] = df_h['precip'].shift(-h)
        df_h['target_radiation'] = df_h['radiation'].shift(-h)
        
        df_h = df_h.dropna()
        train_h = df_h[:train_end]
        
        m = xgb.XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=6, random_state=42)
        m.fit(train_h[feature_cols].astype(float), train_h['target_h'])
        models_direct[h] = m
        if h % 6 == 0: print(f" Trained model for h={h}")

    def evaluate(test_df):
        all_preds = []
        all_actuals = []
        origins = test_df.index[test_df.index.hour == 0]
        for origin in origins:
            if origin + pd.Timedelta(hours=24) > df.index[-1]:
                continue
            actual = df.loc[origin + pd.Timedelta(hours=1) : origin + pd.Timedelta(hours=24), 'target'].values
            preds = []
            for h in range(1, 25):
                target_time = origin + pd.Timedelta(hours=h)
                cal = get_calendar_features(pd.DatetimeIndex([target_time]))
                # Access weather at target time
                w = df.loc[target_time]
                
                feats = pd.DataFrame([{
                    'feat_origin': df.loc[origin, 'target'],
                    'feat_origin_m1': df.loc[origin - pd.Timedelta(hours=1), 'target'],
                    'feat_origin_m2': df.loc[origin - pd.Timedelta(hours=2), 'target'],
                    'feat_24h_aligned': df.loc[origin - pd.Timedelta(hours=24-h), 'target'],
                    'feat_48h_aligned': df.loc[origin - pd.Timedelta(hours=48-h), 'target'],
                    'feat_168h_aligned': df.loc[origin - pd.Timedelta(hours=168-h), 'target'],
                    'target_hour': cal['hour'].values[0],
                    'target_dayofweek': cal['dayofweek'].values[0],
                    'target_is_weekend': cal['is_weekend'].values[0],
                    'target_month': cal['month'].values[0],
                    'target_is_holiday': cal['is_holiday'].values[0],
                    'target_temp': w['temp'],
                    'target_humidity': w['humidity'],
                    'target_dew_point': w['dew_point'],
                    'target_apparent_temp': w['apparent_temp'],
                    'target_wind_speed': w['wind_speed'],
                    'target_cloud_cover': w['cloud_cover'],
                    'target_precip': w['precip'],
                    'target_radiation': w['radiation']
                }]).astype(float)
                preds.append(models_direct[h].predict(feats[feature_cols])[0])
            all_preds.append(preds)
            all_actuals.append(actual)
        return np.array(all_actuals), np.array(all_preds)

    aug_df = df['2025-08-01 00:00:00':'2025-08-31 23:00:00']
    mar_df = df['2026-03-01 00:00:00':'2026-03-31 23:00:00']
    
    for window_name, t_df in [("August 2025", aug_df), ("March 2026", mar_df)]:
        act, pred = evaluate(t_df)
        print(f"\n{window_name}:", calculate_metrics(act.flatten(), pred.flatten(), train_df['target']))

if __name__ == "__main__":
    run_phase3()
