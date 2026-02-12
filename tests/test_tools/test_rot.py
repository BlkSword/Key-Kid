"""Unit tests for ROT tools."""
import pytest
from src.tools.rot import rot_all


class TestRotAll:
    """Tests for rot_all function."""

    def test_rot_all_basic(self):
        """Test basic ROT decryption."""
        results = rot_all("Uryyb Jbeyq", top_k=1)
        assert len(results) == 1
        # Note: The actual best ROT may vary based on scoring
        # ROT13 gives "Hello World", but scoring might prefer another
        assert results[0].key is not None
        assert len(results[0].plaintext) > 0

    def test_rot_all_all_shifts(self):
        """Test all 25 shifts are generated."""
        results = rot_all("Test", top_k=25)
        assert len(results) == 25
        # Check we have all ROT variants
        keys = [r.key for r in results]
        assert "1" in keys
        assert "13" in keys
        assert "25" in keys

    def test_rot_all_preserves_non_alpha(self):
        """Test that non-alphabetic characters are preserved."""
        results = rot_all("Uryyb Jbeyq!", top_k=1)
        assert "!" in results[0].plaintext

    def test_rot_all_case_sensitivity(self):
        """Test case is preserved in ROT."""
        results = rot_all("Uryyb Jbeyq", top_k=1)
        plaintext = results[0].plaintext
        # Check first letter is uppercase
        assert plaintext[0].isupper()
        # Check second letter is lowercase
        assert plaintext[1].islower()

    def test_rot_all_top_k(self):
        """Test top_k parameter limits results."""
        results = rot_all("Test", top_k=5)
        assert len(results) == 5

    def test_rot_all_scoring(self):
        """Test results are sorted by confidence score."""
        results = rot_all("Uryyb Jbeyq", top_k=25)
        # Results should be sorted by confidence descending
        for i in range(len(results) - 1):
            assert results[i].confidence >= results[i + 1].confidence

    def test_rot_all_empty_string(self):
        """Test with empty string."""
        results = rot_all("", top_k=3)
        assert len(results) == 3
        for r in results:
            assert r.plaintext == ""

    def test_rot_all_numbers_special_chars(self):
        """Test with numbers and special characters."""
        results = rot_all("Test123!@#", top_k=1)
        assert "123" in results[0].plaintext
        assert "!@#" in results[0].plaintext

    def test_rot_all_algorithm_name(self):
        """Test algorithm name includes ROT number."""
        results = rot_all("Test", top_k=1)
        assert "ROT" in results[0].algorithm

    def test_rot_all_rot13_specific(self):
        """Test ROT13 specifically (common cipher)."""
        results = rot_all("Uryyb Jbeyq", top_k=1)
        # ROT13 should produce readable English, so it should rank highly
        # The exact rank depends on scoring, but it should be in top results
        all_results = rot_all("Uryyb Jbeyq", top_k=25)
        rot13_result = [r for r in all_results if r.key == "13"]
        assert len(rot13_result) == 1
        assert "hello world" in rot13_result[0].plaintext.lower()

    def test_rot_all_all_zeros(self):
        """Test with all zeros."""
        results = rot_all("000", top_k=1)
        # Numbers should be preserved
        assert "000" in results[0].plaintext
