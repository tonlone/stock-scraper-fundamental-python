import requests
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
from colorama import init, Fore, Style

# Initialize colorama
init()

# Download the 'punkt' resource
nltk.download('punkt')
# Download the 'stopwords' resource
nltk.download('stopwords')
# Download the 'wordnet' resource
nltk.download('wordnet')

symbol_lists = ["GRRR", "PWM", "NVAX", "ALPP"]
date = "2023-06-01"
SERPAPI_API_KEY = "a0519f1fc863161114d77812690f9c07c0f9c2ad89370b70032d6b615c02ad4a"

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

def generate_trading_signal(sentiment_score):
    if sentiment_score > 0.5:
        return Fore.GREEN + 'Strong Buy' + Style.RESET_ALL
    elif sentiment_score > 0.2:
        return Fore.GREEN + 'Buy' + Style.RESET_ALL
    elif sentiment_score < -0.5:
        return Fore.RED + 'String Sell' + Style.RESET_ALL
    elif sentiment_score < -0.2:
        return Fore.MAGENTA + 'Sell' + Style.RESET_ALL
    else:
        return 'Hold'
    
def sentiment(sentiment_score):
    if sentiment_score > 0.5:
        return Fore.GREEN + 'Very Positive' + Style.RESET_ALL
    elif sentiment_score > 0.2:
        return Fore.GREEN + 'Positive' + Style.RESET_ALL
    elif sentiment_score < -0.5:
        return Fore.RED + 'Very Negative' + Style.RESET_ALL
    elif sentiment_score < -0.2:
        return Fore.MAGENTA + 'Negative' + Style.RESET_ALL
    else:
        return 'Neutral'
    
def printSymbol(symbol):
    return Fore.BLUE + symbol + Style.RESET_ALL

for symbol in symbol_lists:
    cumulative_vader_sentiment_score = 0

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
        print(printSymbol(symbol))
        # Print the titles and snippets
        for i in range(len(titles)):
            
            print(f"{i+1}:")
            print("Title:", titles[i])
            print("Snippet:", snippets[i])
            print("URL:", urls[i])
            content = titles[i] + " " + snippets[i]
            preprocessed_text = preprocess_text(content)
            vader_sentiment_score = perform_VaderSentiment_sentiment_analysis(preprocessed_text)
            sentiment_label = sentiment(vader_sentiment_score)
            print("vader sentiment score:", str(vader_sentiment_score), "[" + sentiment_label + "]")
            cumulative_vader_sentiment_score += vader_sentiment_score
            print()
        average_sentiment_score = cumulative_vader_sentiment_score / len(titles)
        trading_signal = generate_trading_signal(average_sentiment_score)
        print("Trading signal using VaderSentiment on " + printSymbol(symbol) + ":", trading_signal)
        print("Average final score (-0.5 <= Negative, >= 0.5 - Positive):", average_sentiment_score)
        print("===============================================================================================================================================\n")
    else:
        print("No news found for ", symbol )