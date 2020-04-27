from typing import List

from text2digits.tokens_basic import Token, WordType
from text2digits.rules import CombinationRule, ConcatenationRule
from text2digits.text_processing_helpers import split_glues, find_similar_word


class Text2Digits(object):
    def __init__(self, similarity_threshold=1.0, convert_ordinals=True, add_ordinal_ending=False):
        """
        This class can be used to convert text representations of numbers to digits. That is, it replaces all occurrences of numbers (e.g. forty-two) to the digit representation (e.g. 42).

        Basic usage:

        >>> from text2digits import text2digits
        >>> t2d = text2digits.Text2Digits()
        >>> t2d.convert("twenty ten and twenty one")
        >>> 2010 and 21

        :param similarity_threshold: Used for spelling correction. It specifies the minimal similarity in the range [0, 1] of a word to one of the number words. 0 inidcates that every other word is similar and 1 requires a perfect match, i.e. no spelling correction is performed with a value of 1.
        :param convert_ordinals: Whether to convert ordinal numbers (e.g. third --> 3).
        :param add_ordinal_ending: Whether to add the ordinal ending to the converted ordinal number (e.g. twentieth --> 20th). Implies convert_ordinals=True.
        """
        self.similarity_threshold = similarity_threshold

        if self.similarity_threshold < 0 or self.similarity_threshold > 1:
            raise ValueError('The similarity_threshold must be in the range [0, 1]')

        self.convert_ordinals = convert_ordinals
        self.add_ordinal_ending = add_ordinal_ending

        # Keeping the ordinal ending implies that we convert ordinal numbers
        if self.add_ordinal_ending:
            self.convert_ordinals = True

    def convert(self, text: str) -> str:
        """
        Converts all number representations to digits.

        :param text: The input string.
        :return: The input string with all numbers replaced with their corresponding digit representation.
        """

        # Tokenize the input string by assigning a type to each word (e.g. representing the number type like units (e.g. one) or teens (twelve))
        # This makes it easier for the subsequent steps to decide which parts of the sentence need to be combined
        # e.g. I like forty-two apples --> I [WordType.Other] like [WordType.Other] forty [WordType.TENS] two [WordType.UNITS] apples [WordType.Other]
        tokens = self._lex(text)

        # Apply a set of rules to the tokens to combine the numeric tokens and replace them with the corresponding digit
        # e.g. I [WordType.Other] like [WordType.Other] 42 [ConcatenatedToken] apples [WordType.Other] (it merged the TENS and UNITS tokens)
        text = self._parse(tokens)

        return text

    def _lex(self, text: str) -> List[Token]:
        """
        This function takes an arbitrary input string, splits it into tokens (words) and assigns each token a type corresponding to the role in the sentence.

        :param text: The input string.
        :return: The tokenized input string.
        """
        tokens = []

        conjunctions = []
        for i, (word, glue) in enumerate(split_glues(text)):
            # Address spelling corrections
            if self.similarity_threshold != 1:
                matched_num = find_similar_word(word, Token.numwords.keys(), self.similarity_threshold)
                if matched_num is not None:
                    word = matched_num

            token = Token(word, glue)
            tokens.append(token)

            # Conjunctions need special treatment since they can be used for both, to combine numbers or to combine other parts in the sentence
            if token.type == WordType.CONJUNCTION:
                conjunctions.append(i)

        # A word should only have the type WordType.CONJUNCTION when it actually combines two digits and not some other words in the sentence
        for i in conjunctions:
            if i >= len(tokens) - 1 or tokens[i + 1].type in [WordType.CONJUNCTION, WordType.OTHER]:
                tokens[i].type = WordType.OTHER

        return tokens

    def _parse(self, tokens: List[Token]) -> str:
        """
        Parses the tokenized input based on predefined rules which combine certain tokens to find the correct digit representation of the textual number description.

        :param tokens: The tokenized input string.
        :return: The transformed input string.
        """
        rules = [CombinationRule(), ConcatenationRule()]

        # Apply each rule to process the tokens
        for rule in rules:
            new_tokens = []
            i = 0

            while i < len(tokens):
                if tokens[i].is_ordinal() and not self.convert_ordinals:
                    # When keeping ordinal numbers, treat the whole number (which may consists of multiple parts, e.g. ninety-seventh) as a normal word
                    tokens[i].type = WordType.OTHER

                if tokens[i].type != WordType.OTHER:
                    # Check how many tokens this rule wants to process...
                    n_match = rule.match(tokens[i:])
                    if n_match > 0:
                        # ... and then merge these tokens into a new one (e.g. a token representing the digit)
                        token = rule.action(tokens[i:i + n_match])
                        new_tokens.append(token)
                        i += n_match
                    else:
                        new_tokens.append(tokens[i])
                        i += 1
                else:
                    new_tokens.append(tokens[i])
                    i += 1

            tokens = new_tokens

        # Combine the tokens back to a string (with special handling of ordinal numbers)
        text = ''
        for token in tokens:
            if token.is_ordinal() and not self.convert_ordinals:
                text += token.word_raw
            else:
                text += token.text()
                if token.is_ordinal() and self.add_ordinal_ending:
                    text += token.ordinal_ending

            text += token.glue

        return text
