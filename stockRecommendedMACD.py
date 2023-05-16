import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Define the ticker symbols of the stocks you want to analyze
ticker_symbols = ['BTC-USD']
#ticker_symbols = ['COST', 'MSFT', 'PYPL', 'PG', 'UNH', 'V', 'WMT', 'DIS' ]
#ticker_symbols = ['BTC-USD', 'ETH-USD', 'DOGE-USD', 'USDT-USD', 'ADA-USD', 'BNB-USD', 'XRP-USD']

start_date = '2023-02-01'

print("MACD (Short term)")
print("============",)

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

    macd, signal = calc_macd(data['Close'], 12, 26, 9)
    data['MACD_line'] = macd
    data['Signal_line'] = signal

    #data[['Close']].plot(label='Prices', figsize=(10, 6))
    #plt.plot(macd, label='MACD Line', linestyle='--')
    #plt.plot(signal, label='Signal Line', linestyle=':')
    #plt.legend()
    #plt.title("MACD - " + ticker)
    #plt.show()

    intersection_points = np.where(np.diff(np.sign(macd - signal)))[0]
    intersection_dates = data.index[intersection_points + 1]
    intersection_values = data['MACD_line'].iloc[intersection_points + 1]

    print("ticker",ticker)

    #data.query(f"Date>='{start_date}'")[['MACD_line','Signal_line']].plot(figsize=(10,6))
    data[['MACD_line', 'Signal_line']].plot(figsize=(10, 6))
    plt.scatter(intersection_dates, intersection_values, color='red', label='Intersection')
    for i in range(len(intersection_points)):
        index = intersection_points[i] + 1
        if macd.iloc[index] > signal.iloc[index]:
            label = 'Buy({})'.format(intersection_dates[i].strftime('%m-%d'))
            print(label + " @ Price = {}".format(data['Close'].loc[intersection_dates[i]]))
            plt.annotate(label, (intersection_dates[i], intersection_values[i]), xytext=(5, 5),
                         textcoords='offset points', color='green')
        else:
            label = 'Sell({})'.format(intersection_dates[i].strftime('%m-%d'))
            print(label + "@ Price = {}".format(data['Close'].loc[intersection_dates[i]]))
            plt.annotate(label, (intersection_dates[i], intersection_values[i]), xytext=(5, 5),
                         textcoords='offset points', color='red')
    print("============",)
    plt.legend()
    plt.title("MACD (Short term) - " + ticker)
    plt.show()