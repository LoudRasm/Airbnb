"""Evaluate only paired labels; reject duplicate IDs and invalid labels."""
from .llm import SENTIMENTS

def evaluate(predictions, labels, source):
    truth = {}
    for row in labels:
        if row["sentiment"] not in SENTIMENTS or row["review_id"] in truth:
            raise ValueError("Manual labels must have unique review_id and valid sentiment")
        truth[row["review_id"]] = row["sentiment"]
    pairs = [(truth[r["review_id"]], r["sentiment"]) for r in predictions if r["review_id"] in truth]
    if not pairs:
        return []
    f1s = []
    for label in sorted(SENTIMENTS):
        tp = sum(a == b == label for a, b in pairs)
        fp = sum(a != label and b == label for a, b in pairs)
        fn = sum(a == label and b != label for a, b in pairs)
        f1s.append(2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0)
    return [{"source": source, "paired_n": len(pairs), "manual_n": len(truth),
             "accuracy": sum(a == b for a, b in pairs)/len(pairs), "macro_f1": sum(f1s)/3,
             "meets_100_paired": len(pairs) >= 100}]
