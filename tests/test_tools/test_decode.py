"""Unit tests for decode/detection tools."""

from src.tools.decode import decode_common, detect_encoding


class TestDetectEncoding:
    """Tests for detect_encoding function."""

    def test_detect_base64(self):
        """Test detecting base64 encoding."""
        results = detect_encoding("SGVsbG8gd29ybGQ=", top_k=5)
        assert len(results) > 0
        base64_results = [r for r in results if r.name == "base64"]
        assert len(base64_results) > 0
        assert "hello world" in base64_results[0].decoded.lower()

    def test_detect_hex(self):
        """Test detecting hex encoding."""
        results = detect_encoding("48656c6c6f", top_k=5)
        hex_results = [r for r in results if r.name == "hex"]
        assert len(hex_results) > 0
        assert "hello" in hex_results[0].decoded.lower()

    def test_detect_url(self):
        """Test detecting URL encoding."""
        results = detect_encoding("Hello%20World%21", top_k=5)
        url_results = [r for r in results if r.name == "url"]
        assert len(url_results) > 0
        assert "Hello World!" in url_results[0].decoded

    def test_detect_multiple(self):
        """Test detecting multiple possible encodings."""
        # Some text could be interpreted multiple ways
        results = detect_encoding("SGVsbG8=", top_k=10)
        assert len(results) > 0

    def test_detect_top_k(self):
        """Test top_k parameter limits results."""
        results = detect_encoding("SGVsbG8gd29ybGQ=", top_k=2)
        assert len(results) <= 2

    def test_detect_scoring(self):
        """Test results are scored by English likeness."""
        results = detect_encoding("SGVsbG8gd29ybGQ=", top_k=5)
        # Results should be sorted by score
        for i in range(len(results) - 1):
            assert results[i].score >= results[i + 1].score
        # All scores should be between 0 and 1
        for r in results:
            assert 0 <= r.score <= 1


class TestDecodeCommon:
    """Tests for decode_common function."""

    def test_decode_common_base64(self):
        """Test decoding base64."""
        results = decode_common("SGVsbG8gd29ybGQ=", limit=10)
        base64_results = [r for r in results if r.name == "base64"]
        assert len(base64_results) > 0

    def test_decode_common_hex(self):
        """Test decoding hex."""
        results = decode_common("48656c6c6f", limit=10)
        hex_results = [r for r in results if r.name == "hex"]
        assert len(hex_results) > 0

    def test_decode_common_no_duplicates(self):
        """Test duplicate decodings are removed."""
        # Same text in hex - might decode to same as other encoding
        results = decode_common("48656c6c6f", limit=10)
        # Check no duplicate decoded texts
        decoded_texts = [r.decoded for r in results]
        assert len(decoded_texts) == len(set(decoded_texts))

    def test_decode_common_limit(self):
        """Test limit parameter."""
        results = decode_common("48656c6c6f", limit=3)
        assert len(results) <= 3

    def test_decode_common_sorted_by_score(self):
        """Test results are sorted by score."""
        results = decode_common("SGVsbG8gd29ybGQ=", limit=10)
        for i in range(len(results) - 1):
            assert results[i].score >= results[i + 1].score

    def test_decode_common_binary(self):
        """Test binary decoding."""
        # "Hello" in binary: 01001000 01100101 01101100 01101100 01101111
        binary_str = "0100100001100101011011000110110001101111"
        results = decode_common(binary_str, limit=10)
        binary_results = [r for r in results if r.name == "binary"]
        assert len(binary_results) > 0
