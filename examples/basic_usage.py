"""Basic usage examples for Key-Kid MCP server."""
import sys
import os
sys.path.insert(0, os.path.abspath("."))

# Direct imports (not via MCP)
from src.tools.rot import rot_all
from src.tools.xor import xor_single_break, xor_repeating_break
from src.tools.classic import caesar_break, vigenere_break
from src.tools.decode import detect_encoding, decode_common
from src.tools.number import factor_integer


def main():
    print("=== Key-Kid 基础用法示例 ===\n")

    # 1. ROT 破解
    print("1. ROT 破解:")
    results = rot_all("Uryyb Jbeyq", top_k=1)
    print(f"   密文: Uryyb Jbeyq")
    print(f"   明文: {results[0].plaintext}")
    print(f"   密钥: ROT{results[0].key}")
    print()

    # 2. Caesar 破解
    print("2. Caesar 破解:")
    result = caesar_break("Uryyb Jbeyq")
    print(f"   密文: Uryyb Jbeyq")
    print(f"   明文: {result.plaintext}")
    print(f"   密钥: {result.key}")
    print()

    # 3. XOR 单字节破解
    print("3. XOR 单字节破解:")
    results = xor_single_break("3f292c2c2b", encoding="hex", top_k=1)
    print(f"   密文 (hex): 3f292c2c2b")
    print(f"   明文: {results[0].plaintext}")
    print(f"   密钥: {results[0].key}")
    print()

    # 4. Vigenère 破解
    print("4. Vigenère 破解:")
    results = vigenere_break("Lxfopvefrnhr", max_key_len=8, top_k=1)
    print(f"   密文: Lxfopvefrnhr")
    print(f"   明文: {results[0].plaintext}")
    print(f"   密钥: {results[0].key}")
    print()

    # 5. 编码检测
    print("5. 编码检测:")
    results = detect_encoding("SGVsbG8gd29ybGQ=", top_k=3)
    print(f"   输入: SGVsbG8gd29ybGQ=")
    for r in results:
        print(f"   - {r.name}: {r.decoded[:30]}...")
    print()

    # 6. 因式分解
    print("6. 整数因式分解:")
    result = factor_integer(10403, prefer_yafu=False)
    print(f"   n = {result.n}")
    print(f"   因子 = {' × '.join(result.factors)}")
    print()


if __name__ == "__main__":
    main()
