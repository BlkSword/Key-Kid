"""Unit tests for classic cipher tools."""
from src.tools.classic import (
    affine_break,
    caesar_break,
    playfair_break,
    rail_fence_break,
    transposition_break,
    vigenere_break,
)


class TestCaesarBreak:
    """Tests for caesar_break function."""

    def test_caesar_break_basic(self):
        """Test breaking Caesar cipher."""
        result = caesar_break("Uryyb Jbeyq")
        assert result.algorithm == "Caesar"
        assert result.key == "13"
        assert "hello world" in result.plaintext.lower()

    def test_caesar_break_rot13(self):
        """Test ROT13 specifically."""
        result = caesar_break("Guvf vf n frperg")
        assert result.key == "13"
        assert "this is a secret" in result.plaintext.lower()

    def test_caesar_break_preserves_non_alpha(self):
        """Test non-alphabetic characters are preserved."""
        result = caesar_break("Uryyb123!")
        assert "123" in result.plaintext
        assert "!" in result.plaintext


class TestVigenereBreak:
    """Tests for vigenere_break function."""

    def test_vigenere_break_basic(self):
        """Test breaking Vigenère cipher."""
        results = vigenere_break("Lxfopvefrnhr", max_key_len=8, top_k=1)
        assert len(results) == 1
        assert results[0].algorithm == "Vigenere"
        assert "testing" in results[0].plaintext.lower()

    def test_vigenere_break_top_k(self):
        """Test top_k parameter limits results."""
        results = vigenere_break("Lxfopvefrnhr", max_key_len=8, top_k=3)
        assert len(results) == 3

    def test_vigenere_break_key_length(self):
        """Test max_key_len parameter."""
        results = vigenere_break("Lxfopvefrnhr", max_key_len=5, top_k=1)
        assert len(results) == 1
        # Key length should be <= 5
        assert len(results[0].key) <= 5


class TestAffineBreak:
    """Tests for affine_break function."""

    def test_affine_break_basic(self):
        """Test breaking affine cipher."""
        results = affine_break("ZEBBW", top_k=1)
        assert len(results) == 1
        assert "attack" in results[0].plaintext.lower()

    def test_affine_break_top_k(self):
        """Test top_k parameter."""
        results = affine_break("ZEBBW", top_k=5)
        assert len(results) == 5

    def test_affine_break_key_format(self):
        """Test key is formatted as 'a=...,b=...'."""
        results = affine_break("ZEBBW", top_k=1)
        assert "a=" in results[0].key
        assert "b=" in results[0].key


class TestRailFenceBreak:
    """Tests for rail_fence_break function."""

    def test_rail_fence_break_basic(self):
        """Test breaking Rail Fence cipher."""
        results = rail_fence_break("WECRLTEERDSOEEFEAOCAIVDEN", max_rails=5, top_k=1)
        assert len(results) == 1
        assert results[0].algorithm == "RailFence"
        assert "discovered" in results[0].plaintext.lower()
        assert results[0].key == "3"  # 3 rails

    def test_rail_fence_break_top_k(self):
        """Test top_k parameter."""
        results = rail_fence_break("WECRLTEERDSOEEFEAOCAIVDEN", max_rails=5, top_k=3)
        assert len(results) == 3

    def test_rail_fence_break_max_rails(self):
        """Test max_rails parameter."""
        results = rail_fence_break("WECRLTEERDSOEEFEAOCAIVDEN", max_rails=3, top_k=1)
        assert len(results) == 1
        # Key (rail count) should be <= 3
        assert int(results[0].key) <= 3


class TestTranspositionBreak:
    """Tests for transposition_break function."""

    def test_transposition_break_basic(self):
        """Test breaking columnar transposition."""
        # This is a simple example - results may vary
        results = transposition_break("TEST", max_key_len=3, top_k=1)
        assert len(results) == 1
        assert results[0].algorithm == "Transposition"

    def test_transposition_break_key_format(self):
        """Test key is a permutation."""
        results = transposition_break("TEST", max_key_len=3, top_k=1)
        # Key should be in format like '0-1-2' or '1-0-2'
        assert "-" in results[0].key


class TestPlayfairBreak:
    """Tests for playfair_break function."""

    def test_playfair_break_without_key(self):
        """Test without key hint returns empty result."""
        results = playfair_break("TEST", key_hint=None, top_k=1)
        assert len(results) == 1
        assert results[0].plaintext == ""

    def test_playfair_break_with_key(self):
        """Test with key hint."""
        results = playfair_break("TEST", key_hint="test", top_k=1)
        assert len(results) == 1
        assert results[0].algorithm == "Playfair"
        assert results[0].key == "test"
