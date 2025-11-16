import math

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

def english_score(s: str) -> float:
    total = 0.0
    count = 0
    for ch in s:
        c = ch.lower()
        if c in LETTER_FREQ:
            total += LETTER_FREQ[c]
            count += 1
        elif c.isprintable():
            total += 0.001
            count += 1
    if count == 0:
        return 0.0
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