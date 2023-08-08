import pandas as pd
import yfinance as yf

# Reference:
# https://geekonomics.co.uk/find-bull-market-winners-by-using-mark-minervinis-advice/


GROWTH_SINCE = '2021-12-01' # The lower date to calculate the stock performance
GROUPBY_COL = 'GICS Sector' # Use 'GICS Sector' or 'GICS Sub-Industry'
S_AND_P_URL = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
NUM_PER_GROUP = 3 # The top n winning stocks per group


if __name__ == '__main__':
    
    # This reads in the current list of S&P500 stocks from wikipedia, which
    # also includes information on the stock's sector, and sub industry
    ticker_info = pd.read_html(S_AND_P_URL)[0]
    
    # Replace any dots with dashes in ticker names to prevent errors in
    # downloading A and B stocks
    tickers = [
        ticker.replace('.', '-')
        for ticker in ticker_info['Symbol'].unique().tolist()
    ]
    
    # Download the price data for all the stocks in the S&P list
    ticker_prices = yf.download(
        tickers,
        start = GROWTH_SINCE,
        threads = True,
    )
    
    # Filter to only the closing prices (this is used for the comparison)
    ticker_prices = ticker_prices[
        [col for col in ticker_prices.columns if col[0] == 'Close']
    ]
    
    # Clean up the price dataframe, noting we don't require the date column
    # since we are calculating the performance over the entire interval
    ticker_prices = (
        ticker_prices
        .dropna()
        .reset_index()
        .drop(columns = 'Date')
    )
    
    # Find the stock growth in percent
    growth = 100*(ticker_prices.iloc[-1]/ticker_prices.iloc[0] - 1)
    
    # Cleaning of the growth pandas series, changing it back to a dataframe
    # so that we can merge with the sector/industry to find the winning stocks
    # per that group
    growth = (
        growth
        .to_frame()
        .reset_index()
        .drop(columns = ['level_0'])
        .rename(columns = {'level_1': 'Symbol', 0: 'Growth'})    
    )
    
    # Merge the growth with the ticker information dataframe to obtain the
    # column used for the groupby
    growth = growth.merge(
        ticker_info[['Symbol', GROUPBY_COL]],
        on = 'Symbol',
        how = 'left',
    )
    
    # Find the ranking of each stock per sector
    growth['sector_rank'] = (
        growth
        .groupby(GROUPBY_COL)
        ['Growth']
        .rank(ascending = False)
    )
    
    # Filter to only the winning stocks, and sort the values
    growth = (
        growth[growth['sector_rank'] <= NUM_PER_GROUP]
        .sort_values(
            [GROUPBY_COL, 'Growth'],
            ascending = False,
        )
    )

    print(growth)