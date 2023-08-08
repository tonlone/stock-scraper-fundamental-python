import numpy as np
import pandas as pd
import yfinance as yf

import plotly.io as pio
import plotly.graph_objects as go
from plotly.subplots import make_subplots
pio.renderers.default='browser'

LOOKBACK = 60
LOOKBACK_SHORT = 20

START_DATE = '2023-02-01'
END_DATE = '2023-08-07'

STOCK = 'SMCI'
INDEX = 'QQQ'

def get_candlestick_plot(
    df: pd.DataFrame,
    df_idx: pd.DataFrame,
):
    '''
    Generate the figure showing the comparison between the stock and the index
    (top plot), and the relative strength calculations (bottom plot)
    Parameters
    ----------
    df : pd.DataFrame
        The stock price dataframe (with the relative strength columns).
    df_idx : pd.DataFrame
        The index fund price dataframe
    '''
    
    # The specs allows us to plot two instruments on the same chart, with one
    # scale on the left and another on the right
    fig = make_subplots(
        rows = 2,
        cols = 1,
        shared_xaxes = True,
        vertical_spacing = 0.05,
        row_width = [0.2, 0.5],
        specs = [[{"secondary_y": True}], [{"secondary_y": False}]],
    )
    
    # Plot the chart for the index first, so it appears behind the stock
    fig.add_trace(
        go.Candlestick(
            x = df_idx['Date'],
            open = df_idx['Open'], 
            high = df_idx['High'],
            low = df_idx['Low'],
            close = df_idx['Close'],
            name = f'{INDEX}',
            increasing_line_color= 'rgba(0, 0, 0, 0.5)', 
            decreasing_line_color= 'rgba(0.5, 0.5, 0.5, 0.5)'
        ),
        row = 1,
        col = 1,
        secondary_y = True,
    )
    
    # Add the candlestick chart for the stock
    fig.add_trace(
        go.Candlestick(
            x = df['Date'],
            open = df['Open'], 
            high = df['High'],
            low = df['Low'],
            close = df['Close'],
            name = f'{STOCK}',
        ),
        row = 1,
        col = 1,
        secondary_y = False,
    )
    
    # Plot the relative strength lines
    fig.add_trace(
        go.Scatter(
            x = df['Date'], 
            y = df['relative_strength'], 
            name = 'Long term relative strength',
            line = {'color': 'rgba(189, 104, 189, 1)'},
        ),
        row = 2,
        col = 1
    )
    
    fig.add_trace(
        go.Scatter(
            x = df['Date'], 
            y = df['relative_strength_short'], 
            name = 'Short term relative strength',
            line = {'color': 'rgba(82, 82, 170, 1)'},
        ),
        row = 2,
        col = 1,
    )
    
    # Update the layout and axes labels of the figure
    fig.update_xaxes(
        rangebreaks = [{'bounds': ['sat', 'mon']}],
        rangeslider_visible = False,
        tickvals = pd.date_range(START_DATE, END_DATE, freq='BMS'),
        tickangle = 45,
        tickformat = '%b-%y'
    )
    
    fig.update_layout(
        width = 700,
        height = 800,
        legend = {'orientation': 'h', 'y': -0.15},
        margin = {'l': 50, 'r': 50, 'b': 50, 't': 25},
        xaxis2 = {'title': 'Date'},
        yaxis1 = {'title': STOCK},
        yaxis2 = {'title': INDEX},
        yaxis3 = {'title': 'Relative Strength'},
    )
    
    return fig


def get_relative_strength(
        df: pd.DataFrame,
        df_idx: pd.DataFrame,
        lookback: int
    ) -> np.array:
    '''
    Calculate the relative strength between a stock and the index fund, this
    is performed by comparing the closing prices.
    Parameters
    ----------
    df : pd.DataFrame
        The price dataframe for the stock
    df_idx : pd.DataFrame
        The price dataframe for the index
    lookback : int
        The number of days to lookback and calculate the relative strength
    Returns
    -------
    rs : np.array
        The relative strength values 
    '''
    
    # Merge the dataframes to ensure the data is correctly aligned
    df = df.merge(
        df_idx[['Date', 'Close']].rename(columns={'Close': 'Close_index'}), 
        on = 'Date', 
        how = 'left',
    )
    
    # Initialise the array to store the relative strength values in
    rs = np.zeros(len(df))
    
    close = df['Close'].values
    close_idx = df['Close_index'].values
    
    for n in range(lookback, close.shape[0]):
        
        # Scale both the time series to the furthest day back
        close_scaled = close[n-lookback:n]/close[n-lookback]
        close_idx_scaled = close_idx[n-lookback:n]/close_idx[n-lookback]
        
        rs[n] = np.mean(close_scaled-close_idx_scaled)
    
    return rs


def date_filter(df: pd.DataFrame) -> pd.DataFrame:
    '''
    Filter the dataframe to the date range specified in the global variables
    '''
    
    return df[
       (df['Date'] >= START_DATE)
       & (df['Date'] <= END_DATE)
    ]


if __name__ == '__main__':
    
    df = yf.download(f'{STOCK}').reset_index()
    df_idx = yf.download(f'{INDEX}').reset_index()
    
    df.loc[:, 'relative_strength'] = get_relative_strength(
        df=df, 
        df_idx=df_idx, 
        lookback=LOOKBACK,
    )
    
    df.loc[:, 'relative_strength_short'] = get_relative_strength(
        df=df, 
        df_idx=df_idx, 
        lookback=LOOKBACK_SHORT,
    )
    
    fig = get_candlestick_plot(
        df=date_filter(df), 
        df_idx=date_filter(df_idx),
    )

    fig.show()