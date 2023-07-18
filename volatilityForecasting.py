
import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
from arch import arch_model

ticker = "ACN"

# Retrieve historical volatility data for GS
stock = yf.Ticker(ticker)
volatility_data = stock.history(period="max")
# Calculate the rolling mean and standard deviation
rolling_mean = volatility_data["Close"].rolling(window=30).mean()
rolling_std = volatility_data["Close"].rolling(window=30).std()
# Plot the rolling mean and standard deviation
plt.figure(figsize=(10, 6))
plt.plot(volatility_data.index, volatility_data["Close"], label="Volatility")
plt.plot(rolling_mean.index, rolling_mean, label="Rolling Mean")
plt.plot(rolling_std.index, rolling_std, label="Rolling Std")
plt.xlabel("Date")
plt.ylabel("Volatility")
plt.title(f"Rolling Mean and Standard Deviation of Volatility Data - {ticker}")
plt.legend()
plt.grid(True)
plt.show()

# Calculate log returns
returns = np.log(volatility_data["Close"]).diff().dropna()
# Fit the GARCH(1, 1) model
model = arch_model(returns, vol="Garch", p=1, q=1)
results = model.fit()
# Estimate the volatility
volatility = results.conditional_volatility
# Plot the estimated and actual volatility
plt.figure(figsize=(10, 6))
plt.plot(volatility.index, volatility, label="Estimated Volatility")
plt.plot(returns.index, returns, label="Actual Volatility")
plt.xlabel("Date")
plt.ylabel("Volatility")
plt.title(f"Estimated and Actual Volatility - {ticker}")
plt.legend()
plt.grid(True)
plt.show()

# Forecast the volatility
forecast = results.forecast(start=0, horizon=30)
forecast_volatility = forecast.variance.dropna().values.flatten()
# Plot the forecasted volatility
plt.figure(figsize=(10, 6))
plt.plot(forecast_volatility, label="Forecasted Volatility")
plt.xlabel("Time")
plt.ylabel("Volatility")
plt.title(f"Forecasted Volatility - {ticker}")
plt.legend()
plt.grid(True)
plt.show()


# Calculate the mean absolute error (MAE)
mae = np.mean(np.abs(volatility - returns))
print("Mean Absolute Error (MAE):", mae)

# Calculate the root mean squared error (RMSE)
rmse = np.sqrt(np.mean((volatility - returns) ** 2))
print("Root Mean Squared Error (RMSE):", rmse)
# Calculate the forecast errors
errors = volatility - returns

# Plot the histogram of forecast errors
plt.figure(figsize=(10, 6))
plt.hist(errors, bins=30, density=True)
plt.xlabel("Forecast Error")
plt.ylabel("Density")
plt.title(f"Histogram of Forecast Errors - {ticker}")
plt.grid(True)

plt.show()