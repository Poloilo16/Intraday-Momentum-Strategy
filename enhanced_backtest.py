import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load your data - fix CSV parsing
price_df = pd.read_csv('sp500_30min_14d.csv', header=0, skiprows=[1, 2])
bounds_df = pd.read_csv('daily_noise_bounds.csv')

# The 'Price' column contains the datetime, rename it
price_df = price_df.rename(columns={'Price': 'Datetime'})
price_df['Datetime'] = pd.to_datetime(price_df['Datetime'])

# Convert price columns to numeric
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

print(f"Enhanced Strategy: Loaded {len(merged)} data points from {merged['Date'].nunique()} trading days")

# Enhanced Parameters
INITIAL_AUM = 100_000
COMMISSION_PER_SHARE = 0.0035
SLIPPAGE_PER_SHARE = 0.001
STOP_LOSS_PCT = 0.015  # 1.5% stop loss
MAX_POSITION_SIZE = 0.95  # Use max 95% of AUM per trade
BOUNDS_BUFFER = 0.0005  # 0.05% buffer to avoid false breakouts

# Enhanced variables
aum = INITIAL_AUM
position = 0  # 0 = flat, 1 = long, -1 = short
entry_price = None
entry_time = None
shares = 0
stop_loss_price = None
trade_log = []
equity_curve = []
equity_times = []

for idx, row in merged.iterrows():
    t = row['Time']
    dt = row['Datetime']
    price = row['Close']
    open_price = row['Open']
    high_price = row['High']
    low_price = row['Low']
    upper = row['UpperBound']
    lower = row['LowerBound']
    
    # Add buffer to bounds to reduce false signals
    upper_buffered = upper * (1 + BOUNDS_BUFFER)
    lower_buffered = lower * (1 - BOUNDS_BUFFER)

    # Position sizing - use volatility-adjusted sizing
    if position == 0:
        max_shares = int((aum * MAX_POSITION_SIZE) / price)
        shares = max_shares

    # Check stop loss first
    should_exit = False
    exit_reason = ""
    exit_price = price
    
    if position != 0 and stop_loss_price is not None:
        if position == 1 and low_price <= stop_loss_price:  # Long stop loss
            should_exit = True
            exit_reason = "Stop Loss"
            exit_price = stop_loss_price
        elif position == -1 and high_price >= stop_loss_price:  # Short stop loss
            should_exit = True
            exit_reason = "Stop Loss"
            exit_price = stop_loss_price

    # Entry logic with buffered bounds
    if position == 0 and not should_exit:
        if price > upper_buffered:
            # Go long (call)
            position = 1
            entry_price = float(price + SLIPPAGE_PER_SHARE)
            entry_time = dt
            entry_shares = shares
            stop_loss_price = entry_price * (1 - STOP_LOSS_PCT)
            print(f"LONG entry at {dt}: Price={price:.2f}, Upper={upper:.2f}, Entry={entry_price:.2f}, Stop={stop_loss_price:.2f}")
        elif price < lower_buffered:
            # Go short
            position = -1
            entry_price = float(price - SLIPPAGE_PER_SHARE)
            entry_time = dt
            entry_shares = shares
            stop_loss_price = entry_price * (1 + STOP_LOSS_PCT)
            print(f"SHORT entry at {dt}: Price={price:.2f}, Lower={lower:.2f}, Entry={entry_price:.2f}, Stop={stop_loss_price:.2f}")

    # Exit conditions
    if position != 0:
        if not should_exit and t == '19:30':  # Market close
            should_exit = True
            exit_reason = "Market Close"
            exit_price = price - SLIPPAGE_PER_SHARE * position
        elif not should_exit and position == 1 and price < lower_buffered:  # Long reversal
            should_exit = True
            exit_reason = "Long -> Short Signal"
            exit_price = price - SLIPPAGE_PER_SHARE
        elif not should_exit and position == -1 and price > upper_buffered:  # Short reversal
            should_exit = True
            exit_reason = "Short -> Long Signal"
            exit_price = price + SLIPPAGE_PER_SHARE
    
    if should_exit and entry_price is not None:
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
            'Shares': entry_shares, 'Exit Reason': exit_reason,
            'Stop Loss': stop_loss_price
        })
        print(f"EXIT {exit_reason}: PnL=${pnl:.2f}, New AUM=${aum:.2f}")
        
        # Check for immediate re-entry on signal reversal
        if exit_reason in ["Long -> Short Signal", "Short -> Long Signal"]:
            max_shares = int((aum * MAX_POSITION_SIZE) / price)
            if exit_reason == "Long -> Short Signal":
                position = -1
                entry_price = float(price - SLIPPAGE_PER_SHARE)
                entry_time = dt
                entry_shares = max_shares
                stop_loss_price = entry_price * (1 + STOP_LOSS_PCT)
                print(f"IMMEDIATE SHORT entry at {dt}: Price={price:.2f}, Stop={stop_loss_price:.2f}")
            else:  # "Short -> Long Signal"
                position = 1
                entry_price = float(price + SLIPPAGE_PER_SHARE)
                entry_time = dt
                entry_shares = max_shares
                stop_loss_price = entry_price * (1 - STOP_LOSS_PCT)
                print(f"IMMEDIATE LONG entry at {dt}: Price={price:.2f}, Stop={stop_loss_price:.2f}")
        else:
            position = 0
            entry_price = None
            entry_time = None
            stop_loss_price = None
            shares = 0
            
    equity_curve.append(aum)
    equity_times.append(dt)

trades_df = pd.DataFrame(trade_log)

# Calculate enhanced performance metrics
total_return = (aum - INITIAL_AUM) / INITIAL_AUM * 100
num_trades = len(trades_df)
win_rate = len(trades_df[trades_df['PnL'] > 0]) / num_trades * 100 if num_trades > 0 else 0

# Calculate additional metrics
if num_trades > 0:
    profits = trades_df[trades_df['PnL'] > 0]['PnL']
    losses = trades_df[trades_df['PnL'] < 0]['PnL']
    avg_win = profits.mean() if len(profits) > 0 else 0
    avg_loss = losses.mean() if len(losses) > 0 else 0
    profit_factor = abs(profits.sum() / losses.sum()) if len(losses) > 0 and losses.sum() != 0 else float('inf')
    
    # Calculate maximum drawdown
    equity_series = pd.Series(equity_curve)
    rolling_max = equity_series.expanding().max()
    drawdown = (equity_series - rolling_max) / rolling_max * 100
    max_drawdown = drawdown.min()
else:
    avg_win = avg_loss = profit_factor = max_drawdown = 0

print(f"\n=== ENHANCED BACKTEST RESULTS ===")
print(f"Initial AUM: ${INITIAL_AUM:,.2f}")
print(f"Final AUM: ${aum:,.2f}")
print(f"Total Return: {total_return:.2f}%")
print(f"Number of Trades: {num_trades}")
print(f"Win Rate: {win_rate:.1f}%")
print(f"Maximum Drawdown: {max_drawdown:.2f}%")

if num_trades > 0:
    print(f"Average PnL per Trade: ${trades_df['PnL'].mean():.2f}")
    print(f"Average Win: ${avg_win:.2f}")
    print(f"Average Loss: ${avg_loss:.2f}")
    print(f"Profit Factor: {profit_factor:.2f}")
    print(f"Best Trade: ${trades_df['PnL'].max():.2f}")
    print(f"Worst Trade: ${trades_df['PnL'].min():.2f}")
    
    # Count stop loss exits
    stop_loss_exits = len(trades_df[trades_df['Exit Reason'] == 'Stop Loss'])
    print(f"Stop Loss Exits: {stop_loss_exits} ({stop_loss_exits/num_trades*100:.1f}%)")

# Plot enhanced results
plt.figure(figsize=(20, 12))

# Equity curve
plt.subplot(3, 1, 1)
plt.plot(equity_times, equity_curve, linewidth=2)
plt.title('Enhanced Strategy - Equity Curve', fontsize=14)
plt.xlabel('Time')
plt.ylabel('AUM ($)')
plt.grid(True, alpha=0.3)

# Drawdown
plt.subplot(3, 1, 2)
equity_series = pd.Series(equity_curve, index=equity_times)
rolling_max = equity_series.expanding().max()
drawdown = (equity_series - rolling_max) / rolling_max * 100
plt.fill_between(equity_times, drawdown, 0, color='red', alpha=0.3)
plt.plot(equity_times, drawdown, color='red', linewidth=1)
plt.title('Drawdown (%)', fontsize=14)
plt.xlabel('Time')
plt.ylabel('Drawdown (%)')
plt.grid(True, alpha=0.3)

# Price with bounds and signals
plt.subplot(3, 1, 3)
plt.plot(merged['Datetime'], merged['Close'], label='S&P 500 Price', alpha=0.8, linewidth=1)
plt.plot(merged['Datetime'], merged['UpperBound'], label='Upper Bound', color='red', linestyle='--', alpha=0.7)
plt.plot(merged['Datetime'], merged['LowerBound'], label='Lower Bound', color='green', linestyle='--', alpha=0.7)

# Mark trade entries and exits
if num_trades > 0:
    long_entries = trades_df[trades_df['Position'] == 'Long']
    short_entries = trades_df[trades_df['Position'] == 'Short']
    stop_loss_exits = trades_df[trades_df['Exit Reason'] == 'Stop Loss']
    
    if len(long_entries) > 0:
        plt.scatter(long_entries['Entry Time'], long_entries['Entry Price'], 
                   color='green', marker='^', s=100, label='Long Entry', zorder=5)
    if len(short_entries) > 0:
        plt.scatter(short_entries['Entry Time'], short_entries['Entry Price'], 
                   color='red', marker='v', s=100, label='Short Entry', zorder=5)
    if len(stop_loss_exits) > 0:
        plt.scatter(stop_loss_exits['Exit Time'], stop_loss_exits['Exit Price'], 
                   color='orange', marker='x', s=100, label='Stop Loss Exit', zorder=5)

plt.title('Price Action with Enhanced Trading Signals', fontsize=14)
plt.xlabel('Time')
plt.ylabel('Price')
plt.legend()
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('enhanced_backtest_results.png', dpi=150, bbox_inches='tight')
plt.show()

print(f"\n=== ENHANCED TRADE LOG ===")
if num_trades > 0:
    print(trades_df.to_string(index=False))
else:
    print("No trades executed")

# Compare with original strategy
print(f"\n=== STRATEGY COMPARISON ===")
print(f"Original Strategy Return: -0.48%")
print(f"Enhanced Strategy Return: {total_return:.2f}%")
print(f"Improvement: {total_return - (-0.48):.2f} percentage points")