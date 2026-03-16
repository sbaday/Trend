"""
Sentiment Analyzer
------------------
Reddit/HN/Google Trends phrase'leri için duygu analizi yapar.
VADER (Valence Aware Dictionary and sEntiment Reasoner) kullanır.

Pozitif/negatif duygu sinyali, trend kalitesini iyileştirir:
  +1.0  → çok olumlu ("I love this!")
   0.0  → nötr
  -1.0  → çok olumsuz ("this is terrible")

Kullanım:
    from analyzer.sentiment import score_sentiment
    s = score_sentiment("this is absolutely hilarious and I love it!")
    # → 0.87 (çok olumlu)
"""

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_analyzer = SentimentIntensityAnalyzer()


def score_sentiment(text: str) -> float:
    """
    Metni analiz eder ve bileşik duygu skoru döndürür.
    -1.0 (çok negatif) ile +1.0 (çok pozitif) arasında.
    """
    if not text or not text.strip():
        return 0.0
    scores = _analyzer.polarity_scores(text)
    return round(scores["compound"], 4)


def sentiment_label(score: float) -> str:
    """Skoru okunabilir etikete çevirir."""
    if score >= 0.05:
        return "positive"
    elif score <= -0.05:
        return "negative"
    else:
        return "neutral"
