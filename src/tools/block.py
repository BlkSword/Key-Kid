import base64

try:
    from Crypto.Cipher import AES as PYCAES
    from Crypto.Cipher import DES as PYCDES

    HAS_PYCRYPTO = True
except Exception:
    HAS_PYCRYPTO = False

try:
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

    HAS_CRYPTOGRAPHY = True
except Exception:
    HAS_CRYPTOGRAPHY = False


def _parse(data: str, enc: str) -> bytes:
    if enc == "hex":
        return bytes.fromhex(data)
    if enc == "b64":
        return base64.b64decode(data)
    return data.encode()


def _pkcs7_unpad(b: bytes) -> bytes:
    if not b:
        return b
    pad = b[-1]
    if pad == 0 or pad > len(b):
        return b
    if b.endswith(bytes([pad]) * pad):
        return b[:-pad]
    return b


def _aes_pycrypto(ct: bytes, key: bytes, iv: bytes | None, mode: str) -> bytes:
    m = mode.upper()
    if m == "ECB":
        cipher = PYCAES.new(key, PYCAES.MODE_ECB)
    elif m == "CBC":
        if iv is None:
            raise ValueError("IV is required for CBC mode")
        cipher = PYCAES.new(key, PYCAES.MODE_CBC, iv)  # type: ignore[assignment]
    else:
        raise ValueError("Unsupported AES mode")
    pt = cipher.decrypt(ct)
    return _pkcs7_unpad(pt)


def _des_pycrypto(ct: bytes, key: bytes, iv: bytes | None, mode: str) -> bytes:
    m = mode.upper()
    if m == "ECB":
        cipher = PYCDES.new(key, PYCDES.MODE_ECB)
    elif m == "CBC":
        if iv is None:
            raise ValueError("IV is required for CBC mode")
        cipher = PYCDES.new(key, PYCDES.MODE_CBC, iv)
    else:
        raise ValueError("Unsupported DES mode")
    pt = cipher.decrypt(ct)
    return _pkcs7_unpad(pt)


def _aes_cryptography(ct: bytes, key: bytes, iv: bytes | None, mode: str) -> bytes:
    m = mode.upper()
    if m == "ECB":
        cipher_obj = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
    elif m == "CBC":
        if iv is None:
            raise ValueError("IV is required for CBC mode")
        cipher_obj = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())  # type: ignore[arg-type]
    else:
        raise ValueError("Unsupported AES mode")
    decryptor = cipher_obj.decryptor()
    pt = decryptor.update(ct) + decryptor.finalize()
    return _pkcs7_unpad(pt)


def _des_cryptography(ct: bytes, key: bytes, iv: bytes | None, mode: str) -> bytes:
    m = mode.upper()
    if m == "ECB":
        # Use TripleDES for backward compatibility
        cipher_obj = Cipher(algorithms.TripleDES(key), modes.ECB(), backend=default_backend())
    elif m == "CBC":
        if iv is None:
            raise ValueError("IV is required for CBC mode")
        cipher_obj = Cipher(algorithms.TripleDES(key), modes.CBC(iv), backend=default_backend())  # type: ignore[arg-type]
    else:
        raise ValueError("Unsupported DES mode")
    decryptor = cipher_obj.decryptor()
    pt = decryptor.update(ct) + decryptor.finalize()
    return _pkcs7_unpad(pt)


async def aes_decrypt(
    ciphertext: str,
    cipher_encoding: str = "hex",
    key: str | None = None,
    key_encoding: str = "hex",
    iv: str | None = None,
    iv_encoding: str = "hex",
    mode: str = "CBC",
    ctx: object | None = None,
) -> str:
    ct = _parse(ciphertext, cipher_encoding)
    if key is None:
        if ctx is not None and hasattr(ctx, "elicit"):
            from pydantic import BaseModel

            class AESParams(BaseModel):
                key: str
                key_encoding: str = "hex"
                iv: str | None = None
                iv_encoding: str = "hex"
                mode: str = "CBC"

            res = await ctx.elicit("需要 AES 解密参数", AESParams)  # type: ignore[attr-defined]
            if res.action == "accept" and res.data:
                key = res.data.key
                key_encoding = res.data.key_encoding
                iv = res.data.iv
                iv_encoding = res.data.iv_encoding
                mode = res.data.mode
            else:
                return ""
        else:
            return ""
    k = _parse(key, key_encoding)
    ivb = _parse(iv, iv_encoding) if iv else None
    if HAS_PYCRYPTO:
        pt = _aes_pycrypto(ct, k, ivb, mode)
    elif HAS_CRYPTOGRAPHY:
        pt = _aes_cryptography(ct, k, ivb, mode)
    else:
        return ""
    return pt.decode(errors="ignore")


async def des_decrypt(
    ciphertext: str,
    cipher_encoding: str = "hex",
    key: str | None = None,
    key_encoding: str = "hex",
    iv: str | None = None,
    iv_encoding: str = "hex",
    mode: str = "CBC",
    ctx: object | None = None,
) -> str:
    ct = _parse(ciphertext, cipher_encoding)
    if key is None:
        if ctx is not None and hasattr(ctx, "elicit"):
            from pydantic import BaseModel

            class DESParams(BaseModel):
                key: str
                key_encoding: str = "hex"
                iv: str | None = None
                iv_encoding: str = "hex"
                mode: str = "CBC"

            res = await ctx.elicit("需要 DES 解密参数", DESParams)  # type: ignore[attr-defined]
            if res.action == "accept" and res.data:
                key = res.data.key
                key_encoding = res.data.key_encoding
                iv = res.data.iv
                iv_encoding = res.data.iv_encoding
                mode = res.data.mode
            else:
                return ""
        else:
            return ""
    k = _parse(key, key_encoding)
    ivb = _parse(iv, iv_encoding) if iv else None
    if HAS_PYCRYPTO:
        pt = _des_pycrypto(ct, k, ivb, mode)
    elif HAS_CRYPTOGRAPHY:
        pt = _des_cryptography(ct, k, ivb, mode)
    else:
        return ""
    return pt.decode(errors="ignore")
