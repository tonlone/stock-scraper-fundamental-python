import numpy as np
import pandas as pd
import yfinance as yf

import plotly.io as pio
#pio.renderers.default='svg' # Change to browser for an interactive version
pio.renderers.default='browser' # Change to browser for an interactive version
import plotly.graph_objects as go
from plotly.subplots import make_subplots

MAX_PERC = -0.2 # Maximum percentage between open and close to count as a distribution day
ROLLING_PERIOD = 15 # Period to check over (days)
HIGHLIGHT_COUNT = 5 # Highlight on the chart if the count exceeds this
TICKER = 'CRM'
#ticker_symbols = ['ACN', 'ADBE', 'CRM', 'CSCO', 'DIS', 'MSFT', 'PG', 'PYPL', 'UNH', 'V', 'WMT', 'AAPL', 'NFLX', 'NVDA', 'TSLA' ]

# Upper and lower limits for plotting
LOWER_DATE = '2022-01-01'
UPPER_DATE = '2023-07-19'


if __name__ == '__main__':

    df = yf.download(TICKER).reset_index()
    
    # Find all locations where the percentage difference between the open and
    # the close is below the maximum allowed percentage
    df.loc[:, 'below_max_perc'] = np.where(
        100*(df['Close']/df['Open'] - 1) <= MAX_PERC,
        True,
        False,
    )
    
    # We classify a distribution day as any day where we have larger volume
    # than the previousj day and we are below the maximum percentage difference
    df.loc[:, 'is_distribution'] = np.where(
        df['below_max_perc'] & (df['Volume'] > df['Volume'].shift(1)),
        True,
        False,
    )
    
    # This counts up the number of distribution days over the last
    # ROLLING_PERIOD days. Note the closed='both' keyword argument allows the
    # most recent day to be in the calculation
    df.loc[:, 'distribution_count'] = (
        df['is_distribution']
        .rolling(ROLLING_PERIOD, closed='both')
        .sum() 
    )
    
    # This finds all days where we are above the rolling distribution count
    df.loc[:, 'above_count'] = df['distribution_count'] >= HIGHLIGHT_COUNT
    
    # Filter between the lower and upper dates for plotting, this prevents
    # having a chart that's too 'busy' and hard to understand
    df = df[
        (df['Date'] >= LOWER_DATE)
        & (df['Date'] <= UPPER_DATE)
    ]
    
    fig = make_subplots(
        rows = 2,
        cols = 1,
        shared_xaxes = True,
        vertical_spacing = 0.1,
        subplot_titles = (f'{TICKER} Chart', 'Number of Distribution Days'),
        row_width = [0.3, 0.7]
    )

    fig.add_trace(
        go.Candlestick(
            x = df['Date'],
            open = df['Open'],
            high = df['High'],
            low = df['Low'],
            close = df['Close'],
            showlegend = False
        ), 
        row=1, col=1,
    )
    
    # This code plots highlighted sections where we are above the max count
    df_counts = (
        df[df['above_count']]
        .groupby((~df['above_count']).cumsum())
        ['Date']
        .agg(['first', 'last'])
    )
    
    for idx, row in df_counts.iterrows():
        fig.add_vrect(
            x0 = row['first'], 
            x1 = row['last'],
            line_width = 0,
            fillcolor = 'red',
            opacity = 0.2,
        )
    
    fig.add_trace(
        go.Scatter(
            x = df['Date'],
            y = df['distribution_count'],
            showlegend=False,
        ),
        row = 2,
        col = 1,
    )

    fig.update_xaxes(
        rangebreaks = [{'bounds': ['sat', 'mon']}],
        rangeslider_visible = False,
    )
    
    fig.update_layout(
        yaxis = {
            'range': [df['Low'].min(), df['High'].max()], 
            'title': 'Price ($)'
        },
        margin = {'l': 50, 'r': 50, 'b': 50, 't': 25},
        width = 800,
        height = 800,
    )

    fig.show()