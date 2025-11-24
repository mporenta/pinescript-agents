"""
Supertrend Trading Strategy - Python Implementation

Converted from TradingView PineScript v6.
Original: MP - Claude Supertrend Strategy with Risk Management & Alerts

This strategy implements:
- Triple Supertrend confirmation system
- Dynamic position sizing with commission adjustments
- Risk management (stop loss, take profit, trailing stops)
- Volume analysis and filtering
- Moving average trend filters
- Support/resistance level detection
- Daily profit tracking and reset logic
- JSON alert message builders for broker integration
"""

from typing import Optional, Dict, Tuple, List, Any
import pandas as pd
import numpy as np
from datetime import datetime, date
from pathlib import Path
import sys
import os

# Technical Analysis Library - Numba-accelerated indicators
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tools'))
from tools.numba_indicators import (
    ema as numba_ema,
    sma as numba_sma,
    rsi as numba_rsi,
    calc_supertrend_numba,
    pivot_high_numba,
    pivot_low_numba,
)

# Logging setup with loguru
from loguru import logger

try:
    # Python 3.9+
    from zoneinfo import ZoneInfo
except ImportError:
    ZoneInfo = None  # type: ignore


class StrategyLogConfig:
    """Centralized logging configuration for the Supertrend strategy"""

    def __init__(self, root_dir: str = None, log_level: str = "INFO"):
        self._configured: bool = False
        self.root_dir = root_dir or str(Path(__file__).parent)
        self.logs_dir = os.path.join(self.root_dir, "logs")

        # Ensure logs directory exists
        os.makedirs(self.logs_dir, exist_ok=True)

        print(f"StrategyLogConfig initialized with root_dir: {self.root_dir}")
        print(f"Logs will be written to: {self.logs_dir}")

        # Timezone for all logging date decisions
        self.tz_name = "America/New_York"
        self.log_level = log_level

        # Common format for all logs
        self.log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )

        # Format for detailed debugging
        self.debug_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "Process: {process} | Thread: {thread} | "
            "<level>{message}</level>"
        )

    def _today_str(self) -> str:
        """Return today's date string in the configured timezone (YYYY_MM_DD)."""
        tz = None
        if ZoneInfo is not None:
            try:
                tz = ZoneInfo(self.tz_name)
            except Exception:
                pass
        dt = datetime.now(tz) if tz else datetime.now()
        return dt.strftime("%Y_%m_%d")

    def _parse_dated_prefix(self, filename: str) -> Optional[date]:
        """Parse a leading YYYY_MM_DD_ date from a filename into a date object."""
        try:
            parts = filename.split('_', 3)
            if len(parts) < 4:
                return None
            y, m, d = parts[0], parts[1], parts[2]
            if not (len(y) == 4 and len(m) == 2 and len(d) == 2):
                return None
            return date(int(y), int(m), int(d))
        except Exception:
            return None

    def _cleanup_old_dated_logs(self, today_str: str):
        """Delete any log files whose leading date is older than today."""
        today_parts = today_str.split('_')
        today_dt = date(int(today_parts[0]), int(today_parts[1]), int(today_parts[2]))
        removed: List[str] = []

        for fname in os.listdir(self.logs_dir):
            if not fname.endswith('.log') and not fname.endswith('.log.zip'):
                continue
            f_date = self._parse_dated_prefix(fname)
            if f_date and f_date < today_dt:
                full_path = os.path.join(self.logs_dir, fname)
                try:
                    os.remove(full_path)
                    removed.append(fname)
                except Exception as e:
                    print(f"[StrategyLogConfig] Failed to remove old log {fname}: {e}")

        if removed:
            print(f"[StrategyLogConfig] Removed outdated log files: {', '.join(removed)}")

    def setup(self):
        """Set up logging configuration"""
        if self._configured:
            return

        # Remove any existing handlers
        logger.remove()

        # Derive today's date in specified timezone
        today_str = self._today_str()

        # Clean up old dated logs
        try:
            self._cleanup_old_dated_logs(today_str)
        except Exception as e:
            print(f"[StrategyLogConfig] Warning: cleanup failed: {e}")

        # Build dated filenames
        strategy_log_path = os.path.join(self.logs_dir, f"{today_str}_strategy.log")
        error_log_path = os.path.join(self.logs_dir, f"{today_str}_strategy_error.log")
        debug_log_path = os.path.join(self.logs_dir, f"{today_str}_strategy_debug.log")
        trades_log_path = os.path.join(self.logs_dir, f"{today_str}_trades.log")

        # Add console logging
        logger.add(
            sink=sys.stderr,
            level=self.log_level,
            format=self.log_format,
            enqueue=True,
            colorize=True
        )

        # Primary strategy log
        logger.add(
            sink=strategy_log_path,
            level=self.log_level,
            format=self.log_format,
            rotation="10 MB",
            retention="1 week",
            compression="zip",
            enqueue=True
        )

        # Error-only logs with more detail
        logger.add(
            sink=error_log_path,
            level="ERROR",
            format=self.debug_format,
            rotation="10 MB",
            retention="1 month",
            compression="zip",
            backtrace=True,
            diagnose=True,
            enqueue=True
        )

        # Debug logs with full detail
        if self.log_level == "DEBUG":
            logger.add(
                sink=debug_log_path,
                level="DEBUG",
                format=self.debug_format,
                rotation="100 MB",
                retention="3 days",
                compression="zip",
                enqueue=True
            )

        # Trades-only log (INFO and WARNING for trade signals)
        logger.add(
            sink=trades_log_path,
            level="INFO",
            format=self.log_format,
            rotation="5 MB",
            retention="1 month",
            compression="zip",
            enqueue=True,
            filter=lambda record: "TRADE" in record["message"] or "SIGNAL" in record["message"]
        )

        self._configured = True
        logger.info(f"✓ Logging configured: strategy={strategy_log_path}")
        logger.debug(f"Debug log: {debug_log_path}")
        logger.debug(f"Error log: {error_log_path}")
        logger.debug(f"Trades log: {trades_log_path}")

    def format_order(self, order: Dict[str, Any]) -> str:
        """Format order data into a readable string"""
        if not order:
            return "No order data"

        return (
            f"\n    Symbol: {order.get('symbol', 'N/A')}"
            f"\n    Action: {order.get('orderAction', 'N/A')}"
            f"\n    Quantity: {order.get('quantity', 0):,.0f}"
            f"\n    Entry: ${order.get('limit_price', 0):,.2f}"
            f"\n    Stop Loss: ${order.get('stop_loss', 0):,.2f}"
            f"\n    Take Profit: ${order.get('take_profit_price', 0):,.2f}"
            f"\n    Risk/Reward: {order.get('rewardRiskRatio', 0):.2f}"
            f"\n    Notes: {order.get('notes', 'N/A')}"
        )

    def format_state(self, state: Dict[str, Any]) -> str:
        """Format strategy state into a readable string"""
        if not state:
            return "No state data"

        position = "LONG" if state.get('long_position') else "SHORT" if state.get('short_position') else "FLAT"

        return (
            f"\n    Position: {position} ({state.get('position_size', 0):,.0f} shares)"
            f"\n    Daily P&L: ${state.get('daily_net_profit', 0):,.2f}"
            f"\n    Trend: {'UP' if state.get('up_trend') else 'DOWN' if state.get('dn_trend') else 'NEUTRAL'}"
            f"\n    Long Stop: ${state.get('long_stop') or 0:,.2f} | Target: ${state.get('long_target') or 0:,.2f}"
            f"\n    Short Stop: ${state.get('short_stop') or 0:,.2f} | Target: ${state.get('short_target') or 0:,.2f}"
            f"\n    Bar Index: {state.get('bar_index', 0)}"
        )


# Create global logging instance
strategy_log_config = StrategyLogConfig(log_level="INFO")


class SupertrendStrategy:
    """
    Supertrend trading strategy with triple confirmation, risk management,
    and dynamic position sizing.

    This class maintains state across bars and can be used for live trading
    or backtesting. All strategy parameters are configurable via __init__.

    NOTE: Profit-based exits (profit_sig_bool) require external P&L updates.
    By default, strategy_net_profit and strategy_open_profit are not updated,
    so profit threshold exits will not trigger. Call update_pnl() before
    process_bar() if using profit-based exit logic with live broker data.
    """

    def __init__(
        self,
        # Entry Settings
        unix_time: int = 1761140099,
        use_trailing_stop_loss: bool = False,

        # Source Settings
        src_column: str = 'close',

        # Main Supertrend Settings
        atr_period: int = 10,
        factor: float = 3.0,

        # Triple Supertrend Confirmation Settings
        atr_period1: int = 10,
        factor1: float = 1.0,
        atr_period2: int = 11,
        factor2: float = 2.0,
        atr_period3: int = 12,
        factor3: float = 3.0,

        # Trailing Stop Settings
        ts_factor: float = 1.5,
        ts_period: int = 3,

        # Risk Settings
        bias: str = "both",  # "both", "Long", "Short"
        profit_threshold: float = 300.0,
        reward_risk_ratio: float = 1.5,
        risk_percentage: float = 1.0,
        commission_value: float = 0.0,
        account_balance: float = 0.0,

        # Order Settings
        stop_type: str = "tick",  # "tick", "kcStop", "vStop", "pivot"
        set_market_order: bool = False,
        take_profit_bool: bool = True,
        profit_sig_bool: bool = True,

        # Strategy Settings
        initial_capital: float = 25000.0,
        default_qty_type: str = "percent_of_equity",
        default_qty_value: float = 100.0,
        margin_long: int = 25,
        margin_short: int = 25,

        # Timeframe Settings
        timeframe: str = "1",  # Main timeframe period

        # Symbol Settings
        symbol: str = "STOCK"
    ):
        """
        Initialize the Supertrend Strategy with all configurable parameters.

        Args:
            unix_time: Unix timestamp threshold for trading activation (seconds)
            use_trailing_stop_loss: Enable trailing stop loss functionality
            src_column: Column name to use as price source
            atr_period: ATR period for main Supertrend
            factor: Multiplier for main Supertrend
            atr_period1-3: ATR periods for triple confirmation Supertrends
            factor1-3: Multipliers for triple confirmation Supertrends
            ts_factor: Trailing stop Supertrend factor
            ts_period: Trailing stop Supertrend period
            bias: Trading direction ("both", "Long", "Short")
            profit_threshold: Maximum profit target before closing
            reward_risk_ratio: Target profit as multiple of risk
            risk_percentage: Percentage of account to risk per trade
            commission_value: Commission per share
            account_balance: Override account balance (0 = use initial_capital)
            stop_type: Type of stop loss calculation
            set_market_order: Use market orders vs limit orders
            take_profit_bool: Enable take profit targets
            profit_sig_bool: Enable profit threshold exits
            initial_capital: Starting account balance
            default_qty_type: Position sizing method
            default_qty_value: Position size value
            margin_long: Margin requirement for long positions
            margin_short: Margin requirement for short positions
            timeframe: Trading timeframe
            symbol: Trading symbol
        """
        # Store configuration parameters
        self.unix_time = unix_time
        self.use_trailing_stop_loss = use_trailing_stop_loss
        self.src_column = src_column

        # Supertrend parameters
        self.atr_period = atr_period
        self.factor = factor
        self.atr_period1 = atr_period1
        self.factor1 = factor1
        self.atr_period2 = atr_period2
        self.factor2 = factor2
        self.atr_period3 = atr_period3
        self.factor3 = factor3

        # Trailing stop parameters
        self.ts_factor = ts_factor
        self.ts_period = ts_period

        # Risk parameters
        self.bias = bias
        self.profit_threshold = profit_threshold
        self.reward_risk_ratio = reward_risk_ratio
        self.risk_percentage = risk_percentage
        self.commission_value = commission_value
        self.account_balance_input = account_balance

        # Order parameters
        self.stop_type = stop_type
        self.set_market_order = set_market_order
        self.take_profit_bool = take_profit_bool
        # NOTE: Requires update_pnl() calls to work
        self.profit_sig_bool = profit_sig_bool

        # Strategy parameters
        self.initial_capital = initial_capital
        self.default_qty_type = default_qty_type
        self.default_qty_value = default_qty_value
        self.margin_long = margin_long
        self.margin_short = margin_short

        # Timeframe and symbol
        self.timeframe = timeframe
        self.symbol = symbol
        self.reset_hour = 18  # 6pm ET for futures, 0 for stocks
        self.reset_timezone = "America/New_York"

        # Constants
        self.volume_multiplier = 6  # Minimum volume multiplier for trade eligibility
        self.entry_delay_ms = 6000  # Delay in milliseconds before entry confirmation
        self.min_commission = 1.0
        self.max_percentage = 0.01

        # Initialize state variables
        self._initialize_state_variables()

        # Setup logging
        self.logger = logger
        logger.info(f"✓ SupertrendStrategy initialized for {self.symbol}")
        logger.debug(f"Configuration: bias={self.bias}, risk%={self.risk_percentage}, "
                    f"reward_risk={self.reward_risk_ratio}, capital=${self.initial_capital:,.2f}")
        logger.debug(f"Supertrend params: period={self.atr_period}, factor={self.factor}, "
                    f"triple=[{self.atr_period1}/{self.factor1}, {self.atr_period2}/{self.factor2}, "
                    f"{self.atr_period3}/{self.factor3}]")

    def _initialize_state_variables(self):
        """Initialize all state tracking variables."""
        # Action tracking
        self.action = ""
        self.notes = "tick-boom"

        # Profit tracking
        self.daily_net_profit = 0.0
        self.last_net_profit = 0.0
        self.trade_profits: List[float] = []

        # Position and account management
        self.time_close_now: Optional[int] = None
        self.account_balance_dyn: Optional[float] = None
        self.position_size: Optional[float] = None
        self.long_e = False
        self.short_e = False
        self.close_all_sig = False
        self.enter = False
        self.profit_close: Optional[float] = None
        self.profit_sig = False

        # Risk management and commissions
        self.dyn_risk_reward: Optional[float] = None
        self.broker_comish: Optional[float] = None
        self.per_share_risk: Optional[float] = None
        self.qty_tl: Optional[float] = None
        self.qty_ts: Optional[float] = None
        self.update_price_alert = False
        self.long_target: Optional[float] = None
        self.short_target: Optional[float] = None
        self.long_stop: Optional[float] = None
        self.short_stop: Optional[float] = None

        # Supertrend state
        self.supertrend_sl_check: Optional[float] = None
        self.up_trend = False
        self.dn_trend = False
        self.vstop_sl_fix: Optional[float] = None

        # Volume state
        self.volume_var = False
        self.vol_cond = False
        self.adj_volume: Optional[float] = None
        self.volume_first = False
        self.highest_volume: Optional[float] = None

        # Session and timing
        self.open_bar_unix: Optional[int] = None
        self.alert_sent = False
        self.close_all = False

        # MA trend state
        self.long_ma = False
        self.short_ma = False
        self.ema9_one_min: Optional[float] = None
        self.rma9_one_min: Optional[float] = None

        # Exit tracking
        self.close_direction: Optional[int] = None
        self.vstop_sl_fix_cross = False

        # Support/resistance
        self.high_use_pivot: Optional[float] = None
        self.low_use_pivot: Optional[float] = None

        # Strategy tracking (simulated)
        self.strategy_position_size = 0.0
        self.strategy_net_profit = 0.0
        self.strategy_open_profit = 0.0

        # Bar counter for tracking
        self.bar_index = 0

        # Timeframe adjustment
        self.tf_int = 1

    def daily_reset(self):
        """
        Reset daily state variables at the start of a new trading day.

        NOTE: Currently resets at midnight in local timezone. For futures trading,
        consider implementing reset_hour (e.g., 18:00 ET for ES/NQ) by comparing
        against a timezone-aware reset boundary.
        """
        logger.info(f"📅 Daily reset triggered | Previous day P&L: ${self.daily_net_profit:,.2f}")

        self.notes = ""
        self.time_close_now = None

        # Position and account management
        self.broker_comish = None
        self.account_balance_dyn = None
        self.position_size = None
        self.long_e = False
        self.short_e = False
        self.close_all_sig = False
        self.enter = False
        self.profit_sig = False
        self.profit_close = None

        # Risk management
        self.dyn_risk_reward = None
        self.per_share_risk = None
        self.qty_tl = None
        self.qty_ts = None
        self.update_price_alert = False
        self.long_target = None
        self.short_target = None
        self.long_stop = None
        self.short_stop = None
        self.supertrend_sl_check = None

        # Flags
        self.close_all_sig = False
        self.close_all = False
        self.enter = False
        self.up_trend = False
        self.dn_trend = False
        self.open_bar_unix = None

        # Volume
        self.volume_first = False
        self.vol_cond = False
        self.volume_var = False

        # Save daily profit
        self.trade_profits.append(self.daily_net_profit)
        self.daily_net_profit = 0.0
        self.alert_sent = False

    def update_pnl(self, net_profit: float, open_profit: float = 0.0) -> None:
        """
        Update strategy P&L from external source (e.g. IBKR account).
        Call this before process_bar() if using profit-based exits.

        This method enables the profit threshold exit logic by providing
        real-time P&L data from a broker account or backtesting engine.

        Args:
            net_profit: Realized net profit/loss for the session
            open_profit: Unrealized profit/loss on open positions

        Example:
            # Before processing each bar in live trading:
            account_pnl = broker.get_account_pnl()
            strategy.update_pnl(
                net_profit=account_pnl['realized'],
                open_profit=account_pnl['unrealized']
            )
            result = strategy.process_bar(bar_data, historical_data)
        """
        self.strategy_net_profit = net_profit
        self.strategy_open_profit = open_profit
        logger.debug(f"P&L updated: net=${net_profit:,.2f}, open=${open_profit:,.2f}")

    def _adjust_timeframe(self, timeframe: str) -> int:
        """
        Adjust calculations based on timeframe.

        Args:
            timeframe: Timeframe string (e.g., "1", "5S", "10S", "15S")

        Returns:
            Integer multiplier for timeframe adjustments
        """
        if timeframe == "10S":
            return 6
        elif timeframe == "5S":
            return 12
        elif timeframe == "15S":
            return 4
        else:
            return 1

    def _build_state_dict(self) -> Dict[str, Any]:
        """
        Always returns consistent state dictionary.

        This ensures process_bar() always returns a valid state regardless
        of execution path or errors.

        Returns:
            Dictionary containing current strategy state
        """
        return {
            'position_size': self.strategy_position_size,
            'long_position': self.long_e,
            'short_position': self.short_e,
            'daily_net_profit': self.daily_net_profit,
            'up_trend': self.up_trend,
            'dn_trend': self.dn_trend,
            'long_stop': self.long_stop,
            'long_target': self.long_target,
            'short_stop': self.short_stop,
            'short_target': self.short_target,
            'vstop_sl_fix': self.vstop_sl_fix,
            'profit_sig': self.profit_sig,
            'bar_index': self.bar_index
        }

    def _required_history(self) -> int:
        """
        Minimum bars needed to compute all indicators reliably.

        This prevents O(N²) performance degradation by limiting the
        historical data window to only what's necessary for calculations.

        Returns:
            Number of bars required for indicator calculations
        """
        base_atr = self.atr_period * self.tf_int
        triple_atr = max(self.atr_period1, self.atr_period2, self.atr_period3)
        ts_atr = self.ts_period * self.tf_int
        ema9_len = 9 * self.tf_int
        rsi_len = 14
        vol_len = 10 * self.tf_int
        pivot_len = 7  # 3 left + 3 right + 1 current

        core = max(base_atr, triple_atr, ts_atr, ema9_len, rsi_len, vol_len, pivot_len)
        return core + 50  # Extra buffer for ATR warmup


    def calculate_ema(self, source: pd.Series, period: int) -> pd.Series:
        """
        Calculate Exponential Moving Average (EMA) using numba_indicators.

        Args:
            source: Price series
            period: EMA period

        Returns:
            Series of EMA values
        """
        ema_values = numba_ema(source.values, period, smoothing=2.0)
        return pd.Series(ema_values, index=source.index)

    def calculate_rma(self, source: pd.Series, period: int) -> pd.Series:
        """
        Calculate Wilder's Moving Average (RMA).
        RMA is also known as SMMA (Smoothed Moving Average).

        Note: numba_indicators does not provide a direct RMA function. This implementation
        uses pandas EWM with alpha=1/period, which is equivalent to Wilder's smoothing
        and compatible with the numba-based approach.

        Args:
            source: Price series
            period: RMA period

        Returns:
            Series of RMA values
        """
        alpha = 1.0 / period
        return source.ewm(alpha=alpha, adjust=False).mean()

    def calculate_sma(self, source: pd.Series, period: int) -> pd.Series:
        """
        Calculate Simple Moving Average (SMA) using numba_indicators.

        Args:
            source: Price series
            period: SMA period

        Returns:
            Series of SMA values
        """
        sma_values = numba_sma(source.values, period)
        return pd.Series(sma_values, index=source.index)

    def calculate_supertrend(self, high: pd.Series, low: pd.Series,
                            close: pd.Series, atr_period: int,
                            factor: float) -> Tuple[pd.Series, pd.Series]:
        """
        Calculate Supertrend indicator using Numba-optimized implementation.

        The Supertrend uses ATR (calculated with RMA for TradingView parity) to create
        dynamic support/resistance levels.
        Direction: -1 for uptrend, 1 for downtrend

        Args:
            high: High prices
            low: Low prices
            close: Close prices
            atr_period: ATR period
            factor: ATR multiplier

        Returns:
            Tuple of (supertrend values, direction values)

        Raises:
            ValueError: If inputs are invalid
            Exception: For calculation errors
        """
        try:
            # Validate inputs
            if factor <= 0:
                raise ValueError(f"Supertrend factor must be positive, got {factor}")
            if atr_period <= 0:
                raise ValueError(f"ATR period must be positive, got {atr_period}")

            # Call Numba-optimized function (uses RMA for TradingView parity)
            st_values, dir_values = calc_supertrend_numba(
                high.values,
                low.values,
                close.values,
                atr_period,
                factor
            )

            supertrend = pd.Series(st_values, index=close.index)
            direction = pd.Series(dir_values, index=close.index)

            logger.debug(f"Calculated Supertrend (Numba): period={atr_period}, factor={factor}, "
                        f"last_value={supertrend.iloc[-1]:.2f}, direction={direction.iloc[-1]}")
            return supertrend, direction

        except ValueError as e:
            logger.error(f"Supertrend calculation validation error: {e}")
            raise
        except Exception as e:
            logger.error(f"Supertrend calculation failed: {e}", exc_info=True)
            raise

    def calculate_pivot_high(self, high: pd.Series, left_bars: int, right_bars: int) -> pd.Series:
        # Pass numpy array to Numba
        pivots = pivot_high_numba(high.values, left_bars, right_bars)
        return pd.Series(pivots, index=high.index)

    def calculate_pivot_low(self, low: pd.Series, left_bars: int, right_bars: int) -> pd.Series:
        # Pass numpy array to Numba
        pivots = pivot_low_numba(low.values, left_bars, right_bars)
        return pd.Series(pivots, index=low.index)

    def fixnan(self, series: pd.Series) -> pd.Series:
        """
        Forward-fill NaN values (equivalent to PineScript's fixnan).

        Args:
            series: Series with potential NaN values

        Returns:
            Series with NaN values forward-filled
        """
        return series.ffill()

    def crossover(self, series1: float, series2: float,
                 prev_series1: float, prev_series2: float) -> bool:
        """
        Check if series1 crosses over series2.

        Args:
            series1: Current value of first series
            series2: Current value of second series
            prev_series1: Previous value of first series
            prev_series2: Previous value of second series

        Returns:
            True if crossover occurred
        """
        return series1 > series2 and prev_series1 <= prev_series2

    def crossunder(self, series1: float, series2: float,
                  prev_series1: float, prev_series2: float) -> bool:
        """
        Check if series1 crosses under series2.

        Args:
            series1: Current value of first series
            series2: Current value of second series
            prev_series1: Previous value of first series
            prev_series2: Previous value of second series

        Returns:
            True if crossunder occurred
        """
        return series1 < series2 and prev_series1 >= prev_series2

    def calculate_position_size_long(self, entry_price: float,
                                    stop_price: float) -> float:
        """
        Calculate position size for long entry with commission adjustments.

        Args:
            entry_price: Planned entry price
            stop_price: Stop loss price

        Returns:
            Position size (number of shares)
        """
        # Per-share risk
        per_share_risk = abs(entry_price - stop_price)

        # Account balance
        account_bal = (self.account_balance_input if self.account_balance_input > 0
                      else self.initial_capital)

        # Tolerated risk (account risk minus minimum commission)
        tolerated_risk = abs((self.risk_percentage / 100 * account_bal) - self.min_commission)

        # Preliminary quantity
        p_qty_l = round(min(
            tolerated_risk / per_share_risk,
            np.floor(account_bal / entry_price)
        ))

        # Calculate commission
        gross_commission = p_qty_l * 0.005
        trade_value = p_qty_l * entry_price
        broker_comish = min(
            max(gross_commission, self.min_commission),
            trade_value * self.max_percentage
        )

        # Final quantity accounting for commission
        qty_tl = round(min(
            (tolerated_risk - broker_comish) / per_share_risk,
            np.floor(account_bal / entry_price)
        ))

        return qty_tl

    def calculate_position_size_short(self, entry_price: float,
                                     stop_price: float) -> float:
        """
        Calculate position size for short entry with commission adjustments.

        Args:
            entry_price: Planned entry price
            stop_price: Stop loss price

        Returns:
            Position size (number of shares)
        """
        # Per-share risk
        per_share_risk = abs(entry_price - stop_price)

        # Account balance
        account_bal = (self.account_balance_input if self.account_balance_input > 0
                      else self.initial_capital)

        # Tolerated risk
        tolerated_risk = abs((self.risk_percentage / 100 * account_bal) - self.min_commission)

        # Preliminary quantity
        p_qty_s = round(min(
            tolerated_risk / per_share_risk,
            np.floor(account_bal / entry_price)
        ))

        # Calculate commission
        gross_commission = p_qty_s * 0.005
        trade_value = p_qty_s * entry_price
        broker_comish = min(
            max(gross_commission, self.min_commission),
            trade_value * self.max_percentage
        )

        # Final quantity
        qty_ts = round(min(
            (tolerated_risk - broker_comish) / per_share_risk,
            np.floor(account_bal / entry_price)
        ))

        return qty_ts

    def build_update_price_json(self, close: float, vstop_sl_fix: float,
                               alert_notes: str = "") -> Dict:
        """
        Build JSON message for price update alerts.

        Args:
            close: Current close price
            vstop_sl_fix: Stop loss trigger price
            alert_notes: Optional notes for the alert

        Returns:
            Dictionary with order update information
        """
        # Calculate take profit prices
        tp_short = close - self.reward_risk_ratio * (vstop_sl_fix - close)
        tp_long = close + self.reward_risk_ratio * (close - vstop_sl_fix)
        tp_price = tp_long if close > vstop_sl_fix else tp_short

        return {
            "symbol": self.symbol,
            "orderAction": "updateIbPrice",
            "rewardRiskRatio": self.reward_risk_ratio,
            "barSizeSetting_tv": self.timeframe,
            "quantity": -1,
            "riskPercentage": self.risk_percentage,
            "kcAtrFactor": 1.5,
            "atrFactor": 1.5,
            "vstopAtrFactor": 1.5,
            "accountBalance": self.account_balance_dyn or self.initial_capital,
            "limit_price": close,
            "stopType": self.stop_type,
            "takeProfitBool": self.take_profit_bool,
            "stop_loss": vstop_sl_fix,
            "take_profit_price": tp_price,
            "unixtime": int(datetime.now().timestamp() * 1000),
            "notes": alert_notes,
            "set_market_order": self.set_market_order
        }

    def build_order_json(self, limit_price: float, action: str, qty: float,
                        stop: float, target: float, notes: str) -> Dict:
        """
        Build JSON message for order execution.

        Args:
            limit_price: Entry limit price
            action: Order action ("BUY" or "SELL")
            qty: Position size
            stop: Stop loss price
            target: Take profit price
            notes: Order notes

        Returns:
            Dictionary with complete order information
        """
        quantity = qty if qty is not None else -1

        return {
            "symbol": self.symbol,
            "orderAction": action,
            "rewardRiskRatio": self.reward_risk_ratio,
            "barSizeSetting_tv": self.timeframe,
            "quantity": quantity,
            "riskPercentage": self.risk_percentage,
            "accountBalance": self.account_balance_dyn or self.initial_capital,
            "limit_price": limit_price,
            "stop_loss": stop,
            "take_profit_price": target,
            "set_market_order": self.set_market_order,
            "takeProfitBool": self.take_profit_bool,
            "stopType": self.stop_type,
            "unixtime": int(datetime.now().timestamp() * 1000),
            "notes": notes + str(int(datetime.now().timestamp() * 1000))
        }

    def build_close_all_json(self, close: float, notes: str,
                            uptrend_fn_bool: bool) -> Dict:
        """
        Build JSON message for closing all positions.

        Args:
            close: Current close price
            notes: Exit reason
            uptrend_fn_bool: Current trend direction

        Returns:
            Dictionary with close all order information
        """
        return {
            "symbol": self.symbol,
            "orderAction": "close_all",
            "rewardRiskRatio": 1,
            "barSizeSetting_tv": self.timeframe,
            "quantity": -1,
            "riskPercentage": self.risk_percentage,
            "kcAtrFactor": 1.5,
            "atrFactor": 1.5,
            "vstopAtrFactor": 1.5,
            "accountBalance": self.account_balance_dyn or self.initial_capital,
            "limit_price": close,
            "stopType": self.stop_type,
            "takeProfitBool": self.take_profit_bool,
            "stop_loss": close,
            "unixtime": int(datetime.now().timestamp() * 1000),
            "uptrend": uptrend_fn_bool,
            "test": False,
            "notes": notes,
            "set_market_order": self.set_market_order
        }

    def check_volume_conditions(self, volume: float, close: float,
                               volume_history: pd.Series) -> bool:
        """
        Check if volume conditions are met for entry.

        WARNING: volume_condition_2 may be overly restrictive for thinly traded stocks.
        For a $50k account with $20 stock and multiplier=6:
          Required volume > ($50k / $20) * 6 = 15,000 shares

        Consider adjusting volume_multiplier or using average volume instead
        of account balance for thin markets.

        Args:
            volume: Current bar volume
            close: Current close price
            volume_history: Historical volume series

        Returns:
            True if volume conditions allow entry
        """
        adj_mean = volume_history.mean()
        account_bal = (self.account_balance_input if self.account_balance_input > 0
                      else self.initial_capital)

        # Condition 1: Current volume exceeds average
        volume_condition_1 = volume >= adj_mean

        # Condition 2: Sufficient volume relative to account size
        # This ensures we can fill our position without excessive market impact
        max_shares = account_bal / close
        required_volume = max_shares * self.volume_multiplier
        volume_condition_2 = volume > required_volume

        logger.debug(f"Volume check: current={volume:,.0f}, avg={adj_mean:,.0f}, "
                    f"required={required_volume:,.0f}, pass={volume_condition_1 and volume_condition_2}")

        return volume_condition_1 and volume_condition_2

    def check_support_resistance_squeeze(self, close: float,
                                        r1: Optional[float],
                                        s1: Optional[float]) -> bool:
        """
        Check if price is squeezed between support and resistance.

        Args:
            close: Current close price
            r1: Resistance level (pivot high)
            s1: Support level (pivot low)

        Returns:
            True if price is squeezed (avoid trading)
        """
        if r1 is None or s1 is None:
            return False
        return close < r1 and close > s1

    def calculate_rsi(self, close: pd.Series, period: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index (RSI) using numba_indicators.

        Args:
            close: Close price series
            period: RSI period (default 14)

        Returns:
            Series of RSI values
        """
        # Calculate RSI using numba_indicators (uses Wilder's smoothing internally)
        rsi_values = numba_rsi(close.values, period, smoothing=2.0, f_sma=True, f_clip=True, f_abs=True)
        return pd.Series(rsi_values, index=close.index)

    def calculate_vwap(self, high: pd.Series, low: pd.Series,
                      close: pd.Series, volume: pd.Series) -> pd.Series:
        """
        Calculate Volume Weighted Average Price (VWAP).

        Args:
            high: High price series
            low: Low price series
            close: Close price series
            volume: Volume series

        Returns:
            Series of VWAP values
        """
        typical_price = (high + low + close) / 3
        vwap = (typical_price * volume).cumsum() / volume.cumsum()
        return vwap

    def process_bar(self, bar_data: Dict, historical_data: pd.DataFrame) -> Dict:
        """
        Process a single bar of market data and generate trading signals.

        FIXES APPLIED:
        - Fix 1: Added _build_state_dict() helper for consistent state returns
        - Fix 2: Fixed sticky MA flags (long_ma/short_ma) to reset each bar
        - Fix 3: Added historical data trimming to prevent O(N²) performance
        - Fix 6: Fixed daily reset to use proper date comparison

        This is the main method that should be called for each new bar.
        It updates internal state and returns any trading actions.

        Args:
            bar_data: Dictionary with current bar data:
                - timestamp: datetime
                - open: float
                - high: float
                - low: float
                - close: float
                - volume: float
            historical_data: DataFrame with OHLCV history for calculations
                Required columns: open, high, low, close, volume, timestamp

        Returns:
            Dictionary with:
                - signal: "BUY", "SELL", "CLOSE_ALL", or None
                - order_details: Dict with order information if signal exists
                - state: Dict with current strategy state
                - alerts: List of alert messages
                - error: Error message if processing failed

        Raises:
            ValueError: If inputs are invalid
            Exception: For processing errors
        """
        # Initialize return structure
        result = {
            "signal": None,
            "order_details": None,
            "state": {},
            "alerts": [],
            "error": None
        }

        try:
            # Validate inputs
            required_bar_fields = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
            missing_fields = [f for f in required_bar_fields if f not in bar_data]
            if missing_fields:
                raise ValueError(f"Missing required bar data fields: {missing_fields}")

            required_hist_columns = ['open', 'high', 'low', 'close', 'volume']
            missing_columns = [c for c in required_hist_columns if c not in historical_data.columns]
            if missing_columns:
                raise ValueError(f"Missing required historical data columns: {missing_columns}")

            # Fix 3: Trim historical data to prevent O(N²) performance
            lookback = self._required_history()
            if len(historical_data) < lookback:
                logger.warning(f"Need {lookback} bars, have {len(historical_data)}")
                result['error'] = "Insufficient historical data"
                result['state'] = self._build_state_dict()
                return result

            hist = historical_data.tail(lookback)

            # Extract current bar data
            timestamp = bar_data['timestamp']
            open_price = bar_data['open']
            high = bar_data['high']
            low = bar_data['low']
            close = bar_data['close']
            volume = bar_data['volume']

            logger.debug(f"Processing bar: {timestamp} | O:{open_price:.2f} H:{high:.2f} "
                        f"L:{low:.2f} C:{close:.2f} V:{volume:,.0f}")

            # Check if new day (daily reset) - Fix 6: Use proper date comparison
            # Use historical_data instead of maintaining separate price_history list
            if len(historical_data) > 1 and 'timestamp' in historical_data.columns:
                # Compare current bar (timestamp) vs previous bar in history
                prev_timestamp = historical_data['timestamp'].iloc[-2]
                if timestamp.date() > prev_timestamp.date():
                    self.daily_reset()

            # Update bar counter
            self.bar_index += 1

            # Adjust timeframe multiplier
            self.tf_int = self._adjust_timeframe(self.timeframe)

            # Update account balance
            if self.account_balance_dyn is None:
                self.account_balance_dyn = (self.account_balance_input
                                           if self.account_balance_input > 0
                                           else self.initial_capital)

            # Calculate profit tracking
            current_net_profit = self.strategy_net_profit + self.strategy_open_profit
            profit_change = current_net_profit - self.last_net_profit
            self.daily_net_profit += profit_change
            self.last_net_profit = current_net_profit

            # Unix time condition
            unix_time_cond = int(timestamp.timestamp()) > self.unix_time

            if not unix_time_cond:
                result['state'] = self._build_state_dict()
                return result  # Not yet activated

            # Calculate indicators (using trimmed hist DataFrame)
            # Main Supertrend
            supertrend, direction = self.calculate_supertrend(
            hist['high'],
            hist['low'],
            hist['close'],
            self.atr_period * self.tf_int,
            self.factor
        )

            # Triple Supertrend confirmation
            supertrend1, direction1 = self.calculate_supertrend(
                hist['high'],
                hist['low'],
                hist['close'],
                self.atr_period1,
                self.factor1
            )
            supertrend2, direction2 = self.calculate_supertrend(
                hist['high'],
                hist['low'],
                hist['close'],
                self.atr_period2,
                self.factor2
            )
            supertrend3, direction3 = self.calculate_supertrend(
                hist['high'],
                hist['low'],
                hist['close'],
                self.atr_period3,
                self.factor3
            )

            # Trailing stop Supertrend
            supertrend_sl, direction_sl = self.calculate_supertrend(
                hist['high'],
                hist['low'],
                hist['close'],
                self.ts_period * self.tf_int,
                self.ts_factor
            )

            # Get current values
            current_idx = len(hist) - 1
            curr_direction = direction.iloc[current_idx]
            curr_direction_sl = direction_sl.iloc[current_idx]
            curr_supertrend_sl = supertrend_sl.iloc[current_idx]

            # Previous values
            prev_direction = direction.iloc[current_idx - 1] if current_idx > 0 else curr_direction
            prev_direction_sl = direction_sl.iloc[current_idx - 1] if current_idx > 0 else curr_direction_sl

            # Update trend confirmation
            self.up_trend = (direction1.iloc[current_idx] == -1 and
                            direction2.iloc[current_idx] == -1 and
                            direction3.iloc[current_idx] == -1)
            self.dn_trend = (direction1.iloc[current_idx] == 1 and
                            direction2.iloc[current_idx] == 1 and
                            direction3.iloc[current_idx] == 1)

            if self.up_trend:
                self.dn_trend = False
            if self.dn_trend:
                self.up_trend = False

            # Update stop loss tracking
            if not pd.isna(curr_supertrend_sl):
                self.vstop_sl_fix = curr_supertrend_sl

            # Calculate moving averages
            ema9 = self.calculate_ema(hist['close'], 9 * self.tf_int)
            rma9 = self.calculate_rma(hist['close'], 9 * self.tf_int)
            self.ema9_one_min = ema9.iloc[current_idx]
            self.rma9_one_min = rma9.iloc[current_idx]

            # Update MA trend flags (Fix 2: Reset flags every bar to prevent stale values)
            ema_ok = not pd.isna(self.ema9_one_min) and not pd.isna(self.rma9_one_min)

            self.long_ma = (
                ema_ok
                and close > open_price
                and self.ema9_one_min > self.rma9_one_min
                and close > self.ema9_one_min
            )

            self.short_ma = (
                ema_ok
                and close < open_price
                and self.ema9_one_min < self.rma9_one_min
                and close < self.ema9_one_min
            )

            # Calculate support/resistance
            pivot_high = self.calculate_pivot_high(hist['high'], 3, 3)
            pivot_low = self.calculate_pivot_low(hist['low'], 3, 3)
            self.high_use_pivot = self.fixnan(pivot_high).iloc[current_idx]
            self.low_use_pivot = self.fixnan(pivot_low).iloc[current_idx]

            r1 = self.high_use_pivot
            s1 = self.low_use_pivot
            level_squeeze = self.check_support_resistance_squeeze(close, r1, s1)

            # Calculate RSI
            rsi_series = self.calculate_rsi(hist['close'], 14)
            rsi = rsi_series.iloc[current_idx]

            # Volume analysis
            # Simplified volume check (full implementation would track session bars)
            vol_cond = self.check_volume_conditions(
                volume, close,
                hist['volume'].tail(10 * self.tf_int)
            )

            # Update position flags
            self.enter = self.strategy_position_size != 0
            self.long_e = self.strategy_position_size > 0
            self.short_e = self.strategy_position_size < 0

            # Entry signals (only if no position)
            if not self.enter and not level_squeeze and vol_cond and not self.profit_sig:

                # Check for long entry
                long_signal = (curr_direction != 1 and
                              prev_direction == 1 and
                              curr_direction_sl != 1 and
                              not pd.isna(curr_supertrend_sl))

                # Check for short entry
                short_signal = (curr_direction == 1 and
                               prev_direction != 1 and
                               curr_direction_sl == 1 and
                               not pd.isna(curr_supertrend_sl))

                # Long entry conditions
                if (not self.short_ma and long_signal and
                    close > self.ema9_one_min and close > self.rma9_one_min and
                    self.bias != "Short" and self.up_trend and close > open_price):

                    try:
                        logger.info(f"🟢 LONG ENTRY TRIGGERED | Price: ${close:.2f} | "
                                   f"Trend: {'UP' if self.up_trend else 'N/A'}")

                        # Calculate stop and target
                        self.long_stop = curr_supertrend_sl - 0.02
                        per_share_risk = abs(close - self.long_stop)
                        self.long_target = close + self.reward_risk_ratio * (close - self.long_stop)

                        logger.debug(f"Long entry calculations: stop=${self.long_stop:.2f}, "
                                    f"target=${self.long_target:.2f}, risk_per_share=${per_share_risk:.2f}")

                        # Calculate position size
                        qty = self.calculate_position_size_long(close, self.long_stop)
                        self.qty_tl = qty

                        if qty <= 0:
                            logger.warning(f"Invalid position size calculated: {qty}, skipping entry")
                            raise ValueError(f"Position size must be positive, got {qty}")

                        logger.info(f"Position size calculated: {qty:,.0f} shares | "
                                   f"Entry: ${close:.2f} | Risk: ${per_share_risk * qty:,.2f}")

                        # Create order
                        self.notes = f"supertrend Long{timestamp}"
                        result['signal'] = "BUY"
                        result['order_details'] = self.build_order_json(
                            close, "BUY", qty, self.long_stop, self.long_target, self.notes
                        )

                        # Update state
                        self.long_e = True
                        self.strategy_position_size = qty
                        self.alert_sent = True

                        result['alerts'].append(f"LONG ENTRY: qty={qty}, stop={self.long_stop:.2f}, target={self.long_target:.2f}")
                        logger.info(f"✓ LONG ORDER CREATED | Qty: {qty:,.0f} | Stop: ${self.long_stop:.2f} | "
                                   f"Target: ${self.long_target:.2f} | R:R={self.reward_risk_ratio}")

                    except Exception as e:
                        logger.error(f"Failed to create long entry: {e}", exc_info=True)
                        result['alerts'].append(f"ERROR: Long entry failed - {e}")

                # Short entry conditions
                elif (not self.long_ma and short_signal and
                      close < self.ema9_one_min and close < self.rma9_one_min and
                      self.bias != "Long" and self.dn_trend and close < open_price):

                    try:
                        logger.info(f"🔴 SHORT ENTRY TRIGGERED | Price: ${close:.2f} | "
                                   f"Trend: {'DOWN' if self.dn_trend else 'N/A'}")

                        # Calculate stop and target
                        self.short_stop = curr_supertrend_sl + 0.02
                        per_share_risk = abs(close - self.short_stop)
                        self.short_target = close - self.reward_risk_ratio * (self.short_stop - close)

                        logger.debug(f"Short entry calculations: stop=${self.short_stop:.2f}, "
                                    f"target=${self.short_target:.2f}, risk_per_share=${per_share_risk:.2f}")

                        # Calculate position size
                        qty = self.calculate_position_size_short(close, self.short_stop)
                        self.qty_ts = qty

                        if qty <= 0:
                            logger.warning(f"Invalid position size calculated: {qty}, skipping entry")
                            raise ValueError(f"Position size must be positive, got {qty}")

                        logger.info(f"Position size calculated: {qty:,.0f} shares | "
                                   f"Entry: ${close:.2f} | Risk: ${per_share_risk * qty:,.2f}")

                        # Create order
                        self.notes = f"supertrend short{timestamp}"
                        result['signal'] = "SELL"
                        result['order_details'] = self.build_order_json(
                            close, "SELL", qty, self.short_stop, self.short_target, self.notes
                        )

                        # Update state
                        self.short_e = True
                        self.strategy_position_size = -qty
                        self.alert_sent = True

                        result['alerts'].append(f"SHORT ENTRY: qty={qty}, stop={self.short_stop:.2f}, target={self.short_target:.2f}")
                        logger.info(f"✓ SHORT ORDER CREATED | Qty: {qty:,.0f} | Stop: ${self.short_stop:.2f} | "
                                   f"Target: ${self.short_target:.2f} | R:R={self.reward_risk_ratio}")

                    except Exception as e:
                        logger.error(f"Failed to create short entry: {e}", exc_info=True)
                        result['alerts'].append(f"ERROR: Short entry failed - {e}")

            # Exit logic (only if in position)
            if self.enter and not pd.isna(self.vstop_sl_fix):
                exit_reason = None

                # Trailing stop exits
                if self.use_trailing_stop_loss:
                    if self.long_e and low <= self.vstop_sl_fix:
                        exit_reason = "crossdownStop close_all"
                    elif self.short_e and high >= self.vstop_sl_fix:
                        exit_reason = "crossUpStop close_all"

                # Profit threshold exit
                profit_close = self.strategy_open_profit + self.strategy_net_profit
                profit_threshold_break = (profit_close >= self.profit_threshold or
                                         profit_close <= (self.account_balance_dyn *
                                                         (self.risk_percentage / 100)) * -1)

                if self.profit_sig_bool and profit_threshold_break and not self.close_all:
                    exit_reason = "profitSig"
                    self.profit_sig = True

                # Take profit and RSI exits
                if self.long_e and not self.close_all:
                    # Check crossover for take profit
                    if self.long_target is not None and high >= self.long_target:
                        exit_reason = "crossupTP close_all"
                    # RSI overbought
                    elif (self.long_target is not None and
                          close >= self.long_target and rsi >= 80):
                        exit_reason = "exitRSI close_all"

                if self.short_e and not self.close_all:
                    # Check crossunder for take profit
                    if self.short_target is not None and low <= self.short_target:
                        exit_reason = "crossdownTP close_all"
                    # RSI oversold
                    elif (self.short_target is not None and
                          close <= self.short_target and rsi <= 20):
                        exit_reason = "exitRSI close_all"

                # Execute exit if triggered
                if exit_reason and not self.close_all:
                    try:
                        uptrend_fn_bool = (curr_direction_sl == -1 or self.up_trend)
                        position_type = "LONG" if self.long_e else "SHORT" if self.short_e else "UNKNOWN"

                        logger.warning(f"🚪 EXIT TRIGGERED: {exit_reason} | Position: {position_type} | "
                                      f"Price: ${close:.2f} | Size: {abs(self.strategy_position_size):,.0f}")

                        result['signal'] = "CLOSE_ALL"
                        result['order_details'] = self.build_close_all_json(
                            close, exit_reason, uptrend_fn_bool
                        )

                        # Reset position
                        prev_position_size = self.strategy_position_size
                        self.strategy_position_size = 0
                        self.long_e = False
                        self.short_e = False
                        self.close_all = True
                        self.close_all_sig = False

                        result['alerts'].append(f"EXIT: {exit_reason}")
                        logger.info(f"✓ CLOSE ALL ORDER CREATED | Reason: {exit_reason} | "
                                   f"Closed: {abs(prev_position_size):,.0f} shares")

                    except Exception as e:
                        logger.error(f"Failed to create exit order: {e}", exc_info=True)
                        result['alerts'].append(f"ERROR: Exit order failed - {e}")

            # Update state dictionary before return (Fix 1: Ensure consistent state)
            result['state'] = self._build_state_dict()

            # Log signal if generated
            if result['signal']:
                logger.info(f"🔔 TRADE SIGNAL: {result['signal']} at {timestamp} | "
                           f"Price: ${close:.2f} | Bar: {self.bar_index}")
                if result['order_details']:
                    logger.info(f"Order Details:{strategy_log_config.format_order(result['order_details'])}")

            # Log state periodically (every 100 bars)
            if self.bar_index % 100 == 0:
                logger.debug(f"Strategy State:{strategy_log_config.format_state(result['state'])}")

            return result

        except ValueError as e:
            logger.error(f"Validation error in process_bar: {e}")
            result['error'] = str(e)
            result['state'] = self._build_state_dict()
            return result
        except KeyError as e:
            logger.error(f"Missing data key in process_bar: {e}", exc_info=True)
            result['error'] = f"Missing data: {e}"
            result['state'] = self._build_state_dict()
            return result
        except Exception as e:
            logger.error(f"Unexpected error in process_bar: {e}", exc_info=True)
            result['error'] = f"Processing error: {e}"
            result['state'] = self._build_state_dict()
            return result


# ============================================================================
# MARKET DATA PLACEHOLDER
# ============================================================================

def get_market_data() -> pd.DataFrame:
    """
    Placeholder function for market data retrieval.

    Replace this with actual data source integration (broker API, database, CSV, etc.)

    Expected DataFrame format:
        - timestamp: datetime64[ns]
        - open: float64
        - high: float64
        - low: float64
        - close: float64
        - volume: float64

    Returns:
        DataFrame with OHLCV data

    Raises:
        NotImplementedError: This is a placeholder
    """
    raise NotImplementedError(
        "Market data source not implemented. "
        "Replace this function with actual data feed integration."
    )


# ============================================================================
# TESTING NOTES
# ============================================================================
# After fixes applied:
# 1. Missing return bug: process_bar() always returns dict with 'state' key
# 2. Sticky MA flags: long_ma/short_ma reset properly each bar
# 3. O(N²) fix: Indicators calculated on fixed window (~150-200 bars max)
# 4. P&L tracking: Disabled by default, call update_pnl() to enable
# 5. Volume filter: Documented calculation, may need tuning per symbol
# 6. Daily reset: Now uses proper date comparison across month boundaries
# 7. Indicator library: Replaced TA-Lib with numba_indicators for better performance
# ============================================================================

# ============================================================================
# USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    """
    Example usage of the SupertrendStrategy class with logging.

    This demonstrates how to:
    1. Set up logging
    2. Initialize the strategy with custom parameters
    3. Load market data
    4. Process bars sequentially
    5. Handle trading signals and errors
    """

    # STEP 1: Set up logging (IMPORTANT: Do this first!)
    print("="*60)
    print("Setting up logging...")
    print("="*60)
    strategy_log_config.setup()
    logger.info("="*60)
    logger.info("Supertrend Strategy - Example Execution")
    logger.info("="*60)

    try:
        # STEP 2: Initialize strategy with custom parameters
        logger.info("Initializing strategy...")
        strategy = SupertrendStrategy(
            unix_time=1700000000,  # Activation timestamp
            use_trailing_stop_loss=True,
            bias="both",
            profit_threshold=500.0,
            reward_risk_ratio=2.0,
            risk_percentage=1.5,
            account_balance=50000.0,
            atr_period=10,
            factor=3.0,
            symbol="AAPL"
        )

        logger.info("✓ Strategy initialized successfully!")
        logger.info(f"Symbol: {strategy.symbol}")
        logger.info(f"Initial Capital: ${strategy.initial_capital:,.2f}")
        logger.info(f"Risk per Trade: {strategy.risk_percentage}%")
        logger.info(f"Reward/Risk Ratio: {strategy.reward_risk_ratio}")

        # STEP 3: Create sample data for testing
        # In production, replace this with actual market data
        logger.info("Generating sample market data...")
        dates = pd.date_range(start='2024-01-01', periods=100, freq='1min')
        sample_data = pd.DataFrame({
            'timestamp': dates,
            'open': np.random.uniform(150, 160, 100),
            'high': np.random.uniform(155, 165, 100),
            'low': np.random.uniform(145, 155, 100),
            'close': np.random.uniform(150, 160, 100),
            'volume': np.random.uniform(1000000, 5000000, 100)
        })
        logger.info(f"Generated {len(sample_data)} sample bars")

        # STEP 4: Process each bar
        logger.info("="*60)
        logger.info("Starting bar processing...")
        logger.info("="*60)

        signal_count = {'BUY': 0, 'SELL': 0, 'CLOSE_ALL': 0, 'ERROR': 0}

        for idx in range(20, len(sample_data)):  # Start at 20 to have enough history
            try:
                historical = sample_data.iloc[:idx+1]
                current_bar = {
                    'timestamp': sample_data.iloc[idx]['timestamp'],
                    'open': sample_data.iloc[idx]['open'],
                    'high': sample_data.iloc[idx]['high'],
                    'low': sample_data.iloc[idx]['low'],
                    'close': sample_data.iloc[idx]['close'],
                    'volume': sample_data.iloc[idx]['volume']
                }

                # Process the bar
                result = strategy.process_bar(current_bar, historical)

                # Check for errors
                if result.get('error'):
                    logger.error(f"Bar {idx} processing error: {result['error']}")
                    signal_count['ERROR'] += 1
                    continue

                # Handle signals
                if result['signal']:
                    signal_count[result['signal']] += 1
                    logger.info(f"\n{'='*60}")
                    logger.info(f"Bar {idx}: {result['signal']} SIGNAL")
                    logger.info(f"Time: {current_bar['timestamp']}")
                    logger.info(f"Price: ${current_bar['close']:.2f}")

                    if result['order_details']:
                        logger.info(f"Order Details:{strategy_log_config.format_order(result['order_details'])}")

                    for alert in result['alerts']:
                        logger.info(f"  Alert: {alert}")

                    logger.info(f"{'='*60}\n")

            except Exception as e:
                logger.error(f"Unexpected error processing bar {idx}: {e}", exc_info=True)
                signal_count['ERROR'] += 1
                continue

        # STEP 5: Summary
        logger.info("="*60)
        logger.info("Execution Summary")
        logger.info("="*60)
        logger.info(f"Total bars processed: {len(sample_data) - 20}")
        logger.info(f"BUY signals: {signal_count['BUY']}")
        logger.info(f"SELL signals: {signal_count['SELL']}")
        logger.info(f"CLOSE_ALL signals: {signal_count['CLOSE_ALL']}")
        logger.info(f"Errors: {signal_count['ERROR']}")
        logger.info(f"Daily P&L: ${strategy.daily_net_profit:,.2f}")
        logger.info("="*60)

        logger.success("✓ Example execution complete")
        logger.info("\n📝 Note: This example uses random data for demonstration.")
        logger.info("For production use, replace get_market_data() with a real data source.")
        logger.info(f"\n📁 Logs saved to: {strategy_log_config.logs_dir}")

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        raise
    except Exception as e:
        logger.error(f"Fatal error in example execution: {e}", exc_info=True)
        raise
