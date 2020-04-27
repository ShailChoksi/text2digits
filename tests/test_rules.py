from text2digits import text2digits
from text2digits.rules import CombinationRule, ConcatenationRule


def test_parer_combination_rule():
    cases = [('twenty one thousand three hundred', 5), ('twenty one', 2), ('hundred twenty one', 3)]
    rule = CombinationRule()
    t2d = text2digits.Text2Digits()

    for example, number in cases:
        assert rule.match(t2d._lex(example)) == number


def test_parer_concatenation_rule():
    cases = [('one ten', 2), ('three', 1), ('nineteen', 1)]
    rule = ConcatenationRule()
    t2d = text2digits.Text2Digits()

    for example, number in cases:
        assert rule.match(t2d._lex(example)) == number
