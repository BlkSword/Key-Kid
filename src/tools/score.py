def wordlist_score(text: str, words: list[str]) -> float:
    if not words:
        return 0.0
    t = text.lower()
    hits = 0
    for w in words:
        if w and w in t:
            hits += 1
    return min(1.0, hits / max(1, len(words)))
