"""RSA attacks commonly seen in CTF challenges.

All functions accept string or integer inputs and return plain dictionaries so
that callers (including MCP wrappers) can inspect ``success`` before reading
other fields.
"""

from collections.abc import Sequence
from math import gcd, isqrt
from typing import Any

# Reject numbers that are far too large for these textbook attacks.
_MAX_RSA_BITS = 8192


def _to_int(value: int | str) -> int:
    return int(value, 0) if isinstance(value, str) else value


def _check_size(n: int) -> str | None:
    if n.bit_length() > _MAX_RSA_BITS:
        return f"modulus exceeds {_MAX_RSA_BITS} bits"
    return None


def _bytes_from_int(x: int) -> bytes:
    """Convert a non-negative integer to its minimal big-endian byte representation."""
    return x.to_bytes((x.bit_length() + 7) // 8, "big") if x > 0 else b"\x00"


def _continued_fraction(n: int, d: int) -> list[tuple[int, int]]:
    """Return convergents of n/d as (numerator, denominator)."""
    cf: list[int] = []
    a, b = n, d
    while b:
        q = a // b
        cf.append(q)
        a, b = b, a - q * b
    if not cf:
        return [(1, 1)]

    result: list[tuple[int, int]] = []
    p0, p1 = 1, cf[0]
    q0, q1 = 0, 1
    result.append((p1, q1))
    for ai in cf[1:]:
        p2 = ai * p1 + p0
        q2 = ai * q1 + q0
        result.append((p2, q2))
        p0, p1 = p1, p2
        q0, q1 = q1, q2
    return result


def wiener_attack(n: int | str, e: int | str) -> dict[str, Any]:
    """Wiener's attack: recover d when it is small (d < n^0.25/3).

    Returns a dict with ``success``, ``p``, ``q``, ``d``, ``m`` (decoded bytes as hex).
    """
    n_val = _to_int(n)
    e_val = _to_int(e)
    err = _check_size(n_val)
    if err:
        return {"success": False, "error": err}

    for k, d in _continued_fraction(e_val, n_val):
        if k == 0:
            continue
        # ed - 1 = k * phi(n)
        phi_times_k = e_val * d - 1
        if phi_times_k % k != 0:
            continue
        phi = phi_times_k // k
        # phi = n - p - q + 1  =>  p + q = n - phi + 1
        s = n_val - phi + 1
        # x^2 - s*x + n = 0
        discriminant = s * s - 4 * n_val
        if discriminant < 0:
            continue
        sqrt_disc = isqrt(discriminant)
        if sqrt_disc * sqrt_disc != discriminant:
            continue
        p = (s + sqrt_disc) // 2
        q = (s - sqrt_disc) // 2
        if p * q == n_val:
            return {
                "success": True,
                "p": str(p),
                "q": str(q),
                "d": str(d),
            }
    return {"success": False, "error": "Wiener attack failed"}


def common_modulus_attack(
    c1: int | str, c2: int | str, e1: int | str, e2: int | str, n: int | str
) -> dict[str, Any]:
    """Common modulus attack: same n, coprime e1/e2.

    Returns ``success`` and ``plaintext`` (hex).
    """
    c1_val = _to_int(c1)
    c2_val = _to_int(c2)
    e1_val = _to_int(e1)
    e2_val = _to_int(e2)
    n_val = _to_int(n)
    err = _check_size(n_val)
    if err:
        return {"success": False, "error": err}

    if gcd(e1_val, e2_val) != 1:
        return {"success": False, "error": "public exponents are not coprime"}

    # Bezout coefficients: s*e1 + t*e2 = 1
    def extended_gcd(a: int, b: int) -> tuple[int, int, int]:
        if b == 0:
            return a, 1, 0
        g, x1, y1 = extended_gcd(b, a % b)
        return g, y1, x1 - (a // b) * y1

    _, s, t = extended_gcd(e1_val, e2_val)
    m = (pow(c1_val, s, n_val) * pow(c2_val, t, n_val)) % n_val
    return {"success": True, "plaintext": _bytes_from_int(m).hex()}


def hastad_broadcast_attack(
    ciphertexts: Sequence[int | str], moduli: Sequence[int | str], exponent: int | str
) -> dict[str, Any]:
    """Hastad's broadcast attack: same small e, different coprime moduli."""
    cs = [_to_int(c) for c in ciphertexts]
    ns = [_to_int(n) for n in moduli]
    e_val = _to_int(exponent)

    if len(cs) < e_val or len(ns) < e_val or len(cs) != len(ns):
        return {
            "success": False,
            "error": "need at least e distinct (ciphertext, modulus) pairs",
        }

    for n in ns:
        err = _check_size(n)
        if err:
            return {"success": False, "error": err}

    # Take the first e pairs
    cs = cs[:e_val]
    ns = ns[:e_val]

    # CRT to find m^e
    product = 1
    for n in ns:
        product *= n

    total = 0
    for c_i, n_i in zip(cs, ns, strict=False):
        p_i = product // n_i
        total += c_i * p_i * pow(p_i, -1, n_i)

    m_e = total % product
    m = round(m_e ** (1 / e_val))
    # Verify integer root
    if pow(m, e_val) != m_e:
        # Try nearby integers for floating point rounding
        for delta in range(-5, 6):
            if pow(m + delta, e_val) == m_e:
                m = m + delta
                break
        else:
            return {"success": False, "error": "could not recover integer e-th root"}

    return {"success": True, "plaintext": _bytes_from_int(m).hex()}


def fermat_factor(n: int | str, max_iters: int = 100000) -> dict[str, Any]:
    """Fermat's factorization for n = p*q where p and q are close."""
    n_val = _to_int(n)
    err = _check_size(n_val)
    if err:
        return {"success": False, "error": err}

    if n_val % 2 == 0:
        return {"success": True, "p": "2", "q": str(n_val // 2)}

    a = isqrt(n_val) + 1
    b2 = a * a - n_val
    iters = 0
    while b2 >= 0 and iters < max_iters:
        b = isqrt(b2)
        if b * b == b2:
            p = a + b
            q = a - b
            return {"success": True, "p": str(p), "q": str(q)}
        a += 1
        b2 = a * a - n_val
        iters += 1
    return {"success": False, "error": "Fermat factorization did not converge"}


def pollard_p1(n: int | str, smoothness_bound: int = 100000) -> dict[str, Any]:
    """Pollard p-1 factorization for n with a smooth p-1 subgroup."""
    n_val = _to_int(n)
    err = _check_size(n_val)
    if err:
        return {"success": False, "error": err}

    if n_val % 2 == 0:
        return {"success": True, "factor": "2", "cofactor": str(n_val // 2)}

    a = 2
    for j in range(2, smoothness_bound + 1):
        a = pow(a, j, n_val)
        d = gcd(a - 1, n_val)
        if 1 < d < n_val:
            return {"success": True, "factor": str(d), "cofactor": str(n_val // d)}
    return {"success": False, "error": "Pollard p-1 did not find a factor"}


def rsa_decrypt(ciphertext: int | str, n: int | str, d: int | str) -> dict[str, Any]:
    """Raw RSA decryption: m = c^d mod n, returned as hex bytes."""
    c_val = _to_int(ciphertext)
    n_val = _to_int(n)
    d_val = _to_int(d)
    err = _check_size(n_val)
    if err:
        return {"success": False, "error": err}
    m = pow(c_val, d_val, n_val)
    return {"success": True, "plaintext": _bytes_from_int(m).hex()}
