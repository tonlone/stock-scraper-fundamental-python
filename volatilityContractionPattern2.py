import numpy as np
import pandas as pd
import yfinance as yf

# Reference:
# https://geekonomics.co.uk/mark-minervini-trend-template-in-python/

def best_fit_slope(y: np.array) -> float:
    '''
    Determine the slope for the linear regression line

    Parameters
    ----------
    y : TYPE
        The time-series to find the linear regression line for

    Returns
    -------
    m : float
        The gradient (slope) of the linear regression line
    '''
    
    x = np.arange(0, y.shape[0])
    
    x_bar = np.mean(x)
    y_bar = np.mean(y)
    
    return np.sum((x-x_bar)*(y-y_bar))/np.sum((x-x_bar)**2)


def apply_trend_template(df: pd.DataFrame) -> pd.DataFrame:
    '''
    Apply Mark Minervini's trend criteria and obtain a new boolean column
    to indicate where the criteria is applied
    
    Parameters
    ----------
    df : pd.DataFrame
        The stock price dataframe
        
    Returns
    -------
    df : pd.DataFrame
        The stock price dataframe with the new trend boolean column
    '''
    
    # Find the moving averages
    df['200_ma'] = df['Close'].rolling(200).mean()
    df['150_ma'] = df['Close'].rolling(150).mean()
    df['50_ma'] = df['Close'].rolling(50).mean()
    
    # Determine the 52 week high and low
    df['52_week_low'] = df['Close'].rolling(52*5).min()
    df['52_week_high'] = df['Close'].rolling(52*5).max()
    
    # Get the linear regression slope of the 200 day SMA
    df['slope'] = df['200_ma'].rolling(40).apply(best_fit_slope)
    
    # Constraints for the trend template
    df['trend_template'] = (
        (df['Close'] > df['200_ma'])
        & (df['Close'] > df['150_ma'])
        & (df['150_ma'] > df['200_ma'])
        & (df['slope'] > 0)
        & (df['50_ma'] > df['150_ma'])
        & (df['50_ma'] > df['200_ma'])
        & (df['Close'] > df['50_ma'])
        & (df['Close']/df['52_week_low'] > 1.3)
        & (df['Close']/df['52_week_high'] > 0.8) 
    )
    
    return df

if __name__ == '__main__':
    start_date = '2023-01-01'
    end_date = '2023-08-07'
    # Get the list of S&P 500 tickers
    sp500_tickers = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]['Symbol'].tolist()
    for stock in sp500_tickers:
        try:
            df = yf.download(f'{stock}').reset_index()
            df = apply_trend_template(df)
        
            if df['trend_template'].values[-1]:
                print(f'{stock} is in VPC trending! Go to https://finviz.com/quote.ashx?t={stock}&p=d')
            # else:
            #     print(f'{stock} is not trending :(')
        except Exception as e:
            print(f"Could not gather data on {stock}. Skipping...")