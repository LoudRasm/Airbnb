"""Deliberately simple English keyword baseline; evaluate language/domain bias."""
import re

def predict(review):
    words = set(re.findall(r"[a-z]+", review["comments"].lower()))
    positive = bool(words & {"great", "clean", "excellent", "lovely", "comfortable"})
    negative = bool(words & {"dirty", "noisy", "bad", "unsafe", "broken"})
    sentiment = "mixed" if positive and negative else "negative" if negative else "positive" if positive else "mixed"
    return {"review_id": review["review_id"], "sentiment": sentiment, "source": "keyword_baseline"}
