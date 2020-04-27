import re
from typing import Iterator, List


def bigram_similarity(word1: str, word2: str) -> float:
    """
    Returns a number within the range [0, 1] determining how similar
    item1 is to item2. 0 indicates perfect dissimilarity while 1
    indicates equality. The similarity value is calculated by counting
    the number of bigrams both words share in common.
    """
    word1 = word1.lower()
    word2 = word2.lower()
    word1_length = len(word1)
    word2_length = len(word2)
    pairs1 = []
    pairs2 = []

    for i in range(word1_length):
        if i == word1_length - 1:
            continue
        pairs1.append(word1[i] + word1[i + 1])

    for i in range(word2_length):
        if i == word2_length - 1:
            continue
        pairs2.append(word2[i] + word2[i + 1])

    similar = [word for word in pairs1 if word in pairs2]

    return float(len(similar)) / float(max(len(pairs1), len(pairs2)))


def find_similar_word(word: str, collection: List, threshold: float) -> str:
    """
    Returns the most syntactically similar word in the collection
    to the specified word.
    """
    match = None
    max_similarity = 0

    for item in collection:
        similarity = bigram_similarity(word, item)

        # The similarity must be above the threshold and if this is true for
        # multiple words, we take the most similar one
        if similarity > max(max_similarity, threshold):
            match = item
            max_similarity = similarity

    return match


def split_glues(text: str, separator=r'\s+|(?<=\D)[.,;:\-_](?=\D)') -> Iterator[str]:
    """
    Splits a string and preserves the glue, i.e. the separator fragments.
    This is useful when words of a sentence should be processed while still
    keeping the possibility to recover the original sentence.

    :param text: The string to be split.
    :param separator: The separator to use for splitting (defaults to
    whitespace).
    :return: A generator yielding (match, glue) pairs, e.g. the word and
             the whitespace next to it. If no glue is left, an empty string
             is returned.
    """
    while True:
        match = re.search(separator, text)
        if not match:
            # The last word does not have a glue
            yield text, ''
            break

        yield text[:match.start()], match.group()

        # Proceed with the remaining string
        text = text[match.end():]
