import time
import numba as nb
import numpy as np
import pandas as pd
import yfinance as yf

from typing import Tuple

import plotly.io as pio
import plotly.graph_objects as go
pio.renderers.default = 'browser'

# Breakout examples in the format [ticker, start date, end date]
BREAKOUTS = [
    ['MNKD', '2020-11-03', '2020-12-10'],
    ['MNKD', '2013-02-27', '2013-03-28'],
    ['AMD', '2021-07-15', '2021-10-12'],
    ['AMD', '2019-10-03', '2019-12-11'],
    ['AMD', '2018-04-30', '2018-07-25'],
    ['NVAX', '2020-03-12', '2020-05-08'],
    ['LEU', '2021-08-25', '2021-10-08'],
    ['LEU', '2020-11-18', '2020-12-11'],
    ['LEU', '2020-05-06', '2020-05-29'],
    ['FUTU', '2020-04-29', '2020-06-12'],
    ['LAC', '2021-08-18', '2021-10-11'],
    ['LAC', '2020-07-16', '2020-09-11'],
]

# This says we are going to compare a time-series of length LENGTH to all the
# breakout examples (which could be longer or shorter)
LENGTH = 35

# Upper DTW cost threshold to be considered as a breakout candidate
THRESHOLD = 12.23

# Upper and lower dates limits for the plot
# PLOT_LOWER_DATE = '2019-10-01'
# PLOT_UPPER_DATE = '2020-10-01'
PLOT_LOWER_DATE = '2020-08-01'
PLOT_UPPER_DATE = '2023-08-07'


@nb.jit(nopython = True)
def get_cost_matrix(ts1: np.array, ts2: np.array) -> np.array:
    '''
    Get the dynamic time warping cost matrix, which is used to determine
    the warping path and hence the overall cost of the path.
    
    Parameters
    ----------
    ts1 : np.array
        The first time series to compare.
    ts2 : np.array
        The second time series to compare.
    
    Returns
    -------
    C : np.array
        The dynamic time warping cost matrix.
    '''
    
    # Initialise a full cost matrix, filled with np.inf. This is so we can
    # start the algorithm and not get stuck on the boundary
    C = np.full(
        shape = (ts1.shape[0] + 1, ts2.shape[0] + 1), 
        fill_value = np.inf,
    )
    
    # Place the corner to zero, so that we don't have the minimum of 3 infs
    C[0, 0] = 0
    
    for i in range(1, ts1.shape[0] + 1):
        for j in range(1, ts2.shape[0] + 1):
            
            # Euclidian distance between the two points
            dist = abs(ts1[i-1] - ts2[j-1])
            
            # Find the cheapest cost of all three neighbours
            prev_min = min(C[i-1, j], C[i, j-1], C[i-1, j-1])
            
            # Populate the entry in the cost matrix
            C[i, j] = dist + prev_min
            
    return C[1:, 1:]


@nb.jit(nopython = True)
def get_path_cost(C: np.array) -> Tuple[list, float]:
    '''
    Get the optimal path and overall cost of the path.
    
    Parameters
    ----------
    C : np.array
        The DTW cost matrix.
    
    Returns
    -------
    path, cost : Tuple[list, float]
        The optimal path coordinates and the overall cost.
    '''
    
    i = C.shape[0] - 1
    j = C.shape[1] - 1
    
    path = [[i, j]]

    while (i > 0) | (j > 0):
        
        min_cost = min(C[i-1, j-1], C[i-1, j], C[i, j-1])
        
        if min_cost == C[i-1, j-1]:
            i -= 1
            j -= 1
        elif min_cost == C[i-1, j]:
            i -= 1
        elif min_cost == C[i, j-1]:
            j -= 1
        
        path.append([i, j])
        
    return path, C[-1, -1]


@nb.jit(nopython = True)
def standard_scale(ts: np.array) -> np.array:
    return (ts - np.mean(ts))/np.std(ts)

def get_time_series(ticker: str, date_start: str, date_end: str) -> np.array:
    '''
    Retrieve the stock data for the specified range, and scale using a z-score scaling approach.
    
    Parameters
    ----------
    ticker : str
        The ticker symbol of the stock.
    date_start : str
        Starting date for the time series in the format yyyy-mm-dd
    date_end : str
        Ending date for the time series in the format yyyy-mm-dd
    
    Returns
    -------
    np.array
        The scaled time series.
    '''
    data = yf.download(ticker, start=date_start, end=date_end)
    return standard_scale(data['Close'].values), data.index


@nb.jit(nopython = True)
def get_avg_cost(ts: np.array, breakouts: list) -> float:
    '''
    Compare the time series with all the breakout examples, and return the
    mean of all costs.
    Parameters
    ----------
    ts : np.array
        The time series we are comparing.
    breakouts : list
        A list of time series with the breakout examples.
    Returns
    -------
    float
        The mean of all costs from the time series comparisons.
    '''
    
    costs = []
    
    for i in range(len(breakouts)):
        C = get_cost_matrix(ts, breakouts[i])
        _, path_cost = get_path_cost(C.astype(np.float64))
        
        costs.append(path_cost)
            
    return np.mean(np.array(costs))


def load_breakout_examples() -> list:
    '''
    Load all breakout examples for the time-series comparisons
    Returns
    -------
    list
        A list of scaled time series for comparisons
    '''
    
    breakouts = []
    
    for b in BREAKOUTS:
        ticker, date_start, date_end = b[0], b[1], b[2]
        ts, _ = get_time_series(ticker, date_start, date_end)  # Get time series and ignore the index
        breakouts.append(ts)  # No need to convert to list, already using NumPy array
    
    return breakouts


@nb.jit(nopython = True)
def run_scanner(close: np.array, 
                breakouts: list,
                length: int,
                threshold: float) -> np.array:
    '''
    Run the scanner over the entire of the stock history, and return an array
    to indicate whether the region is a breakout candidate (1) or not (0)
    Parameters
    ----------
    close : np.array
        The stock closing prices.
    breakouts : list
        A list of time series with the breakout examples.
    length : int
        The lookback period for the scanner.
    threshold : float
        The scanner threshold (values less than this are considered a breakout) 
    Returns
    -------
    np.array
        A binary array indicating the positions where the scanner returns a
        positive result.
    '''
    
    candidates = []
    for idx in range(length, close.shape[0]):
        
        ts = standard_scale(close[idx-length:idx])
        
        cost = get_avg_cost(ts, breakouts)
        
        if cost < threshold:
            candidates.append(1)
        else:
            candidates.append(0)
            
    return np.array(candidates)


def plot_result(df: pd.DataFrame):
    df = df[
        (df.index >= PLOT_LOWER_DATE)
        & (df.index <= PLOT_UPPER_DATE)
    ]
    
    df.loc[:, 'breakout_region'] = np.where(
        df['filtered'],
        df['High'].max(),
        df['Low'].min(),
    )
    
    fig = go.Figure()
    
    fig.add_trace(
        go.Candlestick(
            x = df.index,  # Update x-axis to use DataFrame index
            open = df['Open'],
            high = df['High'],
            low = df['Low'],
            close = df['Close'],
            showlegend = False,        
        ),
    )
    
    fig.add_trace(
        go.Scatter(
            x = df.index,  # Update x-axis to use DataFrame index
            y = df['breakout_region'],
            fill = 'tonexty',
            fillcolor = 'rgba(0, 236, 109, 0.2)',
            mode = 'lines',
            line = {'width': 0, 'shape': 'hvh'},
            showlegend = False,
        ),
    )
    
    fig.update_layout(
        xaxis = {'title': 'Date'},
        yaxis = {'range': [df['Low'].min(), df['High'].max()], 'title': 'Price ($)'},
        title = 'TSLA - Breakout Candidates',
        width = 700,
        height = 700,
    )
    
    fig.update_xaxes(
        rangebreaks = [{'bounds': ['sat', 'mon']}],
        rangeslider_visible = False,
    )
    
    fig.show()
    
    return


if __name__ == '__main__':
    
    ticker = "TSLA"
    df = yf.download(ticker)
    
    t0 = time.time()
    
    candidates = run_scanner(
        df['Close'].values,
        nb.typed.List(load_breakout_examples()),
        LENGTH,
        THRESHOLD,
    )
    
    df = df.iloc[LENGTH:].copy()  # Keep only rows after the lookback period
    df.loc[:, 'filtered'] = candidates
    
    print('Number of scans performed:', len(df))
    print('Time taken:', time.time() - t0)
    
    plot_result(df)