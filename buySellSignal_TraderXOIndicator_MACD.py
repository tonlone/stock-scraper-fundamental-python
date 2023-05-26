import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Define the ticker symbols of the stocks you want to analyze
ticker_symbols = ['JPM']
#ticker_symbols = ['COST', 'MSFT', 'PYPL', 'PG', 'UNH', 'V', 'WMT', 'NFLX', 'NVDA', 'CMCSA' ]
#ticker_symbols  = ['AAPL', 'ABT', 'ABBV', 'ACN', 'ADBE', 'AMZN', 'BAC', 'BMY', 'CMCSA', 'COST', 'CSCO', 'CRM', 'CVX', 'DHR', 'DIS', 'GOOGL', 'HD', 'HON', 'INTC', 'JNJ', 'JPM', 'KO', 'LIN', 'LLY', 'MA', 'MCD', 'MMM', 'MRK', 'MSFT', 'NEE', 'NFLX', 'NVDA', 'NKE', 'ORCL', 'PFE', 'PEP', 'PG', 'PM', 'PYPL', 'T', 'TMO', 'TSLA', 'UNH', 'UNP', 'V', 'VZ', 'WMT', 'XOM']
#ticker_symbols = ['BTC-USD', 'ETH-USD', 'DOGE-USD', 'USDT-USD', 'ADA-USD', 'BNB-USD', 'XRP-USD']

start_date = '2022-10-01'

# Define the Trader XO indicator calculation function
def calc_trader_xo(prices, period):
    xo = np.zeros_like(prices)
    xo[period:] = np.where(prices[period:].reset_index(drop=True) > prices[:-period].reset_index(drop=True), 10, -10)
    return xo

# own MACD calculation function
def calc_macd(prices, fast_window, slow_window, signal_window):
    fast_ewma = prices.ewm(span=fast_window, adjust=False).mean()
    slow_ewma = prices.ewm(span=slow_window, adjust=False).mean()
    macd = fast_ewma - slow_ewma
    signal = macd.ewm(span=signal_window, adjust=False).mean()
    return macd, signal

# Iterate through the ticker symbols
for ticker in ticker_symbols:
    # Download historical data for the current ticker
    data = yf.download(ticker, start=start_date)
    xo = calc_trader_xo(data['Close'], 14)
    data['Trader_XO'] = xo

    intersection_points = np.where(np.diff(np.sign(xo)))[0]
    intersection_dates = data.index[intersection_points + 1]
    intersection_values = data['Close'].iloc[intersection_points + 1]


    # In house MACD line
    macd, signal = calc_macd(data['Close'], 26, 100, 9)
    data['MACD_line'] = macd
    data['Signal_line'] = signal
    data['MACD_histogram'] = macd - signal


    print("Ticker:", ticker)

    # Plot the Trader XOgraph
    plt.figure(figsize=(10, 6))
    plt.plot(data.index, data['Close'], label='Prices')
    plt.plot(data.index, xo, label='Trader XO (G->Buy, R->Sell)', linestyle='--', color='orange')
    # Change line color to green where Trader XO value is 10
    plt.plot(data.index[xo == 10], xo[xo == 10], 'g.')

    # Change line color to red where Trader XO value is -10
    plt.plot(data.index[xo == -10], xo[xo == -10], 'r.')


    # Plot MACD histogram from using in-house function
    plt.bar(data.index, data['MACD_histogram'] * 10, label='MACD Histogram (Buy>0, Sell<0)', color='purple')

    plt.xlim(pd.to_datetime(start_date), data.index[-1])

    # Initialize variables for profit/loss calculation
    buy_price = 0
    sell_price = 0
    total_profit_loss = 0

    for i in range(len(intersection_points)):
        index = intersection_points[i] + 1
        if xo[index] == 10:  # Buy signal
            buy_price = data['Close'].loc[intersection_dates[i]]
        elif xo[index] == -10 and buy_price != 0:  # Sell signal and valid buy price exists
            sell_price = data['Close'].loc[intersection_dates[i]]
            profit_loss = sell_price - buy_price
            total_profit_loss += profit_loss

            # Print buy and sell details
            print("Buy({}) @ Price = {}".format(intersection_dates[i].strftime('%m-%d'), buy_price))
            print("Sell({}) @ Price = {}".format(intersection_dates[i].strftime('%m-%d'), sell_price))
            print("Profit/Loss = {}".format(profit_loss))
            print("===================")

            # Reset buy_price for the next cycle
            buy_price = 0

    # Print overall profit/loss
    print("Overall Profit/Loss: {}".format(total_profit_loss))
    print("===================")

    plt.legend()
    plt.title("Trader XO, MACD Histogram - " + ticker)
    plt.show()
