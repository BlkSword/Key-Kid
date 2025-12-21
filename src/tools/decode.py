import base64
import binascii
from typing import List
from urllib.parse import unquote

from .models import DetectionCandidate
from ..utils.scoring import english_score

def _try_decode_base64(s: str) -> str | None:
    try:
        return base64.b64decode(s, validate=True).decode(errors="ignore")
    except Exception:
        return None

def _try_decode_base32(s: str) -> str | None:
    try:
        return base64.b32decode(s, casefold=True).decode(errors="ignore")
    except Exception:
        return None

def _try_decode_base16(s: str) -> str | None:
    try:
        return base64.b16decode(s, casefold=True).decode(errors="ignore")
    except Exception:
        return None

def _try_decode_b85(s: str) -> str | None:
    try:
        return base64.b85decode(s).decode(errors="ignore")
    except Exception:
        return None

def _try_decode_hex(s: str) -> str | None:
    try:
        return bytes.fromhex(s).decode(errors="ignore")
    except Exception:
        return None

def _try_decode_url(s: str) -> str | None:
    try:
        t = unquote(s)
        if t != s:
            return t
        return None
    except Exception:
        return None

def _try_decode_unicode_escape(s: str) -> str | None:
    try:
        return s.encode("utf-8").decode("unicode_escape")
    except Exception:
        return None

def _try_decode_binary(s: str) -> str | None:
    """Try to decode binary string (e.g., '0100100001100101...')"""
    s_clean = s.replace(" ", "").replace("\n", "")
    if not s_clean or len(s_clean) % 8 != 0:
        return None
    if not all(c in "01" for c in s_clean):
        return None
    try:
        # Split into 8-bit chunks
        bytes_list = [int(s_clean[i:i+8], 2) for i in range(0, len(s_clean), 8)]
        return bytes(bytes_list).decode(errors="ignore")
    except Exception:
        return None

DECODERS = [
    ("base64", _try_decode_base64),
    ("base32", _try_decode_base32),
    ("base16", _try_decode_base16),
    ("base85", _try_decode_b85),
    ("hex", _try_decode_hex),
    ("url", _try_decode_url),
    ("unicode_escape", _try_decode_unicode_escape),
    ("binary", _try_decode_binary),
]

def detect_encoding(text: str, top_k: int = 5) -> List[DetectionCandidate]:
    cands: List[DetectionCandidate] = []
    for name, fn in DECODERS:
        decoded = fn(text)
        if decoded is not None:
            score = english_score(decoded)
            cands.append(DetectionCandidate(name=name, score=score, decoded=decoded))
    cands.sort(key=lambda x: x.score, reverse=True)
    return cands[:top_k]

def decode_common(text: str, limit: int = 10) -> List[DetectionCandidate]:
    seen = {}
    out: List[DetectionCandidate] = []
    for name, fn in DECODERS:
        decoded = fn(text)
        if decoded is not None:
            if decoded in seen:
                continue
            seen[decoded] = True
            out.append(DetectionCandidate(name=name, score=english_score(decoded), decoded=decoded))
            if len(out) >= limit:
                break
    out.sort(key=lambda x: x.score, reverse=True)
    return out