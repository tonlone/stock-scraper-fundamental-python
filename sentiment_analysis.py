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

#test_text = "Famed investor, Stanley Druckenmiller hasnt been shy about how bearish he is on the market, stating that he still believes there will be a hard landing sometime in the next year."

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
if response.status_code == 200:
    # Get the JSON data from the response
    json_data = response.json()

    # Extract content field from articles
    contents = [article['content'] for article in json_data['articles']]
    
    # Print the contents
    for content in contents:
        print(content)
        preprocessed_text = preprocess_text(content)
        print("Preprocessed text: " + preprocessed_text)
        vader_sentiment_score = perform_VaderSentiment_sentiment_analysis(preprocessed_text)
        print("Sentiment Score using VaderSentiment: " + str(vader_sentiment_score))
        cumulateive_vader_sentiment_score += vader_sentiment_score
        textBlob_sentiment_score = perform_TextBlob_sentiment_analysis(preprocessed_text)
        print("Sentiment Score using Textblob: " + str(textBlob_sentiment_score))
        cumulateive_textBlob_sentiment_score += textBlob_sentiment_score
        print()
else:
    # Print the error message if the request was not successful
    print("Error:", response.status_code)


# Example usage
trading_signal = generate_trading_signal(cumulateive_vader_sentiment_score / len(contents), 0.5)
print("Trading signal using VaderSentiment on" , symbol,  ": [", trading_signal, "], Average final score (-0.5 <= Negative, >= 0.5 - Postive):: ", cumulateive_vader_sentiment_score / len(contents))

trading_signal = generate_trading_signal(cumulateive_textBlob_sentiment_score / len(contents), 0.5)
print("Trading signal using Textblob Sentiment on" , symbol,  ": [", trading_signal, "], Average final score (-0.5 <= Negative, >= 0.5 - Postive):: ", cumulateive_textBlob_sentiment_score / len(contents))


