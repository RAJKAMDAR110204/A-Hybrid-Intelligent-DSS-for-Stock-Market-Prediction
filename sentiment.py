from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

def get_sentiment(text_list):

    if not text_list:
        return 0

    scores = []

    for text in text_list:
        score = analyzer.polarity_scores(text)['compound']

        if score > 0.5:
            score *= 1.2
        elif score < -0.5:
            score *= 1.2

        scores.append(score)

    return sum(scores) / len(scores)