
from ..utils.scoring import english_score
from .models import BreakResult


def rot_all(text: str, top_k: int = 3) -> list[BreakResult]:
    results: list[BreakResult] = []
    for k in range(1, 26):
        out = []
        for c in text:
            if "A" <= c <= "Z":
                out.append(chr((ord(c) - 65 - k) % 26 + 65))
            elif "a" <= c <= "z":
                out.append(chr((ord(c) - 97 - k) % 26 + 97))
            else:
                out.append(c)
        pt = "".join(out)
        score = english_score(pt)
        results.append(BreakResult(algorithm=f"ROT{k}", plaintext=pt, key=str(k), confidence=score))
    results.sort(key=lambda x: x.confidence, reverse=True)
    return results[:top_k]
