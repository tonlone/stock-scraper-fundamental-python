import subprocess
import os
import datetime

stockList = ["MA", "V", "GOOGL", "MSFT"]
#stockList = ['AAPL', 'ABT', 'ABBV', 'ACN', 'ADBE', 'AMZN', 'BAC', 'BMY', 'CMCSA', 'COST', 'CSCO', 'CRM', 'CVX', 'DHR', 'DIS', 'FB', 'GOOGL', 'HD', 'HON', 'INTC', 'JNJ', 'JPM', 'KO', 'LIN', 'LLY', 'MA', 'MCD', 'MMM', 'MRK', 'MSFT', 'NEE', 'NFLX', 'NVDA', 'NKE', 'ORCL', 'PFE', 'PEP', 'PG', 'PM', 'PYPL', 'T', 'TMO', 'TSLA', 'UNH', 'UNP', 'V', 'VZ', 'WMT', 'XOM']


home_dir = "C:\git-repo\GPT-Fund" # home directory name
data_dir = "C:\git-repo\GPT-Fund\data"  # data directory name
isQuarterly = False # Set to True if you wan quarterly result.  Otherwise set to False
isSkippedDownload = False
isSkippedParsing = False

# change directory to "C:\git-repo\GPT-Fund"
os.chdir(home_dir)

stock_str = ', '.join(stockList)
print("List of Stocks being evaluated(" + str(len(stockList)) + "): " + stock_str + "\n")
print("isQuarterly: "  + str(isQuarterly) + "\n")
print("isSkippedDownload: "  + str(isSkippedDownload) + "\n")
print("isSkippedParsing: "  + str(isSkippedParsing) + "\n\n")

current_time = datetime.datetime.now()
print("Start time: " + str(current_time) + "\n");
process_time = len(stockList) * 0.25;
print("Processing time: " + str(process_time) + " minutes\n");
new_time = current_time + datetime.timedelta(minutes=process_time)
print("Expected completion time: " + str(new_time) + "\n");
print("Loading...\n\n");

if isSkippedDownload != True:
    # Command to download data 
    collect_script_path = os.path.join(os.getcwd(), "collectData.py")
    collect_data_command = ["python", collect_script_path]
    collect_data_command.extend(stockList)
    collect_data_command.extend(["--data_dir", data_dir])
    collect_data_command.extend(["--isQuarterly", str(isQuarterly)])

if isSkippedParsing != True:
    # Command to parse data 
    parse_script_path = os.path.join(os.getcwd(), "parseData.py")
    parse_data_command = ["python", parse_script_path]
    parse_data_command.extend(["--data_dir", data_dir])
    parse_data_command.extend(["--home_dir", home_dir])

# analyze data 
analyze_script_path = os.path.join(os.getcwd(), "analyzeData.py")
analyze_data_command = ["python", analyze_script_path]
analyze_data_command.extend(["--home_dir", home_dir])
analyze_data_command.extend(["--isQuarterly", str(isQuarterly)])

subprocess.run(collect_data_command)
subprocess.run(parse_data_command)
subprocess.run(analyze_data_command)

currentDateTime = datetime.datetime.now()
print("Updated time: " + str(currentDateTime)  + "\n")

#subprocess.run(['python', 'parseData.py'])
#subprocess.run(['python', 'analyzeData.py'])