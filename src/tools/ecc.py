"""Pure-Python elliptic-curve arithmetic for prime-field short Weierstrass curves.

Provides point addition, scalar multiplication, and small-order discrete-log
helpers without requiring SageMath. All coordinates are modular integers.
"""

from typing import Any

_MAX_ECC_BITS = 2048


def _to_int(value: int | str) -> int:
    return int(value, 0) if isinstance(value, str) else value


def _check_size(n: int, name: str) -> str | None:
    if n.bit_length() > _MAX_ECC_BITS:
        return f"{name} exceeds {_MAX_ECC_BITS} bits"
    return None


def _mod_inverse(a: int, p: int) -> int:
    return pow(a, -1, p)


def _is_infinity(coord: int | str | None) -> bool:
    return coord is None or (isinstance(coord, str) and coord.lower() == "inf")


def _to_int_or_none(value: int | str | None) -> int | None:
    if value is None or (isinstance(value, str) and value.lower() == "inf"):
        return None
    return _to_int(value)


def ecc_add(
    a: int | str,
    b: int | str,
    p: int | str,
    p1: tuple[int | str | None, int | str | None],
    p2: tuple[int | str | None, int | str | None],
) -> dict[str, Any]:
    """Add two points on the curve y² = x³ + ax + b (mod p).

    The point at infinity is represented by (None, None) or ("inf", "inf").
    """
    a_val = _to_int(a)
    b_val = _to_int(b)
    p_val = _to_int(p)

    for val, name in ((a_val, "a"), (b_val, "b"), (p_val, "p")):
        err = _check_size(val, name)
        if err:
            return {"success": False, "x": None, "y": None, "error": err}

    x1 = _to_int_or_none(p1[0])
    y1 = _to_int_or_none(p1[1])
    x2 = _to_int_or_none(p2[0])
    y2 = _to_int_or_none(p2[1])

    # Point at infinity handling
    if x1 is None:
        return {
            "success": True,
            "x": str(x2) if x2 is not None else None,
            "y": str(y2) if y2 is not None else None,
            "error": None,
        }
    if x2 is None:
        return {"success": True, "x": str(x1), "y": str(y1), "error": None}

    # After the None checks above, both points are finite.
    assert x1 is not None and y1 is not None and x2 is not None and y2 is not None

    if x1 == x2 and (y1 + y2) % p_val == 0:
        return {"success": True, "x": None, "y": None, "error": None}

    if x1 == x2 and y1 == y2:
        # Point doubling
        if y1 % p_val == 0:
            return {"success": True, "x": None, "y": None, "error": None}
        m = ((3 * x1 * x1 + a_val) * _mod_inverse(2 * y1, p_val)) % p_val
    else:
        m = ((y2 - y1) * _mod_inverse(x2 - x1, p_val)) % p_val

    x3 = (m * m - x1 - x2) % p_val
    y3 = (m * (x1 - x3) - y1) % p_val
    return {"success": True, "x": str(x3), "y": str(y3), "error": None}


def ecc_scalar_mult(
    a: int | str,
    b: int | str,
    p: int | str,
    point: tuple[int | str, int | str],
    k: int | str,
) -> dict[str, Any]:
    """Compute k*P on the curve y² = x³ + ax + b (mod p) using double-and-add."""
    a_val = _to_int(a)
    b_val = _to_int(b)
    p_val = _to_int(p)
    x = _to_int(point[0])
    y = _to_int(point[1])
    k_val = _to_int(k)

    for val, name in ((a_val, "a"), (b_val, "b"), (p_val, "p"), (k_val, "k")):
        err = _check_size(val, name)
        if err:
            return {"success": False, "x": None, "y": None, "error": err}

    rx: int | None = None  # point at infinity
    ry: int | None = None
    qx: int | None = x % p_val
    qy: int | None = y % p_val
    while k_val > 0:
        if k_val & 1:
            if rx is None:
                rx, ry = qx, qy
            else:
                res = ecc_add(a_val, b_val, p_val, (rx, ry), (qx, qy))
                if res["x"] is None:
                    rx, ry = None, None
                else:
                    rx, ry = int(res["x"]), int(res["y"])
        k_val >>= 1
        if k_val:
            res = ecc_add(a_val, b_val, p_val, (qx, qy), (qx, qy))
            if res["x"] is None:
                qx, qy = None, None
            else:
                qx, qy = int(res["x"]), int(res["y"])

    return {
        "success": True,
        "x": str(rx) if rx is not None else None,
        "y": str(ry) if ry is not None else None,
        "error": None,
    }


def ecc_discrete_log_brute(
    a: int | str,
    b: int | str,
    p: int | str,
    base: tuple[int | str, int | str],
    target: tuple[int | str, int | str],
    max_steps: int = 100000,
) -> dict[str, Any]:
    """Brute-force discrete log on an elliptic curve for small-order points."""
    a_val = _to_int(a)
    b_val = _to_int(b)
    p_val = _to_int(p)
    tx = _to_int(target[0])
    ty = _to_int(target[1])

    for val, name in ((a_val, "a"), (b_val, "b"), (p_val, "p")):
        err = _check_size(val, name)
        if err:
            return {"success": False, "x": None, "error": err}

    current = (None, None)  # infinity
    for i in range(max_steps + 1):
        cx = None if current[0] is None else int(current[0])
        if cx == tx and (current[1] is None or int(current[1]) == ty):
            return {"success": True, "k": str(i), "error": None}
        res = ecc_add(a_val, b_val, p_val, current, base)
        if res["x"] is None:
            # Reached infinity without finding target
            return {"success": False, "k": None, "error": "target not found within order"}
        current = (res["x"], res["y"])
    return {"success": False, "k": None, "error": f"exceeded max_steps={max_steps}"}
