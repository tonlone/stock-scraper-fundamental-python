import argparse
import os
import csv
import json

def analyzeData(data_dir, isQuarterly=False):
#def analyzeData(isQuarterly=False):    

    data_dir = "C:\git-repo\GPT-Fund"  # directory name
    full_file_path = os.path.join(data_dir, 'stock_data.csv')

    # Read in the CSV file
    with open(full_file_path, mode='r') as file:
        reader = csv.DictReader(file)
        stocks = [row for row in reader]

    # Find recommended stocks
    recommended_stocks = []
    failed_stocks = []
    positve_debt_ratio_stocks = []
    negative_income_growth_rate_stocks = []
    negative_revenue_growth_rate_stocks = []
    for stock in stocks:
        if float(stock['Debt-to-Equity Ratio']) < 1 and float(stock['Net Income Growth Rate']) > 0 and float(stock['Revenue Growth Rate']) > 0:
            recommended_stocks.append(stock)
        elif float(stock['Debt-to-Equity Ratio']) >= 1:
            positve_debt_ratio_stocks.append({stock['Stock']})
        elif float(stock['Net Income Growth Rate']) <= 0:
            negative_income_growth_rate_stocks.append({stock['Stock']})
        elif float(stock['Revenue Growth Rate']) <= 0:
            negative_revenue_growth_rate_stocks.append({stock['Stock']})
        else:
            failed_stocks.append(stock)

    if isQuarterly:
        print("Recommended stocks using Quarterly result:")
    else:
        print("Recommended stocks using Annual result:")

    # Output recommended stocks
    if recommended_stocks:
        print("")
        for i, stock in enumerate(recommended_stocks):
            print(f"{i+1}. Stock: {stock['Stock']}")
            print(f"- Net Income Growth Rate: {stock['Net Income Growth Rate']}")
            print(f"- Revenue Growth Rate: {stock['Revenue Growth Rate']}")
            print(f"- Debt-to-Equity Ratio: {stock['Debt-to-Equity Ratio']}")
            print("")
    else:
        print("No recommended stocks.")

    # Output failed stocks
    # if failed_stocks:
    #     print("Failed stocks:")
    #     print("")
    #     for stock in failed_stocks:
    #         if float(stock['Debt-to-Equity Ratio']) >= 1:
    #             print(f"Stock {stock['Stock']} failed because Debt-to-Equity Ratio is not less than 1.")
    #         elif float(stock['Net Income Growth Rate']) <= 0:
    #             print(f"Stock {stock['Stock']} failed because Net Income Growth Rate is not greater than 0.")
    #         elif float(stock['Revenue Growth Rate']) <= 0:
    #             print(f"Stock {stock['Stock']} failed because Revenue Growth Rate is not greater than 0.")
    #         print("")

    if positve_debt_ratio_stocks or negative_income_growth_rate_stocks or negative_revenue_growth_rate_stocks or failed_stocks:
        print("Failed stocks:")

    if positve_debt_ratio_stocks:
        print("Positive Debt-to-Equity Ratio (Debt-to-Equity Ratio > 1):")
        positve_debt_ratio_stocks_str = ', '.join([str(item) for item in positve_debt_ratio_stocks])
        print(positve_debt_ratio_stocks_str.replace("{", "").replace("}", "").replace("'", ""))
        print("")

    if negative_income_growth_rate_stocks:
        print("Negative income growth rate:")
        negative_income_growth_rate_stocks_str = ', '.join(str(item) for item in negative_income_growth_rate_stocks)
        print(negative_income_growth_rate_stocks_str.replace("{", "").replace("}", "").replace("'", ""))
        print("")
    
    if negative_revenue_growth_rate_stocks:
        print("Negative Revenue growth rate:")
        negative_revenue_growth_rate_stocks_str = ', '.join(str(item) for item in negative_revenue_growth_rate_stocks)
        print(negative_revenue_growth_rate_stocks_str.replace("{", "").replace("}", "").replace("'", ""))
        print("")

    if failed_stocks:
        print("Other failed stocks:")
        failed_stocks_str = ', '.join(failed_stocks)
        print(failed_stocks_str)
        print("")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--home_dir", help="Home directory for generating result")
    parser.add_argument("--isQuarterly", help="IsSearching for Quarterly result ?")

    args = parser.parse_args()

    output_data_dir = args.home_dir
    isQuarterly = args.isQuarterly.lower() == 'true'

    if not output_data_dir:
         output_data_dir = os.getcwd()

    analyzeData(output_data_dir,isQuarterly)
    #analyzeData()

if __name__ == "__main__":
    main()