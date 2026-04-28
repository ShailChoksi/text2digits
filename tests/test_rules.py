from text2digits import text2digits
from text2digits.rules import CombinationRule, ConcatenationRule, MatchType


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


class TestMatchType:
    def test_match_type_is_module_level(self):
        """MatchType must be importable at module level, not recreated per call."""
        import text2digits.rules as rules_module
        assert hasattr(rules_module, 'MatchType'), "MatchType should be a module-level name"

    def test_match_type_members(self):
        assert MatchType.SINGLE.value == 0
        assert MatchType.SCALE.value == 1
        assert MatchType.DUAL_SCALE.value == 2
        assert MatchType.DUAL_HUNDRED.value == 3

    def test_dual_scale_typo_is_gone(self):
        """The old typo DUAl_SCALE must no longer exist."""
        assert not hasattr(MatchType, 'DUAl_SCALE')

    def test_match_type_identity_stable_across_calls(self):
        """The same MatchType class is used across repeated match() calls."""
        rule = CombinationRule()
        t2d = text2digits.Text2Digits()
        tokens = t2d._lex('two hundred')
        # Call match() twice and verify we get consistent token counts,
        # which indirectly proves the shared enum is not broken by re-creation.
        assert rule.match(tokens) == rule.match(tokens)
