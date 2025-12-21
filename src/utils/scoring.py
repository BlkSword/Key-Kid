import math
import re

LETTER_FREQ = {
    "a": 0.08167,
    "b": 0.01492,
    "c": 0.02782,
    "d": 0.04253,
    "e": 0.12702,
    "f": 0.02228,
    "g": 0.02015,
    "h": 0.06094,
    "i": 0.06966,
    "j": 0.00153,
    "k": 0.00772,
    "l": 0.04025,
    "m": 0.02406,
    "n": 0.06749,
    "o": 0.07507,
    "p": 0.01929,
    "q": 0.00095,
    "r": 0.05987,
    "s": 0.06327,
    "t": 0.09056,
    "u": 0.02758,
    "v": 0.00978,
    "w": 0.02360,
    "x": 0.00150,
    "y": 0.01974,
    "z": 0.00074,
    " ": 0.13000,
}

# Top 30 English Bigrams (approximate frequencies)
BIGRAM_FREQ = {
    "th": 0.0152, "he": 0.0128, "in": 0.0094, "er": 0.0094, "an": 0.0082,
    "re": 0.0068, "nd": 0.0063, "at": 0.0059, "on": 0.0057, "nt": 0.0056,
    "ha": 0.0056, "es": 0.0056, "st": 0.0055, "en": 0.0055, "ed": 0.0053,
    "to": 0.0052, "it": 0.0050, "ou": 0.0050, "ea": 0.0047, "hi": 0.0046,
    "is": 0.0046, "or": 0.0043, "ti": 0.0034, "as": 0.0033, "te": 0.0027,
    "et": 0.0019, "ng": 0.0018, "of": 0.0016, "al": 0.0009, "de": 0.0009,
    "se": 0.0008, "le": 0.0008, "sa": 0.0006, "si": 0.0005, "ar": 0.0004,
    "ve": 0.0004, "ra": 0.0004, "ld": 0.0002, "ur": 0.0002,
}

FLAG_PATTERN = re.compile(r"(flag|ctf|key|secret)\{.*?\}", re.IGNORECASE)

def english_score(s: str) -> float:
    """
    Calculate a score for how 'English-like' the text is.
    Considers letter frequency, bigrams, and specific CTF flag patterns.
    """
    if not s:
        return 0.0
    
    # 1. Flag detection shortcut
    if FLAG_PATTERN.search(s):
        return 10.0  # Immediate high score for flag-like patterns

    s_lower = s.lower()
    n = len(s)
    
    # 2. Letter frequency score
    letter_score = 0.0
    printable_count = 0
    for ch in s:
        if ch.lower() in LETTER_FREQ:
            letter_score += LETTER_FREQ[ch.lower()]
        if ch.isprintable():
            printable_count += 1
            
    # Penalize heavily if mostly non-printable
    if n > 0 and (printable_count / n) < 0.7:
        return 0.0

    # Normalize letter score (max approx 1.0 for perfect distribution)
    # We just sum probabilities, so for a long perfect text, sum/n ~ sum(p^2)? 
    # No, here we just sum freq[char]. For perfect English, expected sum per char is sum(p_i^2) ≈ 0.065
    # But the original implementation just summed them. Let's keep it simple but robust.
    # We'll use the Coefficient of Determination or Chi-Squared in a full implementation,
    # but here let's just normalize by length.
    avg_letter_score = letter_score / n if n > 0 else 0
    # Expected avg for random garbage is 1/26 ≈ 0.038 (ignoring space). 
    # Expected avg for English is ≈ 0.065.
    # Scale: (val - 0.03) / (0.07 - 0.03)
    normalized_letter = (avg_letter_score - 0.03) * 25 
    normalized_letter = max(0.0, min(1.0, normalized_letter))

    # 3. Bigram score
    bigram_score = 0.0
    if n > 1:
        for i in range(n - 1):
            bg = s_lower[i:i+2]
            if bg in BIGRAM_FREQ:
                bigram_score += BIGRAM_FREQ[bg]
        # Normalize bigram score
        # Max possible bigram sum per char is small. Let's just add it as a boost.
        bigram_score = bigram_score * 5 # Heuristic boost

    total = normalized_letter * 0.7 + bigram_score * 0.3
    
    # Penalize rare characters / high ascii if needed, but isprintable check handles most garbage.
    
    return min(1.0, total)

def ioc(s: str) -> float:
    freq = {}
    for ch in s:
        if ch.isalpha():
            c = ch.lower()
            freq[c] = freq.get(c, 0) + 1
    n = sum(freq.values())
    if n <= 1:
        return 0.0
    num = sum(v * (v - 1) for v in freq.values())
    den = n * (n - 1)
    return num / den

def hamming_distance(a: bytes, b: bytes) -> int:
    x = bytes(x ^ y for x, y in zip(a, b))
    return sum(bin(byte).count("1") for byte in x)