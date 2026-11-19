    for cls in CLASS_ORDER:
        tp = confusion[cls][cls]
        fp = sum(confusion[g][cls] for g in CLASS_ORDER if g != cls)
        fn = sum(confusion[cls][p] for p in CLASS_ORDER if p != cls)
        support = tp + fn
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        denom = 2 * tp + fp + fn
        f1 = (2 * tp) / denom if denom > 0 else 0.0
        per_class[cls] = {
            'precision': round(precision, 6),
            'recall': round(recall, 6),
            'f1': round(f1, 6),
            'support': support,
        }
        if denom > 0:
            active_f1s.append(f1)

