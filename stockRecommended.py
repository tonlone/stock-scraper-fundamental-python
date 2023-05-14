import yfinance as yf
import pandas as pd

# Define the ticker symbols of the stocks you want to analyze
#ticker_symbols = ['MSFT']
ticker_symbols  = ['AAPL', 'ABT', 'ABBV', 'ACN', 'ADBE', 'AMZN', 'BAC', 'BMY', 'CMCSA', 'COST', 'CSCO', 'CRM', 'CVX', 'DHR', 'DIS', 'GOOGL', 'HD', 'HON', 'INTC', 'JNJ', 'JPM', 'KO', 'LIN', 'LLY', 'MA', 'MCD', 'MMM', 'MRK', 'MSFT', 'NEE', 'NFLX', 'NVDA', 'NKE', 'ORCL', 'PFE', 'PEP', 'PG', 'PM', 'PYPL', 'T', 'TMO', 'TSLA', 'UNH', 'UNP', 'V', 'VZ', 'WMT', 'XOM']

# Create an empty DataFrame to store the results
results = pd.DataFrame(columns=['Ticker', 'Moving Average', 'RSI', 'A/D Lines', 'ADX', 'Recommendation'])

# Iterate through the ticker symbols
for ticker in ticker_symbols:
    # Download historical data for the current ticker
    data = yf.download(ticker, start='2000-01-01')

    # Calculate the 200-day moving average
    data['MA'] = data['Close'].rolling(window=200).mean()

    # Calculate the RSI
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    # Calculate A/D Lines
    data['UpMove'] = data['High'] - data['High'].shift(1)
    data['DownMove'] = data['Low'].shift(1) - data['Low']
    data['UpVolume'] = data['UpMove'] * data['Volume']
    data['DownVolume'] = data['DownMove'] * data['Volume']
    data['PosDM'] = data['UpMove']
    data['NegDM'] = data['DownMove']
    data.loc[data.UpMove < data.DownMove, 'PosDM'] = 0
    data.loc[data.UpMove > data.DownMove, 'NegDM'] = 0
    data['PosDI'] = data['PosDM'].rolling(window=14).mean()
    data['NegDI'] = data['NegDM'].rolling(window=14).mean()
    data['AD'] = (data['PosDI'] - data['NegDI']) / (data['PosDI'] + data['NegDI'])

    # Calculate ADX
    data['ADX'] = 100 * (data['PosDI'] - data['NegDI']) / (data['PosDI'] + data['NegDI'])
    data['ADX'] = data['ADX'].rolling(window=14).mean()

    # Determine the recommendation

    # current stock close price is higher than the 200-day moving average, the RSI is greater than 70, the A/D line is increasing, and the ADX is greater than 25, the recommendation is to buy the stock
    if data['Close'].iloc[-1] > data['MA'].iloc[-1] and rsi.iloc[-1] > 70 and data['AD'].iloc[-1] > data['AD'].iloc[
        -2] and data['ADX'].iloc[-1] > 25:
        recommendation = 'Buy'
    #  If the current stock close price is lower than the 200-day moving average, the RSI is less than 30, the A/D line is decreasing, and the ADX is greater than 25, the recommendation is to sell the stock
    elif data['Close'].iloc[-1] < data['MA'].iloc[-1] and rsi.iloc[-1] < 30 and data['AD'].iloc[-1] < data['AD'].iloc[
        -2] and data['ADX'].iloc[-1] > 25:
        recommendation = 'Sell'
    # Otherwise
    else:
        recommendation = 'Hold'

    # Append the results to the DataFrame
    new_row = {'Ticker': ticker,
           'Moving Average': data['MA'].iloc[-1],
           'RSI': rsi.iloc[-1],
           'A/D Lines': data['AD'].iloc[-1],
           'ADX': data['ADX'].iloc[-1],
           'Last Close Price':data['Close'].iloc[-1],
           'Date': data.index[-1].strftime('%Y-%m-%d'),
           'Recommendation': recommendation}
    results = pd.concat([results, pd.DataFrame(new_row, index=[0])], ignore_index=True)

# Print the results
print(results)