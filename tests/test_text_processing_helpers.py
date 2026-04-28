from text2digits.text_processing_helpers import bigram_similarity, find_similar_word


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


class TestFindSimilarWord:
    def test_exact_threshold_is_accepted(self):
        """A candidate whose similarity equals the threshold must be returned."""
        # "night" vs "night" → similarity 1.0; threshold 1.0 should still match.
        assert find_similar_word("night", ["night"], threshold=1.0) == "night"

    def test_below_threshold_is_rejected(self):
        """A candidate whose similarity is strictly below the threshold returns None."""
        # "abc" vs "xyz" → similarity 0.0; any positive threshold rejects it.
        assert find_similar_word("abc", ["xyz"], threshold=0.1) is None

    def test_most_similar_wins_above_threshold(self):
        """When multiple candidates meet the threshold, the most similar one wins."""
        result = find_similar_word("night", ["nightly", "night", "days"], threshold=0.5)
        assert result == "night"

    def test_no_candidates_returns_none(self):
        assert find_similar_word("hello", [], threshold=0.5) is None

    def test_threshold_zero_accepts_any_positive_similarity(self):
        """threshold=0 accepts a word as long as it has any bigram overlap."""
        # "abc" vs "abz" share the bigram "ab", so similarity > 0
        result = find_similar_word("abc", ["abz"], threshold=0.0)
        assert result == "abz"

    def test_zero_similarity_never_returned(self):
        """A candidate with 0.0 similarity is never returned, even at threshold=0."""
        # "abc" vs "xyz" share no bigrams → similarity == 0.0, ties with
        # the initial max_similarity of 0, so the strict > check keeps it out.
        result = find_similar_word("abc", ["xyz"], threshold=0.0)
        assert result is None
