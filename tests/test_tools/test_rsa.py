"""Unit tests for RSA attack tools."""

from src.tools.rsa import (
    common_modulus_attack,
    fermat_factor,
    hastad_broadcast_attack,
    pollard_p1,
    rsa_decrypt,
    wiener_attack,
)


class TestWienerAttack:
    """Tests for Wiener's small private exponent attack."""

    def test_wiener_attack_success(self):
        """Test recovering a small private exponent."""
        # p=1009, q=1013, n=1022117, phi=1020096, d=17, e=180017
        result = wiener_attack(1022117, 180017)
        assert result["success"]
        assert {result["p"], result["q"]} == {"1009", "1013"}
        assert result["d"] == "17"

    def test_wiener_attack_failure(self):
        """Test failure on a non-Wiener key."""
        # n=3233, e=17, d=2753 (not small enough)
        result = wiener_attack(3233, 17)
        assert not result["success"]


class TestFermatFactor:
    """Tests for Fermat's factorization."""

    def test_fermat_factor_close_primes(self):
        """Test factoring n = p*q with close primes."""
        result = fermat_factor(1009 * 1013)
        assert result["success"]
        assert {result["p"], result["q"]} == {"1009", "1013"}

    def test_fermat_factor_even(self):
        """Test handling an even number."""
        result = fermat_factor(2 * 1013)
        assert result["success"]
        assert result["p"] == "2"
        assert result["q"] == "1013"


class TestPollardP1:
    """Tests for Pollard p-1 factorization."""

    def test_pollard_p1_smooth(self):
        """Test finding a factor with smooth p-1."""
        result = pollard_p1(10403, smoothness_bound=1000)
        assert result["success"]
        assert result["factor"] == "101"
        assert result["cofactor"] == "103"

    def test_pollard_p1_even(self):
        """Test handling an even number."""
        result = pollard_p1(2026)
        assert result["success"]
        assert result["factor"] == "2"


class TestCommonModulusAttack:
    """Tests for common modulus attack."""

    def test_common_modulus_attack(self):
        """Test recovering plaintext from two coprime public exponents."""
        n = 3233
        m = 65
        e1, e2 = 17, 27
        c1 = pow(m, e1, n)
        c2 = pow(m, e2, n)
        result = common_modulus_attack(c1, c2, e1, e2, n)
        assert result["success"]
        assert result["plaintext"] == "41"

    def test_common_modulus_not_coprime(self):
        """Test failure when exponents are not coprime."""
        result = common_modulus_attack(1, 1, 6, 9, 3233)
        assert not result["success"]


class TestHastadBroadcastAttack:
    """Tests for Hastad's broadcast attack."""

    def test_hastad_broadcast_attack(self):
        """Test recovering plaintext broadcast with e=3."""
        n1, n2, n3 = 101 * 103, 107 * 109, 113 * 127
        m = 42
        c1 = pow(m, 3, n1)
        c2 = pow(m, 3, n2)
        c3 = pow(m, 3, n3)
        result = hastad_broadcast_attack([c1, c2, c3], [n1, n2, n3], 3)
        assert result["success"]
        assert result["plaintext"] == "2a"

    def test_hastad_insufficient_ciphertexts(self):
        """Test failure with fewer ciphertexts than the exponent."""
        result = hastad_broadcast_attack([1], [2], 3)
        assert not result["success"]


class TestRSADecrypt:
    """Tests for raw RSA decryption helper."""

    def test_rsa_decrypt(self):
        """Test decrypting a ciphertext with a known private exponent."""
        n = 3233
        d = 2753
        m = 65
        c = pow(m, 17, n)
        result = rsa_decrypt(c, n, d)
        assert result["success"]
        assert result["plaintext"] == "41"
