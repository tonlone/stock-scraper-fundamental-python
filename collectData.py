import argparse
import os
from pyhtml2pdf import converter
import PyPDF2

#stockList = ["MA", "V", "GOOGL", "MSFT", "PG", "KO", "JNJ" ]
#output_data_dir = "C:\git-repo\GPT-Fund\data"  # directory name
options = {'page-size': 'A4','margin-top': '0mm','margin-right': '0mm','margin-bottom': '0mm','margin-left': '0mm', 'zoom': '0.80'}

def cleanup(output_data_dir):
    for filename in os.listdir(output_data_dir):
        if (filename.endswith("-income.pdf") or filename.endswith("-debt.pdf")):
            file_path = os.path.join(output_data_dir, filename)
            os.remove(file_path)
    print("Cleanup working file ends with -income.pdf or -debt.pdf")
    print("")

def combineFile(output_data_dir, income_full_file_path, debt_full_file_path, stock):
    print("Combine File PDF file for stock :", stock)
    pdf1_path = income_full_file_path
    pdf2_path = debt_full_file_path
    output_file = f'{stock}-total.pdf'
    output_full_file_path = os.path.join(output_data_dir, output_file)

    # Open the first PDF file
    pdf1_file = open(pdf1_path, 'rb')
    pdf1_reader = PyPDF2.PdfReader(pdf1_file)

    # Open the second PDF file
    pdf2_file = open(pdf2_path, 'rb')
    pdf2_reader = PyPDF2.PdfReader(pdf2_file)

    # Create a new PDF file
    pdf_writer = PyPDF2.PdfWriter()

    # Copy pages from the first PDF file
    for page_num in range(len(pdf1_reader.pages)):
        page = pdf1_reader.pages[page_num]
        pdf_writer.add_page(page)

    # Copy pages from the second PDF file
    for page_num in range(len(pdf2_reader.pages)):
        page = pdf2_reader.pages[page_num]
        pdf_writer.add_page(page)

    # Write the combined PDF file
    output_file = open(output_full_file_path, 'wb')
    pdf_writer.write(output_file)

    # Close all the files
    pdf1_file.close()
    pdf2_file.close()
    output_file.close()

    print("Combined file:",output_full_file_path)
    print("")

def downloadPDF(stock, output_data_dir, isQuarterly=False):
    print("Downloading PDF file for stock :", stock)
    #print("isQuarterly :", isQuarterly)
    income_Url = f'https://stockanalysis.com/stocks/{stock.lower()}/financials/'
    if isQuarterly:
        income_Url += '?p=quarterly'
    income_pdf_file = f'{stock}-income.pdf'
    income_full_file_path = os.path.join(output_data_dir, income_pdf_file)
    print("calling URL:", income_Url)
    converter.convert(income_Url, income_full_file_path)

    debt_Url = f'https://stockanalysis.com/stocks/{stock.lower()}/financials/ratios/'
    if isQuarterly:
        debt_Url += '?p=quarterly'
    debt_pdf_file = f'{stock}-debt.pdf'
    debt_full_file_path = os.path.join(output_data_dir, debt_pdf_file,)
    print("calling URL:", debt_Url)
    converter.convert(debt_Url, debt_full_file_path)

    combineFile(output_data_dir, income_full_file_path, debt_full_file_path, stock)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("stockList", nargs="*", help="List of stock symbols")
    parser.add_argument("--data_dir", help="Output directory for PDF files")
    parser.add_argument("--isQuarterly", help="IsSearching for Quarterly result ?")

    args = parser.parse_args()

    stockList = args.stockList
    output_data_dir = args.data_dir
    isQuarterly = args.isQuarterly.lower() == 'true'

    if not output_data_dir:
        output_data_dir = os.getcwd()

    for stock in stockList:
        downloadPDF(stock, output_data_dir, isQuarterly)
    cleanup(output_data_dir)

if __name__ == "__main__":
    main()