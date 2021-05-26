import enum
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import List, Union

from text2digits.tokens_basic import WordType, Token, NoneToken
from text2digits.tokens_rules import CombinedToken, ConcatenatedToken, RuleToken


class Rule(ABC):
    """
    Rules are used to parse a sequence of tokens and to apply a rule on the detected tokens to retrieve a new number representation.
    """

    @abstractmethod
    def match(self, tokens: List[Union[Token, RuleToken]]) -> int:
        """
        Analyses the tokens and tries to find a consecutive sequence of tokens which should be combined for the specified rule. The focus of this function lies on *which* tokens should be combined (instead of *how*).

        :param tokens: List of tokens.
        :return: Number of tokens which match the specified rule.
        """
        pass

    @abstractmethod
    def action(self, tokens: List[Union[Token, RuleToken]]) -> RuleToken:
        """
        Combines the tokens and replaces it with a new token (e.g. converted number). The focus of this function lies on *how* tokens should be combined (instead of *which*).

        :param tokens: The tokens to be combined.
        :return: The new token which replaces the input tokens.
        """
        pass


class CombinationRule(Rule):
    """
    This rule handles all the (complicated) cases where we actually need to calculate the output number (e.g. two hundred forty-two --> 2*100 + 40 + 2 = 242).
    """

    def __init__(self):
        self.valid_types = [WordType.LITERAL_INT, WordType.LITERAL_FLOAT, WordType.UNITS, WordType.TEENS, WordType.TENS, WordType.SCALES]

    def match(self, tokens: List[Token]) -> int:
        class MatchType(enum.Enum):
            SINGLE = 0
            SCALE = 1
            DUAl_SCALE = 2
            DUAL_HUNDRED = 3

        # We need at least two tokens to combine something
        if len(tokens) < 2:
            return 0

        last_match = None
        last_scale = 0
        consumed_tokens = 0
        while consumed_tokens < len(tokens):
            consumed_conjunctions = 0
            first = tokens[consumed_tokens]

            # In case of a conjunction, we are interested in the word which follows next
            if consumed_tokens > 0 and first.type == WordType.CONJUNCTION:
                # Consume the conjunction
                consumed_conjunctions = 1
                first = tokens[consumed_tokens + consumed_conjunctions]

            # Same for the second considered token. However, it is a bit more complicated in this case since we may reach the end of the string
            second = tokens[consumed_tokens + consumed_conjunctions + 1] if consumed_tokens < len(tokens) - consumed_conjunctions - 1 else NoneToken()
            if second.type == WordType.CONJUNCTION:
                consumed_conjunctions = 1
                second = tokens[consumed_tokens + consumed_conjunctions + 1] if consumed_tokens < len(tokens) - consumed_conjunctions - 1 else NoneToken()

            # Now the tricky part: we need to decide how many tokens we need to combine
            if last_match != MatchType.DUAL_HUNDRED and first.type == WordType.TENS and second.type == WordType.UNITS:
                # e.g. twenty one -> consume both
                consumed_tokens += 2
                last_match = MatchType.DUAL_HUNDRED
            elif first.type in self.valid_types and second.has_large_scale():
                # e.g. 2.1 hundred -> consume both (result 210)
                consumed_tokens += 2
                last_match = MatchType.DUAl_SCALE
                last_scale = second.scale()
            elif first.has_large_scale() and (second.type in self.valid_types or last_match == MatchType.DUAL_HUNDRED):
                # e.g. *hundred two -> consume hundred
                # e.g. twenty one *hundred -> twenty one already consumed by the first condition

                # It is important to just consume the scale to handle cases like hundred twenty one
                consumed_tokens += 1
                last_match = MatchType.SCALE
                last_scale = first.scale()
            elif last_match in [MatchType.SCALE, MatchType.DUAl_SCALE] and first.has_large_scale():
                # Two consecutive scales are only allowed when the scale increases
                # e.g. hundred thousand -> ok
                # e.g. thousand hundred -> no valid number
                if first.scale() > last_scale:
                    consumed_tokens += 1
                    last_match = MatchType.SCALE
                else:
                    last_match = None
            elif last_match in [MatchType.SCALE, MatchType.DUAl_SCALE] and first.type in self.valid_types:
                # e.g. hundred *two -> consume two
                consumed_tokens += 1
                last_match = MatchType.SINGLE
            else:
                last_match = None

            if last_match is None:
                break

            consumed_tokens += consumed_conjunctions

        return consumed_tokens

    def action(self, tokens: List[Token]) -> CombinedToken:
        assert len(tokens) >= 2, 'At least two tokens are required'

        current = Decimal(0)
        result = Decimal(0)
        last_glue = ''
        prev_scale = 1
        all_scales = [token.scale() for token in tokens]

        for index, token in enumerate(tokens):
            assert token.type != WordType.OTHER, 'Invalid token type (only numbers are allowed here)'

            if token.has_large_scale():
                # Multiply the scale at least with a value of 1 (and not 0)
                current = max(1, current)

            if token.scale() < prev_scale and prev_scale > max(all_scales[index:]):
                # Flush the result when switching from a larger to a smaller scale
                # e.g. one thousand *FLUSH* six hundred *FLUSH* sixty six
                result += current
                current = Decimal(0)

            current = current * token.scale() + token.value()
            last_glue = token.glue
            prev_scale = token.scale()

        result += current

        return CombinedToken(tokens, result, last_glue)

class ConcatenationRule(Rule):
    """
    This rule handles all the "year cases" like twenty twenty where we simply concatenate the numbers together. The numbers are already transformed to digits by the CombinationRule.
    """
    def __init__(self):
        self.valid_types = [WordType.UNITS, WordType.TEENS, WordType.TENS, WordType.SCALES, WordType.REPLACED]

    def match(self, tokens: List[Union[Token, CombinedToken]]) -> int:
        i = 0

        # Find all numeric tokens
        while i < len(tokens):
            if tokens[i].type in self.valid_types and not tokens[i].is_ordinal():
                # Avoid ordinals. Example: 'look at the second one' should convert into '2nd 1' not '21'
                i += 1
            else:
                break

        return i

    def action(self, tokens: List[Union[Token, CombinedToken]]) -> ConcatenatedToken:
        assert len(tokens) >= 1, 'At least one token is required'

        last_glue = ''
        result = ''

        for token in tokens:
            result += token.text()
            last_glue = token.glue

        return ConcatenatedToken(tokens, result, last_glue)
