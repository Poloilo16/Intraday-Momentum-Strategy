import pandas as pd
import matplotlib.pyplot as plt

# Load your data
price_df = pd.read_csv('sp500_30min_14d.csv')
bounds_df = pd.read_csv('daily_noise_bounds.csv')

# Prepare datetime if possible
if 'Datetime' in price_df.columns:
    price_df['Datetime'] = pd.to_datetime(price_df['Datetime'])
else:
    # If not, try to create from Date and Time if available
    if 'Date' in price_df.columns and 'Time' in price_df.columns:
        price_df['Datetime'] = pd.to_datetime(price_df['Date'] + ' ' + price_df['Time'])
    else:
        # Fallback: create a fake Datetime from Date only (may not be accurate for plotting)
        price_df['Datetime'] = pd.to_datetime(price_df['Date'])

# Add Date and Time columns for merging
if 'Datetime' in price_df.columns:
    price_df['Date'] = price_df['Datetime'].dt.date
    price_df['Time'] = price_df['Datetime'].dt.strftime('%H:%M')
else:
    price_df['Date'] = pd.to_datetime(price_df['Date']).dt.date

bounds_df['Date'] = pd.to_datetime(bounds_df['Date']).dt.date

merged = pd.merge(price_df, bounds_df, on='Date', how='inner')
merged = merged.sort_values('Datetime')

INITIAL_AUM = 100_000
COMMISSION_PER_SHARE = 0.0035
SLIPPAGE_PER_SHARE = 0.001

aum = INITIAL_AUM
position = 0  # 0 = flat, 1 = long, -1 = short
entry_price = None
entry_time = None
shares = 0
trade_log = []
equity_curve = []
equity_times = []

for idx, row in merged.iterrows():
    t = row['Time']
    dt = row['Datetime']
    price = row['Close']
    open_price = row['Open']
    upper = row['UpperBound']
    lower = row['LowerBound']

    # Position sizing at market open
    if t == '09:30' and position == 0:
        shares = int(aum / open_price)

    # Entry logic
    if position == 0:
        if price > upper:
            position = 1
            entry_price = float(price + SLIPPAGE_PER_SHARE)
            entry_time = dt
            entry_shares = shares
        elif price < lower:
            position = -1
            entry_price = float(price - SLIPPAGE_PER_SHARE)
            entry_time = dt
            entry_shares = shares

    # Exit at market close
    if position != 0 and t == '16:00':
        if entry_price is None:
            continue
        exit_price = float(price - SLIPPAGE_PER_SHARE * position)
        exit_time = dt
        if position == 1:
            pnl = (exit_price - entry_price) * entry_shares - COMMISSION_PER_SHARE * entry_shares * 2
        else:
            pnl = (entry_price - exit_price) * entry_shares - COMMISSION_PER_SHARE * entry_shares * 2
        aum += pnl
        trade_log.append({
            'Entry Time': entry_time, 'Entry Price': entry_price,
            'Exit Time': exit_time, 'Exit Price': exit_price,
            'PnL': pnl, 'Position': 'Long' if position == 1 else 'Short', 'Shares': entry_shares
        })
        position = 0
        entry_price = None
        entry_time = None
        shares = int(aum / open_price)
    equity_curve.append(aum)
    equity_times.append(dt)

trades_df = pd.DataFrame(trade_log)

# Plot equity curve
plt.figure(figsize=(12, 6))
plt.plot(equity_times, equity_curve)
plt.title('Equity Curve (Daily Bounds, No Stop Loss)')
plt.xlabel('Time')
plt.ylabel('AUM ($)')
plt.grid(True)
plt.tight_layout()
plt.show()

print(trades_df)
