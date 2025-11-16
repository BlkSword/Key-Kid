import sys, os
sys.path.insert(0, os.path.abspath("."))
from src.tools.rot import rot_all
from src.tools.decode import detect_encoding, decode_common
from src.tools.xor import xor_single_break, xor_repeating_break
from src.tools.classic import caesar_break, vigenere_break, affine_break, rail_fence_break
from src.tools.rc4 import rc4
from src.tools.number import factor_integer
from src.tools.block import HAS_PYCRYPTO, HAS_CRYPTOGRAPHY, aes_decrypt, des_decrypt

def main():
    r = rot_all("Uryyb Jbeyq", top_k=1)
    print("rot_all:", r[0].plaintext)
    d = detect_encoding("SGVsbG8gd29ybGQ=", top_k=1)
    print("detect_encoding:", d[0].name, d[0].decoded)
    dc = decode_common("48656c6c6f", limit=1)
    print("decode_common:", dc[0].name, dc[0].decoded)
    xs = xor_single_break("3f292c2c2b", encoding="hex", top_k=1)
    print("xor_single_break:", xs[0].key, xs[0].plaintext)
    xr = xor_repeating_break("5468697320697320612074657374", encoding="hex")
    print("xor_repeating_break:", xr.key, xr.plaintext[:16])
    cb = caesar_break("Uryyb Jbeyq")
    print("caesar_break:", cb.key, cb.plaintext)
    vb = vigenere_break("Lxfopvefrnhr", max_key_len=8, top_k=1)
    print("vigenere_break:", vb[0].key, vb[0].plaintext)
    ab = affine_break("ZEBBW", top_k=1)
    print("affine_break:", ab[0].key, ab[0].plaintext)
    rf = rail_fence_break("WECRLTEERDSOEEFEAOCAIVDEN", max_rails=5, top_k=1)
    print("rail_fence_break:", rf[0].key, rf[0].plaintext[:10])
    pt = rc4(bytes.fromhex("b2396305f03dc6a7bafefb7f59f13f0b"), b"Key")
    print("rc4:", pt.hex()[:8])
    fr = factor_integer(10403, prefer_yafu=False)
    print("factor_integer (internal):", fr.n, fr.factors)
    fr6 = factor_integer(6, prefer_yafu=True)
    print("factor_integer (yafu prefer, 6):", fr6.n, fr6.factors)
    if HAS_PYCRYPTO or HAS_CRYPTOGRAPHY:
        try:
            # AES CBC PKCS7 example (hex inputs). This is illustrative; actual values may differ
            pt_aes = awaitable(aes_decrypt("6bc1bee22e409f96e93d7e117393172a", "hex", "2b7e151628aed2a6abf7158809cf4f3c", "hex", "000102030405060708090a0b0c0d0e0f", "hex", "CBC"))
            print("aes_decrypt:", pt_aes[:8])
        except Exception as e:
            print("aes_decrypt: skipped", str(e))
        try:
            pt_des = awaitable(des_decrypt("85e813540f0ab405", "hex", "133457799BBCDFF1", "hex", None, "hex", "ECB"))
            print("des_decrypt:", pt_des[:8])
        except Exception as e:
            print("des_decrypt: skipped", str(e))

def awaitable(coro):
    try:
        import asyncio
        return asyncio.get_event_loop().run_until_complete(coro)
    except RuntimeError:
        import asyncio
        return asyncio.run(coro)

if __name__ == "__main__":
    main()