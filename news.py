import requests

API_KEY = "0c922dd156e7408faddd85feddaa700f"

def get_news(stock):

    company = stock.replace(".NS","")

    url = (
        f"https://newsapi.org/v2/everything?"
        f"q={company}&"
        f"language=en&"
        f"sortBy=publishedAt&"
        f"pageSize=10&"
        f"apiKey={API_KEY}"
    )

    r = requests.get(url)
    data = r.json()

    headlines = []

    if "articles" in data:
        for article in data["articles"]:
            headlines.append(article["title"])

    return headlines