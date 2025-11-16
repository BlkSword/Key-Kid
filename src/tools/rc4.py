from typing import Optional
import base64
from pydantic import BaseModel

def _parse(data: str, enc: str) -> bytes:
    if enc == "hex":
        return bytes.fromhex(data)
    if enc == "b64":
        return base64.b64decode(data)
    return data.encode()

def rc4(data: bytes, key: bytes) -> bytes:
    s = list(range(256))
    j = 0
    for i in range(256):
        j = (j + s[i] + key[i % len(key)]) % 256
        s[i], s[j] = s[j], s[i]
    i = 0
    j = 0
    out = bytearray()
    for b in data:
        i = (i + 1) % 256
        j = (j + s[i]) % 256
        s[i], s[j] = s[j], s[i]
        k = s[(s[i] + s[j]) % 256]
        out.append(b ^ k)
    return bytes(out)

class RC4Params(BaseModel):
    key: str
    key_encoding: str = "raw"

async def rc4_decrypt(ciphertext: str, cipher_encoding: str = "hex", key: Optional[str] = None, key_encoding: str = "raw", ctx: object | None = None) -> str:
    c = _parse(ciphertext, cipher_encoding)
    if not key:
        if ctx is not None:
            res = await ctx.elicit("需要 RC4 密钥", RC4Params)
            if res.action == "accept" and res.data:
                key = res.data.key
                key_encoding = res.data.key_encoding
            else:
                return ""
        else:
            return ""
    k = _parse(key, key_encoding)
    pt = rc4(c, k)
    return pt.decode(errors="ignore")