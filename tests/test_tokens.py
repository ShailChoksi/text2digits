from decimal import Decimal

import pytest

from text2digits import text2digits
from text2digits.tokens_basic import Token, WordType


def test_lexer():
    example = "one hundred 2.2 50 eleven forty twenty and two and bus third and lakh crore arab kharab"
    types = [
        WordType.UNITS,
        WordType.SCALES,
        WordType.LITERAL_FLOAT,
        WordType.LITERAL_INT,
        WordType.TEENS,
        WordType.TENS,
        WordType.TENS,
        WordType.CONJUNCTION,
        WordType.UNITS,
        WordType.OTHER,
        WordType.OTHER,
        WordType.UNITS,
        WordType.CONJUNCTION,
        WordType.SCALES,
        WordType.SCALES,
        WordType.SCALES,
        WordType.SCALES,
    ]

    t2d = text2digits.Text2Digits()
    tokens = t2d._lex(example)
    for token, type in zip(tokens, types):
        assert token.type == type, token.text()

    t1 = Token("100", "")
    assert t1.has_large_scale()
    assert t1.scale() == 100

    t2 = Token("5", "")
    assert not t2.has_large_scale()
    assert t2.scale() == 1


class TestOtherTokenValueScale:
    """value() and scale() must raise ValueError for OTHER tokens, not silently return None."""

    def _other_token(self) -> Token:
        t = Token("bus", "")
        assert t.type == WordType.OTHER
        return t

    def test_value_raises_for_other(self):
        with pytest.raises(ValueError, match="Cannot compute value"):
            self._other_token().value()

    def test_scale_raises_for_other(self):
        with pytest.raises(ValueError, match="Cannot compute scale"):
            self._other_token().scale()

    def test_error_message_includes_word(self):
        t = Token("foobar", "")
        with pytest.raises(ValueError, match="foobar"):
            t.value()

    def test_value_valid_for_numword_types(self):
        """Sanity-check that non-OTHER tokens still return a Decimal, not None."""
        from decimal import Decimal

        assert Token("twelve", "").value() == Decimal(12)
        assert Token("hundred", "").value() == Decimal(0)
        assert Token("42", "").value() == Decimal(42)

    def test_scale_valid_for_numword_types(self):
        assert Token("twelve", "").scale() == Decimal(1)
        assert Token("hundred", "").scale() == Decimal(100)
        assert Token("100", "").scale() == Decimal(100)


class TestOhToken:
    """'oh' is a spoken alias for zero (phone numbers) and must NOT be an ordinal."""

    def test_oh_type_is_units(self):
        assert Token("oh", "").type == WordType.UNITS

    def test_oh_is_not_ordinal(self):
        assert Token("oh", "").is_ordinal() is False

    def test_oh_value_is_zero(self):
        assert Token("oh", "").value() == Decimal(0)

    def test_oh_scale_is_one(self):
        assert Token("oh", "").scale() == Decimal(1)

    def test_oh_does_not_collide_with_units_index(self):
        """'oh' must have value 0, not 10 (what appending to UNITS list would give)."""
        assert Token("oh", "").value() == Decimal(0)
        assert "oh" not in Token.UNITS

    def test_phone_number_concatenation(self):
        """'four oh seven' should produce '407', not '4 0 7'."""
        t2d = text2digits.Text2Digits()
        assert t2d.convert("four oh seven") == "407"

    def test_oh_case_insensitive(self):
        assert Token("Oh", "").type == WordType.UNITS
        assert Token("OH", "").type == WordType.UNITS


class TestOrdinalEndingBreak:
    """A word matching the first ordinal-ending rule must not be re-processed by the second."""

    def test_twentieth_resolves_to_twenty(self):
        # 'twentieth' matches ('ieth', 'y') → 'twenty'; the loop must stop there.
        # Without the break the loop would continue and try ('th', '') on 'twenty',
        # find 'twen' which is not in numwords, but mutate _word to 'twen' first.
        t = Token("twentieth", "")
        assert t._word == "twenty"
        assert t.is_ordinal()

    def test_thirtieth_resolves_to_thirty(self):
        t = Token("thirtieth", "")
        assert t._word == "thirty"
        assert t.is_ordinal()

    def test_fortieth_resolves_to_forty(self):
        t = Token("fortieth", "")
        assert t._word == "forty"
        assert t.is_ordinal()

    def test_ieth_match_does_not_fall_through_to_th(self):
        """After an 'ieth' match the token type must be TENS, not OTHER."""
        t = Token("twentieth", "")
        assert t.type == WordType.TENS

    def test_plain_th_ordinal_still_works(self):
        """Words that only match the 'th' rule are unaffected by the break."""
        t = Token("sixth", "")
        assert t._word == "six"
        assert t.is_ordinal()
        assert t.type == WordType.UNITS
