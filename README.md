# Intraday Momentum Bounds Trading Strategy

A quantitative trading strategy that uses volatility-based bounds to identify intraday momentum breakouts in the S&P 500. The strategy goes long when price breaks above the upper bound and short when price breaks below the lower bound.

## Strategy Overview

### Core Concept
The strategy calculates dynamic upper and lower bounds based on historical volatility and uses them to detect potential trend breakouts:

- **Upper Bound**: `max(today_open, yesterday_close) × (1 + σ)`
- **Lower Bound**: `min(today_open, yesterday_close) × (1 - σ)`
- **σ (Sigma)**: Mean absolute daily return over the previous 13 trading days

### Trading Rules
- **Long Entry**: Price breaks above upper bound → Buy/Call
- **Short Entry**: Price breaks below lower bound → Sell/Short  
- **Exit Conditions**: Market close (19:30 UTC) or signal reversal
- **Timeframe**: 30-minute intervals on S&P 500 (^GSPC)

## Performance Results

| Strategy Version | Total Return | Win Rate | # Trades | Max Drawdown | Profit Factor |
|------------------|--------------|----------|----------|--------------|---------------|
| **Original**     | -0.48%       | 22.2%    | 9        | N/A          | N/A           |
| **Enhanced** ✅  | +0.17%       | 33.3%    | 6        | -0.24%       | 1.57          |

**Key Improvement**: +0.65 percentage points return improvement through enhanced risk management.

## Repository Structure

```
├── README.md                      # This file
├── Intraday_bounds.py             # Bounds calculation with visualization
├── 2_week_bounds.py               # Daily bounds calculation for backtesting
├── backtest.py                    # Original strategy implementation
├── enhanced_backtest.py           # Enhanced strategy with risk management
├── final_strategy_report.md       # Comprehensive analysis report
├── backtest_summary.md            # Quick backtest summary
├── sp500_30min_14d.csv           # S&P 500 30-minute price data
├── daily_noise_bounds.csv        # Pre-calculated daily bounds
├── noise_bounds_sample.csv       # Sample bounds data
├── backtest_results.png          # Original strategy results chart
├── enhanced_backtest_results.png # Enhanced strategy results chart
└── Model_Graphical_example.png   # Bounds visualization example
```

## Getting Started

### Prerequisites
```bash
pip install pandas numpy matplotlib yfinance
```

### Quick Start

1. **Calculate Bounds for Today**:
```bash
python Intraday_bounds.py
```
Generates intraday bounds and visualization for the current trading day.

2. **Generate Historical Bounds**:
```bash
python 2_week_bounds.py
```
Creates `daily_noise_bounds.csv` with bounds for the past 14 days.

3. **Run Original Backtest**:
```bash
python backtest.py
```
Tests the basic strategy without risk management.

4. **Run Enhanced Backtest**:
```bash
python enhanced_backtest.py
```
Tests the improved strategy with stop losses and position sizing.

## Strategy Implementation Details

### Enhanced Features (enhanced_backtest.py)

#### Risk Management
- **Stop Loss**: 1.5% stop loss on all positions
- **Position Sizing**: Maximum 95% of capital per trade
- **Bounds Buffer**: 0.05% buffer to reduce false breakouts

#### Transaction Costs
- **Commission**: $0.0035 per share
- **Slippage**: $0.001 per share
- **Initial Capital**: $100,000

#### Performance Improvements
- **Reduced False Signals**: Bounds buffer filters noise
- **Better Risk Control**: Stop losses limit maximum loss per trade
- **Improved Trade Quality**: Fewer but higher-quality trades

### Bounds Calculation Methodology

The volatility-based bounds are calculated using:

1. **Historical Volatility (σ)**: 
   - Mean absolute return over previous 13 trading days
   - `σ = mean(|close_t / open_t - 1|)` for t-13 to t-1

2. **Dynamic Bounds**:
   - Upper: Uses higher of today's open or yesterday's close as base
   - Lower: Uses lower of today's open or yesterday's close as base
   - Adjusted by historical volatility to capture breakout potential

## Key Findings

### What Works ✅
- **Bounds identification** correctly captures breakout levels
- **Risk management** significantly improves performance  
- **Signal filtering** reduces false breakouts
- **Position sizing** controls risk exposure

### Areas for Improvement ⚠️
- **Win rate** still relatively low at 33%
- **Market regime sensitivity** - needs testing in different conditions
- **Entry timing** - some signals trigger after moves have started

## Usage Examples

### Live Bounds Calculation
```python
# Get today's bounds
python Intraday_bounds.py

# View the bounds visualization
# Output: Model_Graphical_example.png
```

### Custom Backtesting
```python
import pandas as pd
from enhanced_backtest import *

# Load your own data
price_df = pd.read_csv('your_price_data.csv')
bounds_df = pd.read_csv('your_bounds_data.csv')

# Run backtest with custom parameters
STOP_LOSS_PCT = 0.02  # 2% stop loss
MAX_POSITION_SIZE = 0.8  # 80% max position
```

## Future Enhancements

### Recommended Improvements
1. **Signal Optimization**
   - Volume confirmation for breakouts
   - Momentum filters
   - Market microstructure effects

2. **Risk Management**
   - Dynamic stop losses based on volatility
   - Position sizing based on signal strength
   - Maximum daily loss limits

3. **Market Regime Adaptation**
   - Trend vs range-bound market detection
   - Volatility regime adjustments
   - Economic calendar integration

4. **Extended Testing**
   - Longer backtesting periods
   - Multiple market conditions
   - Out-of-sample validation

## Data Sources

- **Price Data**: Yahoo Finance (yfinance) - S&P 500 30-minute intervals
- **Timeframe**: 14-day rolling window
- **Market Hours**: 13:30-19:30 UTC (9:30-15:30 ET)


*Strategy developed and tested on S&P 500 30-minute data from June 16 - July 2, 2025*
