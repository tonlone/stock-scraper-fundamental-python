import numpy as np
import talib as ta
import pandas as pd
import yfinance as yf

from copy import deepcopy
from typing import Tuple
from scipy.optimize import minimize, LinearConstraint

import plotly.io as pio
import plotly.graph_objects as go
from plotly.subplots import make_subplots
pio.renderers.default='browser'

# Reference:
# https://geekonomics.co.uk/simple-technical-analysis-time-the-bear-market/

RSI_LENGTH = 14
PRICE_FIELD = 'Close'

TREND_LOOKBACK = 22

TITLE = '2020 Financial Crisis'

PLOT_RANGE = ['2019-10-07', '2023-12-01']
MARKET_BOTTOM = '2022-10-16'

def convert_to_weekly(df: pd.DataFrame) -> pd.DataFrame:
    '''
    Change a dataframe of daily data into weekly data
    '''
    return (
        df
        .groupby(pd.Grouper(freq='W', key='Date'))
        .agg({
            'Open': 'first',
            'Close': 'last',
            'High': 'max',
            'Low': 'min',
        })
    )

def get_rsi(df: pd.DataFrame, price_field: str, rsi_length: int) -> pd.DataFrame:
    '''
    Add the RSI technical indicator as a new column to the price dataset
    '''
    
    df.loc[:, 'RSI'] = ta.RSI(
        df[price_field],
        timeperiod=rsi_length
    )
    
    return df.dropna()

def trend_line(case: str, prices: np.array) -> Tuple[float, float]:
    '''
    Obtain the support or resistance trend line
    Parameters
    ----------
    case : str
        Either 'support' or 'resistance'.
    prices : np.array
        The values to get the trend line for.
    
    Returns
    -------
    [float, float]
        The gradient and intercept terms for the trend line
    '''
    
    pos = np.argmax(prices) if case == 'resistance' else np.argmin(prices)
        
    # Form the points for the objective function
    x = np.arange(0, prices.shape[0])
    X = x-x[pos]
    Y = prices-prices[pos]
    
    if case == 'resistance':
        const = LinearConstraint(
            X.reshape(-1, 1),
            Y,
            np.full(X.shape, np.inf),
        )
    else:
        const = LinearConstraint(
            X.reshape(-1, 1),
            np.full(X.shape, -np.inf),
            Y,
        )
    
    # Min the objective function with a zero starting point for the gradient
    ans = minimize(
        fun = lambda m: np.sum((m*X-Y)**2),
        x0 = [0],
        jac = lambda m: np.sum(2*X*(m*X-Y)),
        method = 'SLSQP',
        constraints = (const),
    )
    
    # Return the gradient (m) and the intercept (c)
    return ans.x[0], prices[pos]-ans.x[0]*x[pos] 

def get_gradients(vals: np.array, lookback: int) -> np.array:
    '''
    Roll over all values in vals and get the gradient of the support line over
    the lookback period
    '''
    
    gradients = np.full(vals.shape[0], np.nan)
    
    for idx in range(lookback, vals.shape[0]):
        
        lookback_vals = vals[idx-lookback:idx]
        
        gradients[idx], _ = trend_line(
            case='support',
            prices=lookback_vals,
        )
    
    return gradients 

def plot_result(df: pd.DataFrame):
    
    df = df[(df['Date'] >= PLOT_RANGE[0]) & (df['Date'] <= PLOT_RANGE[1])]
    
    df_trend = df[df['Date'] <= MARKET_BOTTOM]
    price_m, price_c = trend_line(
        'support', 
        df_trend['Low'].values[-TREND_LOOKBACK:],
    )
    rsi_m, rsi_c = trend_line(
        'support', 
        df_trend['RSI'].values[-TREND_LOOKBACK:],
    )
    
    fig = make_subplots(
        rows = 3,
        cols = 1,
        shared_xaxes = True,
        vertical_spacing = 0.05,
        horizontal_spacing = 0.1,
        row_width = [0.2, 0.2, 0.5],
    )
    
    fig.add_trace(
        go.Candlestick(
            x = df['Date'],
            open = df['Open'], 
            high = df['High'],
            low = df['Low'],
            close = df['Close'],
            showlegend = False,
        ),
        row = 1,
        col = 1,
    )
    
    fig.add_trace(
        go.Scatter(
            x = df_trend['Date'][-TREND_LOOKBACK:],
            y = price_m*np.arange(0, TREND_LOOKBACK) + price_c,
            showlegend = False,
            mode = 'lines',
            line = {'color': 'rgba(50, 95, 211, 1)'},
        ),
        row = 1,
        col = 1,
    )
    
    fig.add_trace(
        go.Scatter(
            x = df['Date'], 
            y = df['RSI'], 
            name = 'RSI',
            mode = 'lines',
        ),
        row = 2,
        col = 1,
    )
    
    fig.add_trace(
        go.Scatter(
            x = df_trend['Date'][-TREND_LOOKBACK:],
            y = rsi_m*np.arange(0, TREND_LOOKBACK) + rsi_c,
            showlegend = False,
            mode = 'lines',
            line = {'color': 'rgba(50, 95, 211, 1)'},
        ),
        row = 2,
        col = 1,
    )
    
    fig.add_trace(
        go.Scatter(
            x = df['Date'], 
            y = df['price_gradient'], 
            name = 'Price Gradient',
            mode = 'lines',
        ),
        row = 3,
        col = 1,
    )
    
    fig.add_trace(
        go.Scatter(
            x = df['Date'], 
            y = df['RSI_gradient'], 
            name = 'RSI Gradient',
            mode = 'lines',
        ),
        row = 3,
        col = 1,
    )
    
    df = df.reset_index(drop = True)
    dates = df['Date'].tolist()
    df_div_idx = df[df['divergence']].index.values

    for idx in df_div_idx:
        try:
            fig.add_vrect(
                x0=dates[idx-1], 
                x1=dates[idx+1], 
                line_width=0, 
                fillcolor = 'rgba(239, 177, 101, 0.15)',
            )
        except:
            pass
    
    
    fig.update_xaxes(
        rangeslider_visible = False,
    )
    
    fig.update_layout(
        width = 700,
        height = 800,
        legend = {'orientation': 'h', 'y': -0.1},
        margin = {'l': 50, 'r': 50, 'b': 50, 't': 25},
        xaxis3 = {'title': 'Date'},
        yaxis1 = {'title': 'SPY (Weekly Chart)'},
        yaxis2 = {'title': 'RSI'},
        yaxis3 = {'title': 'Gradient Values'},
        title = TITLE
    )
    
    fig.show()
    fig.write_image(f'{TITLE}.png')
    
    return

if __name__ == '__main__':

    df = yf.download('SPY').reset_index()
    
    df = convert_to_weekly(df)
    df = get_rsi(df, PRICE_FIELD, RSI_LENGTH)
    
    df.loc[:, 'price_gradient'] = get_gradients(
        deepcopy(df['Low'].values), 
        TREND_LOOKBACK,
    )
    
    df.loc[:, 'RSI_gradient'] = get_gradients(
        deepcopy(df['RSI'].values),
        TREND_LOOKBACK,    
    )
    
    df = df.dropna()
    
    df.loc[:, 'divergence'] = (
        (df['price_gradient'] <= 0) & (df['RSI_gradient'] >= 0)
    )
    
    plot_result(df.reset_index())