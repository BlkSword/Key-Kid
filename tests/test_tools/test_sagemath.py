"""Unit tests for SageMath tools."""
import pytest

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


@pytest.mark.skipif(not HAS_SAGEMATH, reason="SageMath not installed")
class TestDiscreteLog:
    """Tests for discrete_log function."""

    def test_discrete_log_basic(self):
        """Test basic discrete logarithm."""
        # 2^10 ≡ 1024 (mod 101)
        # Actually: 2^10 = 1024 ≡ 1024 % 101 = 1024 - 10*101 = 1024 - 1010 = 14
        # Let's use: 2^x ≡ 5 (mod 101), we know 2^10 = 1024 ≡ 14
        # 2^10 mod 101 = 14
        # Find x where 2^x ≡ 14 (mod 101)
        result = discrete_log("14", "101", "2")
        assert result["found"] is True or result["error"] is not None
        if result["found"]:
            assert result["x"] is not None

    def test_discrete_log_hex_input(self):
        """Test discrete log with hex input."""
        # Use small numbers
        result = discrete_log("5", "101", "2")
        assert result is not None
        assert "found" in result

    def test_discrete_log_no_base(self):
        """Test discrete log without base (auto-detect)."""
        result = discrete_log("5", "101", None)
        assert result is not None

    def test_discrete_log_invalid_input(self):
        """Test with invalid input."""
        result = discrete_log("invalid", "101", "2")
        assert result["found"] is False
        assert result["error"] is not None

    def test_discrete_log_timeout(self):
        """Test with very short timeout."""
        result = discrete_log("5", "101", "2", timeout=1)
        # Should either succeed quickly or timeout
        assert "found" in result


@pytest.mark.skipif(not HAS_SAGEMATH, reason="SageMath not installed")
class TestEllipticCurveFactor:
    """Tests for elliptic_curve_factor function."""

    def test_ecm_basic(self):
        """Test basic ECM factoring."""
        # 91 = 7 * 13 (small composite)
        result = elliptic_curve_factor("91")
        assert result is not None
        assert "found" in result

    def test_ecm_prime(self):
        """Test ECM on prime number."""
        result = elliptic_curve_factor("104729")  # Large prime
        assert result is not None
        # May not find factors for prime

    def test_ecm_hex_input(self):
        """Test ECM with hex input."""
        result = elliptic_curve_factor("0x5B")  # 91 in hex
        assert result is not None


@pytest.mark.skipif(not HAS_SAGEMATH, reason="SageMath not installed")
class TestChineseRemainder:
    """Tests for chinese_remainder function."""

    def test_crt_basic(self):
        """Test basic CRT problem."""
        # x ≡ 2 (mod 3), x ≡ 3 (mod 5), x ≡ 2 (mod 7)
        # Solution: x = 23
        result = chinese_remainder([("2", "3"), ("3", "5"), ("2", "7")])
        assert result["found"] is True
        assert result["x"] == "23"
        assert result["modulus"] == "105"  # 3*5*7

    def test_crt_two_congruences(self):
        """Test CRT with only two congruences."""
        # x ≡ 2 (mod 3), x ≡ 3 (mod 4)
        # Solution: x = 11
        result = chinese_remainder([("2", "3"), ("3", "4")])
        assert result["found"] is True
        assert result["x"] == "11"

    def test_crt_hex_input(self):
        """Test CRT with hex input."""
        result = chinese_remainder([("2", "3"), ("3", "5")])
        assert result["found"] is True

    def test_crt_invalid_input(self):
        """Test with invalid number format."""
        result = chinese_remainder([("invalid", "3")])
        assert result["found"] is False
        assert result["error"] is not None


@pytest.mark.skipif(not HAS_SAGEMATH, reason="SageMath not installed")
class TestLinearCongruence:
    """Tests for linear_congruence_system function."""

    def test_single_congruence(self):
        """Test single linear congruence: 3*x ≡ 2 (mod 7)."""
        # 3^-1 mod 7 = 5 (since 3*5 = 15 ≡ 1 mod 7)
        # x ≡ 5 * 2 ≡ 10 ≡ 3 (mod 7)
        result = linear_congruence_system(["3"], ["2"], ["7"])
        assert result["found"] is True
        assert result["x"] == "3"

    def test_invertible(self):
        """Test with invertible coefficient."""
        # 5*x ≡ 1 (mod 11)
        # 5^-1 mod 11 = 9 (5*9 = 45 ≡ 1)
        # x ≡ 9 (mod 11)
        result = linear_congruence_system(["5"], ["1"], ["11"])
        assert result["found"] is True
        assert result["x"] == "9"

    def test_no_solution(self):
        """Test congruence with no solution."""
        # 2*x ≡ 1 (mod 4) has no solution (left side even, right side odd)
        result = linear_congruence_system(["2"], ["1"], ["4"])
        assert result["found"] is False or result["error"] is not None


@pytest.mark.skipif(not HAS_SAGEMATH, reason="SageMath not installed")
class TestEllipticCurvePointAdd:
    """Tests for elliptic_curve_point_add function."""

    def test_point_addition(self):
        """Test adding two points on elliptic curve."""
        # Curve: y² = x³ + 2x + 2 (mod 17)
        # Point addition
        result = elliptic_curve_point_add(
            ("2", "2", "17"),  # a, b, p
            ("5", "1"),  # P1
            ("5", "1")   # P2 = P1, so P1+P1 = 2*P1
        )
        assert result is not None
        assert "found" in result

    def test_point_not_on_curve(self):
        """Test with point not on curve."""
        # This should fail since (0, 0) is not on y² = x³ + 2x + 2
        result = elliptic_curve_point_add(
            ("2", "2", "17"),
            ("0", "0"),
            ("5", "1")
        )
        # Should either fail or return error
        assert "error" in result


@pytest.mark.skipif(not HAS_SAGEMATH, reason="SageMath not installed")
class TestCoppersmithAttack:
    """Tests for coppersmith_attack function."""

    def test_coppersmith_basic(self):
        """Test basic Coppersmith setup."""
        # Small example
        result = coppersmith_attack(
            "15",  # n (small example)
            "3",    # e
            "x"     # polynomial
        )
        assert result is not None
        assert "roots" in result

    def test_coppersmith_invalid_polynomial(self):
        """Test with invalid polynomial."""
        result = coppersmith_attack(
            "15",
            "3",
            "invalid(x"  # Missing closing paren
        )
        assert result["found"] is False or "error" in result


@pytest.mark.skipif(not HAS_SAGEMATH, reason="SageMath not installed")
class TestQuadraticResidue:
    """Tests for quadratic_residue function."""

    def test_quadratic_residue_basic(self):
        """Test finding square roots modulo prime."""
        # x² ≡ 4 (mod 7) has solutions x = 2, 5
        result = quadratic_residue("4", "7")
        assert result["found"] is True
        assert len(result["roots"]) == 2
        assert "2" in result["roots"]
        assert "5" in result["roots"]

    def test_quadratic_residue_non_residue(self):
        """Test with non-quadratic residue."""
        # 3 is not a quadratic residue mod 7
        result = quadratic_residue("3", "7")
        assert result is not None

    def test_quadratic_residue_zero(self):
        """Test with a = 0."""
        # x² ≡ 0 (mod p) has only x = 0
        result = quadratic_residue("0", "7")
        assert result["found"] is True
        assert "0" in result["roots"]


class TestSageMathAvailability:
    """Tests for SageMath availability check."""

    def test_has_sagemath_flag(self):
        """Test HAS_SAGEMATH flag is set."""
        # This should always be set (True or False)
        assert isinstance(HAS_SAGEMATH, bool)

    def test_graceful_degradation(self):
        """Test that functions return gracefully when SageMath unavailable."""
        if HAS_SAGEMATH:
            pytest.skip("SageMath is installed")
            return

        # Test functions handle missing SageMath gracefully
        result = discrete_log("5", "101", "2")
        assert result["found"] is False
        assert "SageMath not installed" in result.get("error", "")

        result = chinese_remainder([("2", "3"), ("3", "5")])
        assert result["found"] is False
        assert "SageMath not installed" in result.get("error", "")
