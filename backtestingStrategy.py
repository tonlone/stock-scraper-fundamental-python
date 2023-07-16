import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf
import seaborn as sns

class BacktestingSystem:
    def __init__(self, initial_cash=100):
        self.data = None
        self.initial_cash = initial_cash
    
    def load_data(self, symbol, start_date, end_date):
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start_date, end=end_date)
        self.data = df[['Open', 'High', 'Low', 'Close', 'Volume']]
        self.data.columns = ['open', 'high', 'low', 'close', 'volume']
    
    def plot_results(self, portfolio, strategyName, symbol):
        sns.set(style='whitegrid')
        fig, ax = plt.subplots(2, 1, figsize=(12, 8))
    
        ax[0].plot(self.data['close'], label='Price', color='steelblue', linewidth=2)
        ax[0].set_ylabel('Price', fontsize=12)
        
        # Add buy and sell signals on the price graph
        buy_signals = portfolio[portfolio['position'] == 1]
        sell_signals = portfolio[portfolio['position'] == -1]
        ax[0].scatter(buy_signals.index, buy_signals['close'], marker='^', color='green', label='Buy')
        ax[0].scatter(sell_signals.index, sell_signals['close'], marker='v', color='red', label='Sell')
        
        ax[0].legend(loc='upper left', fontsize=10)
    
        ax[1].plot(portfolio['total'], label='Portfolio Value', color='forestgreen', linewidth=2)
        ax[1].set_ylabel(f'Portfolio Value (Initial Value = {self.initial_cash})', fontsize=12)
        ax[1].legend(loc='upper left', fontsize=10)
    
        ax[1].set_xlabel('Date', fontsize=12)
    
        plt.tight_layout(pad=2)
        fig.suptitle(f'Backtesting Results ({strategyName}) - {symbol}', fontsize=16, fontweight='bold')
        plt.tick_params(axis='both', which='both', bottom=False, left=False)
    
        for axis in ['top', 'right']:
            ax[0].spines[axis].set_visible(False)
            ax[1].spines[axis].set_visible(False)
    
        plt.show(block=False)
    
    def backtest_strategy(self, strategy):
        signals = strategy.generate_signals()
        positions = signals['signal'].diff()
        portfolio = pd.DataFrame(index=self.data.index)
        portfolio['position'] = positions
        portfolio['close'] = self.data['close']
        portfolio['holdings'] = portfolio['position'].cumsum() * portfolio['close']
        portfolio['cash'] = self.initial_cash - (portfolio['position'] * portfolio['close']).cumsum()
        portfolio['total'] = portfolio['cash'] + portfolio['holdings']
        portfolio['returns'] = portfolio['total'].pct_change()
        return portfolio

class MovingAverageCrossoverStrategy:
    def __init__(self, data, short_window, long_window):
        self.data = data
        self.short_window = short_window
        self.long_window = long_window
        self.name = "MovingAverageCrossover"

    def generate_signals(self):
        signals = pd.DataFrame(index=self.data.index)
        signals['signal'] = 0
        signals['short_mavg'] = self.data['close'].rolling(window=self.short_window, min_periods=1).mean()
        signals['long_mavg'] = self.data['close'].rolling(window=self.long_window, min_periods=1).mean()

        signals.loc[signals.index[self.short_window:], 'signal'] = np.where(
            signals['short_mavg'][self.short_window:] > signals['long_mavg'][self.short_window:], 1, 0
        )

        return signals


class MACDStrategy:
    def __init__(self, data, short_window=12, long_window=26, signal_window=9):
        self.data = data
        self.short_window = short_window
        self.long_window = long_window
        self.signal_window = signal_window
        self.name = "MACD"

    def generate_signals(self):
        signals = pd.DataFrame(index=self.data.index)
        signals['signal'] = 0

        signals['macd_line'] = self.data['close'].ewm(span=self.short_window).mean() - self.data['close'].ewm(
            span=self.long_window).mean()

        signals['signal_line'] = signals['macd_line'].ewm(span=self.signal_window).mean()

        signals.loc[signals.index[self.short_window:], 'signal'] = np.where(
            signals['macd_line'][self.short_window:] > signals['signal_line'][self.short_window:], 1, 0
        )

        return signals


class RSIStrategy:
    def __init__(self, data, rsi_period=14, oversold_threshold=30, overbought_threshold=70):
        self.data = data
        self.rsi_period = rsi_period
        self.oversold_threshold = oversold_threshold
        self.overbought_threshold = overbought_threshold
        self.name = "RSI"

    def generate_signals(self):
        signals = pd.DataFrame(index=self.data.index)
        signals['signal'] = 0

        delta = self.data['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        avg_gain = gain.rolling(window=self.rsi_period).mean()
        avg_loss = loss.rolling(window=self.rsi_period).mean()

        rsi = 100 - (100 / (1 + avg_gain / avg_loss))

        signals.loc[signals.index[self.rsi_period:], 'signal'] = np.where(
            rsi[self.rsi_period:] < self.oversold_threshold, 1,
            np.where(rsi[self.rsi_period:] > self.overbought_threshold, -1, 0)
        )

        return signals


# Example usage
if __name__ == '__main__':
    initial_cash = 100  # Set your desired initial cash value
    backtester = BacktestingSystem(initial_cash=initial_cash)
    symbol = "0001.HK"
    start_date = "2022-10-01"
    end_date = "2023-07-16"
    backtester.load_data(symbol, start_date, end_date)
    macd_strategy = MACDStrategy(backtester.data)
    portfolio = backtester.backtest_strategy(macd_strategy)
    backtester.plot_results(portfolio, macd_strategy.name, symbol)

    moving_average_crossover_strategy = MovingAverageCrossoverStrategy(backtester.data, short_window=50, long_window=200)
    portfolio = backtester.backtest_strategy(moving_average_crossover_strategy)
    backtester.plot_results(portfolio, moving_average_crossover_strategy.name, symbol)

    rsi_strategy = RSIStrategy(backtester.data)
    portfolio = backtester.backtest_strategy(rsi_strategy)
    backtester.plot_results(portfolio, rsi_strategy.name, symbol)

    # Show all plots
    plt.legend()
    plt.show()
