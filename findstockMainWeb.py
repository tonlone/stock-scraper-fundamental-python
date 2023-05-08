import subprocess
import os
from flask import Flask
from flask_socketio import SocketIO, emit
import datetime

app = Flask(__name__)
socketio = SocketIO(app, async_mode='threading')


@app.route('/stocks')
def get_stocks():
    stockList = ["MA", "V", "GOOGL", "MSFT", "PG", "KO", "JNJ"]
    #stockList = ['AAPL', 'AMZN', 'MSFT']
    #stockList = ['AAPL', 'ABT', 'ABBV', 'ACN', 'ADBE', 'AMZN', 'BAC', 'BMY', 'CMCSA', 'COST', 'CSCO', 'CRM', 'CVX', 'DHR', 'DIS', 'FB', 'GOOGL', 'HD', 'HON', 'INTC', 'JNJ', 'JPM', 'KO', 'LIN', 'LLY', 'MA', 'MCD', 'MMM', 'MRK', 'MSFT', 'NEE', 'NFLX', 'NVDA', 'NKE', 'ORCL', 'PFE', 'PEP', 'PG', 'PM', 'PYPL', 'T', 'TMO', 'TSLA', 'UNH', 'UNP', 'V', 'VZ', 'WMT', 'XOM']
    home_dir = "C:\git-repo\GPT-Fund"
    data_dir = "C:\git-repo\GPT-Fund\data"
    output_recommended_file = "recommended.txt"
    isQuarterly = True
    isSkippedDownload = False
    isSkippedParsing = False

    # change directory to "C:\git-repo\GPT-Fund"
    os.chdir(home_dir)

    # Command to download data 
    collect_script_path = os.path.join(os.getcwd(), "collectData.py")
    collect_data_command = ["python", collect_script_path]
    collect_data_command.extend(stockList)
    collect_data_command.extend(["--data_dir", data_dir])
    collect_data_command.extend(["--isQuarterly", str(isQuarterly)])

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

    stock_str = ', '.join(stockList)

    with open(output_recommended_file, 'w') as f:

        yield "List of Stocks being evaluated(" + str(len(stockList)) + "): " + stock_str + "<br/>"
        yield "isQuarterly: "  + str(isQuarterly) + "<br/><br/>"
        yield "isSkippedDownload: "  + str(isSkippedDownload) + "<br/><br/>"
        yield "isSkippedParsing: "  + str(isSkippedParsing) + "<br/><br/>"

        f.write("List of Stocks being evaluated(" + str(len(stockList)) + "): " + stock_str + "\n")
        f.write("isQuarterly: "  + str(isQuarterly) + "\n\n")
        f.write("isSkippedDownload: "  + str(isSkippedDownload) + "\n\n")
        f.write("isSkippedParsing: "  + str(isSkippedParsing) + "\n\n")

        
        current_time = datetime.datetime.now()
        yield "Start time: " + str(current_time) + "<br/><br/>";
        process_time = len(stockList) * 0.4;
        yield "Processing time: " + str(process_time) + " minutes<br/><br/>";
        new_time = current_time + datetime.timedelta(minutes=process_time)
        yield "Expected completion time: " + str(new_time) + "<br/><br/>";
        yield "Loading...<br/><br/>";

        if isSkippedDownload != True:
            process = subprocess.Popen(collect_data_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            for line in iter(process.stdout.readline, b''):
                print(line.decode('utf-8') + "\n")
                yield line.decode('utf-8') + "<br/>";
                update = line.decode('utf-8') 
                socketio.emit('update', {'data': update})
            process.wait()

        if isSkippedParsing != True:
            process = subprocess.Popen(parse_data_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            for line in iter(process.stdout.readline, b''):
                print(line.decode('utf-8') + "\n")
                yield line.decode('utf-8') + "<br/>";
                update = line.decode('utf-8') 
                socketio.emit('update', {'data': update})
            process.wait()

        process = subprocess.Popen(analyze_data_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for line in iter(process.stdout.readline, b''):
            yield line.decode('utf-8') + "<br/>"
            f.write(line.decode('utf-8') + "\n")
        process.wait()

        
        currentDateTime = datetime.datetime.now()
        yield "<br/>";
        yield "Updated time: " + str(currentDateTime) ;
        f.write("\n")
        f.write("Updated time: " + str(currentDateTime)  + "\n")
socketio.start_background_task(get_stocks)

if __name__ == '__main__':
    app.run(debug=True, port=5555)