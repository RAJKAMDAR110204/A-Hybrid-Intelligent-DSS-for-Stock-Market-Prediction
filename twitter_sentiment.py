import snscrape.modules.twitter as sntwitter
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

def get_twitter_sentiment(query):

    try:
        tweets = []

        for i, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
            if i > 10:
                break
            tweets.append(tweet.content)

        if not tweets:
            return 0

        scores = []
        for t in tweets:
            score = analyzer.polarity_scores(t)
            scores.append(score['compound'])

        return sum(scores) / len(scores)

    except Exception as e:
        print("Twitter fetch failed:", e)
        return 0   # fallback neutral sentiment