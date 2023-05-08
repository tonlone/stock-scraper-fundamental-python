# stock-scraper-fundamental-python
This python scipts to export data from stockanalysis.com into a PDF file. Perform parsing to extract Revenue Growth YoY, Net Income Growth and Debt / Equity Ratio
to determine of the symbol is recommended to consider. This is the based on ChatGPT recommendation (we called it naive ChatGPT recommendation).

https://stockanalysis.com/stocks/googl/financials/  => {symbol}-income.pdf

https://stockanalysis.com/stocks/googl/financials/ratios/ => {symbol}-debt.pdf


-----------------
How to configure:
-----------------
Note: Adjust the following in your desired list and your local directory
Files: findstockMain.py or findstockMainWeb.py

stockList = ['AAPL', 'ABT', 'ABBV', 'ACN', 'ADBE', 'AMZN', 'BAC', 'BMY', 'CMCSA', 'COST', 'CSCO', 'CRM', 'CVX', 'DHR', 'DIS', 'FB', 'GOOGL', 'HD', 'HON', 'INTC', 'JNJ', 'JPM', 'KO', 'LIN', 'LLY', 'MA', 'MCD', 'MMM', 'MRK', 'MSFT', 'NEE', 'NFLX', 'NVDA', 'NKE', 'ORCL', 'PFE', 'PEP', 'PG', 'PM', 'PYPL', 'T', 'TMO', 'TSLA', 'UNH', 'UNP', 'V', 'VZ', 'WMT', 'XOM']  <== (default)

home_dir = "C:\git-repo\GPT-Fund"       <== (default)

data_dir = "C:\git-repo\GPT-Fund\data"  <== (default)

-----------------
How to to run:
-----------------
1) Run it via a browser, run this python script findstockMainWeb.py and launch http://127.0.0.1:5555/stocks

Output: will be shown in browser / <home_dir>/recommended.txt

2) Run it via command, run this python script findstockMain.py 

Output: will be shown in console only

Note:Total Runtime: About 18 minutes for 49 symbols above
