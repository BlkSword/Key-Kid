from ..utils.scoring import english_score
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


def vigenere_break(ciphertext: str, max_key_len: int = 16, top_k: int = 3) -> list[BreakResult]:
    text = ciphertext
    cands: list[tuple[str, float, str]] = []
    for klen in range(2, max_key_len + 1):
        key = []
        for i in range(klen):
            column = []
            for j, ch in enumerate(text):
                if ch.isalpha():
                    if j % klen == i:
                        column.append(ch)
            best_s = 0.0
            best_k = 0
            for k in range(26):
                pt = "".join(_shift_char(c, k) for c in column)
                s = english_score(pt)
                if s > best_s:
                    best_s = s
                    best_k = k
            key.append(chr(best_k + 65))
        key_str = "".join(key)
        out = []
        ci = 0
        for ch in text:
            if ch.isalpha():
                k = ord(key_str[ci % len(key_str)]) - 65
                out.append(_shift_char(ch, k))
                ci += 1
            else:
                out.append(ch)
        pt = "".join(out)
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
