import pytest
from text2digits.text_processing_helpers import bigram_similarity


class TestBigramSimilarity:
    def test_identical_single_char(self):
        """Two identical single-character strings have no bigrams; should return 1.0."""
        assert bigram_similarity("a", "a") == 1.0

    def test_different_single_chars(self):
        """Two different single-character strings have no bigrams; should return 0.0."""
        assert bigram_similarity("a", "b") == 0.0

    def test_single_char_vs_longer(self):
        """One single-char string vs. a longer one: no bigrams in common, returns 0.0."""
        assert bigram_similarity("a", "ab") == 0.0

    def test_identical_strings(self):
        assert bigram_similarity("hello", "hello") == 1.0

    def test_completely_different(self):
        assert bigram_similarity("abc", "xyz") == 0.0

    def test_partial_overlap(self):
        similarity = bigram_similarity("night", "nightly")
        assert 0.0 < similarity < 1.0

    def test_case_insensitive(self):
        assert bigram_similarity("Hello", "hello") == 1.0

    def test_empty_strings(self):
        """Both empty → no bigrams → identical empty strings → 1.0."""
        assert bigram_similarity("", "") == 1.0

    def test_one_empty_one_nonempty(self):
        assert bigram_similarity("", "a") == 0.0
