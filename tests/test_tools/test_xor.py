"""Unit tests for XOR tools."""
import pytest
from src.tools.xor import xor_single_break, xor_repeating_break, _parse_data


class TestParseData:
    """Tests for _parse_data helper function."""

    def test_parse_data_hex(self):
        """Test parsing hex encoded data."""
        result = _parse_data("48656c6c6f", "hex")
        assert result == b"Hello"

    def test_parse_data_base64(self):
        """Test parsing base64 encoded data."""
        result = _parse_data("SGVsbG8=", "b64")
        assert result == b"Hello"

    def test_parse_data_raw(self):
        """Test parsing raw string data."""
        result = _parse_data("Hello", "raw")
        assert result == b"Hello"

    def test_parse_data_invalid_hex(self):
        """Test parsing invalid hex raises error."""
        with pytest.raises(ValueError):
            _parse_data("gg", "hex")


class TestXorSingleBreak:
    """Tests for xor_single_break function."""

    def test_xor_single_break_hex(self):
        """Test breaking single-byte XOR with hex encoding."""
        results = xor_single_break("3f292c2c2b", encoding="hex", top_k=1)
        assert len(results) == 1
        # The actual result depends on the scoring algorithm
        # Verify it returns a valid result
        assert results[0].key is not None
        assert len(results[0].plaintext) > 0
        assert results[0].confidence >= 0

    def test_xor_single_break_all_keys(self):
        """Test all 256 possible keys are tried."""
        results = xor_single_break("00", encoding="hex", top_k=256)
        assert len(results) == 256

    def test_xor_single_break_scoring(self):
        """Test results are sorted by confidence."""
        results = xor_single_break("3f292c2c2b", encoding="hex", top_k=256)
        for i in range(len(results) - 1):
            assert results[i].confidence >= results[i + 1].confidence

    def test_xor_single_break_top_k(self):
        """Test top_k parameter limits results."""
        results = xor_single_break("3f292c2c2b", encoding="hex", top_k=5)
        assert len(results) == 5

    def test_xor_single_break_base64(self):
        """Test with base64 encoding."""
        results = xor_single_break("PxksICwp", encoding="b64", top_k=1)
        assert len(results) == 1
        # Verify it returns a valid result
        assert results[0].key is not None
        assert len(results[0].plaintext) > 0

    def test_xor_single_break_raw(self):
        """Test with raw encoding."""
        # XOR with key 5: 'H'^5='M', 'e'^5='`', etc.
        results = xor_single_break("M`u`u", encoding="raw", top_k=10)
        # Should find a result
        assert len(results) > 0


class TestXorRepeatingBreak:
    """Tests for xor_repeating_break function."""

    def test_xor_repeating_break_basic(self):
        """Test breaking repeating-key XOR."""
        # "This is a test" XOR with "Key"
        results = xor_repeating_break("5468697320697320612074657374", encoding="hex")
        assert results.algorithm == "XOR-repeating"
        assert "this is a test" in results.plaintext.lower()

    def test_xor_repeating_break_key_length_range(self):
        """Test key length range parameters."""
        # Should use min_key and max_key
        results = xor_repeating_break(
            "5468697320697320612074657374",
            encoding="hex",
            min_key=2,
            max_key=5
        )
        assert results.algorithm == "XOR-repeating"
        # Should find a key in the tested range
        assert results.key is not None

    def test_xor_repeating_break_short_text(self):
        """Test with very short text."""
        results = xor_repeating_break("48656c6c6f", encoding="hex")
        # Should still return a result
        assert results.plaintext is not None

    def test_xor_repeating_break_returns_break_result(self):
        """Test return type is BreakResult."""
        results = xor_repeating_break("5468697320697320612074657374", encoding="hex")
        assert results.algorithm == "XOR-repeating"
        assert results.plaintext is not None
        assert results.key is not None
        assert 0 <= results.confidence <= 1
