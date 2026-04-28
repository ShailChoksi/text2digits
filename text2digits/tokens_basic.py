import enum
import re
import types
from decimal import Decimal
from typing import NamedTuple, Optional


class NumEntry(NamedTuple):
    scale: int
    value: int


class WordType(enum.Enum):
    OTHER = 0
    LITERAL_INT = 1
    LITERAL_FLOAT = 2
    UNITS = 3
    TEENS = 4
    TENS = 5
    SCALES = 6
    CONJUNCTION = 7
    REPLACED = 8


class Token(object):
    # Static init code (only executed once and not for each token instance)
    UNITS = ('zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine')
    TEENS = ('ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen',
             'nineteen')
    TENS = ('twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety')
    SCALES = ('hundred', 'thousand', 'million', 'billion', 'trillion')
    # Literal numeric tokens whose value equals one of these are treated as large-scale
    # multipliers by has_large_scale(), enabling expressions like "10000 million".
    # This set is intentionally hand-curated — do NOT derive it mechanically from
    # SCALES + INDIAN_SCALES: that approach drops 10_000 (ten-thousand, a valid
    # combined scale) and would silently break inputs such as "10000 million".
    #   100            → hundred
    #   1_000          → thousand
    #   10_000         → ten thousand (combined scale, not in SCALES directly)
    #   1_000_000      → million
    #   10_000_000     → ten million (lakh-equivalent combined scale)
    #   1_000_000_000  → billion / arab
    #   100_000_000_000 → hundred billion / kharab
    #   1_000_000_000_000 → trillion
    SCALE_VALUES = frozenset({
        100,               # hundred
        1_000,             # thousand
        10_000,            # ten thousand (combined; intentionally kept)
        1_000_000,         # million
        10_000_000,        # ten million / lakh-range
        1_000_000_000,     # billion / arab
        100_000_000_000,   # hundred billion / kharab
        1_000_000_000_000, # trillion
    })
    INDIAN_SCALES = ('lakh', 'crore', 'arab', 'kharab')
    CONJUNCTION = frozenset({'and'})
    ORDINAL_WORDS = types.MappingProxyType({'first': 'one', 'second': 'two', 'third': 'three', 'fifth': 'five',
                                            'eighth': 'eight', 'ninth': 'nine', 'twelfth': 'twelve'})
    ORDINAL_ENDINGS = (('ieth', 'y'), ('th', ''))

    _numwords_build = {
        'and': NumEntry(scale=1, value=0)
    }
    for idx, word in enumerate(UNITS):
        _numwords_build[word] = NumEntry(scale=1, value=idx)
    for idx, word in enumerate(TEENS):
        _numwords_build[word] = NumEntry(scale=1, value=idx + 10)
    for idx, word in enumerate(TENS):
        _numwords_build[word] = NumEntry(scale=1, value=(idx + 2) * 10)
    for idx, word in enumerate(SCALES):
        _numwords_build[word] = NumEntry(scale=10 ** (idx * 3 or 2), value=0)
    for idx, word in enumerate(INDIAN_SCALES):
        _numwords_build[word] = NumEntry(scale=10 ** (5 + idx * 2), value=0)
    _numwords_build['oh'] = NumEntry(scale=1, value=0)  # alias for zero; kept separate to avoid index-10 collision in UNITS enumeration
    numwords = types.MappingProxyType(_numwords_build)
    del _numwords_build

    def __init__(self, word: str, glue: str) -> None:
        """
        Represents a word in the text with some additional knowledge about the word (e.g. information about its type).

        :param word: The string representation in the text.
        :param glue: The glue (e.g. whitespace) which follows the word.
        """
        self.word_raw = word
        self.glue = glue

        # Basic preprocessing of the word to find the type
        self._word = word.lower().replace(',', '')

        # Try to match ordinal numbers and then treat them as cardinal ones
        self.ordinal_ending = None  # We need to keep a reference to the original ending in case the user wants to preserve it
        if self._word in Token.ORDINAL_WORDS:
            self.ordinal_ending = self._word[-2:]
            self._word = Token.ORDINAL_WORDS[self._word]

        for ending, replacement in Token.ORDINAL_ENDINGS:
            if self._word.endswith(ending):
                replaced = self._word[:-len(ending)] + replacement
                if replaced in Token.numwords:
                    self.ordinal_ending = self._word[-2:]
                    self._word = replaced
                    break

        # Assign a type to each token (from specific to general)
        if self._word == 'oh':
            self.type = WordType.UNITS
        elif self._word in Token.UNITS:
            self.type = WordType.UNITS
        elif self._word in Token.TEENS:
            self.type = WordType.TEENS
        elif self._word in Token.TENS:
            self.type = WordType.TENS
        elif self._word in Token.SCALES or self._word in Token.INDIAN_SCALES:
            self.type = WordType.SCALES
        elif self._word in Token.CONJUNCTION:
            self.type = WordType.CONJUNCTION
        elif re.fullmatch(r'\d+\.\d*|\d*\.\d+', self._word):
            self.type = WordType.LITERAL_FLOAT
        elif re.fullmatch(r'\d+', self._word):
            self.type = WordType.LITERAL_INT
        else:
            self.type = WordType.OTHER

    def __repr__(self) -> str:
        return f'{self._word} ({self.type})'

    def is_ordinal(self) -> bool:
        return self.ordinal_ending is not None

    def has_large_scale(self) -> bool:
        """
        Returns True when the token has a scale >= 100.
        """
        if self.type == WordType.SCALES:
            return True
        elif self.type in [WordType.LITERAL_INT, WordType.LITERAL_FLOAT]:
            return Decimal(self._word) in self.SCALE_VALUES
        else:
            return False

    def value(self) -> Decimal:
        """
        Returns the value of a token (e.g. twelve -> 12). SCALES have a value of 0 since they are defined by their scale and not by their value, e.g. for two hundred we calculate 2 * 100 + 0.
        """
        if self.type in [WordType.LITERAL_INT, WordType.LITERAL_FLOAT]:
            if self.has_large_scale():
                return Decimal(0)
            else:
                return Decimal(self._word)
        elif self.type != WordType.OTHER:
            return Decimal(Token.numwords[self._word].value)
        raise ValueError(f"Cannot compute value for token of type {self.type!r} (word={self.word_raw!r})")

    def scale(self) -> Decimal:
        """
        Returns the scale of a token (e.g. hundred -> 100).
        """
        if self.type in [WordType.LITERAL_INT, WordType.LITERAL_FLOAT]:
            if self.has_large_scale():
                return Decimal(self._word)
            else:
                return Decimal(1)
        elif self.type != WordType.OTHER:
            return Decimal(Token.numwords[self._word].scale)
        raise ValueError(f"Cannot compute scale for token of type {self.type!r} (word={self.word_raw!r})")

    def text(self) -> str:
        """
        Returns the textual (digit) representation of the token (e.g. twelve -> 12).
        """
        if self.type in [WordType.LITERAL_INT, WordType.LITERAL_FLOAT, WordType.CONJUNCTION, WordType.OTHER]:
            # Keep the original representation of the literal in case there were e.g. some thousand separators
            return self.word_raw
        elif self.type == WordType.SCALES:
            return str(self.scale())
        else:
            return str(self.value())


class NoneToken(object):
    """
    Special token type which serves as a mock-up for a word which does not exist in the input.
    """

    def __init__(self) -> None:
        self.type: Optional[WordType] = None

    def is_ordinal(self) -> bool:
        return False

    def has_large_scale(self) -> bool:
        return False
