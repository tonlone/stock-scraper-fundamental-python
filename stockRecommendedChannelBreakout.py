import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Define the ticker symbols of the stocks you want to analyze
ticker_symbols = ['COST']
#ticker_symbols = ['COST', 'MSFT', 'PYPL', 'PG', 'UNH', 'V', 'WMT', 'DIS' ]
#ticker_symbols  = ['AAPL', 'ABT', 'ABBV', 'ACN', 'ADBE', 'AMZN', 'BAC', 'BMY', 'CMCSA', 'COST', 'CSCO', 'CRM', 'CVX', 'DHR', 'DIS', 'GOOGL', 'HD', 'HON', 'INTC', 'JNJ', 'JPM', 'KO', 'LIN', 'LLY', 'MA', 'MCD', 'MMM', 'MRK', 'MSFT', 'NEE', 'NFLX', 'NVDA', 'NKE', 'ORCL', 'PFE', 'PEP', 'PG', 'PM', 'PYPL', 'T', 'TMO', 'TSLA', 'UNH', 'UNP', 'V', 'VZ', 'WMT', 'XOM']
start_date = '2023-02-01'

print("channel_breakout (Take profit and Buy signal)")
print("============",)

def channel_breakout(data, ticker, window=20, n_std=2):
    rolling_mean = data['Close'].rolling(window=window).mean()
    rolling_std = data['Close'].rolling(window=window).std()
    upper_band = rolling_mean + (rolling_std * n_std)
    lower_band = rolling_mean - (rolling_std * n_std)
    
    buy_signal = None
    sell_signal = None
    hold_signal=None
    print("ticker",ticker)
    for i in range(window, len(data)):
        # If the closing price is above the upper band, it sets the sell_signal to the current index 
        if data.iloc[i]['Close'] > upper_band[i]:
            sell_signal = data.index[i]
            date = str(sell_signal).split()[0].split("-")[1:]
            formatted_date = "-".join(date)
            print("sell_signal",formatted_date)
        # ElseIf  If the closing price is below the lower band, it sets the buy_signal to the current index 
        elif data.iloc[i]['Close'] < lower_band[i]:
            buy_signal = data.index[i]
            date = str(buy_signal).split()[0].split("-")[1:]
            formatted_date = "-".join(date)
            print("buy_signal",formatted_date)
        else:
            #hold_signal=i
            hold_signal = data.index[i]
    print("============",)
    return buy_signal, sell_signal,hold_signal, rolling_mean, upper_band, lower_band


# Iterate through the ticker symbols
for ticker in ticker_symbols:
    # Download historical data for the current ticker
    data = yf.download(ticker, start=start_date)

    buy_signal, sell_signal,hold_signal, rolling_mean, upper_band, lower_band = channel_breakout(data, ticker)
    x=data.index.values
    plt.figure(figsize=(15,5))
    data['Close'].plot()
    plt.plot(rolling_mean, label='Rolling Mean', color='red')
    plt.plot(upper_band, label='Upper Band', color='green')
    plt.plot(lower_band, label='Lower Band', color='yellow')
    if buy_signal is not None:
        plt.axvline(x=buy_signal, color='blue', linestyle='--', label='Buy Signal')
    if sell_signal is not None:
        plt.axvline(x=sell_signal, color='black', linestyle='--', label='Sell Signal')
    plt.legend(loc="lower left")
    plt.title("Channel Breakout (Take profit and Buy signal) - " + ticker)
     # Set the x-axis limits
    plt.xlim(pd.Timestamp(start_date), pd.Timestamp.now())
    plt.show()
"""
# Calculate the number of rows and columns for subplots
num_plots = len(ticker_symbols)
num_rows = int(np.ceil(num_plots / 2))
num_cols = 2

# Create subplots
fig, axs = plt.subplots(num_rows, num_cols, figsize=(15, 5*num_rows))

# Iterate through the ticker symbols and plot each ticker in a separate subplot
for i, ticker in enumerate(ticker_symbols):
    # Calculate the subplot index
    row = i // num_cols
    col = i % num_cols

    # Download historical data for the current ticker
    data = yf.download(ticker, start=start_date)

    buy_signal, sell_signal, hold_signal, rolling_mean, upper_band, lower_band = channel_breakout(data)

    # Plot the stock's data and indicators in the corresponding subplot
    axs[row, col].plot(data['Close'], label='Close')
    axs[row, col].plot(rolling_mean, label='Rolling Mean', color='red')
    axs[row, col].plot(upper_band, label='Upper Band', color='green')
    axs[row, col].plot(lower_band, label='Lower Band', color='yellow')

    if buy_signal is not None:
        axs[row, col].axvline(x=buy_signal, color='blue', linestyle='--', label='Buy Signal')
    if sell_signal is not None:
        axs[row, col].axvline(x=sell_signal, color='black', linestyle='--', label='Sell Signal')

    # Set subplot properties
    axs[row, col].legend(loc="lower left")
    axs[row, col].set_title("Channel Breakout - " + ticker)
    axs[row, col].set_xlim(pd.Timestamp(start_date), pd.Timestamp.now())

# Adjust the spacing between subplots
plt.tight_layout()

# Show all the plots
plt.show() 
"""