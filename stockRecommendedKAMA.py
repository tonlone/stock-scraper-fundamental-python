import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Define the ticker symbols of the stocks you want to analyze
ticker_symbols = ['BTC-USD']
#ticker_symbols = ['COST', 'MSFT', 'PYPL', 'PG', 'UNH', 'V', 'WMT', 'DIS' ]
#ticker_symbols = ['BTC-USD', 'ETH-USD', 'DOGE-USD', 'USDT-USD', 'ADA-USD', 'BNB-USD', 'XRP-USD']
start_date = '2023-01-01'

print("KAMA (Long term)")
print("============",)

def kama_indicator(price, period=10, period_fast=2, period_slow=30):
 
    #Efficiency Ratio
    change = abs(price-price.shift(period))
    volatility = (abs(price-price.shift())).rolling(period).sum()
    er = change/volatility
    
    #Smoothing Constant
    sc_fatest = 2/(period_fast + 1)
    sc_slowest = 2/(period_slow + 1)
    sc= (er * (sc_fatest - sc_slowest) + sc_slowest)**2
    
    #KAMA
    kama=np.zeros_like(close)
    kama[period-1] = close[period-1]
    for i in range(period, len(data)):
        kama[i] = kama[i-1] + sc[i] * (close[i] - kama[i-1])
        kama[kama==0]=np.nan
    
    return kama

# Iterate through the ticker symbols
for ticker in ticker_symbols:
    # Download historical data for the current ticker
    data = yf.download(ticker, start=start_date)
    close=data['Adj Close']

    period = 10
    period_fast = 2
    #period_fast = 5
    period_slow = 30

    kama2=kama_indicator(close, period, period_fast, period_slow)
    data['kama2']=kama2
    data['sma_10days']=close.rolling(period).mean()

    figsize=(12,6)
    
    """
    data[['kama2','Adj Close']].plot(figsize=figsize)
    data['sma_10days'].plot(linestyle="--")
    plt.legend(['KAMA','Close','SMA_10day'])
    plt.title("KAMA - " + ticker + "({0},{1},{2})".format(period, period_fast, period_slow))
    plt.show()
    """

    kama5=kama_indicator(close, period, 5, period_slow)
    data['kama5']=kama5
    data[['kama2','Adj Close','kama5']].plot(figsize=figsize)

   
    # Labeling the intersections as "Buy" or "Sell"
    buy_signals = (data['kama2'] > data['kama5']) & (data['kama2'].shift() < data['kama5'].shift())
    sell_signals = (data['kama2'] < data['kama5']) & (data['kama2'].shift() > data['kama5'].shift())
    
    print("ticker",ticker)
    # Annotating "Buy" at the intersection points
    for i, buy_signal in enumerate(buy_signals):
        if buy_signal:
            buy_date = data.index[i].strftime('%m-%d')
            print(f'Buy({buy_date}) @ Price = {data["Adj Close"][i]}')
            plt.annotate(f'Buy({buy_date})', xy=(data.index[i], data['Adj Close'][i]), xytext=(10, 30),
                         textcoords='offset points', color='green', arrowprops=dict(arrowstyle='->', lw=1))
    
    # Annotating "Sell" at the intersection points
    for i, sell_signal in enumerate(sell_signals):
        if sell_signal:
            sell_date = data.index[i].strftime('%m-%d')
            print(f'Sell({sell_date}) @ Price = {data["Adj Close"][i]}')
            plt.annotate(f'Sell({sell_date})', xy=(data.index[i], data['Adj Close'][i]), xytext=(10, -30),
                         textcoords='offset points', color='red', arrowprops=dict(arrowstyle='->', lw=1))
    print("============",)
    plt.legend(['KAMA2','Close','KAMA5'])
    plt.title("KAMA5 (Long term) - " + ticker + "({0},{1},{2})".format(period, 5, period_slow))
    plt.show()
    