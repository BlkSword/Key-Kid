"""Lightweight performance benchmark for key Key-Kid tools.

Runs each tool several times and prints the average elapsed time. This script
is intentionally standalone (no pytest dependency) so it can be run in
production-like containers.
"""

import os
import sys
import time

sys.path.insert(0, os.path.abspath("."))

from src.tools.classic import caesar_break, vigenere_break
from src.tools.number import factor_integer
from src.tools.rsa import fermat_factor, wiener_attack
from src.tools.xor import xor_repeating_break, xor_single_break


def _timeit(fn, args, rounds=5):
    start = time.perf_counter()
    for _ in range(rounds):
        fn(*args)
    elapsed = time.perf_counter() - start
    return elapsed / rounds


def main():
    benchmarks = [
        ("caesar_break", caesar_break, ("Uryyb Jbeyq",), 100),
        ("xor_single_break", xor_single_break, ("3f292c2c2b",), 10),
        (
            "xor_repeating_break",
            xor_repeating_break,
            ("5468697320697320612074657374",),
            10,
        ),
        (
            "vigenere_break",
            vigenere_break,
            (
                "llg gelkaqih bk lgcph srf klx xpcx ml zmfuig zitv "
                "teweuv jbfh kk unagmcc uwjqii lgqgfrx wpuv hhww",
            ),
            10,
        ),
        ("factor_integer (small)", factor_integer, (10403,), 20),
        ("factor_integer (medium)", factor_integer, (999800019,), 10),
        ("wiener_attack", wiener_attack, (1022117, 180017), 20),
        ("fermat_factor", fermat_factor, (1009 * 1013,), 20),
    ]

    print(f"{'benchmark':<30} {'avg_s':>10} {'rounds':>8}")
    print("-" * 52)
    for name, fn, args, rounds in benchmarks:
        avg = _timeit(fn, args, rounds)
        print(f"{name:<30} {avg:>10.6f} {rounds:>8}")


if __name__ == "__main__":
    main()
