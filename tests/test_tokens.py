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
