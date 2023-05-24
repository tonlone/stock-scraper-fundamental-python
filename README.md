# 1) stock-scraper-fundamental-python
This python scipts to export data from stockanalysis.com into a PDF file. Perform parsing to extract Revenue Growth YoY, Net Income Growth and Debt / Equity Ratio
to determine of the symbol is recommended to consider. This is the based on ChatGPT recommendation (we called it naive ChatGPT recommendation).

https://stockanalysis.com/stocks/googl/financials/  => {symbol}-income.pdf

https://stockanalysis.com/stocks/googl/financials/ratios/ => {symbol}-debt.pdf

The script will merge both pdf files into a single one for analysis => {symbol}-total.pdf

-----------------
Related scripts:
-----------------
findstockMainWeb.py

findstockMain.py

collectData.py

parseData.py

analyzeData.py

-----------------
Workflow:
-----------------
1. Run it via a browser

findstockMainWeb.py -> collectData.py -> parseData.py -> analyzeData.py -> output [(Webpage / recommended.txt)]  

OR

2. Run it via console

findstockMain.py -> collectData.py -> parseData.py -> analyzeData.py -> output [(recommended.txt) or console ]

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

-------------------
Known Issue / bugs:
-------------------

1.  After the all the PDF files are downloaed, the script may not continue to process the PDF files.
    
    Workaround: 
     
     i) You may stop the program, e.g. findstockMain.py or findstockMainWeb.py
    
     ii) Update the flag isSkipDownload = True in the scripts
     
     iii) Re-run the script again
    


# 2) predict-stock-movement-python

This python scipts to gather historical data and using different model to predict their price movement. We are using this page as reference.

https://medium.com/@mrconnor/technical-analysis-to-predict-stock-movement-95650daa5c4f

Available models: Keltner Channel, Bollinger Bands, MACD, William R%, RSI, RSI Fast, RSI Slow, IchmokuCloud

You may use the model against Stocks, Cryptocurrency, FX Currency to see if it fits

-----------------
How to configure
-----------------
ticker = 'MSFT'

stoploss = False        (There is a stop loss feature and you may try it out)

strategy_name = "RSI"

start_date = '2022-10-01'

end_date = '2023-05-23'

-----------------
Workflow:
-----------------

Execute the script below

python predictStockMovement.py


# 3) other individual scripts

stockRecommendedChannelBreakout.py  - recommend when to buy and sell instrument based on strategy Channel Breakout

stockRecommendedMACD.py - recommend when to buy and sell instrument based on strategy MACD

stockRecommendedRSI.py - recommend when to buy and sell instrument based on strategy RSI

stockRecommendedKAMA.py - recommend when to buy and sell instrument based on strategy KAMA

stockRecommended.py   - recommend which stocks to buy, sell and hold (still work in progress)
