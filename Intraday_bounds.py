import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Download 30-min interval data for 14 days
data = yf.download("^GSPC", period="14d", interval="30m")
if data is None or data.empty:
    raise ValueError("No data was downloaded. Please check the ticker or your internet connection.")
data.index = pd.to_datetime(data.index)
data['Date'] = data.index.to_series().dt.date
data['Time'] = data.index.to_series().dt.time

# Step 1: Split into days
grouped = data.groupby('Date')
dates = list(grouped.groups.keys())

# Prepare dict to store σ per HH:MM
sigma_dict = {}

# Set open and close times in UTC (Yahoo Finance default)
OPEN_TIME_UTC = pd.to_datetime("13:30").time()
CLOSE_TIME_UTC = pd.to_datetime("19:30").time()

# Step 2: For each HH:MM, compute move_t-1 for 13 prior days
times = sorted(set(data['Time']))
for time in times:
    moves = []
    for i in range(1, len(dates)):
        day = dates[i - 1]
        day_group = grouped.get_group(day)
        open_utc_row = day_group[day_group['Time'] == OPEN_TIME_UTC]
        close_row = day_group[day_group['Time'] == time]
        if open_utc_row.shape[0] == 0:
            # Use earliest available time
            first_time = day_group['Time'].min()
            open_utc_row = day_group[day_group['Time'] == first_time]
        if not isinstance(open_utc_row, pd.DataFrame) or not isinstance(close_row, pd.DataFrame):
            continue
        if open_utc_row.shape[0] > 0 and close_row.shape[0] > 0:
            open_utc = open_utc_row['Open'].iloc[0]
            close = close_row['Close'].iloc[0]
            move = abs(close / open_utc - 1)
            moves.append(move)
    if len(moves) >= 10:
        sigma_dict[time] = np.mean(moves)

# Step 3: Get today's open and yesterday's close
today = dates[-1]
yesterday = dates[-2]

today_group = grouped.get_group(today)
yesterday_group = grouped.get_group(yesterday)

print("Today's available times:", pd.unique(today_group['Time']))
print("Yesterday's available times:", pd.unique(yesterday_group['Time']))

# Robust open and close selection
if OPEN_TIME_UTC in list(today_group['Time']):
    today_open_row = today_group[today_group['Time'] == OPEN_TIME_UTC]
else:
    first_time = today_group['Time'].min()
    today_open_row = today_group[today_group['Time'] == first_time]

if CLOSE_TIME_UTC in list(yesterday_group['Time']):
    yesterday_close_row = yesterday_group[yesterday_group['Time'] == CLOSE_TIME_UTC]
else:
    last_time = yesterday_group['Time'].max()
    yesterday_close_row = yesterday_group[yesterday_group['Time'] == last_time]

if not isinstance(today_open_row, pd.DataFrame) or not isinstance(yesterday_close_row, pd.DataFrame):
    raise ValueError("Open/close row is not a DataFrame.")
if today_open_row.shape[0] > 0 and yesterday_close_row.shape[0] > 0:
    today_open = float(today_open_row['Open'].iloc[0])
    yesterday_close = float(yesterday_close_row['Close'].iloc[0])
    print("today_open type:", type(today_open), "value:", today_open)
    print("yesterday_close type:", type(yesterday_close), "value:", yesterday_close)
else:
    raise ValueError("Missing today's open or yesterday's close data, even after fallback.")

# Step 4: Compute Upper and Lower Bounds for today using the specified formulas
upper_bounds = {}
lower_bounds = {}

# Use today_open as Open_{t,9:30} and yesterday_close as Close_{t-1,16:00}
for time, sigma in sigma_dict.items():
    base_upper = max(today_open, yesterday_close)
    upper = base_upper * (1 + sigma)
    
    base_lower = min(today_open, yesterday_close)
    lower = base_lower * (1 - sigma)
    
    upper_bounds[time] = upper
    lower_bounds[time] = lower

# Combine to DataFrame
noise_df = pd.DataFrame({
    'Time': list(sigma_dict.keys()),
    'Sigma': list(sigma_dict.values()),
    'UpperBound': list(upper_bounds.values()),
    'LowerBound': list(lower_bounds.values())
})

print(noise_df)



noise_df = pd.DataFrame({
    'Time': list(sigma_dict.keys()),
    'Sigma': list(sigma_dict.values()),
    'UpperBound': list(upper_bounds.values()),
    'LowerBound': list(lower_bounds.values())
})
# Calculate move from open as a percentage
open_price = today_open  # already defined in your script

noise_df['UpperPct'] = (noise_df['UpperBound'] / open_price - 1) * 100
noise_df['LowerPct'] = (noise_df['LowerBound'] / open_price - 1) * 100



# Prepare x-axis labels
times_str = [t.strftime('%H:%M') for t in noise_df['Time']]

plt.figure(figsize=(10, 6))
plt.fill_between(times_str, noise_df['LowerPct'], noise_df['UpperPct'], color='khaki', alpha=0.7, label='Noise Area')
plt.plot(times_str, noise_df['UpperPct'], color='deepskyblue', label='Start of Trend Up')
plt.plot(times_str, noise_df['LowerPct'], color='coral', label='Start of Trend Down')

#plot yesterday's close as a horizontal line
yclose_pct = (yesterday_close / open_price - 1) * 100
plt.axhline(y=yclose_pct, color='black', linestyle='dotted')
plt.text(len(times_str) - 1, yclose_pct, 'YClosure', va='bottom', ha='right')

plt.title('Model Graphical Example')
plt.xlabel('Time of Day')
plt.ylabel('Move from Open (%)')
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()


