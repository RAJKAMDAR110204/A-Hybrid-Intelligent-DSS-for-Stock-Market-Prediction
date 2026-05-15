def make_decision(prediction, sentiment_score, confidence):

    score = 0

    score += 2 if prediction == 1 else -2
    score += sentiment_score * 2

    if confidence > 75:
        score += 1
    elif confidence < 60:
        score -= 1

    if score >= 2:
        return "BUY 📈 (Strong)"
    elif score >= 0:
        return "BUY 📈 (Moderate)"
    elif score < -2:
        return "SELL 📉 (Strong)"
    elif score < 0:
        return "SELL 📉 (Weak)"
    else:
        return "HOLD 🤝"


def get_risk(confidence):

    if confidence > 75:
        return "Low Risk 🟢"
    elif confidence > 60:
        return "Medium Risk 🟡"
    else:
        return "High Risk 🔴"