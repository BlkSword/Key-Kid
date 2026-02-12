

def hash_identify(text: str) -> list[str]:
    s = text.strip()
    out: list[str] = []
    hexchars = set("0123456789abcdefABCDEF")
    is_hex = all(c in hexchars for c in s)
    if is_hex:
        if len(s) == 32:
            out.append("MD5")
        if len(s) == 40:
            out.append("SHA1")
        if len(s) == 56:
            out.append("SHA224")
        if len(s) == 64:
            out.append("SHA256")
        if len(s) == 96:
            out.append("SHA384")
        if len(s) == 128:
            out.append("SHA512")
    b64chars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=")
    if all(c in b64chars for c in s):
        out.append("Base64-like")
    return out
