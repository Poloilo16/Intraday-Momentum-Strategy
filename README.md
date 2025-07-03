# Bounds Trading Strategy

## Overview
This project implements a trading strategy that:
- **Goes LONG when price breaks above upper bound**
- **Goes SHORT when price breaks below lower bound**
- Tests the strategy on S&P 500 30-minute data

## Files in This Project
- `backtest.py` - Basic trading strategy
- `enhanced_backtest.py` - Improved strategy with risk management
- `sp500_30min_14d.csv` - Price data
- `daily_noise_bounds.csv` - Trading bounds data

## How to Run

### Step 1: Install Python Packages
```bash
pip install pandas matplotlib numpy
```

### Step 2: Run the Strategy
```bash
# Basic version
python3 backtest.py

# Enhanced version (recommended)
python3 enhanced_backtest.py
```

## Results

The enhanced strategy achieved:
- **Return**: +0.17% (vs -0.48% for basic version)
- **Win Rate**: 33.3% (vs 22.2% for basic version)
- **Risk Control**: 0.24% maximum drawdown

## What You'll See

When you run the backtest, you'll get:
1. Trade entries and exits printed to console
2. Performance summary with returns and win rate
3. Chart files saved as PNG images

## Strategy Logic

1. Calculate upper and lower bounds using historical volatility
2. When price goes above upper bound → Enter LONG position
3. When price goes below lower bound → Enter SHORT position
4. Exit at market close or when opposite signal occurs

## Enhanced Features

The enhanced version includes:
- 1.5% stop loss protection
- Better position sizing
- Reduced false signals
- Risk management

## Example Output
```
LONG entry at 2025-06-16 13:30:00: Price=6036.65, Upper=6021.35
EXIT Market Close: PnL=$-49.19, New AUM=$99950.81
SHORT entry at 2025-06-17 17:30:00: Price=5987.51, Lower=5991.35
EXIT Market Close: PnL=$81.61, New AUM=$100032.43

=== BACKTEST RESULTS ===
Final AUM: $100,166.29
Total Return: 0.17%
Number of Trades: 6
Win Rate: 33.3%
```

## Requirements
- Python 3.x
- pandas
- matplotlib  
- numpy

All packages can be installed with: `pip install pandas matplotlib numpy`

## What the Strategy Does
- Calculates dynamic trading bounds based on volatility
- Identifies breakout points above/below these bounds
- Executes long/short trades automatically
- Manages risk with stop losses and position sizing
- Tracks performance and generates reports

This is a complete backtesting system that shows whether the bounds trading approach works on historical S&P 500 data.