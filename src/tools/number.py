import random
import shutil
import subprocess
from functools import lru_cache

from .models import FactorResult

# Safety limits: prevent malicious or accidental resource exhaustion.
_MAX_FACTOR_BITS = 4096
_MAX_POLLARD_RHO_ITERS = 100000


def _mul(x: int, y: int, mod: int) -> int:
    return (x * y) % mod


def _powmod(a: int, d: int, n: int) -> int:
    return pow(a, d, n)


@lru_cache(maxsize=256)
def _is_probable_prime(n: int) -> bool:
    if n < 2:
        return False
    small = [2, 3, 5, 7, 11, 13, 17, 19, 23]
    for p in small:
        if n % p == 0:
            return n == p
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
    bases = [2, 3, 5, 7, 11]
    for a in bases:
        if a % n == 0:
            continue
        x = _powmod(a, d, n)
        if x == 1 or x == n - 1:
            continue
        skip = False
        for _ in range(s - 1):
            x = _mul(x, x, n)
            if x == n - 1:
                skip = True
                break
        if skip:
            continue
        return False
    return True


def _gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return a


def _pollards_rho(n: int) -> int | None:
    """Return a non-trivial factor of n, or None if no factor is found quickly."""
    if n % 2 == 0:
        return 2
    for _restart in range(10):
        x = random.randrange(2, n - 1)
        y = x
        c = random.randrange(1, n - 1)
        d = 1
        iters = 0
        while d == 1 and iters < _MAX_POLLARD_RHO_ITERS:
            x = (_mul(x, x, n) + c) % n
            y = (_mul(y, y, n) + c) % n
            y = (_mul(y, y, n) + c) % n
            d = _gcd(abs(x - y), n)
            iters += 1
        if 1 < d < n:
            return d
    return None


def _trial_division(n: int, limit: int = 100000) -> list[int]:
    res = []
    while n % 2 == 0:
        res.append(2)
        n //= 2
    f = 3
    while f * f <= n and f <= limit:
        while n % f == 0:
            res.append(f)
            n //= f
        f += 2
        # Early termination: if n is prime, stop
        if n > 1 and n < 1000000 and _is_probable_prime(n):
            break
    if n > 1:
        res.append(n)
    return res


def _factor_recursive(n: int, out: list[int]) -> None:
    if n == 1:
        return
    if _is_probable_prime(n):
        out.append(n)
        return
    d = _pollards_rho(n)
    if d is None:
        # Could not factor quickly; treat the remainder as a single factor.
        out.append(n)
        return
    _factor_recursive(d, out)
    _factor_recursive(n // d, out)


def _factor_internal(n: int) -> list[int]:
    res = []
    td = _trial_division(n)
    for v in td:
        res.append(v)
    rem = 1
    for v in td:
        rem *= v
    m = n // rem
    if m > 1:
        _factor_recursive(m, res)
    res.sort()
    return res


def _factor_with_yafu(n: int, timeout: int = 10) -> list[int] | None:
    exe = shutil.which("yafu-x64.exe") or shutil.which("yafu.exe") or shutil.which("yafu")
    if not exe:
        return None
    try:
        p = subprocess.run([exe, f"factor({n})"], capture_output=True, text=True, timeout=timeout)
        out = (p.stdout or "") + (p.stderr or "")

        def _parse_ans_line(s: str) -> list[int] | None:
            for line in s.splitlines():
                t = line.strip()
                if t.lower().startswith("ans ="):
                    rhs = t.split("=", 1)[1].strip()
                    parts = [x.strip() for x in rhs.split("*") if x.strip()]
                    vals: list[int] = []
                    for tok in parts:
                        try:
                            vals.append(int(tok))
                        except Exception:
                            return None
                    return vals if vals else None
            return None

        def _parse_fac_lines(s: str) -> list[int] | None:
            last_group: list[int] = []
            current: list[int] = []
            for line in s.splitlines():
                t = line.strip()
                if t.startswith("P") or t.startswith("PRP"):
                    for tok in t.split():
                        try:
                            current.append(int(tok))
                        except Exception:
                            continue
                elif t.startswith("fac:"):
                    # boundary between groups
                    if current:
                        last_group = current
                        current = []
                    # collect any bare integers on fac: lines as a fallback
                    for tok in t.split():
                        try:
                            current.append(int(tok))
                        except Exception:
                            continue
                else:
                    if current:
                        last_group = current
                        current = []
            if current:
                last_group = current
            return last_group if last_group else None

        ans = _parse_ans_line(out)
        fac = _parse_fac_lines(out)
        for factors in (ans, fac):
            if factors:
                prod = 1
                for v in factors:
                    prod *= v
                if prod == n:
                    return sorted(factors)
        return None
    except Exception:
        return None


def factor_integer(
    n: int | str, prefer_yafu: bool = True, timeout: int = 10, ctx=None
) -> FactorResult:
    if isinstance(n, str):
        nn = int(n, 0)
    else:
        nn = n

    # 0 has no prime factorization; negatives factor like their absolute value.
    if nn == 0:
        return FactorResult(n="0", factors=[])
    if nn < 0:
        return FactorResult(n=str(nn), factors=["-1"] + [str(x) for x in _factor_internal(-nn)])

    if nn.bit_length() > _MAX_FACTOR_BITS:
        return FactorResult(
            n=str(nn),
            factors=[],
        )

    if prefer_yafu:
        yf = _factor_with_yafu(nn, timeout)
        if yf:
            return FactorResult(n=str(nn), factors=[str(x) for x in yf])
    res = _factor_internal(nn)
    return FactorResult(n=str(nn), factors=[str(x) for x in res])
