"""SageMath-based advanced cryptography tools.

This module provides tools for advanced cryptography problems using SageMath,
including discrete logarithms, elliptic curves, lattice reduction, etc.

SageMath is a free open-source mathematics software system based on Python.
Install from: https://www.sagemath.org/
"""
import shutil
import subprocess
from typing import Any

# Check if SageMath is available
_SAGE_BINARY = (
    shutil.which("sage")
    or shutil.which("sage.exe")
    or shutil.which("sagemath")
)
HAS_SAGEMATH = _SAGE_BINARY is not None


def _run_sage(code: str, timeout: int = 30) -> str | None:
    """Run SageMath code and return output.

    Args:
        code: SageMath code to execute
        timeout: Timeout in seconds

    Returns:
        stdout output, or None if SageMath is not available or command fails
    """
    if not HAS_SAGEMATH:
        return None

    try:
        result = subprocess.run(
            [_SAGE_BINARY, "--python", "-c", code],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.stdout
    except subprocess.TimeoutExpired:
        return None
    except Exception:
        return None


def discrete_log(g: str, p: str, base: str | None = None, method: str = "auto", timeout: int = 60) -> dict[str, Any]:
    """Solve discrete logarithm problem: find x such that base^x ≡ g (mod p).

    Uses SageMath's built-in discrete_log which employs:
    - Baby-step giant-step for medium-sized problems
    - Pollard's rho for larger problems
    - Pohlig-Hellman for smooth prime factors

    Args:
        g: Target value (decimal or hex with 0x prefix)
        p: Prime modulus (decimal or hex with 0x prefix)
        base: Generator/base (defaults to smallest primitive root if None)
        method: Solver method - "auto", "bsgs", "ph", "rho"
        timeout: Timeout in seconds (default 60)

    Returns:
        Dict with keys:
            - "found": bool - whether solution was found
            - "x": str | None - the discrete logarithm
            - "method": str - method used
            "time": float | None - time taken
            - "error": str | None - error message if failed

    Example:
        >>> # Solve: 2^x ≡ 5 (mod 101)
        >>> discrete_log("5", "101", "2")
        {"found": True, "x": "10", "method": "bsgs", ...}
    """
    if not HAS_SAGEMATH:
        return {
            "found": False,
            "x": None,
            "method": method,
            "error": "SageMath not installed. Install from https://www.sagemath.org/"
        }

    # Parse inputs
    try:
        g_val = int(g, 0) if isinstance(g, str) else g
        p_val = int(p, 0) if isinstance(p, str) else p
        base_val = int(base, 0) if base else None
    except ValueError:
        return {
            "found": False,
            "x": None,
            "method": method,
            "error": "Invalid number format (use decimal or 0x... for hex)"
        }

    # Build SageMath code
    if base_val is None:
        # Let SageMath find a generator
        sage_code = f"""
import time
p = {p_val}
g = {g_val}
F = GF(p)
start = time.time()
try:
    x = discrete_log(F(g), F.multiplicative_generator(), method='{method}')
    elapsed = time.time() - start
    print(f"RESULT: {{x}}")
    print(f"TIME: {{elapsed}}")
except Exception as e:
    print(f"ERROR: {{str(e)}}")
"""
    else:
        sage_code = f"""
import time
p = {p_val}
g = {g_val}
base = {base_val}
F = GF(p)
start = time.time()
try:
    x = discrete_log(F(g), F(base), method='{method}')
    elapsed = time.time() - start
    print(f"RESULT: {{x}}")
    print(f"TIME: {{elapsed}}")
except Exception as e:
    print(f"ERROR: {{str(e)}}")
"""

    output = _run_sage(sage_code, timeout)

    if output is None:
        return {
            "found": False,
            "x": None,
            "method": method,
            "error": f"SageMath execution failed or timeout (> {timeout}s)"
        }

    # Parse output
    result = {"found": False, "x": None, "method": method, "time": None, "error": None}

    for line in output.splitlines():
        if line.startswith("RESULT:"):
            result["found"] = True
            result["x"] = line.split(":", 1)[1].strip()
        elif line.startswith("TIME:"):
            try:
                result["time"] = float(line.split(":", 1)[1].strip())
            except ValueError:
                pass
        elif line.startswith("ERROR:"):
            result["error"] = line.split(":", 1)[1].strip()

    return result


def elliptic_curve_factor(n: str, a: str = "0", b: str = "0", timeout: int = 120) -> dict[str, Any]:
    """Factor integer using Lenstra's Elliptic Curve Method (ECM).

    ECM is effective for finding medium-sized factors (20-60 digits).

    Args:
        n: Integer to factor (decimal or hex with 0x prefix)
        a: Elliptic curve parameter a (default 0, uses random curves)
        b: Elliptic curve parameter b (default 0, uses random curves)
        timeout: Timeout in seconds (default 120)

    Returns:
        Dict with keys:
            - "found": bool - whether factor was found
            - "factor": str | None - non-trivial factor found
            - "remaining": str | None - cofactor
            - "error": str | None - error message

    Example:
        >>> # Find factor of n using ECM
        >>> elliptic_curve_factor("1234567890123456789")
        {"found": True, "factor": "1234567", ...}
    """
    if not HAS_SAGEMATH:
        return {
            "found": False,
            "factor": None,
            "error": "SageMath not installed"
        }

    try:
        n_val = int(n, 0) if isinstance(n, str) else n
    except ValueError:
        return {
            "found": False,
            "factor": None,
            "error": "Invalid number format"
        }

    sage_code = f"""
n = {n_val}
try:
    # Use SageMath's built-in ECM
    from sage.libs.pari import pari
    result = pari('ecm({n})')
    if result and result != n:
        print(f"FACTOR: {{result}}")
        print(f"REMAINING: {{n // result}}")
    else:
        print("NO_FACTOR")
except Exception as e:
    print(f"ERROR: {{str(e)}}")
"""

    output = _run_sage(sage_code, timeout)

    if output is None:
        return {
            "found": False,
            "factor": None,
            "error": f"SageMath execution failed or timeout (> {timeout}s)"
        }

    result = {"found": False, "factor": None, "remaining": None, "error": None}

    for line in output.splitlines():
        if line.startswith("FACTOR:"):
            result["found"] = True
            result["factor"] = line.split(":", 1)[1].strip()
        elif line.startswith("REMAINING:"):
            result["remaining"] = line.split(":", 1)[1].strip()
        elif line.startswith("ERROR:"):
            result["error"] = line.split(":", 1)[1].strip()
        elif line.startswith("NO_FACTOR"):
            result["error"] = "No factor found with ECM"

    return result


def chinese_remainder(congruences: list[tuple[str, str]], timeout: int = 30) -> dict[str, Any]:
    """Solve system of linear congruences using Chinese Remainder Theorem.

    Find x such that:
        x ≡ a1 (mod n1)
        x ≡ a2 (mod n2)
        ...

    Args:
        congruences: List of (remainder, modulus) tuples as strings
        timeout: Timeout in seconds

    Returns:
        Dict with keys:
            - "found": bool - whether solution exists
            - "x": str | None - solution modulo N
            - "modulus": str | None - product of all moduli
            - "error": str | None - error if no solution

    Example:
        >>> # Solve: x ≡ 2 (mod 3), x ≡ 3 (mod 5), x ≡ 2 (mod 7)
        >>> chinese_remainder([("2", "3"), ("3", "5"), ("2", "7")])
        {"found": True, "x": "23", "modulus": "105"}
    """
    if not HAS_SAGEMATH:
        return {
            "found": False,
            "x": None,
            "modulus": None,
            "error": "SageMath not installed"
        }

    # Build congruence list
    cong_list = []
    for rem, mod in congruences:
        try:
            rem_val = int(rem, 0)
            mod_val = int(mod, 0)
            cong_list.append((rem_val, mod_val))
        except ValueError:
            return {
                "found": False,
                "x": None,
                "modulus": None,
                "error": f"Invalid number format: {rem}, {mod}"
            }

    sage_code = f"""
congruences = {cong_list}
try:
    from sage.all import crt
    result = crt([c[1] for c in congruences], [c[0] for c in congruences])
    if result is not None:
        x, N = result
        print(f"X: {{x}}")
        print(f"MODULUS: {{N}}")
    else:
        print("NO_SOLUTION")
except Exception as e:
    print(f"ERROR: {{str(e)}}")
"""

    output = _run_sage(sage_code, timeout)

    if output is None:
        return {
            "found": False,
            "x": None,
            "modulus": None,
            "error": "SageMath execution failed"
        }

    result = {"found": False, "x": None, "modulus": None, "error": None}

    for line in output.splitlines():
        if line.startswith("X:"):
            result["found"] = True
            result["x"] = line.split(":", 1)[1].strip()
        elif line.startswith("MODULUS:"):
            result["modulus"] = line.split(":", 1)[1].strip()
        elif line.startswith("ERROR:"):
            result["error"] = line.split(":", 1)[1].strip()
        elif line.startswith("NO_SOLUTION"):
            result["error"] = "No solution exists (moduli not coprime)"

    return result


def linear_congruence_system(coefficients: list[str], remainders: list[str], moduli: list[str], timeout: int = 30) -> dict[str, Any]:
    """Solve system of linear congruences: Σ(ai * xi) ≡ bi (mod ni).

    Args:
        coefficients: List of coefficient strings [a1, a2, ...]
        remainders: List of remainder strings [b1, b2, ...]
        moduli: List of modulus strings [n1, n2, ...]
        timeout: Timeout in seconds

    Returns:
        Dict with solution status

    Example:
        >>> # Solve: 3*x ≡ 2 (mod 7)
        >>> linear_congruence_system(["3"], ["2"], ["7"])
    """
    if not HAS_SAGEMATH:
        return {"found": False, "error": "SageMath not installed"}

    try:
        coeffs = [int(c, 0) for c in coefficients]
        rems = [int(r, 0) for r in remainders]
        mods = [int(m, 0) for m in moduli]
    except ValueError:
        return {"found": False, "error": "Invalid number format"}

    sage_code = f"""
import time
coeffs = {coeffs}
rems = {rems}
mods = {mods}

try:
    solutions = []
    from sage.all import matrix

    # Solve each congruence independently for single variable case
    if len(coeffs) == 1 and len(rems) == 1 and len(mods) == 1:
        a, b, n = coeffs[0], rems[0], mods[0]
        # Solve a*x ≡ b (mod n)
        from sage.all import inverse_mod
        try:
            if a % n == 0:
                if b % n == 0:
                    print(f"X: ANY")
                else:
                    print(f"NO_SOLUTION")
            else:
                inv_a = inverse_mod(a, n)
                if inv_a is not None:
                    x = (inv_a * b) % n
                    print(f"X: {{x}}")
                    print(f"MODULUS: {{n}}")
                else:
                    print(f"NO_SOLUTION")
        except Exception as e:
            print(f"ERROR: {{str(e)}}")
    else:
        print("ERROR: Multi-variable systems not yet supported")
except Exception as e:
    print(f"ERROR: {{str(e)}}")
"""

    output = _run_sage(sage_code, timeout)

    if output is None:
        return {"found": False, "error": "SageMath execution failed"}

    result = {"found": False, "x": None, "modulus": None, "error": None}

    for line in output.splitlines():
        if line.startswith("X:"):
            val = line.split(":", 1)[1].strip()
            if val == "ANY":
                result["found"] = True
                result["x"] = "any"
            else:
                result["found"] = True
                result["x"] = val
        elif line.startswith("MODULUS:"):
            result["modulus"] = line.split(":", 1)[1].strip()
        elif line.startswith("ERROR:"):
            result["error"] = line.split(":", 1)[1].strip()
        elif line.startswith("NO_SOLUTION"):
            result["error"] = "No solution exists"

    return result


def elliptic_curve_point_add(curve_params: tuple[str, str, str], p: str, p1: tuple[str, str], p2: tuple[str, str], timeout: int = 30) -> dict[str, Any]:
    """Add two points on an elliptic curve: y² ≡ x³ + ax + b (mod p).

    Args:
        curve_params: (a, b, p) - curve parameters and modulus
        p: First point (x1, y1)
        p2: Second point (x2, y2)
        timeout: Timeout in seconds

    Returns:
        Dict with resulting point coordinates
    """
    if not HAS_SAGEMATH:
        return {"found": False, "x": None, "y": None, "error": "SageMath not installed"}

    try:
        a_val = int(curve_params[0], 0)
        b_val = int(curve_params[1], 0)
        p_val = int(p, 0)
        x1_val = int(p1[0], 0)
        y1_val = int(p1[1], 0)
        x2_val = int(p2[0], 0)
        y2_val = int(p2[1], 0)
    except ValueError:
        return {"found": False, "x": None, "y": None, "error": "Invalid number format"}

    sage_code = f"""
p = {p_val}
a = {a_val}
b = {b_val}

E = EllipticCurve(GF(p), [a, b])
P1 = E({x1_val}, {y1_val})
P2 = E({x2_val}, {y2_val})

try:
    P3 = P1 + P2
    print(f"X: {{P3.xy()[0]}}")
    print(f"Y: {{P3.xy()[1]}}")
except Exception as e:
    print(f"ERROR: {{str(e)}}")
"""

    output = _run_sage(sage_code, timeout)

    if output is None:
        return {"found": False, "x": None, "y": None, "error": "SageMath execution failed"}

    result = {"found": False, "x": None, "y": None, "error": None}

    for line in output.splitlines():
        if line.startswith("X:"):
            result["found"] = True
            result["x"] = line.split(":", 1)[1].strip()
        elif line.startswith("Y:"):
            result["y"] = line.split(":", 1)[1].strip()
        elif line.startswith("ERROR:"):
            result["error"] = line.split(":", 1)[1].strip()

    return result


def coppersmith_attack(n: str, e: str, polynomial: str, beta: float = 0.5, timeout: int = 120) -> dict[str, Any]:
    """Coppersmith's method for finding small roots of modular polynomials.

    Useful for attacks on RSA with small exponent or low-exponent attacks.

    Args:
        n: RSA modulus
        e: Public exponent
        polynomial: Polynomial in x (e.g., "x^3 + 4*x^2 + x")
        beta: Size bound of root (0 < beta < 1)
        timeout: Timeout in seconds

    Returns:
        Dict with found small roots
    """
    if not HAS_SAGEMATH:
        return {"found": False, "roots": [], "error": "SageMath not installed"}

    try:
        n_val = int(n, 0)
        e_val = int(e, 0)
    except ValueError:
        return {"found": False, "roots": [], "error": "Invalid number format"}

    sage_code = f"""
n = {n_val}
e = {e_val}
beta = {beta}

P.<x> = PolynomialRing(ZZ)
f = {polynomial}

try:
    from sage.all import small_roots
    roots = f.small_roots(X={n_val}^beta)
    if roots:
        print(f"ROOTS: {{[str(r[0]) for r in roots]}}")
    else:
        print("NO_ROOTS")
except Exception as e:
    print(f"ERROR: {{str(e)}}")
"""

    output = _run_sage(sage_code, timeout)

    if output is None:
        return {"found": False, "roots": [], "error": "SageMath execution failed"}

    result = {"found": False, "roots": [], "error": None}

    for line in output.splitlines():
        if line.startswith("ROOTS:"):
            roots_str = line.split(":", 1)[1].strip()
            # Parse list representation
            import ast
            try:
                result["roots"] = ast.literal_eval(roots_str)
                result["found"] = len(result["roots"]) > 0
            except (ValueError, SyntaxError):
                pass
        elif line.startswith("ERROR:"):
            result["error"] = line.split(":", 1)[1].strip()
        elif line.startswith("NO_ROOTS"):
            result["roots"] = []

    return result


def quadratic_residue(a: str, p: str, timeout: int = 30) -> dict[str, Any]:
    """Find square roots of a modulo prime p: solve x² ≡ a (mod p).

    Uses Tonelli-Shanks algorithm for prime moduli.

    Args:
        a: The quadratic residue
        p: Prime modulus
        timeout: Timeout in seconds

    Returns:
        Dict with square roots
    """
    if not HAS_SAGEMATH:
        return {"found": False, "roots": [], "error": "SageMath not installed"}

    try:
        a_val = int(a, 0)
        p_val = int(p, 0)
    except ValueError:
        return {"found": False, "roots": [], "error": "Invalid number format"}

    sage_code = f"""
a = {a_val}
p = {p_val}

F = GF(p)

try:
    x = F(a).sqrt(all=True)
    print(f"ROOTS: {{[str(r) for r in x]}}")
except Exception as e:
    print(f"ERROR: {{str(e)}}")
"""

    output = _run_sage(sage_code, timeout)

    if output is None:
        return {"found": False, "roots": [], "error": "SageMath execution failed"}

    result = {"found": False, "roots": [], "error": None}

    for line in output.splitlines():
        if line.startswith("ROOTS:"):
            roots_str = line.split(":", 1)[1].strip()
            import ast
            try:
                result["roots"] = ast.literal_eval(roots_str)
                result["found"] = len(result["roots"]) > 0
            except (ValueError, SyntaxError):
                pass
        elif line.startswith("ERROR:"):
            result["error"] = line.split(":", 1)[1].strip()

    return result
