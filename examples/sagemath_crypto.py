"""SageMath advanced cryptography examples."""
import os
import sys

sys.path.insert(0, os.path.abspath("."))

from src.tools.sagemath import (
    HAS_SAGEMATH,
    chinese_remainder,
    coppersmith_attack,
    discrete_log,
    elliptic_curve_factor,
    elliptic_curve_point_add,
    linear_congruence_system,
    quadratic_residue,
)


def main():
    print("=== SageMath Advanced Cryptography Tools Demo ===\n")

    if not HAS_SAGEMATH:
        print("[!] SageMath not installed!")
        print("Visit https://www.sagemath.org/ to install")
        print("\nExamples below show graceful degradation\n")
    else:
        print("[*] SageMath is installed and available\n")

    # 1. Discrete Logarithm (DLP)
    print("=" * 60)
    print("1. Discrete Logarithm Problem")
    print("=" * 60)
    print("Problem: Find x such that 2^x = 5 (mod 101)")
    result = discrete_log("5", "101", "2")
    print(f"Result: {result}")
    if result.get("found"):
        print(f"[+] Solution found: x = {result['x']}")
    elif result.get("error"):
        print(f"[-] Error: {result['error']}")
    print()

    # 2. Chinese Remainder Theorem (CRT)
    print("=" * 60)
    print("2. Chinese Remainder Theorem")
    print("=" * 60)
    print("Problem: Find x satisfying:")
    print("  x = 2 (mod 3)")
    print("  x = 3 (mod 5)")
    print("  x = 2 (mod 7)")
    result = chinese_remainder([("2", "3"), ("3", "5"), ("2", "7")])
    print(f"Result: {result}")
    if result.get("found"):
        print(f"[+] Solution: x = {result['x']}")
        print(f"    Modulus N = {result['modulus']}")
    print()

    # 3. Linear Congruence
    print("=" * 60)
    print("3. Linear Congruence")
    print("=" * 60)
    print("Problem: Solve 3*x = 2 (mod 7)")
    result = linear_congruence_system(["3"], ["2"], ["7"])
    print(f"Result: {result}")
    if result.get("found"):
        print(f"[+] Solution: x = {result['x']}")
    print()

    # 4. Quadratic Residues
    print("=" * 60)
    print("4. Quadratic Residues (Modular Square Roots)")
    print("=" * 60)
    print("Problem: Solve x^2 = 4 (mod 7)")
    result = quadratic_residue("4", "7")
    print(f"Result: {result}")
    if result.get("found"):
        print(f"[+] Found {len(result['roots'])} solutions: {result['roots']}")
    print()

    # 5. Elliptic Curve Factorization (if SageMath available)
    if HAS_SAGEMATH:
        print("=" * 60)
        print("5. Elliptic Curve Method (ECM) Factoring")
        print("=" * 60)
        print("Problem: Factor n = 91")
        result = elliptic_curve_factor("91")
        print(f"Result: {result}")
        if result.get("found"):
            print(f"[+] Factor found: {result['factor']}")
            if result.get("remaining"):
                print(f"    Cofactor: {result['remaining']}")
        print()

    # 6. CTF Combined Example
    print("=" * 60)
    print("6. CTF Real-World Scenarios")
    print("=" * 60)

    # Scenario: RSA partial key exposure attack
    print("Scenario: RSA partial key exposure")
    print("Given: N = p*q, p = 2 (mod 3), p = 5 (mod 7)")
    crt_result = chinese_remainder([("2", "3"), ("5", "7")])
    if crt_result.get("found"):
        print(f"Via CRT: p = {crt_result['x']} (mod {crt_result['modulus']})")
        print(f"Possible p values: {crt_result['x']}, {int(crt_result['x']) + int(crt_result['modulus'])}...")
    print()

    # Scenario: Diffie-Hellman attack
    print("Scenario: Diffie-Hellman discrete log attack")
    print("Params: g=2, p=101, A=14 (public key)")
    dlp_result = discrete_log("14", "101", "2")
    if dlp_result.get("found"):
        print(f"[+] Private key: a = {dlp_result['x']}")
        print(f"Verify: 2^{dlp_result['x']} mod 101 = {pow(2, int(dlp_result['x']), 101)}")
    print()


def advanced_example():
    """More advanced SageMath examples (requires SageMath)"""
    if not HAS_SAGEMATH:
        print("SageMath not installed, skipping advanced examples")
        return

    print("\n=== Advanced Examples (Requires SageMath) ===\n")

    # Elliptic curve point addition
    print("Elliptic curve point addition: y^2 = x^3 + 2x + 2 (mod 17)")
    print("P = (5, 1), compute P + P = 2P")
    result = elliptic_curve_point_add(("2", "2", "17"), ("5", "1"), ("5", "1"))
    print(f"Result: {result}")
    if result.get("found"):
        print(f"[+] 2P = ({result['x']}, {result['y']})")
    print()

    # Coppersmith attack (small example)
    print("Coppersmith method: find small roots")
    print("Polynomial: f(x) = x^3 + x + 1 (mod 15)")
    result = coppersmith_attack("15", "3", "x^3 + x + 1", beta=0.5)
    print(f"Result: {result}")
    if result.get("found") and result.get("roots"):
        print(f"[+] Roots found: {result['roots']}")
    print()


if __name__ == "__main__":
    main()
    if HAS_SAGEMATH:
        advanced_example()
    else:
        print("\nTip: Install SageMath to run advanced examples")
