import yfinance as yf
import pandas as pd
import time

#This script is based on these references:
# https://towardsdatascience.com/making-a-stock-screener-with-python-4f591b198261
# https://medium.datadriveninvestor.com/calculating-the-ibd-rs-rating-with-python-dc357c1e1b24
# https://github.com/jeffreyrdcs/stock-vcpscreener/blob/main/stock_vcpscreener.py

# Set the start and end date for historical data
start_date = '2022-03-01'
end_date = '2023-07-20'
Min_RS_Rating = 85

# Function to calculate RS Rating
def calculate_rs_rating(tickers, start_date, end_date, sp500_return):
    print(f'Calculating RS Rating...')
    relative_returns = []
    stock_data_dict = {}  # Dictionary to store historical data for all tickers
    for ticker in tickers:
        try:
            # Download historical data as CSV for each stock to speed up the process
            stock_data = yf.download(ticker, start=start_date, end=end_date)
            
            # Calculate percent change column
            stock_data['Percent Change'] = stock_data['Adj Close'].pct_change()
            
            # Calculate the relative return with double weight for the most recent quarter
            stock_returns = (1 + stock_data['Percent Change']).cumprod()
            stock_return = (stock_returns.iloc[-1] * 2 + stock_returns.iloc[-63]) / 3  # Double weight for the most recent quarter
            relative_return = round(stock_return / sp500_return, 2)
            relative_returns.append(relative_return)

            # Store historical data in the dictionary
            stock_data_dict[ticker] = stock_data

            # Pause for 0.1 seconds to avoid overloading the server with requests
            time.sleep(0.1)
        except IndexError:
            print(f"Data for {ticker} is not available for the specified date range. Skipping...")
            continue

    # Create dataframe with relative returns and corresponding RS ratings
    rs_df = pd.DataFrame(list(zip(tickers, relative_returns)), columns=['Ticker', 'Relative Return'])
    rs_df['RS_Rating'] = rs_df['Relative Return'].rank(pct=True) * 100
    print(f'Calculating RS Rating...DONE\n')
    #print(rs_df)
    return rs_df, stock_data_dict


# Function to check for volatility contraction pattern
def has_volatility_contraction(df, rs_df, stock):
    sma = [50, 150, 200]
    for x in sma:
        df["SMA_" + str(x)] = round(df['Adj Close'].rolling(window=x).mean(), 2)

    # Storing required values
    currentClose = df["Adj Close"][-1]
    moving_average_50 = df["SMA_50"][-1]
    moving_average_150 = df["SMA_150"][-1]
    moving_average_200 = df["SMA_200"][-1]
    low_of_52week = round(min(df["Low"][-260:]), 2)
    high_of_52week = round(max(df["High"][-260:]), 2)

    try:
        moving_average_200_20 = df["SMA_200"][-20]
    except Exception:
        moving_average_200_20 = 0

    # Condition 1: Current Price > 150 SMA and > 200 SMA
    condition_1 = currentClose > moving_average_150 and currentClose > moving_average_200 

    # Condition 2: 150 SMA > 200 SMA
    condition_2 = moving_average_150 > moving_average_200

    # Condition 3: 200 SMA trending up for at least 1 month
    condition_3 = moving_average_200 > moving_average_200_20

    # Condition 4: 50 SMA > 150 SMA and 50 SMA > 200 SMA
    condition_4 = moving_average_50 > moving_average_150 and moving_average_50 > moving_average_200 

    # Condition 5: Current Price > 50 SMA
    condition_5 = currentClose > moving_average_50

    # Condition 6: Current Price is at least 30% above 52-week low
    condition_6 = currentClose >= (1.3 * low_of_52week)

    # Condition 7: Current Price is within 25% of 52-week high
    condition_7 = currentClose >= (0.75 * high_of_52week)

    # Check if RS Rating is greater than Min_RS_Rating%
    rs_rating = rs_df[rs_df['Ticker'] == stock]['RS_Rating'].iloc[0]
    condition_rs = rs_rating > Min_RS_Rating

    # If all conditions above are true, return True for volatility contraction pattern
    return condition_1 and condition_2 and condition_3 and condition_4 and condition_5 and condition_6 and condition_7 and condition_rs


# Get the list of S&P 500 tickers
sp500_tickers = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]['Symbol'].tolist()

# Fetch historical data for S&P 500 to calculate its return
sp500_data = yf.download('^GSPC', start=start_date, end=end_date)
sp500_returns = (1 + sp500_data['Adj Close'].pct_change()).cumprod()
sp500_return = sp500_returns.iloc[-1]

# Calculate RS Rating for all S&P 500 stocks and store stock data in a dictionary
rs_df, stock_data_dict = calculate_rs_rating(sp500_tickers, start_date, end_date, sp500_return)

# Initialize a list to store dictionaries of stocks that match the Minervini and volatility contraction requirements
exportList = []

print(f'Evaluating volatility contraction pattern from S&P500...')
# Loop through each ticker and check for the Minervini and volatility contraction pattern
for stock in sp500_tickers:
    try:
        # Get historical stock data from the dictionary
        stock_data = stock_data_dict[stock]

        # Check for the Minervini requirements (Conditions 1 to 7)
        # Add your existing Minervini criteria here

        # Check for the volatility contraction pattern 
        if has_volatility_contraction(stock_data, rs_df, stock):
            # Add the stock to the exportList if it meets Minervini's volatility contraction criteria
            exportList.append({'Stock': stock, "RS_Rating": rs_df[rs_df['Ticker'] == stock]['RS_Rating'].iloc[0],
                               "50 Day MA": stock_data["SMA_50"][-1],
                               "150 Day MA": stock_data["SMA_150"][-1],
                               "200 Day MA": stock_data["SMA_200"][-1],
                               "52 Week Low": round(min(stock_data["Low"][-260:]), 2),
                               "52 Week High": round(max(stock_data["High"][-260:]), 2)})
            #print(stock + " meets the Minervini's volatility contraction criteria")
    except Exception as e:
        #print(e)
        print(f"Could not gather data on {stock}. Skipping...")

# Convert the list of dictionaries to a DataFrame
exportList = pd.DataFrame(exportList)

# Print the stocks that match the Minervini's volatility contraction criteria
print(f'Evaluating volatility contraction pattern from S&P500...DONE\n')
print(f"\nStocks with Minervini's volatility contraction criteria (RS Rating > {Min_RS_Rating}%):")
print(exportList)
