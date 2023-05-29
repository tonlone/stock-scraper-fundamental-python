import yfinance as yf
import ta as ta
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import sys

ticker = 'COST'
stoploss = False
strategy_name = "IchmokuCloud"

#strategy_name = "KeltnerChannel"
#strategy_name = "BollingerBands"
#strategy_name = "MA"
#strategy_name = "MACD" *
#strategy_name = "RSI"
#strategy_name = "WR"
#strategy_name = "RSIFast"
#strategy_name = "RSISlow"
#strategy_name = "IchmokuCloud"
valid_strategy_name_list = ["KeltnerChannel", "BollingerBands", "MA", "MACD", "WR", "RSI", "RSIFast", "RSISlow", "IchmokuCloud"]

# Define the ticker symbols of the stocks you want to analyze
#ticker_symbols = [*'COST', 'MSFT', *'PYPL', *'PG', 'UNH', 'V', *'WMT', 'NFLX', 'NVDA' ]
#ticker_symbols = ['BTC-USD', 'ETH-USD', 'DOGE-USD', 'USDT-USD', 'ADA-USD', 'BNB-USD', 'XRP-USD']
#start_date = '2022-05-01'
start_date = '2022-10-01'
end_date = '2023-05-29'
date_fmt = '%Y-%m-%d'

start_date_buffer = datetime.strptime(start_date, date_fmt) - timedelta(days=365)
start_date_buffer = start_date_buffer.strftime(date_fmt)

def strategy_KeltnerChannel_origin(df, **kwargs):
  n = kwargs.get('n', 10)
  data = df.copy()

  k_band = ta.volatility.KeltnerChannel(data.High, data.Low, data.Close, n)

  data['K_BAND_UB'] = k_band.keltner_channel_hband().round(4)
  data['K_BAND_LB'] = k_band.keltner_channel_lband().round(4)

  data['CLOSE_PREV'] = data.Close.shift(1)
  
  data['LONG'] = (data.Close <= data.K_BAND_LB) & (data.CLOSE_PREV > data.K_BAND_LB)
  data['EXIT_LONG'] = (data.Close >= data.K_BAND_UB) & (data.CLOSE_PREV < data.K_BAND_UB)

  data['SHORT'] = (data.Close >= data.K_BAND_UB) & (data.CLOSE_PREV < data.K_BAND_UB)
  data['EXIT_SHORT'] = (data.Close <= data.K_BAND_LB) & (data.CLOSE_PREV > data.K_BAND_LB)

  data.LONG = data.LONG.shift(1)
  data.EXIT_LONG = data.EXIT_LONG.shift(1)
  
  data.SHORT = data.SHORT.shift(1)
  data.EXIT_SHORT = data.EXIT_SHORT.shift(1)

  #print("***** Keltner Channel *****")
  #print(data)
  return data, "Keltner Channel"

def strategy_BollingerBands(df, **kwargs):
  n = kwargs.get('n', 10)
  n_rng = kwargs.get('n_rng', 2)
  data = df.copy()

  boll = ta.volatility.BollingerBands(data.Close, n, n_rng)

  data['BOLL_LBAND_INDI'] = boll.bollinger_lband_indicator()
  data['BOLL_UBAND_INDI'] = boll.bollinger_hband_indicator()

  data['CLOSE_PREV'] = data.Close.shift(1)

  data['LONG'] = data.BOLL_LBAND_INDI == 1
  data['EXIT_LONG'] = data.BOLL_UBAND_INDI == 1

  data['SHORT'] = data.BOLL_UBAND_INDI == 1
  data['EXIT_SHORT'] = data.BOLL_LBAND_INDI == 1

  data.LONG = data.LONG.shift(1)
  data.EXIT_LONG = data.EXIT_LONG.shift(1)
  data.SHORT = data.SHORT.shift(1)
  data.EXIT_SHORT = data.EXIT_SHORT.shift(1)


  #print("***** Bollinger Bands *****")
  #print(data)
  return data, "BollingerBands"

def strategy_MA(df, **kwargs):
  n = kwargs.get('n', 50)
  ma_type = kwargs.get('ma_type', 'sma')
  ma_type = ma_type.strip().lower()
  data = df.copy()
  
  if ma_type == 'sma':
    sma = ta.trend.SMAIndicator(data.Close, n)
    data['MA'] = sma.sma_indicator().round(4)
  elif ma_type == 'ema':
    ema = ta.trend.EMAIndicator(data.Close, n)
    data['MA'] = ema.ema_indicator().round(4)

  data['CLOSE_PREV'] = data.Close.shift(1)

  data['LONG'] = (data.Close > data.MA) & (data.CLOSE_PREV <= data.MA)
  data['EXIT_LONG'] = (data.Close < data.MA) & (data.CLOSE_PREV >= data.MA)

  data['SHORT'] = (data.Close < data.MA) & (data.CLOSE_PREV >= data.MA)
  data['EXIT_SHORT'] = (data.Close > data.MA) & (data.CLOSE_PREV <= data.MA)

  data.LONG = data.LONG.shift(1)
  data.EXIT_LONG = data.EXIT_LONG.shift(1)
  data.SHORT = data.SHORT.shift(1)
  data.EXIT_SHORT = data.EXIT_SHORT.shift(1)

  #print("***** Strategy moving average (MA) *****")
  #print(data)
  return data, "Moving average"

def strategy_MACD(df, **kwargs):
  n_slow = kwargs.get('n_slow', 26)
  n_fast = kwargs.get('n_fast', 12)
  n_sign = kwargs.get('n_sign', 9)
  data = df.copy()

  macd = ta.trend.MACD(data.Close, n_slow, n_fast, n_sign)

  data['MACD_DIFF'] = macd.macd_diff().round(4)
  data['MACD_DIFF_PREV'] = data.MACD_DIFF.shift(1)

  data['LONG'] = (data.MACD_DIFF > 0) & (data.MACD_DIFF_PREV <= 0)
  data['EXIT_LONG'] = (data.MACD_DIFF < 0) & (data.MACD_DIFF_PREV >= 0)

  data['SHORT'] = (data.MACD_DIFF < 0) & (data.MACD_DIFF_PREV >= 0)
  data['EXIT_SHORT'] = (data.MACD_DIFF > 0) & (data.MACD_DIFF_PREV <= 0)

  data.LONG = data.LONG.shift(1)
  data.EXIT_LONG = data.EXIT_LONG.shift(1)
  data.SHORT = data.SHORT.shift(1)
  data.EXIT_SHORT = data.EXIT_SHORT.shift(1)

  #print("***** Strategy Moving Average Convergence Divergence (MACD) *****")
  #print(data)
  return data, "Moving average MACD"

def strategy_RSI(df, **kwargs):
  n = kwargs.get('n', 14)
  data = df.copy()

  rsi = ta.momentum.RSIIndicator(data.Close, n)

  data['RSI'] = rsi.rsi().round(4)
  data['RSI_PREV'] = data.RSI.shift(1)

  data['LONG'] = (data.RSI > 30) & (data.RSI_PREV <= 30)
  data['EXIT_LONG'] = (data.RSI < 70) & (data.RSI_PREV >= 70)

  data['SHORT'] = (data.RSI < 70) & (data.RSI_PREV >= 70)
  data['EXIT_SHORT'] = (data.RSI > 30) & (data.RSI_PREV <= 30)

  data.LONG = data.LONG.shift(1)
  data.EXIT_LONG = data.EXIT_LONG.shift(1)
  data.SHORT = data.SHORT.shift(1)
  data.EXIT_SHORT = data.EXIT_SHORT.shift(1)

  #print("***** Strategy Relative Strength Index (RSI) *****")
  #print(data)
  return data, "Relative Strength Index RSI"

def strategy_WR(df, **kwargs):
  n = kwargs.get('n', 14)
  data = df.copy()

  wr = ta.momentum.WilliamsRIndicator(data.High, data.Low, data.Close, n)

  data['WR'] = wr.williams_r().round(4)
  data['WR_PREV'] = data.WR.shift(1)

  data['LONG'] = (data.WR > -80) & (data.WR_PREV <= -80)
  data['EXIT_LONG'] = (data.WR < -20) & (data.WR_PREV >= -20)

  data['SHORT'] = (data.WR < -20) & (data.WR_PREV >= -20)
  data['EXIT_SHORT'] = (data.WR > -80) & (data.WR_PREV <= -80)

  data.LONG = data.LONG.shift(1)
  data.EXIT_LONG = data.EXIT_LONG.shift(1)
  data.SHORT = data.SHORT.shift(1)
  data.EXIT_SHORT = data.EXIT_SHORT.shift(1)

  #print("***** Strategy Williams %R (WR) *****")
  #print(data)
  return data, "Williams %R WR"

def strategy_Stochastic_fast(df, **kwargs):
  k = kwargs.get('k', 20)
  d = kwargs.get('d', 5)
  data = df.copy()

  sto = ta.momentum.StochasticOscillator(data.High, data.Low, data.Close, k, d)

  data['K'] = sto.stoch().round(4)
  data['D'] = sto.stoch_signal().round(4)
  data['DIFF'] = data['K'] - data['D']
  data['DIFF_PREV'] = data.DIFF.shift(1)
  
  data['LONG'] = (data.DIFF > 0) & (data.DIFF_PREV <= 0)
  data['EXIT_LONG'] = (data.DIFF < 0) & (data.DIFF_PREV >= 0)

  data['SHORT'] = (data.DIFF < 0) & (data.DIFF_PREV >= 0)
  data['EXIT_SHORT'] = (data.DIFF > 0) & (data.DIFF_PREV <= 0)

  data.LONG = data.LONG.shift(1)
  data.EXIT_LONG = data.EXIT_LONG.shift(1)

  data.SHORT = data.SHORT.shift(1)
  data.EXIT_SHORT = data.EXIT_SHORT.shift(1)

  #print("***** Stochastic Oscillator Fast *****")
  #print(data)
  return data, "Stochastic Oscillator Fast"

def strategy_Stochastic_slow(df, **kwargs):
  k = kwargs.get('k', 20)
  d = kwargs.get('d', 5)
  dd = kwargs.get('dd', 3)
  data = df.copy()

  sto = ta.momentum.StochasticOscillator(data.High, data.Low, data.Close, k, d)

  data['K'] = sto.stoch().round(4)
  data['D'] = sto.stoch_signal().round(4)
  
  ma = ta.trend.SMAIndicator(data.D, dd)
  data['DD'] = ma.sma_indicator().round(4)

  data['DIFF'] = data['D'] - data['DD']
  data['DIFF_PREV'] = data.DIFF.shift(1)
  
  data['LONG'] = (data.DIFF > 0) & (data.DIFF_PREV <= 0)
  data['EXIT_LONG'] = (data.DIFF < 0) & (data.DIFF_PREV >= 0)

  data['SHORT'] = (data.DIFF < 0) & (data.DIFF_PREV >= 0)
  data['EXIT_SHORT'] = (data.DIFF > 0) & (data.DIFF_PREV <= 0)

  data.LONG = data.LONG.shift(1)
  data.EXIT_LONG = data.EXIT_LONG.shift(1)

  data.SHORT = data.SHORT.shift(1)
  data.EXIT_SHORT = data.EXIT_SHORT.shift(1)

  #print("***** Stochastic Oscillator Slow *****")
  #print(data)
  return data, "Stochastic Oscillator Slow"

def strategy_Ichmoku(df, **kwargs):
  n_conv = kwargs.get('n_conv', 9)
  n_base = kwargs.get('n_base', 26)
  n_span_b = kwargs.get('n_span_b', 26)
  data = df.copy()

  ichmoku = ta.trend.IchimokuIndicator(data.High, data.Low, n_conv, n_base, n_span_b)

  data['BASE'] = ichmoku.ichimoku_base_line().round(4)
  data['CONV'] = ichmoku.ichimoku_conversion_line().round(4)

  data['DIFF'] = data['CONV'] - data['BASE']
  data['DIFF_PREV'] = data.DIFF.shift(1)
  
  data['LONG'] = (data.DIFF > 0) & (data.DIFF_PREV <= 0)
  data['EXIT_LONG'] = (data.DIFF < 0) & (data.DIFF_PREV >= 0)

  data['SHORT'] = (data.DIFF < 0) & (data.DIFF_PREV >= 0)
  data['EXIT_SHORT'] = (data.DIFF > 0) & (data.DIFF_PREV <= 0)

  data.LONG = data.LONG.shift(1)
  data.EXIT_LONG = data.EXIT_LONG.shift(1)

  data.SHORT = data.SHORT.shift(1)
  data.EXIT_SHORT = data.EXIT_SHORT.shift(1)

  #print("***** Ichimoku Cloud indicator *****")
  #print(data)
  return data, "Ichimoku Cloud indicator"

def evaluate_trading_strategy(ticker, bt_df, strategy_name, stop_loss_enabled=False):
    balance = 1000000
    pnl = 0
    position = 0

    stop_loss_lvl = -2

    last_signal = 'hold'
    last_price = 0
    c = 0

    trade_date_start = []
    trade_date_end = []
    trade_days = []
    trade_side = []
    trade_pnl = []
    trade_ret = []

    cum_value = []

    for index, row in bt_df.iterrows():
        # check and close any positions
        if row.EXIT_LONG and last_signal == 'long':
            trade_date_end.append(row.name)
            trade_days.append(c)

            pnl = (row.Open - last_price) * position
            trade_pnl.append(pnl)
            trade_ret.append((row.Open / last_price - 1) * 100)

            balance = balance + row.Open * position

            position = 0
            last_signal = 'hold'

            c = 0

        elif row.EXIT_SHORT and last_signal == 'short':
            trade_date_end.append(row.name)
            trade_days.append(c)

            pnl = (row.Open - last_price) * position
            trade_pnl.append(pnl)
            trade_ret.append((last_price / row.Open - 1) * 100)

            balance = balance + pnl

            position = 0
            last_signal = 'hold'

            c = 0

        # check signal and enter any possible position
        if row.LONG and last_signal != 'long':
            last_signal = 'long'
            last_price = row.Open
            trade_date_start.append(row.name)
            trade_side.append('long')

            position = int(balance / row.Open)
            cost = position * row.Open
            balance = balance - cost

            c = 0

        elif row.SHORT and last_signal != 'short':
            last_signal = 'short'
            last_price = row.Open
            trade_date_start.append(row.name)
            trade_side.append('short')

            position = int(balance / row.Open) * -1

            c = 0

            # check stop loss if enabled
            if stop_loss_enabled:
                if last_signal == 'long' and c > 0 and (row.Low / last_price - 1) * 100 <= stop_loss_lvl:
                    c = c + 1

                    trade_date_end.append(row.name)
                    trade_days.append(c)

                    stop_loss_price = last_price + round(last_price * (stop_loss_lvl / 100), 4)
                    pnl = (stop_loss_price - last_price) * position
                    trade_pnl.append(pnl)
                    trade_ret.append((stop_loss_price / last_price - 1) * 100)

                    balance = balance + stop_loss_price * position

                    position = 0
                    last_signal = 'hold'

                    c = 0

                elif last_signal == 'short' and c > 0 and (last_price / row.High - 1) * 100 <= stop_loss_lvl:
                    c = c + 1

                    trade_date_end.append(row.name)
                    trade_days.append(c)

                    stop_loss_price = last_price - round(last_price * (stop_loss_lvl / 100), 4)

                    pnl = (stop_loss_price - last_price) * position
                    trade_pnl.append(pnl)
                    trade_ret.append((last_price / stop_loss_price - 1) * 100)

                    balance = balance + pnl

                    position = 0
                    last_signal = 'hold'

                    c = 0

        # compute market value and count days for any possible position
        if last_signal == 'hold':
            market_value = balance
        elif last_signal == 'long':
            c = c + 1
            market_value = position * row.Close + balance
        else:
            c = c + 1
            market_value = (row.Close - last_price) * position + balance

        cum_value.append(market_value)

    cum_ret_df = pd.DataFrame(cum_value, index=bt_df.index, columns=['CUM_RET'])
    cum_ret_df['CUM_RET'] = (cum_ret_df.CUM_RET / 1000000 - 1) * 100
    cum_ret_df['BUY_HOLD'] = (bt_df.Close / bt_df.Open.iloc[0] - 1) * 100
    cum_ret_df['ZERO'] = 0
    partial_title = "[" + ticker +"] - Strategy(" + strategy_name +"), Stop Loss Enabled = " + str(stop_loss_enabled)
    ticker_and_strategy = "[" + ticker +  "] - Strategy(" + strategy_name + ")"
    title = "Cumulative Returns on " + partial_title
    cum_ret_df.plot(title=title, figsize=(15, 5))
    cum_ret_df.iloc[[-1]].round(2)
    plt.xlabel('Trade Date')
    plt.ylabel('Cumulative Return (%)')
    
    # Trade Result
    size = min(len(trade_date_start), len(trade_date_end))
    tarde_dict = {
        'START': trade_date_start[:size],
        'END': trade_date_end[:size],
        'SIDE': trade_side[:size],
        'DAYS': trade_days[:size],
        'PNL': trade_pnl[:size],
        'RET': trade_ret[:size]
    }

    trade_df = pd.DataFrame(tarde_dict)
    print()
    print("***** Trade Result " + partial_title +  " *****")
    #print(trade_df.tail())
    print(trade_df)

    # Trade Summary
    num_trades = trade_df.groupby('SIDE').count()[['START']]
    num_trades_win = trade_df[trade_df.PNL > 0].groupby('SIDE').count()[['START']]
    avg_days = trade_df.groupby('SIDE').mean(numeric_only=True)[['DAYS']]
    avg_ret = trade_df.groupby('SIDE').mean(numeric_only=True)[['RET']]
    avg_ret_win = trade_df[trade_df.PNL > 0].groupby('SIDE').mean(numeric_only=True)[['RET']]
    avg_ret_loss = trade_df[trade_df.PNL < 0].groupby('SIDE').mean(numeric_only=True)[['RET']]
    std_ret = trade_df.groupby('SIDE').std(numeric_only=True)[['RET']]

    detail_df = pd.concat([
                        num_trades, num_trades_win, avg_days,
                        avg_ret, avg_ret_win, avg_ret_loss, std_ret
                        ], axis=1, sort=False)

    detail_df.columns = [
                        'NUM_TRADES', 'NUM_TRADES_WIN', 'AVG_DAYS', 
                        'AVG_RET', 'AVG_RET_WIN', 'AVG_RET_LOSS', 'STD_RET'
                        ]
    print()
    print("***** Trade Summary " + ticker_and_strategy + " *****")
    print(detail_df.round(2))

    # max drawdown
    mv_df = pd.DataFrame(cum_value, index=bt_df.index, columns=['MV'])
    days = len(mv_df)
    roll_max = mv_df.MV.rolling(window=days, min_periods=1).max()
    drawdown_val = mv_df.MV - roll_max
    drawdown_pct = (mv_df.MV / roll_max - 1) * 100
    print()
    print("***** Drawdown " + ticker_and_strategy + " *****")
    print("Max Drawdown value:", round(drawdown_val.min(), 0))
    print("MAx Drawdown Percentage %:", round(drawdown_pct.min(), 2))

    plt.show()
    return (trade_date_start, trade_date_end, trade_days, trade_side, trade_pnl, trade_ret, cum_value)

def prepare_stock_ta_backtest_data(df, start_date, end_date, strategy, **strategy_params):
  df_strategy, strategy_name = strategy(df, **strategy_params)
  bt_df = df_strategy[(df_strategy.index >= start_date) & (df_strategy.index <= end_date)]
  return bt_df, strategy_name

df = yf.download(ticker, start=start_date, end=end_date)

if strategy_name not in valid_strategy_name_list:
    raise ValueError("Invalid Strategy name:", strategy_name)
    sys.exit()

if strategy_name == "BollingerBands":
    bt_df, strategy_name = prepare_stock_ta_backtest_data(
        df, start_date, end_date, strategy_BollingerBands, n=10
    )
elif strategy_name == "KeltnerChannel":
    bt_df, strategy_name = prepare_stock_ta_backtest_data(
        df, start_date, end_date, strategy_KeltnerChannel_origin, n=10
    )
elif strategy_name == "MA":
    bt_df, strategy_name = prepare_stock_ta_backtest_data(
        df, start_date, end_date, strategy_MA, n=10
    )
elif strategy_name == "MACD":
    bt_df, strategy_name = prepare_stock_ta_backtest_data(
        df, start_date, end_date, strategy_MACD, n=10
    )
elif strategy_name == "RSI":
    bt_df, strategy_name = prepare_stock_ta_backtest_data(
        df, start_date, end_date, strategy_RSI, n=10
    )
elif strategy_name == "WR":
    bt_df, strategy_name = prepare_stock_ta_backtest_data(
        df, start_date, end_date, strategy_WR, n=10
    )
elif strategy_name == "RSIFast":
    bt_df, strategy_name = prepare_stock_ta_backtest_data(
        df, start_date, end_date, strategy_Stochastic_fast, n=10
    )
elif strategy_name == "RSISlow":
    bt_df, strategy_name = prepare_stock_ta_backtest_data(
        df, start_date, end_date, strategy_Stochastic_slow, n=10
    )
elif strategy_name == "IchmokuCloud":
    bt_df, strategy_name = prepare_stock_ta_backtest_data(
        df, start_date, end_date, strategy_Ichmoku, n=10
    )    

evaluate_trading_strategy(ticker, bt_df, strategy_name, stoploss)

# strategy_KeltnerChannel_origin(df)

# strategy_BollingerBands(df)

# strategy_MA(df)

# strategy_MACD(df)

# strategy_RSI(df)

# strategy_WR(df)

# strategy_Stochastic_fast(df)

# strategy_Stochastic_slow(df)

# strategy_Ichmoku(df)




# class StockBacktestData:
#   def __init__(self, ticker, start_date, end_date):
#     self._ticker = ticker
#     self._backtest_start_buffer_days = 365
#     self._buffer_days = 90

#     init_start_date, init_end_date = self._get_buffer_start_end_dates(start_date, end_date)
#     self._data = self._download_stock_backtest_data(self._ticker, init_start_date, init_end_date)

  
#   def _get_buffer_start_end_dates(self, start_date, end_date):
#     date_fmt = '%Y-%m-%d'
#     init_start_date = datetime.strptime(start_date, date_fmt) - timedelta(
#         days=(self._backtest_start_buffer_days + self._buffer_days)
#         )
    
#     init_start_date = init_start_date.strftime(date_fmt)

#     init_end_date = datetime.strptime(end_date, date_fmt) + timedelta(days=self._buffer_days)

#     if init_end_date > datetime.today():
#       init_end_date = datetime.today()

#     init_end_date = init_end_date.strftime(date_fmt)

#     return init_start_date, init_end_date


#   def _get_backtest_start_date(self, start_date):
#     date_fmt = '%Y-%m-%d'
#     start_date_buffer = datetime.strptime(start_date, date_fmt) - timedelta(
#         days=self._backtest_start_buffer_days
#         )
    
#     start_date_buffer = start_date_buffer.strftime(date_fmt)
#     return start_date_buffer


#   def _download_stock_backtest_data(self, ticker, start_date, end_date):
#     df = yf.download(ticker, start=start_date, end=end_date)
#     return df


#   def get_stock_backtest_data(self, start_date, end_date):
#     start_date_buffer = self._get_backtest_start_date(start_date)
#     df = self._data[(self._data.index >= start_date_buffer) & (self._data.index <= end_date)]
#     return df.copy()
