"""CTF workflow example - solving a multi-step challenge."""
import sys
import os
sys.path.insert(0, os.path.abspath("."))

from src.tools.decode import detect_encoding
from src.tools.rot import rot_all
from src.tools.xor import xor_single_break


def solve_ctf_challenge(ciphertext: str):
    """
    典型 CTF 工作流:
    1. 检测编码
    2. 解码
    3. 尝试各种密码破解
    """
    print(f"=== 解密密文: {ciphertext} ===\n")

    # 步骤 1: 检测编码
    print("步骤 1: 检测编码")
    encodings = detect_encoding(ciphertext, top_k=5)
    print(f"找到 {len(encodings)} 种可能的编码:")
    for enc in encodings:
        print(f"  - {enc.name}: {enc.decoded[:50]}...")
    print()

    # 步骤 2: 尝试 ROT
    print("步骤 2: 尝试 ROT 破解")
    rot_results = rot_all(ciphertext, top_k=3)
    print("最佳 ROT 候选:")
    for r in rot_results:
        print(f"  - ROT{r.key}: {r.plaintext[:50]} (分数: {r.confidence:.2f})")
    print()

    # 步骤 3: 尝试 XOR (如果是十六进制)
    print("步骤 3: 尝试 XOR 破解")
    try:
        xor_results = xor_single_break(ciphertext, encoding="hex", top_k=1)
        print(f"最佳 XOR 结果:")
        print(f"  - 密钥: {xor_results[0].key}")
        print(f"  - 明文: {xor_results[0].plaintext[:100]}")
    except Exception as e:
        print(f"  XOR 失败: {e}")
    print()


def main():
    print("=== CTF 密码学工作流示例 ===\n")

    # 示例 1: Base64 编码的 ROT13
    print("示例 1: Base64 编码的 ROT13")
    encoded = "Lxfopvefrnhr"  # Vigenère, not ROT13 but similar idea
    solve_ctf_challenge(encoded)

    # 示例 2: 十六进制编码的 XOR
    print("\n示例 2: 十六进制编码的 XOR")
    solve_ctf_challenge("3f292c2c2b")


if __name__ == "__main__":
    main()
