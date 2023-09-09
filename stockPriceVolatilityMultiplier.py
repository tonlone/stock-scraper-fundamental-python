import numpy as np
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# Define the stock ticker of interest
ticker = "NVDA"
# Download historical stock data for the given ticker within the specified date range
stock_data = yf.download(ticker, start="2022-01-01", end="2023-12-30")

# Specify the horizon for which the prediction cone should be plotted
time_horizon = 20

# Compute the daily returns based on the closing prices
stock_data['Returns'] = stock_data['Close'].pct_change()

# Fetch the most recent closing price from the data
current_price = stock_data.iloc[-1]['Close']

# Define multipliers which will determine the width of the cone (a higher multiplier means a wider cone)
std_multipliers = [1, 1.25, 1.5]

# Setup the plotting environment to accommodate plots for each multiplier and volatility calculation method (rolling and expanding)
fig, ax = plt.subplots(len(std_multipliers), 2, figsize=(25, 7 * len(std_multipliers)))

# Set the font size for price labels within the plot
label_font_size = 12

# Loop through each standard deviation multiplier to plot its respective cone
for std_index, std_multiplier in enumerate(std_multipliers):

    # Extract the last 30 days of closing prices
    plot_data = stock_data[-30:]['Close']

    # Create a date range for the prediction horizon
    date_range = pd.date_range(plot_data.index[-1] + pd.DateOffset(1), periods=time_horizon, freq='D')

    # Initialize series to store the upper and lower bounds of the cone
    expected_upper_bounds = pd.Series(index=date_range)
    expected_lower_bounds = pd.Series(index=date_range)

    # Compute the cone boundaries using rolling volatility
    for i in range(time_horizon):
        # Compute rolling volatility based on the past 30 days, updating the window for each day in the prediction horizon
        volatility = stock_data['Returns'].iloc[-(30+i):-i].std() if i > 0 else stock_data['Returns'].iloc[-(30+i):].std()
        expected_price_movement = current_price * volatility * np.sqrt(i + 1) * std_multiplier
        expected_upper_bounds.iloc[i] = current_price + expected_price_movement
        expected_lower_bounds.iloc[i] = current_price - expected_price_movement

    # Plot the last 30 days of actual prices and the predicted cone using rolling volatility
    ax[std_index][0].plot(plot_data, label=f'{ticker} - Past 30 Days')
    ax[std_index][0].plot(expected_upper_bounds, linestyle='--', color='green', label=f'Expected Upper Bound')
    ax[std_index][0].plot(expected_lower_bounds, linestyle='--', color='red', label=f'Expected Lower Bound')
    ax[std_index][0].fill_between(date_range, expected_upper_bounds, expected_lower_bounds, color='gray', alpha=0.3)
    ax[std_index][0].set_title(f'{ticker}- Expected Price Movement in {time_horizon} Days using Rolling Volatility (Std multiplier: {std_multiplier})')

    # Label the cone boundaries every 5 days
    for i in range(0, time_horizon, 5):
        ax[std_index][0].text(date_range[i], expected_upper_bounds[i], f'{expected_upper_bounds[i]:.2f}', color='green', fontsize=label_font_size)
        ax[std_index][0].text(date_range[i], expected_lower_bounds[i], f'{expected_lower_bounds[i]:.2f}', color='red', fontsize=label_font_size)

    # Compute the cone boundaries using expanding window volatility
    for i in range(time_horizon):
        # Compute expanding window volatility from the beginning of the data up to the current point in the prediction horizon
        volatility = stock_data['Returns'].iloc[:-(time_horizon-i)].std() * std_multiplier
        expected_price_movement = current_price * volatility * np.sqrt(i + 1)
        expected_upper_bounds.iloc[i] = current_price + expected_price_movement
        expected_lower_bounds.iloc[i] = current_price - expected_price_movement

    # Plot the last 30 days of actual prices and the predicted cone using expanding window volatility
    ax[std_index][1].plot(plot_data, label=f'{ticker} - Past 30 Days')
    ax[std_index][1].plot(expected_upper_bounds, linestyle='--', color='green', label=f'Expected Upper Bound')
    ax[std_index][1].plot(expected_lower_bounds, linestyle='--', color='red', label=f'Expected Lower Bound')
    ax[std_index][1].fill_between(date_range, expected_upper_bounds, expected_lower_bounds, color='gray', alpha=0.3)
    ax[std_index][1].set_title(f'{ticker}- Expected Price Movement in {time_horizon} Days using Expanding Window Volatility (Std multiplier: {std_multiplier})')

    # Label the cone boundaries every 5 days for expanding window volatility
    for i in range(0, time_horizon, 5):
        ax[std_index][1].text(date_range[i], expected_upper_bounds[i], f'{expected_upper_bounds[i]:.2f}', color='green', fontsize=label_font_size)
        ax[std_index][1].text(date_range[i], expected_lower_bounds[i], f'{expected_lower_bounds[i]:.2f}', color='red', fontsize=label_font_size)

# Adjust the layout to avoid any overlap and display the plots
plt.tight_layout()
plt.show()