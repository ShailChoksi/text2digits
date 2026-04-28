"""Tests for feature 6.1 (negation) and feature 6.2 (decimal word form)."""

import pytest

from text2digits.text2digits import Text2Digits
from text2digits.tokens_basic import Token, WordType

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def convert(text: str, **kwargs) -> str:
    return Text2Digits(**kwargs).convert(text)


# ---------------------------------------------------------------------------
# 6.1 Negation: "negative" / "minus" → unary '-'
# ---------------------------------------------------------------------------


class TestNegationTokenType:
    def test_negative_is_negation_type(self):
        assert Token("negative", "").type == WordType.NEGATION

    def test_minus_is_negation_type(self):
        assert Token("minus", "").type == WordType.NEGATION

    def test_negation_value_raises(self):
        with pytest.raises(ValueError):
            Token("negative", "").value()

    def test_negation_scale_raises(self):
        with pytest.raises(ValueError):
            Token("negative", "").scale()

    def test_negation_text_returns_word(self):
        assert Token("negative", "").text() == "negative"

    def test_minus_text_returns_word(self):
        assert Token("minus", "").text() == "minus"

    def test_negation_is_not_ordinal(self):
        assert not Token("negative", "").is_ordinal()

    def test_negation_has_no_large_scale(self):
        assert not Token("negative", "").has_large_scale()


class TestNegationConversion:
    def test_negative_single_unit(self):
        assert convert("negative five") == "-5"

    def test_minus_single_unit(self):
        assert convert("minus five") == "-5"

    def test_negative_teens(self):
        assert convert("negative thirteen") == "-13"

    def test_negative_tens(self):
        assert convert("negative forty") == "-40"

    def test_negative_compound(self):
        assert convert("negative thirty seven") == "-37"

    def test_negative_hundreds(self):
        assert convert("negative two hundred") == "-200"

    def test_negative_large(self):
        assert convert("negative one thousand two hundred thirty four") == "-1234"

    def test_negative_literal_int(self):
        assert convert("negative 42") == "-42"

    def test_negative_literal_float(self):
        assert convert("negative 3.14") == "-3.14"

    def test_negative_in_sentence(self):
        assert convert("the temperature was negative thirty seven degrees") == ("the temperature was -37 degrees")

    def test_negative_not_before_number_is_preserved(self):
        """'negative' not followed by a number should be kept as-is."""
        assert convert("a negative result") == "a negative result"

    def test_minus_not_before_number_is_preserved(self):
        assert convert("minus sign") == "minus sign"

    def test_multiple_negations(self):
        assert convert("negative one and minus two") == "-1 and -2"

    def test_uppercase_negative(self):
        assert convert("Negative Five") == "-5"

    def test_uppercase_minus(self):
        assert convert("Minus Three") == "-3"


# ---------------------------------------------------------------------------
# 6.2 Decimal word: "point" → '.'
# ---------------------------------------------------------------------------


class TestDecimalSeparatorTokenType:
    def test_point_is_decimal_separator_type(self):
        assert Token("point", "").type == WordType.DECIMAL_SEPARATOR

    def test_decimal_separator_value_raises(self):
        with pytest.raises(ValueError):
            Token("point", "").value()

    def test_decimal_separator_scale_raises(self):
        with pytest.raises(ValueError):
            Token("point", "").scale()

    def test_decimal_separator_text_returns_word(self):
        assert Token("point", "").text() == "point"

    def test_point_is_not_ordinal(self):
        assert not Token("point", "").is_ordinal()

    def test_point_has_no_large_scale(self):
        assert not Token("point", "").has_large_scale()


class TestDecimalWordConversion:
    def test_basic_decimal_word(self):
        assert convert("three point five") == "3.5"

    def test_unit_point_unit(self):
        assert convert("one point two") == "1.2"

    def test_compound_left(self):
        assert convert("one hundred point five") == "100.5"

    def test_compound_right(self):
        assert convert("three point two five") == "3.25"

    def test_both_compound(self):
        assert convert("twenty three point four five") == "23.45"

    def test_literal_left(self):
        assert convert("3 point five") == "3.5"

    def test_literal_right(self):
        assert convert("three point 5") == "3.5"

    def test_both_literals(self):
        assert convert("3 point 5") == "3.5"

    def test_point_in_sentence(self):
        assert convert("the ratio is three point one four") == "the ratio is 3.14"

    def test_point_without_right_number_preserved(self):
        """'point' not followed by a number should be kept as-is."""
        assert convert("make a point about it") == "make a point about it"

    def test_point_without_left_number_preserved(self):
        """'point' not preceded by a number should be kept as-is."""
        assert convert("point five") == "point 5"

    def test_multiple_decimals_in_sentence(self):
        assert convert("one point five and two point three") == "1.5 and 2.3"


# ---------------------------------------------------------------------------
# 6.1 + 6.2 Combined: "negative X point Y" → '-X.Y'
# ---------------------------------------------------------------------------


class TestNegativeDecimalCombined:
    def test_negative_decimal(self):
        assert convert("negative three point five") == "-3.5"

    def test_minus_decimal(self):
        assert convert("minus one point two five") == "-1.25"

    def test_negative_compound_decimal(self):
        assert convert("negative twenty three point four five") == "-23.45"

    def test_negative_decimal_in_sentence(self):
        assert convert("the delta is negative zero point one") == "the delta is -0.1"
