import requests
import json
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob

# Download the 'punkt' resource
nltk.download('punkt')
# Download the 'stopwords' resource
nltk.download('stopwords')
# Download the 'wordnet' resource
nltk.download('wordnet')

# def scrape_news_articles(url):
#     response = requests.get(url)
#     soup = BeautifulSoup(response.content, 'html.parser')
#     articles = soup.find_all('article')  # Adjust based on HTML structure
#     news_data = []
#     for article in articles:
#         title = article.find('h2').text
#         content = article.find('div', {'class': 'content'}).text
#         news_data.append({'title': title, 'content': content})
#     return news_data

# # Example usage
# news_articles = scrape_news_articles('https://cointelegraph.com/news/bitcoin-price-new-all-time-highs-3-countries-btc-31k')
# print(news_articles)

#test_text = "07:42PM Analyst Report: CarMax, Inc. (Morningstar Research) 04:43PM Bitcoin rises, CarMax stock up, Virgin Galactic shares slide: Trending tickers (Yahoo Finance Video) 04:34PM CarMax Stock Sets 2023 High After Earnings Beat Estimates (The Wall Street Journal) 04:24PM US STOCKS-Wall Street ends down, snaps weekly winning streak on Fed worries (Reuters) 04:20PM CarMax Stock Soars As Earnings Smash Estimates; Online Rival Carvana Sinks (Investor's Business Daily) 04:13PM Virgin Galactic, Starbucks fall; Smith & Wesson, CarMax rise, Friday, 6/23/2023 (AP Finance) 04:13PM CarMax Sees Sales Declines Ease as It Works to Lower Prices (The Wall Street Journal) 04:12PM CarMax, Virgin Galactic, Trupanion, Smith & Wesson, and More Market Movers (Barrons.com) 04:00PM US STOCKS-Wall Street ends down, snaps weekly winning streak on Fed worries (Reuters) 03:19PM CarMax Stock Jumps After Earnings Beat Estimates (The Wall Street Journal) 03:16PM Analyst Report: CarMax, Inc. (Morningstar Research) 02:32PM US STOCKS-Wall Street set to snap weekly winning streak on Fed hawkishness (Reuters) 01:38PM CarMax Stock Jumps After Earnings and Sales Top Estimates (Barrons.com) 01:20PM CarMax: good defensive driving does not mean investors should hop in (Financial Times) 01:12PM These Stocks Are Moving the Most Today: CarMax, Virgin Galactic, Trupanion, Smith & Wesson, and More (Barrons.com) 12:51PM CarMax (KMX) Q1 Earnings & Sales Beat Estimates, Decline Y/Y (Zacks) 12:45PM Stocks to Watch Friday: 3M, Siemens Energy, CarMax, Virgin Galactic, Nikola (The Wall Street Journal) 12:36PM US STOCKS-Wall St falls as hawkish Fed comments sap risk appetite (Reuters) 12:28PM CarMax earnings, Starbucks union, Wayfair upgrade, Nikola truck fire: Trending stocks (Yahoo Finance Video) 12:10PM CarMax Shares Soar After Beating Quarterly Profit and Sales Estimates (Investopedia) 11:14AM Crypto Analyst Says Bitcoin Can Break $32K Level, Nikola Moves Forward With Test Road Trips Despite Weak Demand & Internal Conflict, Retailers' Subscriptions Under FTC Scrutiny: Today's Top Stories (Benzinga) 11:00AM CarMax Looks Like a Trainwreck, But Is Bad Good Enough for a Trade? (TheStreet.com) 10:20AM US STOCKS-Wall St falls as hawkish Fed comments sap risk appetite (Reuters) 09:37AM 2 Stocks Defying Friday's Market Downturn (Motley Fool) 09:30AM CarMax (KMX) Reports Q1 Earnings: What Key Metrics Have to Say (Zacks) 08:59AM US STOCKS-Wall St set to open lower as hawkish Fed saps risk appetite (Reuters) 08:40AM CarMax Surges on Earnings Beat, But Can It Keep It in Drive? (TheStreet.com) 08:05AM CarMax (KMX) Q1 Earnings and Revenues Surpass Estimates (Zacks) 07:42AM CarMax says vehicle affordability remains a challenge, cost cuts help profit (Reuters) 07:33AM CarMax Surges After Q2 Earnings Top Forecasts Despite 'Challenging' Market (TheStreet.com) 07:03AM US STOCKS-Futures fall as Powell's hawkish stance dulls market spirits (Reuters) 06:57AM CarMax: Fiscal Q1 Earnings Snapshot (AP Finance) 06:50AM Carmax Reports First Quarter Fiscal 2024 Results (Business Wire) 06:18AM Stocks Slip Lower, 3M Settlement, Fed Bank Lending, CarMax Earnings On Deck, Meta News In Canada - 5 Things To Know (TheStreet.com)"

symbol="NVDA"
date="2023-06-01"
url = f"https://newsapi.org/v2/everything?q={symbol}&from={date}&sortBy=popularity&apiKey=354d0a51c66d4204a24acfb279349040"

print(url)

def preprocess_text(text):
    # Tokenize text
    tokens = word_tokenize(text.lower())
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [token for token in tokens if token not in stop_words]
    # Lemmatize words
    lemmatizer = WordNetLemmatizer()
    lemmatized_tokens = [lemmatizer.lemmatize(token) for token in filtered_tokens]
    # Join tokens back to text
    preprocessed_text = ' '.join(lemmatized_tokens)
    return preprocessed_text

# Example usage
# preprocessed_text = preprocess_text(test_text)
# print("Preprocessed text: " + preprocessed_text)


def perform_VaderSentiment_sentiment_analysis(text):
    analyzer = SentimentIntensityAnalyzer()
    sentiment_scores = analyzer.polarity_scores(text)
    return sentiment_scores['compound']

# Example usage
# sentiment_score = perform_VaderSentiment_sentiment_analysis(preprocessed_text)
# print("Sentiment Score using VaderSentiment (0 - Negative, 1 - Postive): " + str(sentiment_score))


def perform_TextBlob_sentiment_analysis(text):
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity
    return sentiment

# Example usage
# sentiment_score = perform_TextBlob_sentiment_analysis(preprocessed_text)
# print("Sentiment Score using Textblob : " + str(sentiment_score))


def generate_trading_signal(sentiment_score, threshold):
    if sentiment_score > threshold:
        return 'Buy'
    elif sentiment_score < -threshold:
        return 'Sell'
    else:
        return 'Hold'



# Send GET request to the API
response = requests.get(url)

cumulateive_vader_sentiment_score = 0
cumulateive_textBlob_sentiment_score = 0

# Check if the request was successful (status code 200)
if 'test_text' in locals() and len(test_text) > 0:
    preprocessed_text = preprocess_text(test_text)
    print("Preprocessed text for given text: " + preprocessed_text)
    vader_sentiment_score = perform_VaderSentiment_sentiment_analysis(preprocessed_text)
    #print("Sentiment Score using VaderSentiment: " + str(vader_sentiment_score))
    cumulateive_vader_sentiment_score += vader_sentiment_score
    textBlob_sentiment_score = perform_TextBlob_sentiment_analysis(preprocessed_text)
    #print("Sentiment Score using Textblob: " + str(textBlob_sentiment_score))
    cumulateive_textBlob_sentiment_score += textBlob_sentiment_score
    print()

    trading_signal = generate_trading_signal(cumulateive_vader_sentiment_score, 0.5)
    print("Trading signal using VaderSentiment on given text: [", trading_signal, "], Average final score (-0.5 <= Negative, >= 0.5 - Postive):: ", cumulateive_vader_sentiment_score)

    trading_signal = generate_trading_signal(cumulateive_textBlob_sentiment_score, 0.5)
    print("Trading signal using Textblob Sentiment on given text: [", trading_signal, "], Average final score (-0.5 <= Negative, >= 0.5 - Postive):: ", cumulateive_textBlob_sentiment_score)

elif response.status_code == 200:
    # Get the JSON data from the response
    json_data = response.json()

    # Extract content field from articles
    contents = [article['content'] for article in json_data['articles']]
    
    # Print the contents
    for content in contents:
        print(content)
        preprocessed_text = preprocess_text(content)
        print("Preprocessed text from URL: " + preprocessed_text)
        vader_sentiment_score = perform_VaderSentiment_sentiment_analysis(preprocessed_text)
        print("Sentiment Score using VaderSentiment: " + str(vader_sentiment_score))
        cumulateive_vader_sentiment_score += vader_sentiment_score
        textBlob_sentiment_score = perform_TextBlob_sentiment_analysis(preprocessed_text)
        print("Sentiment Score using Textblob: " + str(textBlob_sentiment_score))
        cumulateive_textBlob_sentiment_score += textBlob_sentiment_score
        print()
    # Example usage
    trading_signal = generate_trading_signal(cumulateive_vader_sentiment_score / len(contents), 0.5)
    print("Trading signal using VaderSentiment on" , symbol,  ": [", trading_signal, "], Average final score (-0.5 <= Negative, >= 0.5 - Postive):: ", cumulateive_vader_sentiment_score / len(contents))

    trading_signal = generate_trading_signal(cumulateive_textBlob_sentiment_score / len(contents), 0.5)
    print("Trading signal using Textblob Sentiment on" , symbol,  ": [", trading_signal, "], Average final score (-0.5 <= Negative, >= 0.5 - Postive):: ", cumulateive_textBlob_sentiment_score / len(contents))
else:
    # Print the error message if the request was not successful
    print("Error:", response.status_code)

