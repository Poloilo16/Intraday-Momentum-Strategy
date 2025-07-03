import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load your data - fix CSV parsing
price_df = pd.read_csv('sp500_30min_14d.csv', header=0, skiprows=[1, 2])  # Skip ticker and empty rows
bounds_df = pd.read_csv('daily_noise_bounds.csv')

# The 'Price' column contains the datetime, rename it
price_df = price_df.rename(columns={'Price': 'Datetime'})
price_df['Datetime'] = pd.to_datetime(price_df['Datetime'])

# Convert price columns to numeric (they might be strings)
price_df['Close'] = pd.to_numeric(price_df['Close'], errors='coerce')
price_df['Open'] = pd.to_numeric(price_df['Open'], errors='coerce')
price_df['High'] = pd.to_numeric(price_df['High'], errors='coerce')
price_df['Low'] = pd.to_numeric(price_df['Low'], errors='coerce')

# Remove any rows with NaN values
price_df = price_df.dropna()

# Add Date and Time columns for merging
price_df['Date'] = price_df['Datetime'].dt.date
price_df['Time'] = price_df['Datetime'].dt.strftime('%H:%M')

bounds_df['Date'] = pd.to_datetime(bounds_df['Date']).dt.date

merged = pd.merge(price_df, bounds_df, on='Date', how='inner')
merged = merged.sort_values('Datetime')

print(f"Loaded {len(merged)} data points from {merged['Date'].nunique()} trading days")
print(f"Date range: {merged['Date'].min()} to {merged['Date'].max()}")

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
    if t == '13:30' and position == 0:  # Market opens at 13:30 UTC
        shares = int(aum / open_price)

    # Entry logic: buy (call) when above upper bound, short when below lower bound
    if position == 0:
        if price > upper:
            # Go long (call)
            position = 1
            entry_price = float(price + SLIPPAGE_PER_SHARE)
            entry_time = dt
            entry_shares = shares
            print(f"LONG entry at {dt}: Price={price:.2f}, Upper={upper:.2f}, Entry={entry_price:.2f}")
        elif price < lower:
            # Go short
            position = -1
            entry_price = float(price - SLIPPAGE_PER_SHARE)
            entry_time = dt
            entry_shares = shares
            print(f"SHORT entry at {dt}: Price={price:.2f}, Lower={lower:.2f}, Entry={entry_price:.2f}")

    # Exit at market close or if position reverses
    should_exit = False
    exit_reason = ""
    
    if position != 0 and t == '19:30':  # Market closes at 19:30 UTC
        should_exit = True
        exit_reason = "Market Close"
    elif position == 1 and price < lower:  # Long position hits lower bound
        should_exit = True
        exit_reason = "Long -> Short Signal"
    elif position == -1 and price > upper:  # Short position hits upper bound
        should_exit = True
        exit_reason = "Short -> Long Signal"
    
    if should_exit and entry_price is not None:
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
            'PnL': pnl, 'Position': 'Long' if position == 1 else 'Short', 
            'Shares': entry_shares, 'Exit Reason': exit_reason
        })
        print(f"EXIT {exit_reason}: PnL=${pnl:.2f}, New AUM=${aum:.2f}")
        
        # Check for immediate re-entry on signal reversal
        if exit_reason in ["Long -> Short Signal", "Short -> Long Signal"]:
            if exit_reason == "Long -> Short Signal":
                position = -1
                entry_price = float(price - SLIPPAGE_PER_SHARE)
                entry_time = dt
                entry_shares = int(aum / open_price)
                print(f"IMMEDIATE SHORT entry at {dt}: Price={price:.2f}")
            else:  # "Short -> Long Signal"
                position = 1
                entry_price = float(price + SLIPPAGE_PER_SHARE)
                entry_time = dt
                entry_shares = int(aum / open_price)
                print(f"IMMEDIATE LONG entry at {dt}: Price={price:.2f}")
        else:
            position = 0
            entry_price = None
            entry_time = None
            shares = int(aum / open_price) if open_price > 0 else 0
            
    equity_curve.append(aum)
    equity_times.append(dt)

trades_df = pd.DataFrame(trade_log)

# Calculate performance metrics
total_return = (aum - INITIAL_AUM) / INITIAL_AUM * 100
num_trades = len(trades_df)
win_rate = len(trades_df[trades_df['PnL'] > 0]) / num_trades * 100 if num_trades > 0 else 0

print(f"\n=== BACKTEST RESULTS ===")
print(f"Initial AUM: ${INITIAL_AUM:,.2f}")
print(f"Final AUM: ${aum:,.2f}")
print(f"Total Return: {total_return:.2f}%")
print(f"Number of Trades: {num_trades}")
print(f"Win Rate: {win_rate:.1f}%")

if num_trades > 0:
    print(f"Average PnL per Trade: ${trades_df['PnL'].mean():.2f}")
    print(f"Best Trade: ${trades_df['PnL'].max():.2f}")
    print(f"Worst Trade: ${trades_df['PnL'].min():.2f}")

# Plot equity curve
plt.figure(figsize=(15, 8))
plt.subplot(2, 1, 1)
plt.plot(equity_times, equity_curve)
plt.title('Equity Curve - Bounds Trading Strategy')
plt.xlabel('Time')
plt.ylabel('AUM ($)')
plt.grid(True)

# Plot price with bounds
plt.subplot(2, 1, 2)
plt.plot(merged['Datetime'], merged['Close'], label='S&P 500 Price', alpha=0.7)
plt.plot(merged['Datetime'], merged['UpperBound'], label='Upper Bound', color='red', linestyle='--')
plt.plot(merged['Datetime'], merged['LowerBound'], label='Lower Bound', color='green', linestyle='--')

# Mark trade entries
if num_trades > 0:
    long_entries = trades_df[trades_df['Position'] == 'Long']
    short_entries = trades_df[trades_df['Position'] == 'Short']
    
    if len(long_entries) > 0:
        plt.scatter(long_entries['Entry Time'], long_entries['Entry Price'], 
                   color='green', marker='^', s=100, label='Long Entry', zorder=5)
    if len(short_entries) > 0:
        plt.scatter(short_entries['Entry Time'], short_entries['Entry Price'], 
                   color='red', marker='v', s=100, label='Short Entry', zorder=5)

plt.title('Price Action with Trading Signals')
plt.xlabel('Time')
plt.ylabel('Price')
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('backtest_results.png', dpi=150, bbox_inches='tight')
plt.show()

print(f"\n=== TRADE LOG ===")
if num_trades > 0:
    print(trades_df.to_string(index=False))
else:
    print("No trades executed")
