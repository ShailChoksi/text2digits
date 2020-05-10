from abc import ABC, abstractmethod
from decimal import Decimal
from typing import List

from text2digits.tokens_basic import WordType, Token


class RuleToken(ABC):
    def __init__(self, original_tokens: List[Token]):
        """
        Base class for tokens which are used during rule processing.

        :param original_tokens: List of tokens which are combined by the rule.
        """
        super().__init__()
        self.original_tokens = original_tokens

        # The last token determines the ordinal ending, e.g. thirty-second --> nd
        self.ordinal_ending = self.original_tokens[-1].ordinal_ending

        # Build a representation of the original word consisting of all tokens
        self.word_raw = ''
        for i, token in enumerate(self.original_tokens):
            self.word_raw += token.word_raw
            if i < len(self.original_tokens) - 1:
                # The rule token is responsible for keeping the glue between the individual tokens (e.g. the hyphens in "two-hundred-thousandth") but not the glue of the last token
                self.word_raw += token.glue

    def is_ordinal(self) -> bool:
        return any([token.is_ordinal() for token in self.original_tokens])

    @abstractmethod
    def text(self) -> str:
        pass


class CombinedToken(RuleToken):
    """
    Special token type which is used by the CombinationRule.
    """

    def __init__(self, original_tokens: List[Token], value: Decimal, glue: str):
        super().__init__(original_tokens)
        self._value = value
        self.glue = glue
        self.type = WordType.REPLACED

    def __repr__(self) -> str:
        return str(self._value)

    def value(self) -> Decimal:
        return self._value

    def scale(self) -> Decimal:
        return Decimal(1)

    def text(self) -> str:
        number = self.value()

        # Remove tailing zeros, e.g. 1.2345 hundred -> 123.4500 -> 123.45
        number = number.to_integral() if number == number.to_integral() else number.normalize()

        return str(number)


class ConcatenatedToken(RuleToken):
    """
    Special token type which is used by the ConcatenationRule.
    """

    def __init__(self, original_tokens: List[Token], text: str, glue: str):
        super().__init__(original_tokens)
        self._text = text
        self.glue = glue
        self.type = WordType.REPLACED

    def __repr__(self) -> str:
        return str(self._text)

    def text(self) -> str:
        return self._text
