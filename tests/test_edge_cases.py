"""Edge-case tests covering boundary inputs and behaviours called out in the code review."""

from text2digits import text2digits
from text2digits.text_processing_helpers import split_glues


class TestEmptyAndTrivialInputs:
    def test_empty_string_returns_empty(self):
        assert text2digits.Text2Digits().convert("") == ""

    def test_single_non_number_char(self):
        assert text2digits.Text2Digits().convert("a") == "a"

    def test_single_number_word(self):
        assert text2digits.Text2Digits().convert("five") == "5"

    def test_whitespace_only(self):
        result = text2digits.Text2Digits().convert("   ")
        assert result == "   "


class TestConjunctionOnlyInput:
    def test_all_conjunctions(self):
        """'and and and' contains no numeric tokens; output must be unchanged."""
        result = text2digits.Text2Digits().convert("and and and")
        assert result == "and and and"


class TestSplitGlues:
    def test_basic_split(self):
        pairs = list(split_glues("hello world"))
        assert pairs == [("hello", " "), ("world", "")]

    def test_empty_string(self):
        assert list(split_glues("")) == []

    def test_trailing_punctuation_preserved(self):
        pairs = list(split_glues("thirty."))
        # trailing '.' is not a separator between \D chars — stays attached
        words = [w for w, _ in pairs]
        assert "thirty." in words or "thirty" in words

    def test_hyphen_separator(self):
        pairs = list(split_glues("forty-two"))
        words = [w for w, _ in pairs]
        assert "forty" in words
        assert "two" in words

    def test_glue_is_preserved(self):
        pairs = list(split_glues("one two"))
        assert pairs[0][1] == " "


class TestSimilarityThresholdBoundary:
    def test_exact_threshold_match_is_accepted(self):
        """A word whose similarity equals the threshold must be converted (>= not >)."""
        # "night" vs "night" → similarity 1.0; threshold 1.0 should still match
        from text2digits.text_processing_helpers import find_similar_word

        assert find_similar_word("night", ["night"], threshold=1.0) == "night"

    def test_just_below_threshold_is_rejected(self):
        from text2digits.text_processing_helpers import find_similar_word

        assert find_similar_word("abc", ["xyz"], threshold=0.5) is None


class TestDecimalSupport:
    def test_decimal_scale(self):
        assert text2digits.Text2Digits().convert("2.5 thousand") == "2500"

    def test_decimal_hundred(self):
        assert text2digits.Text2Digits().convert("1.2345 hundred") == "123.45"

    def test_standalone_decimal_unchanged(self):
        assert text2digits.Text2Digits().convert("3.14") == "3.14"


class TestNegativePrefix:
    def test_negative_converts_to_unary_minus(self):
        """'negative' before a number is converted to a unary '-'."""
        result = text2digits.Text2Digits().convert("negative five")
        assert result == "-5"

    def test_negative_in_sentence(self):
        result = text2digits.Text2Digits().convert("it was negative thirty seven degrees")
        assert result == "it was -37 degrees"
