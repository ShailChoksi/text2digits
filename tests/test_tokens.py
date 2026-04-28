import pytest
from text2digits import text2digits
from text2digits.tokens_basic import WordType, Token


def test_lexer():
    example = 'one hundred 2.2 50 eleven forty twenty and two and bus third and lakh crore arab kharab'
    types = [WordType.UNITS, WordType.SCALES, WordType.LITERAL_FLOAT, WordType.LITERAL_INT, WordType.TEENS,
             WordType.TENS, WordType.TENS, WordType.CONJUNCTION, WordType.UNITS, WordType.OTHER, WordType.OTHER,
             WordType.UNITS, WordType.CONJUNCTION, WordType.SCALES, WordType.SCALES, WordType.SCALES, WordType.SCALES]

    t2d = text2digits.Text2Digits()
    tokens = t2d._lex(example)
    for token, type in zip(tokens, types):
        assert token.type == type, token.text()

    t1 = Token('100', '')
    assert t1.has_large_scale()
    assert t1.scale() == 100

    t2 = Token('5', '')
    assert not t2.has_large_scale()
    assert t2.scale() == 1


class TestOtherTokenValueScale:
    """value() and scale() must raise ValueError for OTHER tokens, not silently return None."""

    def _other_token(self) -> Token:
        t = Token('bus', '')
        assert t.type == WordType.OTHER
        return t

    def test_value_raises_for_other(self):
        with pytest.raises(ValueError, match="Cannot compute value"):
            self._other_token().value()

    def test_scale_raises_for_other(self):
        with pytest.raises(ValueError, match="Cannot compute scale"):
            self._other_token().scale()

    def test_error_message_includes_word(self):
        t = Token('foobar', '')
        with pytest.raises(ValueError, match="foobar"):
            t.value()

    def test_value_valid_for_numword_types(self):
        """Sanity-check that non-OTHER tokens still return a Decimal, not None."""
        from decimal import Decimal
        assert Token('twelve', '').value() == Decimal(12)
        assert Token('hundred', '').value() == Decimal(0)
        assert Token('42', '').value() == Decimal(42)

    def test_scale_valid_for_numword_types(self):
        from decimal import Decimal
        assert Token('twelve', '').scale() == Decimal(1)
        assert Token('hundred', '').scale() == Decimal(100)
        assert Token('100', '').scale() == Decimal(100)
