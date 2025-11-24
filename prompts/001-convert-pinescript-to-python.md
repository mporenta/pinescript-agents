<objective>
Convert the PineScript Supertrend trading strategy located at `/home/pinescript-agents/supertrend_strategy.pine` into production-quality Python 3.1x code using object-oriented design.

The end goal is a reusable Python class that can be instantiated with configurable parameters and used for algorithmic trading or backtesting in Python environments. This conversion will enable integration with Python trading frameworks, backtesting engines, and custom trading systems.
</objective>

<context>
The source file is a comprehensive TradingView PineScript v6 strategy (806 lines) implementing:
- Triple Supertrend confirmation system
- Dynamic position sizing with commission adjustments
- Risk management (stop loss, take profit, trailing stops)
- Volume analysis and filtering
- Moving average trend filters
- Support/resistance level detection
- Daily profit tracking and reset logic
- JSON alert message builders for broker integration

Technology requirements:
- Python 3.10+ (use modern type hints where appropriate)
- Object-oriented design with class structure
- All strategy parameters as instance variables (self.{x})
- Market data source as placeholder (to be integrated later)
</context>

<requirements>
1. **Class Design**:
   - Create a `SupertrendStrategy` class with `__init__()` method
   - All input parameters from PineScript (47+ parameters) as `__init__` arguments with default values matching the original
   - State variables (position tracking, account balance, profit tracking, etc.) as instance variables (self.variable_name)
   - Group related parameters logically in the __init__ signature

2. **Core Functionality**:
   - Implement all calculation methods: Supertrend indicators (3 levels), volume analysis, support/resistance, moving averages
   - Entry signal logic: Long and short signals with confirmation delays
   - Position sizing: Replicate the commission-adjusted position sizing logic
   - Risk management: Stop loss, take profit, trailing stops
   - Exit logic: RSI exits, profit thresholds, end-of-day closes, trailing stop crosses
   - Daily reset mechanism for state variables

3. **Data Handling**:
   - Create placeholder for market data input (e.g., pandas DataFrame with OHLCV columns)
   - Use clear method signatures: `calculate_supertrend(self, atr_period, factor)`, `check_entry_signals(self, current_bar)`, etc.
   - Return structured outputs (dictionaries or named tuples for signals, orders, etc.)

4. **Preserve Original Logic**:
   - Maintain exact calculation formulas from PineScript
   - Keep all conditional logic intact (entry conditions, exit conditions)
   - Preserve the triple Supertrend confirmation requirement
   - Maintain volume filtering logic and thresholds

5. **Code Quality**:
   - Use descriptive variable names (convert PineScript names to Pythonic snake_case)
   - Add docstrings to the class and key methods explaining purpose and parameters
   - Include inline comments for complex logic sections (especially position sizing, volume calculations)
   - Use type hints for method signatures
   - Follow PEP 8 style guidelines

6. **JSON Message Builders**:
   - Convert the three JSON alert builders (updateIbPrice, buildJson, alertMessageCloseAll) to Python methods
   - Return Python dictionaries that can be serialized to JSON
</requirements>

<implementation>
Structure the Python file as follows:

```python
from typing import Optional, Dict, Tuple
import pandas as pd
import numpy as np
from datetime import datetime

class SupertrendStrategy:
    """
    Supertrend trading strategy with triple confirmation, risk management,
    and dynamic position sizing.

    Converted from TradingView PineScript v6.
    """

    def __init__(
        self,
        # Entry Settings
        unix_time: int = 1761140099,
        use_trailing_stop_loss: bool = False,

        # Supertrend Settings
        atr_period: int = 10,
        factor: float = 3.0,
        atr_period1: int = 10,
        factor1: float = 1.0,
        # ... all other parameters with defaults

        # Risk Settings
        bias: str = "both",
        profit_threshold: float = 300.0,
        reward_risk_ratio: float = 1.5,
        risk_percentage: float = 1.0,
        # ... etc
    ):
        # Store all parameters as instance variables
        self.unix_time = unix_time
        self.use_trailing_stop_loss = use_trailing_stop_loss
        # ... etc

        # Initialize state variables
        self.action = ""
        self.daily_net_profit = 0.0
        self.last_net_profit = 0.0
        # ... all var variables from PineScript

    def calculate_supertrend(self, close: pd.Series, high: pd.Series,
                            low: pd.Series, atr_period: int,
                            factor: float) -> Tuple[pd.Series, pd.Series]:
        """Calculate Supertrend indicator."""
        # Implementation here
        pass

    def check_volume_conditions(self, volume: pd.Series,
                                close: float) -> bool:
        """Check if volume conditions are met for entry."""
        # Implementation here
        pass

    def calculate_position_size(self, entry_price: float,
                                stop_price: float,
                                direction: str) -> float:
        """Calculate position size with commission adjustment."""
        # Implementation here
        pass

    def check_long_entry(self, bar_data: Dict) -> Optional[Dict]:
        """Check for long entry signal and return order details if triggered."""
        # Implementation here
        pass

    def check_short_entry(self, bar_data: Dict) -> Optional[Dict]:
        """Check for short entry signal and return order details if triggered."""
        # Implementation here
        pass

    def check_exit_conditions(self, bar_data: Dict) -> Optional[str]:
        """Check all exit conditions and return exit reason if triggered."""
        # Implementation here
        pass

    def build_order_json(self, limit_price: float, action: str,
                         qty: float, stop: float,
                         target: float, notes: str) -> Dict:
        """Build order message as dictionary (PineScript: buildJson)."""
        # Implementation here
        pass

    def daily_reset(self):
        """Reset daily state variables (called at start of new trading day)."""
        # Implementation here
        pass

    def process_bar(self, bar_data: Dict) -> Dict:
        """
        Process a single bar of market data.

        Args:
            bar_data: Dictionary with keys: 'open', 'high', 'low', 'close',
                     'volume', 'timestamp', etc.

        Returns:
            Dictionary with signals, orders, and state updates
        """
        # Main processing logic here
        pass
```

**Data Placeholder**:
Create a clear placeholder for market data input. For example:

```python
# PLACEHOLDER: Market data source
# This should be replaced with actual data feed (e.g., from broker API, database, CSV)
# Expected format: pandas DataFrame with columns:
# - timestamp (datetime)
# - open (float)
# - high (float)
# - low (float)
# - close (float)
# - volume (float)

def get_market_data() -> pd.DataFrame:
    """
    Placeholder function for market data retrieval.
    Replace this with actual data source integration.
    """
    raise NotImplementedError("Market data source not implemented")
```

**Why this structure matters**:
- Class-based design allows multiple strategy instances with different parameters
- Instance variables (self.{x}) maintain state across bars (critical for position tracking, profit tracking, daily resets)
- Clear method separation enables testing individual components
- Type hints improve code maintainability and IDE support
- Placeholder approach allows testing the strategy logic before integrating real data feeds
</implementation>

<output>
Create the following file:
- `./supertrend_strategy.py` - Complete Python implementation of the strategy class

The file should:
1. Import necessary libraries (pandas, numpy, typing, datetime)
2. Define the SupertrendStrategy class with all methods
3. Include comprehensive docstrings
4. Add the market data placeholder function
5. Optionally include a usage example at the bottom (commented out or in `if __name__ == "__main__"` block)
</output>

<pinescript_tools>
You have access to specialized PineScript tools and MCP servers:
- `mcp__pinescript-docs__pinescript_reference` - Look up PineScript built-in functions and their behavior
- PineScript skills (pine-developer, pine-debugger, etc.) - Use if you need clarification on PineScript semantics
- `/pinescript-mcp` slash command - For documentation lookup and code validation

Use these resources if you encounter PineScript-specific functions or behaviors that need clarification during conversion. For example:
- `ta.supertrend()` - Look up exact calculation formula
- `ta.pivothigh()` / `ta.pivotlow()` - Understand the lookback behavior
- `fixnan()` - Understand how it propagates values
- `barstate.isconfirmed` - Understand bar state logic
- PineScript variable scope and `var` keyword behavior
</pinescript_tools>

<conversion_notes>
Key PineScript to Python conversions:
1. **Variables**:
   - `var float x = na` → `self.x: Optional[float] = None`
   - `var bool x = false` → `self.x: bool = False`
   - `var int x = na` → `self.x: Optional[int] = None`
   - Arrays: `array.new_float(0)` → `self.trade_profits: List[float] = []`

2. **Built-in Functions**:
   - `ta.supertrend(factor, period)` → Implement ATR-based Supertrend algorithm
   - `ta.ema(source, length)` → Use pandas EMA or implement
   - `ta.rma(source, length)` → Implement RMA (Wilder's moving average)
   - `ta.sma(source, length)` → Use pandas rolling mean
   - `ta.atr(length)` → Implement Average True Range
   - `ta.pivothigh(left, right)` → Implement pivot high detection
   - `ta.pivotlow(left, right)` → Implement pivot low detection
   - `ta.crossover(a, b)` → `(a > b) and (a_prev <= b_prev)`
   - `ta.crossunder(a, b)` → `(a < b) and (a_prev >= b_prev)`
   - `fixnan(value)` → Forward-fill NaN values

3. **Time and Sessions**:
   - `time` → Unix timestamp in milliseconds
   - `time_close` → Bar close timestamp
   - `dayofmonth` → Extract from datetime
   - `session.ismarket`, `session.isfirstbar_regular` → Implement session logic
   - `newDay = dayofmonth != dayofmonth[1]` → Compare current vs previous day

4. **Strategy Functions**:
   - `strategy.position_size` → Track as self.position_size
   - `strategy.netprofit`, `strategy.openprofit` → Calculate and track
   - `strategy.entry()` → Generate order dictionary
   - `strategy.exit()` → Generate exit order dictionary
   - `strategy.close_all()` → Generate close all order

5. **Conditionals**:
   - Ternary: `condition ? true_val : false_val` → `true_val if condition else false_val`
</conversion_notes>

<verification>
After completing the conversion, verify:

1. **All parameters captured**: Check that all 47+ input parameters from the PineScript are in the `__init__` method
2. **All state variables initialized**: Verify all `var` variables from PineScript are instance variables
3. **Core calculations present**: Supertrend (3 levels), volume analysis, MA filters, support/resistance
4. **Entry logic complete**: Both long and short entry conditions with all filters
5. **Exit logic complete**: All 5+ exit conditions (trailing stop, profit threshold, RSI, take profit, end of day)
6. **Position sizing**: Commission-adjusted calculation logic preserved
7. **JSON builders**: All three message builder functions converted to methods returning dictionaries
8. **Daily reset**: Logic to reset state variables at day boundaries
9. **Code quality**: Docstrings, type hints, comments for complex sections

You can use the pine-developer or pine-debugger skills to validate the conversion if needed.
</verification>

<success_criteria>
The conversion is successful when:
1. Python file contains a complete SupertrendStrategy class
2. All PineScript parameters are configurable via __init__
3. All calculations and logic from the original are implemented
4. Code follows Python best practices (PEP 8, type hints, docstrings)
5. Market data integration point is clearly marked as placeholder
6. The class can be instantiated and is ready for integration with a data source
7. Position tracking, profit tracking, and state management work correctly across bars
</success_criteria>