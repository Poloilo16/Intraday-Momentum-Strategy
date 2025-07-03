import pandas as pd
import numpy as np
import yfinance as yf

# Download 30-min interval data for 14 days
data = yf.download("^GSPC", period="14d", interval="30m")
if data is None or data.empty:
    raise ValueError("No data was downloaded. Please check the ticker or your internet connection.")
data.index = pd.to_datetime(data.index)
data['Date'] = data.index.to_series().dt.date
data['Time'] = data.index.to_series().dt.time

all_bounds = []

dates = sorted(data['Date'].unique())
OPEN_TIME_UTC = pd.to_datetime("13:30").time()  # 9:30 NY time in UTC
CLOSE_TIME_UTC = pd.to_datetime("19:30").time() # 16:00 NY time in UTC

for i in range(1, len(dates)):
    today = dates[i]
    yesterday = dates[i-1]
    today_group = data[data['Date'] == today]
    yesterday_group = data[data['Date'] == yesterday]

    # Robust open selection for today
    if OPEN_TIME_UTC in list(today_group['Time']):
        today_open_row = today_group[today_group['Time'] == OPEN_TIME_UTC]
    else:
        first_time = today_group['Time'].min()
        today_open_row = today_group[today_group['Time'] == first_time]

    # Robust close selection for yesterday
    if CLOSE_TIME_UTC in list(yesterday_group['Time']):
        yesterday_close_row = yesterday_group[yesterday_group['Time'] == CLOSE_TIME_UTC]
    else:
        last_time = yesterday_group['Time'].max()
        yesterday_close_row = yesterday_group[yesterday_group['Time'] == last_time]

    if today_open_row.shape[0] > 0 and yesterday_close_row.shape[0] > 0:
        today_open = float(today_open_row['Open'].iloc[0])
        yesterday_close = float(yesterday_close_row['Close'].iloc[0])
    else:
        continue

    # Calculate sigma as mean absolute return of previous N days
    N = min(13, i)
    returns = []
    for j in range(i-N, i):
        prev_day = dates[j]
        prev_group = data[data['Date'] == prev_day]
        # Robust open for prev_day
        if OPEN_TIME_UTC in list(prev_group['Time']):
            prev_open_row = prev_group[prev_group['Time'] == OPEN_TIME_UTC]
        else:
            first_time = prev_group['Time'].min()
            prev_open_row = prev_group[prev_group['Time'] == first_time]
        # Robust close for prev_day
        if CLOSE_TIME_UTC in list(prev_group['Time']):
            prev_close_row = prev_group[prev_group['Time'] == CLOSE_TIME_UTC]
        else:
            last_time = prev_group['Time'].max()
            prev_close_row = prev_group[prev_group['Time'] == last_time]
        if prev_open_row.shape[0] == 0 or prev_close_row.shape[0] == 0:
            continue
        prev_open = prev_open_row['Open'].iloc[0]
        prev_close = prev_close_row['Close'].iloc[0]
        returns.append(abs(prev_close / prev_open - 1))
    if len(returns) == 0:
        continue
    sigma = np.mean(returns)

    base_upper = max(today_open, yesterday_close)
    base_lower = min(today_open, yesterday_close)
    upper = base_upper * (1 + sigma)
    lower = base_lower * (1 - sigma)

    all_bounds.append({
        'Date': today,
        'Sigma': sigma,
        'UpperBound': upper,
        'LowerBound': lower
    })

# Create DataFrame
bounds_df = pd.DataFrame(all_bounds)
bounds_df.to_csv('daily_noise_bounds.csv', index=False)
print(bounds_df)