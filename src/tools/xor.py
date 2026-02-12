import base64
import multiprocessing
from concurrent.futures import ThreadPoolExecutor

from ..utils.scoring import english_score, hamming_distance
from .models import BreakResult


def _parse_data(data: str, encoding: str) -> bytes:
    if encoding == "hex":
        return bytes.fromhex(data)
    if encoding == "b64":
        return base64.b64decode(data)
    return data.encode()


def xor_single_break(data: str, encoding: str = "hex", top_k: int = 3) -> list[BreakResult]:
    b = _parse_data(data, encoding)

    def try_key(k: int) -> BreakResult:
        pt = bytes(x ^ k for x in b)
        txt = pt.decode(errors="ignore")
        score = english_score(txt)
        return BreakResult(algorithm="XOR-single", plaintext=txt, key=str(k), confidence=score)

    # Use parallel processing for better performance
    max_workers = min(256, (multiprocessing.cpu_count() or 4) * 4)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(try_key, range(256)))

    results.sort(key=lambda x: x.confidence, reverse=True)
    return results[:top_k]


def _avg_norm_hamming(b: bytes, key_size: int, blocks: int = 4) -> float:
    chunks = [b[i * key_size : (i + 1) * key_size] for i in range(blocks)]
    if len(chunks) < 2 or any(len(c) != key_size for c in chunks):
        return 1e9
    dists = []
    for i in range(blocks - 1):
        d = hamming_distance(chunks[i], chunks[i + 1])
        dists.append(d / key_size)
    return sum(dists) / len(dists)


def xor_repeating_break(
    data: str, encoding: str = "hex", min_key: int = 2, max_key: int = 40
) -> BreakResult:
    b = _parse_data(data, encoding)
    candidates = []
    for ks in range(min_key, max_key + 1):
        candidates.append((ks, _avg_norm_hamming(b, ks)))
    candidates.sort(key=lambda x: x[1])
    best_pt = ""
    best_key = b""
    best_score = -1.0
    for ks, _ in candidates[:5]:
        key = bytearray()
        for i in range(ks):
            column = bytes(b[j] for j in range(i, len(b), ks))
            best_k = 0
            best_col_score = -1.0
            for k in range(256):
                pt = bytes(x ^ k for x in column)
                txt = pt.decode(errors="ignore")
                sc = english_score(txt)
                if sc > best_col_score:
                    best_col_score = sc
                    best_k = k
            key.append(best_k)
        pt = bytes(b[i] ^ key[i % len(key)] for i in range(len(b)))
        txt = pt.decode(errors="ignore")
        sc = english_score(txt)
        if sc > best_score:
            best_score = sc
            best_pt = txt
            best_key = bytes(key)
    return BreakResult(
        algorithm="XOR-repeating",
        plaintext=best_pt,
        key=best_key.decode(errors="ignore"),
        confidence=best_score,
    )
