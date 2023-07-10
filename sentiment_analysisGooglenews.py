import requests
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

symbol="PWM"
date="2023-06-01"
SERPAPI_API_KEY="a0519f1fc863161114d77812690f9c07c0f9c2ad89370b70032d6b615c02ad4a"

def get_company_news(company_name):
    params = {
        "engine": "google",
        "tbm": "nws",
        "q": company_name,
        "api_key": SERPAPI_API_KEY
    }

    response = requests.get('https://serpapi.com/search', params=params)
    data = response.json()

    return data.get('news_results')

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

def perform_VaderSentiment_sentiment_analysis(text):
    analyzer = SentimentIntensityAnalyzer()
    sentiment_scores = analyzer.polarity_scores(text)
    return sentiment_scores['compound']

def generate_trading_signal(sentiment_score, threshold):
    if sentiment_score > threshold:
        return 'Buy'
    elif sentiment_score < -threshold:
        return 'Sell'
    else:
        return 'Hold'


cumulateive_vader_sentiment_score = 0

# Check if the request was successful (status code 200)
news = get_company_news(symbol)
if news:
    titles = []
    snippets = []
    urls = []
    for result in news:
        title = result.get('title')
        snippet = result.get('snippet')
        url = result.get('link')
        if title and snippet and url:
            titles.append(title)
            snippets.append(snippet)
            urls.append(url)

    
    # Print the titles and snippets
    for i in range(len(titles)):
        print(f"{i+1}:")
        print(f"Title: {titles[i]}")
        print(f"Snippet: {snippets[i]}")
        print(f"URL: {urls[i]}")
        content = titles[i] + " " + snippets[i]
        preprocessed_text = preprocess_text(content)
        #print("Preprocessed text from URL: " + preprocessed_text)
        vader_sentiment_score = perform_VaderSentiment_sentiment_analysis(preprocessed_text)
        print("vader sentiment score: " + str(vader_sentiment_score))
        cumulateive_vader_sentiment_score += vader_sentiment_score
        print()

else:
    print("No news found.")
    
trading_signal = generate_trading_signal(cumulateive_vader_sentiment_score / len(titles), 0.5)
print("Trading signal using VaderSentiment on" , symbol,  ": [", trading_signal, "], Average final score (-0.5 <= Negative, >= 0.5 - Postive):: ", cumulateive_vader_sentiment_score / len(titles))