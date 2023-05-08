# stock-scraper-fundamental-python
This python scipts to export data from stockanalysis.com into a PDF file. Perform parsing to extract Revenue Growth YoY, Net Income Growth and Debt / Equity Ratio
to determine of the symbol is recommended to consider. This is the based on ChatGPT recommendation (we called it naive ChatGPT recommendation).

https://stockanalysis.com/stocks/googl/financials/  => {symbol}-income.pdf

https://stockanalysis.com/stocks/googl/financials/ratios/ => {symbol}-debt.pdf

-----------------
Workflow:
-----------------
findstockMainWeb.py or findstockMain.py -> collectData.py -> parseData.py -> analyzeData.py -> output [(Webpage / recommended.txt) or console ]

-----------------
How to configure:
-----------------
Note: Adjust the following fields as you needed
Files: findstockMain.py or findstockMainWeb.py

stockList = ['AAPL', 'ABT', 'ABBV', 'ACN', 'ADBE', 'AMZN', 'BAC', 'BMY', 'CMCSA', 'COST', 'CSCO', 'CRM', 'CVX', 'DHR', 'DIS', 'FB', 'GOOGL', 'HD', 'HON', 'INTC', 'JNJ', 'JPM', 'KO', 'LIN', 'LLY', 'MA', 'MCD', 'MMM', 'MRK', 'MSFT', 'NEE', 'NFLX', 'NVDA', 'NKE', 'ORCL', 'PFE', 'PEP', 'PG', 'PM', 'PYPL', 'T', 'TMO', 'TSLA', 'UNH', 'UNP', 'V', 'VZ', 'WMT', 'XOM']  <== (default)

home_dir (default: "C:\git-repo\GPT-Fund")

data_dir (default: "C:\git-repo\GPT-Fund\data")

output_recommended_file (default: "recommended.txt")

isQuarterly (Default: True. To retrieve data based on Quarterly report.  Otherwise, data is retrieved on Annual report)

isSkipDownload (Default: False. Always download data from source.  Otherwise, reuse data from data_dir)

isSkipParsing (Default: False. Always parse data in data_dir.  Otherwise, perform analyze directly from data_dir)

-----------------
How to to run:
-----------------
1) Run it via a browser, run this python script findstockMainWeb.py and launch http://127.0.0.1:5555/stocks

Output: will be shown in browser / <home_dir>/recommended.txt

2) Run it via command, run this python script findstockMain.py 

Output: will be shown in console only

Note:Total Runtime: About 18 minutes for 49 symbols above
