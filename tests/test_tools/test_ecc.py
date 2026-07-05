"""Unit tests for pure-Python ECC tools."""

from src.tools.ecc import ecc_add, ecc_discrete_log_brute, ecc_scalar_mult


class TestECCAdd:
    """Tests for elliptic curve point addition."""

    def test_ecc_add_distinct_points(self):
        """Test adding two distinct points."""
        # Curve y^2 = x^3 + 2x + 2 mod 17, P=(5,1), Q=(6,3)
        result = ecc_add(2, 2, 17, (5, 1), (6, 3))
        assert result["success"]
        assert result["x"] == "10"
        assert result["y"] == "6"

    def test_ecc_add_doubling(self):
        """Test point doubling."""
        result = ecc_add(2, 2, 17, (5, 1), (5, 1))
        assert result["success"]
        assert result["x"] == "6"
        assert result["y"] == "3"

    def test_ecc_add_identity(self):
        """Test adding identity element."""
        result = ecc_add(2, 2, 17, ("inf", "inf"), (5, 1))
        assert result["success"]
        assert result["x"] == "5"
        assert result["y"] == "1"


class TestECCScalarMult:
    """Tests for elliptic curve scalar multiplication."""

    def test_ecc_scalar_mult(self):
        """Test scalar multiplication."""
        # 2 * (5,1) should equal (6,3) on the test curve.
        result = ecc_scalar_mult(2, 2, 17, (5, 1), 2)
        assert result["success"]
        assert result["x"] == "6"
        assert result["y"] == "3"

    def test_ecc_scalar_mult_zero(self):
        """Test multiplication by zero returns identity."""
        result = ecc_scalar_mult(2, 2, 17, (5, 1), 0)
        assert result["success"]
        assert result["x"] is None
        assert result["y"] is None


class TestECCDiscreteLog:
    """Tests for small-order ECC discrete log."""

    def test_ecc_discrete_log_brute(self):
        """Test brute-force discrete log on a small curve."""
        # Find k such that k*(5,1) = (6,3); answer is 2.
        result = ecc_discrete_log_brute(2, 2, 17, (5, 1), (6, 3))
        assert result["success"]
        assert result["k"] == "2"
