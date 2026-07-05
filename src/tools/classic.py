from ..utils.scoring import english_score, ioc
from .models import BreakResult


def _letters_only(s: str) -> str:
    return "".join(c for c in s if c.isalpha())


def _shift_char(c: str, k: int) -> str:
    if "A" <= c <= "Z":
        return chr((ord(c) - 65 - k) % 26 + 65)
    if "a" <= c <= "z":
        return chr((ord(c) - 97 - k) % 26 + 97)
    return c


def caesar_break(ciphertext: str) -> BreakResult:
    # Initialize with worst case
    best = BreakResult(algorithm="Caesar", plaintext="", key="0", confidence=0.0)
    for k in range(26):
        pt = "".join(_shift_char(c, k) for c in ciphertext)
        sc = english_score(pt)
        if sc > best.confidence:
            best = BreakResult(algorithm="Caesar", plaintext=pt, key=str(k), confidence=sc)
    return best


# English single-letter frequencies (a-z), used for Vigenère column analysis.
_ENGLISH_FREQ = {
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
}


def _vigenere_decrypt(ciphertext: str, key: str) -> str:
    out = []
    ci = 0
    for ch in ciphertext:
        if ch.isalpha():
            k = ord(key[ci % len(key)]) - 65
            out.append(_shift_char(ch, k))
            ci += 1
        else:
            out.append(ch)
    return "".join(out)


def _best_shift_frequency(column: str) -> int:
    """Return the shift that makes the column's letter frequencies closest to English."""
    best_shift = 0
    best_score = -1.0
    col_lower = column.lower()
    n = len(col_lower)
    if n == 0:
        return 0
    for shift in range(26):
        score = 0.0
        for ch in col_lower:
            if "a" <= ch <= "z":
                p = (ord(ch) - ord("a") - shift) % 26
                score += _ENGLISH_FREQ[chr(p + ord("a"))]
        if score > best_score:
            best_score = score
            best_shift = shift
    return best_shift


def vigenere_break(ciphertext: str, max_key_len: int = 16, top_k: int = 3) -> list[BreakResult]:
    text = ciphertext
    alpha_text = _letters_only(text)

    # Rank key lengths by average column IOC. English text has IOC ~0.067,
    # while Vigenère columns with the wrong key length look closer to random (~0.038).
    key_len_scores: list[tuple[int, float]] = []
    for klen in range(2, min(max_key_len, len(alpha_text)) + 1):
        cols = [alpha_text[i::klen] for i in range(klen)]
        iocs = [ioc(c) for c in cols if len(c) > 1]
        avg_ioc = sum(iocs) / len(iocs) if iocs else 0.0
        key_len_scores.append((klen, avg_ioc))

    # Try all key lengths, but prioritize those with higher IOC.
    key_len_scores.sort(key=lambda x: x[1], reverse=True)

    cands: list[tuple[str, float, str]] = []
    seen_keys: set[str] = set()
    for klen, _ in key_len_scores:
        cols = [alpha_text[i::klen] for i in range(klen)]
        key_chars = [chr(_best_shift_frequency(col) + 65) for col in cols]
        key_str = "".join(key_chars)
        if key_str in seen_keys:
            continue
        seen_keys.add(key_str)
        pt = _vigenere_decrypt(text, key_str)
        sc = english_score(pt)
        cands.append((key_str, sc, pt))

    cands.sort(key=lambda x: x[1], reverse=True)
    return [
        BreakResult(algorithm="Vigenere", plaintext=pt, key=key, confidence=sc)
        for key, sc, pt in cands[:top_k]
    ]


def _affine_inv(a: int) -> int | None:
    for i in range(26):
        if (a * i) % 26 == 1:
            return i
    return None


def affine_break(ciphertext: str, top_k: int = 3) -> list[BreakResult]:
    out: list[BreakResult] = []
    for a in range(1, 26):
        inv = _affine_inv(a)
        if inv is None:
            continue
        for b in range(26):
            res = []
            for ch in ciphertext:
                if "A" <= ch <= "Z":
                    x = ord(ch) - 65
                    p = (inv * (x - b)) % 26
                    res.append(chr(p + 65))
                elif "a" <= ch <= "z":
                    x = ord(ch) - 97
                    p = (inv * (x - b)) % 26
                    res.append(chr(p + 97))
                else:
                    res.append(ch)
            pt = "".join(res)
            sc = english_score(pt)
            out.append(
                BreakResult(algorithm="Affine", plaintext=pt, key=f"a={a},b={b}", confidence=sc)
            )
    out.sort(key=lambda x: x.confidence, reverse=True)
    return out[:top_k]


def _rail_pattern(n: int, rails: int) -> list[int]:
    idx = []
    r = 0
    d = 1
    for _i in range(n):
        idx.append(r)
        r += d
        if r == rails - 1:
            d = -1
        if r == 0:
            d = 1
    return idx


def rail_fence_decrypt(ciphertext: str, rails: int) -> str:
    n = len(ciphertext)
    pat = _rail_pattern(n, rails)
    positions: list[list[int]] = [[] for _ in range(rails)]
    for i, r in enumerate(pat):
        positions[r].append(i)
    res = [""] * n
    pos_idx = 0
    for r in range(rails):
        for i in positions[r]:
            res[i] = ciphertext[pos_idx]
            pos_idx += 1
    out = []
    for i in range(n):
        out.append(res[i])
    return "".join(out)


def rail_fence_break(ciphertext: str, max_rails: int = 10, top_k: int = 3) -> list[BreakResult]:
    out: list[BreakResult] = []
    for rails in range(2, max_rails + 1):
        pt = rail_fence_decrypt(ciphertext, rails)
        sc = english_score(pt)
        out.append(BreakResult(algorithm="RailFence", plaintext=pt, key=str(rails), confidence=sc))
    out.sort(key=lambda x: x.confidence, reverse=True)
    return out[:top_k]


def _column_lengths(n: int, k: int) -> list[int]:
    base = n // k
    extra = n % k
    return [base + (1 if i < extra else 0) for i in range(k)]


def columnar_transposition_decrypt(ciphertext: str, key_order: list[int]) -> str:
    n = len(ciphertext)
    k = len(key_order)
    lens = _column_lengths(n, k)
    cols = ["" for _ in range(k)]
    pos = 0
    for col_idx in range(k):
        real_col = key_order.index(col_idx)
        col_len = lens[real_col]
        cols[real_col] = ciphertext[pos : pos + col_len]
        pos += col_len
    rows = []
    r = max(lens)
    for i in range(r):
        for j in range(k):
            if i < len(cols[j]):
                rows.append(cols[j][i])
    return "".join(rows)


def transposition_break(ciphertext: str, max_key_len: int = 5, top_k: int = 3) -> list[BreakResult]:
    import itertools

    out: list[BreakResult] = []
    for k in range(2, max_key_len + 1):
        for perm in itertools.permutations(range(k)):
            pt = columnar_transposition_decrypt(ciphertext, list(perm))
            sc = english_score(pt)
            out.append(
                BreakResult(
                    algorithm="Transposition",
                    plaintext=pt,
                    key="-".join(str(x) for x in perm),
                    confidence=sc,
                )
            )
    out.sort(key=lambda x: x.confidence, reverse=True)
    return out[:top_k]


def playfair_decrypt(ciphertext: str, key_hint: str) -> str:
    def norm(s: str) -> str:
        t = []
        used = set()
        for ch in s.lower():
            if ch < "a" or ch > "z":
                continue
            c = "i" if ch == "j" else ch
            if c not in used:
                used.add(c)
                t.append(c)
        for ch in "abcdefghijklmnopqrstuvwxyz":
            c = "i" if ch == "j" else ch
            if c not in used:
                used.add(c)
                t.append(c)
        return "".join(t[:25])

    table = norm(key_hint)
    pos = {}
    for i, ch in enumerate(table):
        pos[ch] = (i // 5, i % 5)
    ct = "".join("i" if c.lower() == "j" else c.lower() for c in ciphertext if c.isalpha())
    pairs = []
    i = 0
    while i < len(ct):
        a = ct[i]
        b = ct[i + 1] if i + 1 < len(ct) else "x"
        if a == b:
            b = "x"
            i += 1
        else:
            i += 2
        pairs.append((a, b))
    out = []
    for a, b in pairs:
        ra, ca = pos[a]
        rb, cb = pos[b]
        if ra == rb:
            out.append(table[ra * 5 + (ca - 1) % 5])
            out.append(table[rb * 5 + (cb - 1) % 5])
        elif ca == cb:
            out.append(table[((ra - 1) % 5) * 5 + ca])
            out.append(table[((rb - 1) % 5) * 5 + cb])
        else:
            out.append(table[ra * 5 + cb])
            out.append(table[rb * 5 + ca])
    return "".join(out)


def playfair_break(
    ciphertext: str, key_hint: str | None = None, top_k: int = 1
) -> list[BreakResult]:
    if not key_hint:
        return [BreakResult(algorithm="Playfair", plaintext="", key=None, confidence=0.0)]
    pt = playfair_decrypt(ciphertext, key_hint)
    sc = english_score(pt)
    return [BreakResult(algorithm="Playfair", plaintext=pt, key=key_hint, confidence=sc)]
