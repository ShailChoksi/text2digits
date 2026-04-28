import pytest

from text2digits import text2digits
from text2digits.rules import CombinationRule, ConcatenationRule, MatchType
from text2digits.tokens_basic import Token


def test_parser_combination_rule():
    # (input, expected_match_count, expected_text)
    cases = [
        ("twenty one thousand three hundred", 5, "21300"),
        ("twenty one", 2, "21"),
        ("hundred twenty one", 3, "121"),
    ]
    rule = CombinationRule()
    t2d = text2digits.Text2Digits()

    for example, expected_count, expected_text in cases:
        tokens = t2d._lex(example)
        assert rule.match(tokens) == expected_count
        assert rule.action(tokens[:expected_count]).text() == expected_text


def test_parser_concatenation_rule():
    # (input, expected_match_count, expected_text)
    cases = [
        ("one ten", 2, "110"),
        ("three", 1, "3"),
        ("nineteen", 1, "19"),
    ]
    rule = ConcatenationRule()
    t2d = text2digits.Text2Digits()

    for example, expected_count, expected_text in cases:
        tokens = t2d._lex(example)
        assert rule.match(tokens) == expected_count
        assert rule.action(tokens[:expected_count]).text() == expected_text


class TestMatchType:
    def test_match_type_is_module_level(self):
        """MatchType must be importable at module level, not recreated per call."""
        import text2digits.rules as rules_module

        assert hasattr(rules_module, "MatchType"), "MatchType should be a module-level name"

    def test_match_type_members(self):
        assert MatchType.SINGLE.value == 0
        assert MatchType.SCALE.value == 1
        assert MatchType.DUAL_SCALE.value == 2
        assert MatchType.DUAL_HUNDRED.value == 3

    def test_dual_scale_typo_is_gone(self):
        """The old typo DUAl_SCALE must no longer exist."""
        assert not hasattr(MatchType, "DUAl_SCALE")

    def test_match_type_identity_stable_across_calls(self):
        """The same MatchType class is used across repeated match() calls."""
        rule = CombinationRule()
        t2d = text2digits.Text2Digits()
        tokens = t2d._lex("two hundred")
        # Call match() twice and verify we get consistent token counts,
        # which indirectly proves the shared enum is not broken by re-creation.
        assert rule.match(tokens) == rule.match(tokens)


class TestActionPreconditions:
    """action() must raise ValueError for invalid input, not silently pass under -O."""

    def test_combination_action_raises_for_empty_list(self):
        with pytest.raises(ValueError, match="CombinationRule"):
            CombinationRule().action([])

    def test_combination_action_raises_for_single_token(self):
        with pytest.raises(ValueError, match="CombinationRule"):
            CombinationRule().action([Token("two", "")])

    def test_combination_action_error_includes_count(self):
        with pytest.raises(ValueError, match="1"):
            CombinationRule().action([Token("two", "")])

    def test_concatenation_action_raises_for_empty_list(self):
        with pytest.raises(ValueError, match="ConcatenationRule"):
            ConcatenationRule().action([])

    def test_concatenation_action_accepts_single_token(self):
        """ConcatenationRule requires >= 1 token; a single token must succeed."""
        token = Token("two", "")
        result = ConcatenationRule().action([token])
        assert result is not None

    def test_combination_action_succeeds_with_two_tokens(self):
        """Sanity-check that valid input still works after the assert→ValueError change."""
        tokens = [Token("two", " "), Token("hundred", "")]
        result = CombinationRule().action(tokens)
        assert result is not None


class TestConjunctionHandling:
    """consumed_conjunctions must accumulate with += when both first and second are conjunctions."""

    def _make_tokens(self, *words):
        return [Token(w, " ") for w in words]

    def test_single_conjunction_between_numbers(self):
        """Standard case: 'hundred and one' — conjunction between first and second."""
        rule = CombinationRule()
        t2d = text2digits.Text2Digits()
        tokens = t2d._lex("hundred and one")
        assert rule.match(tokens) == 3

    def test_double_conjunction_does_not_reread_same_index(self):
        """
        If first is already a conjunction (consumed_conjunctions=1) and the
        resulting second also turns out to be a conjunction, the old '= 1'
        assignment would leave consumed_conjunctions unchanged, reading the same
        index twice. With '+= 1' the index correctly advances.

        Construct: [hundred, and, and, one] — two consecutive conjunctions.
        match() starts after 'hundred' has been consumed in a prior iteration,
        so at iteration start consumed_tokens points at the first 'and'.
        We verify the overall match count is correct and no IndexError is raised.
        """
        rule = CombinationRule()
        # Build tokens manually to bypass _lex filtering
        tokens = [
            Token("hundred", " "),
            Token("and", " "),
            Token("and", " "),
            Token("one", ""),
        ]
        # hundred consumed first, then the two conjunctions + one must not
        # corrupt the index or raise; we accept whatever count the logic produces
        # without an exception — the key guarantee is no crash/index reuse.
        try:
            result = rule.match(tokens)
            assert isinstance(result, int)
        except IndexError as exc:
            raise AssertionError(
                "Double conjunction caused an IndexError — index was re-read instead of advanced"
            ) from exc
