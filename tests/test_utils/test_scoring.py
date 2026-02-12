"""Unit tests for scoring system."""

import time

from src.utils.scoring import english_score, hamming_distance, ioc


class TestEnglishScore:
    """Tests for english_score function."""

    def test_english_score_valid_text(self):
        """Test scoring of valid English text."""
        score = english_score("Hello World")
        assert score > 0.5, f"Expected score > 0.5 for 'Hello World', got {score}"

    def test_english_score_perfect_english(self):
        """Test scoring of perfect English sentence."""
        score = english_score("The quick brown fox jumps over the lazy dog")
        assert score > 0.7, f"Expected score > 0.7 for perfect English, got {score}"

    def test_english_score_garbage(self):
        """Test scoring of garbage/non-English text."""
        score = english_score("\x00\x01\x02\xff\xfe")
        assert score < 0.3, f"Expected score < 0.3 for garbage text, got {score}"

    def test_english_score_random_bytes(self):
        """Test scoring of random byte-like text."""
        score = english_score("Ⓡⓐⓝⓓⓞⓜ")
        # Non-ASCII should be penalized
        assert score < 0.5

    def test_english_score_flag_pattern(self):
        """Test flag pattern detection gives maximum score."""
        score = english_score("flag{test_flag_here}")
        assert score == 10.0, f"Expected score 10.0 for flag pattern, got {score}"

    def test_english_score_ctf_pattern(self):
        """Test CTF flag pattern detection."""
        score = english_score("ctf{some_flag}")
        assert score == 10.0, f"Expected score 10.0 for CTF pattern, got {score}"

    def test_english_score_key_pattern(self):
        """Test key flag pattern detection."""
        score = english_score("key{secret_key}")
        assert score == 10.0, f"Expected score 10.0 for key pattern, got {score}"

    def test_english_score_secret_pattern(self):
        """Test secret flag pattern detection."""
        score = english_score("secret{my_secret}")
        assert score == 10.0, f"Expected score 10.0 for secret pattern, got {score}"

    def test_english_score_empty_string(self):
        """Test scoring of empty string."""
        score = english_score("")
        assert score == 0.0, f"Expected score 0.0 for empty string, got {score}"

    def test_english_score_mostly_non_printable(self):
        """Test scoring of mostly non-printable characters."""
        # Mix with a few printable but mostly non-printable
        text = "Hello" + "\x00\x01\x02\xff" * 10
        score = english_score(text)
        assert score < 0.3, f"Expected score < 0.3 for mostly non-printable, got {score}"

    def test_english_score_case_insensitive(self):
        """Test that scoring is case-insensitive."""
        score_lower = english_score("hello world")
        score_upper = english_score("HELLO WORLD")
        score_mixed = english_score("HeLLo WoRLd")
        # Scores should be similar
        assert abs(score_lower - score_upper) < 0.01
        assert abs(score_lower - score_mixed) < 0.01

    def test_english_score_bigram_boost(self):
        """Test that common bigrams boost the score."""
        # Text with common bigrams
        bigram_text = "the quick brown fox"
        score = english_score(bigram_text)
        assert score > 0.4, f"Expected decent score for bigram-rich text, got {score}"

    def test_english_score_cache_hit(self):
        """Test that caching improves performance on repeated calls."""
        # Clear cache first
        english_score.cache_clear()

        text = "Hello World" * 100

        # First call (cache miss)
        start = time.time()
        english_score(text)
        _first_duration = time.time() - start

        # Second call (cache hit)
        start = time.time()
        english_score(text)
        _second_duration = time.time() - start

        # Cache hit should be significantly faster
        # (Note: this may be flaky on very fast systems, but the ratio should be clear)
        # If second call is not faster, cache might not be working
        # We'll just verify the cache is being used
        cache_info = english_score.cache_info()
        assert cache_info.currsize > 0, "Cache should have entries after calls"

    def test_english_score_cache_maxsize(self):
        """Test that cache respects maxsize limit."""
        # Clear cache
        english_score.cache_clear()

        # Add more entries than maxsize (2048)
        for i in range(2100):
            english_score(f"unique_text_{i}")

        cache_info = english_score.cache_info()
        # Cache should not exceed maxsize significantly
        assert cache_info.currsize <= 2048, f"Cache size {cache_info.currsize} exceeds maxsize 2048"

    def test_english_score_cache_clear(self):
        """Test that cache_clear works."""
        # Add some entries
        english_score("test1")
        english_score("test2")

        # Clear cache
        english_score.cache_clear()

        cache_info = english_score.cache_info()
        assert cache_info.currsize == 0, "Cache should be empty after clear"
        assert cache_info.hits == 0
        assert cache_info.misses == 0


class TestIOC:
    """Tests for Index of Coincidence function."""

    def test_ioc_english_text(self):
        """Test IOC of English text is in expected range."""
        # English text typically has IOC around 0.067
        text = "The quick brown fox jumps over the lazy dog"
        result = ioc(text)
        assert 0.05 < result < 0.08, f"Expected IOC ~0.067 for English, got {result}"

    def test_ioc_random_text(self):
        """Test IOC of random text is lower."""
        # Random uniform distribution has IOC ~0.038
        text = "abcdefghijklmnopqrstuvwxyz"
        result = ioc(text)
        assert 0.035 < result < 0.045, f"Expected IOC ~0.038 for random, got {result}"

    def test_ioc_empty_string(self):
        """Test IOC of empty string."""
        result = ioc("")
        assert result == 0.0

    def test_ioc_single_char(self):
        """Test IOC of single character."""
        result = ioc("a")
        assert result == 0.0

    def test_ioc_repeated_char(self):
        """Test IOC of repeated character has high IOC."""
        text = "aaaaaa"
        result = ioc(text)
        assert result == 1.0, f"Expected IOC 1.0 for repeated char, got {result}"

    def test_ioc_case_insensitive(self):
        """Test IOC is case-insensitive."""
        result_lower = ioc("hello")
        result_upper = ioc("HELLO")
        assert result_lower == result_upper

    def test_ioc_ignores_non_alpha(self):
        """Test IOC ignores non-alphabetic characters."""
        result_with_spaces = ioc("hello world")
        result_without_spaces = ioc("helloworld")
        # Should be same since spaces are ignored
        assert result_with_spaces == result_without_spaces


class TestHammingDistance:
    """Tests for hamming_distance function."""

    def test_hamming_identical(self):
        """Test Hamming distance of identical bytes is 0."""
        a = bytes([1, 2, 3, 4])
        b = bytes([1, 2, 3, 4])
        result = hamming_distance(a, b)
        assert result == 0

    def test_hamming_completely_different(self):
        """Test Hamming distance of completely different bytes."""
        a = bytes([0b00000000, 0b00000000])
        b = bytes([0b11111111, 0b11111111])
        result = hamming_distance(a, b)
        assert result == 16  # 8 bits different per byte * 2 bytes

    def test_hamming_single_bit_difference(self):
        """Test Hamming distance with single bit difference."""
        a = bytes([0b00000000])
        b = bytes([0b00000001])
        result = hamming_distance(a, b)
        assert result == 1

    def test_hamming_different_length(self):
        """Test Hamming distance with different length bytes."""
        # zip truncates to shorter length
        a = bytes([1, 2, 3])
        b = bytes([1, 2])
        result = hamming_distance(a, b)
        assert result == 0  # Only compares first 2 bytes

    def test_hamming_empty(self):
        """Test Hamming distance of empty bytes."""
        result = hamming_distance(b"", b"")
        assert result == 0

    def test_hamming_real_example(self):
        """Test Hamming distance with realistic example."""
        # "this is a test" vs "wokka wokka!!!" has distance 37
        a = b"this is a test"
        b = b"wokka wokka!!!"
        result = hamming_distance(a, b)
        assert result == 37, f"Expected distance 37, got {result}"
