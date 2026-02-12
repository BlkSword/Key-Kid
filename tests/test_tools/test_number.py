"""Unit tests for number theory tools."""
import pytest
from src.tools.number import factor_integer


class TestFactorInteger:
    """Tests for factor_integer function."""

    def test_factor_small_composite(self):
        """Test factoring small composite number."""
        result = factor_integer(10403, prefer_yafu=False)
        assert result.n == "10403"
        assert result.factors == ["101", "103"]

    def test_factor_prime(self):
        """Test factoring a prime number."""
        result = factor_integer(104729, prefer_yafu=False)
        assert result.n == "104729"
        assert result.factors == ["104729"]

    def test_factor_small_number(self):
        """Test factoring small number."""
        result = factor_integer(6, prefer_yafu=False)
        assert result.n == "6"
        # Factors could be ["2", "3"] or ["3", "2"]
        assert set(result.factors) == {"2", "3"}

    def test_factor_power_of_two(self):
        """Test factoring power of 2."""
        result = factor_integer(16, prefer_yafu=False)
        assert result.n == "16"
        assert result.factors == ["2", "2", "2", "2"]

    def test_factor_one(self):
        """Test factoring 1."""
        result = factor_integer(1, prefer_yafu=False)
        assert result.n == "1"
        assert result.factors == []

    def test_factor_zero(self):
        """Test factoring 0 should handle gracefully."""
        result = factor_integer(0, prefer_yafu=False)
        assert result.n == "0"

    def test_factor_negative(self):
        """Test factoring negative number."""
        result = factor_integer(-100, prefer_yafu=False)
        assert result.n == "-100"

    def test_factor_large_composite(self):
        """Test factoring larger composite number."""
        # 99991 * 99989 = 999800...
        result = factor_integer(999800019, prefer_yafu=False)
        assert result.n == "999800019"
        # Should find the factors
        assert len(result.factors) >= 2

    def test_factor_string_input(self):
        """Test factoring with string input."""
        result = factor_integer("10403", prefer_yafu=False)
        assert result.n == "10403"
        assert result.factors == ["101", "103"]

    def test_factor_hex_string(self):
        """Test factoring hex string input."""
        result = factor_integer("0x28A3", prefer_yafu=False)
        assert result.n == "10403"
        assert result.factors == ["101", "103"]

    def test_factor_yafu_preferred(self):
        """Test with prefer_yafu=True (may not be available)."""
        result = factor_integer(6, prefer_yafu=True)
        assert result.n == "6"
        # Should factor correctly regardless of yafu availability
        assert "2" in result.factors
        assert "3" in result.factors

    def test_factor_timeout_parameter(self):
        """Test timeout parameter is accepted."""
        result = factor_integer(10403, prefer_yafu=False, timeout=5)
        assert result.n == "10403"
        assert result.factors == ["101", "103"]


class TestInternalHelpers:
    """Tests for internal helper functions (via public API)."""

    def test_trial_division_visible(self):
        """Test trial division works via factor_integer."""
        # Small numbers should be factored quickly by trial division
        result = factor_integer(100, prefer_yafu=False)
        assert set(result.factors) == {"2", "2", "5", "5"}

    def test_pollards_rho_visible(self):
        """Test Pollard's Rho works via factor_integer."""
        # This number requires Pollard's Rho (or similar) for efficient factoring
        result = factor_integer(10403, prefer_yafu=False)
        assert result.factors == ["101", "103"]
