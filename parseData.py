import argparse
import os
import PyPDF2
import re
import csv

def get_financial_indicators(file_path):
    with open(file_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ''
        for page in pdf_reader.pages:
            text += page.extract_text()
        revenue_growth_pattern = r'Revenue Growth \(YoY\)[\s\S]*?([-]?\d+[\d,.]*)[\s\S]*?([-]?\d+[\d,.]*)[\s\S]*?([-]?\d+[\d,.]*)'
        revenue_growth_matches = re.findall(revenue_growth_pattern, text)

        net_income_growth_pattern = r'Net Income Growth[\s\S]*?([-]?\d+[\d,.]*)[\s\S]*?([-]?\d+[\d,.]*)[\s\S]*?([-]?\d+[\d,.]*)'
        net_income_growth_matches = re.findall(net_income_growth_pattern, text)

        debt_to_equity_ratio_pattern = r'Debt \/ Equity Ratio[\s\S]*?([-]?\d+[\d,.]*)[\s\S]*?([-]?\d+[\d,.]*)[\s\S]*?([-]?\d+[\d,.]*)'
        debt_to_equity_ratio_matches = re.findall(debt_to_equity_ratio_pattern, text)


        if revenue_growth_matches and net_income_growth_matches and debt_to_equity_ratio_matches:
            revenue_growth_rates = [float(match[0].replace(',', '')) for match in revenue_growth_matches]
            net_income_growth_rates = [float(match[0].replace(',', '')) for match in net_income_growth_matches]
            debt_to_equity_ratios = [float(match[0].replace(',', '')) for match in debt_to_equity_ratio_matches]
            return revenue_growth_rates, net_income_growth_rates, debt_to_equity_ratios
        else:
            return None

def pick_stocks(data_path, home_path):
    print("Processing...", data_path)
    stock_data = {}
    for file in os.listdir(data_path):
        if file.endswith("-total.pdf"):
            full_file_path = os.path.join(data_path, file)
            print("full_file_path...", full_file_path)
            stock_name = file.split("-")[0]
            financial_indicators = get_financial_indicators(full_file_path)
            if financial_indicators:
                revenue_growth_rates, net_income_growth_rates, debt_to_equity_ratios = financial_indicators
                stock_data[stock_name] = [revenue_growth_rates[0], net_income_growth_rates[0], debt_to_equity_ratios[0]]

    if not stock_data:
        print("No stocks meet the criteria.")
    else:
        output_dir = home_path  # directory name
        output_file_path = os.path.join(output_dir, 'stock_data.csv')
        # Write data to CSV file
        with open(output_file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Stock', 'Revenue Growth Rate', 'Net Income Growth Rate', 'Debt-to-Equity Ratio'])
            #print("stock_data ***",stock_data)
            for stock, data in stock_data.items():
                    writer.writerow([stock, data[0], data[1], data[2]])
    print("")
#data_path = "C:\git-repo\GPT-Fund\data"
#pick_stocks(data_path)         

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", help="Output directory for PDF files")
    parser.add_argument("--home_dir", help="Home directory for generating result")

    args = parser.parse_args()

    home_dir = args.home_dir
    output_data_dir = args.data_dir

    if not output_data_dir:
        output_data_dir = os.getcwd()

    pick_stocks(output_data_dir, home_dir)

if __name__ == "__main__":
    main()
