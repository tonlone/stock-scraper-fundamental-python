import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Define the ticker symbols of the stocks you want to analyze
ticker_symbols = ['COST']
#ticker_symbols = ['COST', 'MSFT', 'PYPL', 'PG', 'UNH', 'V', 'WMT', 'NFLX', 'NVDA' ]
# interesting ticker_symbols = [*'COST', *'MSFT', 'PYPL', *'PG', *'UNH', *'V', *'WMT', *'DIS' ]

#             technical_fund = ['AMZN', 'CMCSA', 'PEP', 'LLY' ]

#ticker_symbols  = ['AAPL', 'ABT', 'ABBV', 'ACN', 'ADBE', 'AMZN', 'BAC', 'BMY', 'CMCSA', 'COST', 'CSCO', 'CRM', 'CVX', 'DHR', 'DIS', 'GOOGL', 'HD', 'HON', 'INTC', 'JNJ', 'JPM', 'KO', 'LIN', 'LLY', 'MA', 'MCD', 'MMM', 'MRK', 'MSFT', 'NEE', 'NFLX', 'NVDA', 'NKE', 'ORCL', 'PFE', 'PEP', 'PG', 'PM', 'PYPL', 'T', 'TMO', 'TSLA', 'UNH', 'UNP', 'V', 'VZ', 'WMT', 'XOM']

#          ticker_symbols = ['BTC-USD', 'ETH-USD', 'DOGE-USD', 'USDT-USD', 'ADA-USD', 'BNB-USD', 'XRP-USD']
# interesting ticker_symbols[*'BTC-USD', *'ETH-USD', *'DOGE-USD', 'USDT-USD', *'ADA-USD', 'BNB-USD', *'XRP-USD']

start_date = '2022-10-01'

def calculate_rsi(prices, window):
    delta = prices.diff()
    gain = delta.mask(delta < 0, 0)
    loss = -delta.mask(delta > 0, 0)

    avg_gain = gain.rolling(window).mean()
    avg_loss = loss.rolling(window).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi

# Iterate through the ticker symbols
for ticker in ticker_symbols:
    # Download historical data for the current ticker
    data = yf.download(ticker, start=start_date)

    rsi = calculate_rsi(data['Close'], window=14)
    data['RSI'] = rsi

    # Plotting RSI
    data[['RSI']].plot(figsize=(10, 6))
    plt.axhline(y=30, color='r', linestyle='--', label='Oversold')
    plt.axhline(y=70, color='g', linestyle='--', label='Overbought')

    # Generate buy and sell signals based on RSI
    data['Signal'] = np.where(data['RSI'] < 30, 'Buy', np.where(data['RSI'] > 70, 'Sell', ''))
    signal_points = np.where(data['Signal'] != '')[0]
    signal_dates = data.index[signal_points]
    signal_values = data['Close'].iloc[signal_points]

    print("Ticker:", ticker)
    for i in range(len(signal_points)):
        signal_type = data['Signal'].iloc[signal_points[i]]
        label = '{} ({})'.format(signal_type, signal_dates[i].strftime('%m-%d'))
        print(label + " @ Price = {}".format(signal_values[i]))

    print("============================")
    plt.legend()
    plt.title("Relative Strength Index (RSI) - " + ticker)
    plt.show()