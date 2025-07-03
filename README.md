# Bounds Trading Strategy - S&P 500 Backtesting Project

## Overview

This project implements and backtests a **bounds trading strategy** for the S&P 500 index using 30-minute intraday data. The strategy identifies dynamic upper and lower bounds based on historical volatility and executes trades when price breaks through these levels.

## Strategy Description

### Trading Rules
- **📈 LONG (Call)**: Enter long position when price moves **above the upper bound**
- **📉 SHORT**: Enter short position when price moves **below the lower bound**
- **🚪 EXIT**: Close positions at market close (19:30 UTC) or on signal reversal
- **⚠️ RISK**: Stop losses and position sizing for risk management

### Bounds Calculation
The bounds are calculated using:
- Historical volatility (sigma) for each 30-minute time slot
- Previous day's close and current day's open prices
- **Upper Bound**: `max(today_open, yesterday_close) × (1 + sigma)`
- **Lower Bound**: `min(today_open, yesterday_close) × (1 - sigma)`

## Files Description

### Core Strategy Files
- **`backtest.py`** - Original bounds trading strategy implementation
- **`enhanced_backtest.py`** - Improved version with stop losses and risk management
- **`Intraday_bounds.py`** - Bounds calculation logic and visualization
- **`2_week_bounds.py`** - Alternative bounds calculation method

### Data Files
- **`sp500_30min_14d.csv`** - S&P 500 30-minute price data (14 days)
- **`daily_noise_bounds.csv`** - Pre-calculated daily bounds
- **`noise_bounds_sample.csv`** - Sample bounds data

### Results & Documentation
- **`backtest_results.png`** - Original strategy performance charts
- **`enhanced_backtest_results.png`** - Enhanced strategy performance charts
- **`Model_Graphical_example.png`** - Bounds visualization example
- **`backtest_summary.md`** - Original strategy analysis
- **`final_strategy_report.md`** - Comprehensive strategy comparison and analysis

## Quick Start

### Prerequisites
```bash
pip install pandas matplotlib numpy
```

### Run the Backtest
```bash
# Original strategy
python3 backtest.py

# Enhanced strategy (recommended)
python3 enhanced_backtest.py
```

### Generate Bounds
```bash
# Calculate intraday bounds
python3 Intraday_bounds.py
```

## Performance Results

| Strategy | Return | Win Rate | Trades | Max Drawdown | Profit Factor |
|----------|--------|----------|--------|--------------|---------------|
| **Original** | -0.48% | 22.2% | 9 | N/A | N/A |
| **Enhanced** | **+0.17%** | **33.3%** | 6 | **0.24%** | **1.57** |

### Key Improvements in Enhanced Strategy
- ✅ **1.5% Stop Loss** - Limits downside risk
- ✅ **0.05% Bounds Buffer** - Reduces false breakouts  
- ✅ **95% Position Sizing** - Controls exposure
- ✅ **Profit Factor 1.57** - Indicates profitability

## Data Period
- **Instrument**: S&P 500 Index (^GSPC)
- **Timeframe**: 30-minute intervals
- **Period**: June 16 - July 2, 2025 (12 trading days)
- **Data Points**: 156 observations

## Key Features

### Risk Management
- Stop loss implementation (1.5% of entry price)
- Position sizing based on available capital
- Maximum drawdown monitoring
- Commission and slippage modeling

### Signal Quality
- Bounds buffering to avoid false breakouts
- High/Low data utilization for stop triggers
- Market session timing (13:30-19:30 UTC)
- Signal reversal detection

### Performance Analytics
- Win rate and profit factor calculation
- Maximum drawdown analysis
- Trade-by-trade logging
- Comprehensive visualization

## Strategy Logic Flow

1. **Market Open** (13:30 UTC) → Calculate position size
2. **Price Monitoring** → Check for bound breakouts
3. **Entry Signal** → Execute trade with stop loss
4. **Exit Conditions** → Market close or signal reversal
5. **Performance Tracking** → Log trade and update equity

## Usage Examples

### Basic Backtest
```python
# Load and run basic strategy
python3 backtest.py
```

### Enhanced Strategy with Risk Management
```python
# Run enhanced version
python3 enhanced_backtest.py
```

### Visualize Bounds
```python
# Generate bounds chart
python3 Intraday_bounds.py
```

## Results Summary

The **enhanced bounds trading strategy** demonstrates:
- ✅ **Positive Returns**: +0.17% over 12 trading days
- ✅ **Controlled Risk**: Maximum drawdown of only 0.24%
- ✅ **Profitable System**: Profit factor of 1.57
- ✅ **Risk Management**: No stop loss triggers needed

## Next Steps

1. **Extend Backtesting** - Test on longer time periods
2. **Parameter Optimization** - Fine-tune bounds calculation
3. **Market Regime Detection** - Adapt to different market conditions
4. **Paper Trading** - Validate real-time performance

## Technical Requirements

- **Python 3.x**
- **pandas** - Data manipulation
- **matplotlib** - Visualization  
- **numpy** - Numerical calculations

## Contributing

This project demonstrates systematic trading strategy development with:
- Data preprocessing and cleaning
- Strategy implementation and backtesting
- Risk management and position sizing
- Performance analysis and reporting

---

**⚠️ Disclaimer**: This is for educational and research purposes only. Past performance does not guarantee future results. Always conduct thorough testing before live trading.

*Last updated: July 3, 2025*