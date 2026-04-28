"""
Regression tests for bugs reported by users.

Each class names the symptom and documents what the old (broken) behaviour was
so that we can detect if any fix is accidentally reverted.
"""

from text2digits import text2digits

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def convert(text: str, **kwargs) -> str:
    return text2digits.Text2Digits(**kwargs).convert(text)


# ---------------------------------------------------------------------------
# "hundred twenty three million …" was returned as '23057289'
# ---------------------------------------------------------------------------


class TestLeadingHundredWithoutMultiplier:
    """
    A leading "hundred" (without a preceding multiplier) used to be dropped,
    producing '23057289' instead of '123456789'.
    """

    def test_hundred_twenty_three_million(self):
        result = convert("hundred twenty three million four hundred fifty six thousand seven hundred and eighty nine")
        assert result == "123456789"

    def test_hundred_as_standalone_leading_scale(self):
        assert convert("hundred and two") == "102"

    def test_hundred_forty_two(self):
        assert convert("hundred forty two") == "142"


# ---------------------------------------------------------------------------
# Ordinal + following number used to be concatenated ('second one' → '21')
# ---------------------------------------------------------------------------


class TestOrdinalNotConcatenatedWithFollowingNumber:
    """
    'second one' was being joined by ConcatenationRule into '21'.
    Ordinals must not be concatenated with the word that follows them.
    """

    def test_second_one_default(self):
        assert convert("second one") == "2 1"

    def test_second_one_in_sentence(self):
        result = convert("Those were my friends. Particularly the second one there")
        assert result == "Those were my friends. Particularly the 2 1 there"

    def test_second_one_with_ordinal_ending(self):
        result = convert(
            "Those were my friends. Particularly the second one there",
            convert_ordinals=True,
            add_ordinal_ending=True,
        )
        assert result == "Those were my friends. Particularly the 2nd 1 there"

    def test_second_one_ordinals_disabled(self):
        result = convert(
            "Those were my friends. Particularly the second one there",
            convert_ordinals=False,
        )
        assert result == "Those were my friends. Particularly the second 1 there"

    def test_add_ordinal_ending_does_not_crash(self):
        """Used to raise TypeError: can only concatenate str (not "NoneType") to str."""
        result = convert("look at the second one", convert_ordinals=True, add_ordinal_ending=True)
        assert "2nd" in result
        assert "1" in result


# ---------------------------------------------------------------------------
# Numbers with punctuation (comma-thousands, embedded dots) pass through
# ---------------------------------------------------------------------------


class TestPunctuationInNumbers:
    """
    Inputs like 'r.23,813' or 'Er...23,813,' used to be partially consumed,
    producing wrong output.  They should always be returned verbatim.
    """

    def test_leading_letter_dot_number(self):
        assert convert("r.23,813 ") == "r.23,813 "

    def test_ellipsis_before_number_with_comma(self):
        assert convert("Er...23,813, Archchancellor, said the Bursar.") == (
            "Er...23,813, Archchancellor, said the Bursar."
        )

    def test_comma_thousands_separator_unchanged(self):
        assert convert("23,813") == "23,813"

    def test_comma_thousands_large(self):
        assert convert("1,000,000") == "1,000,000"

    def test_comma_thousands_in_sentence(self):
        assert convert("there are 23,813 items") == "there are 23,813 items"


# ---------------------------------------------------------------------------
# Hyphen-separated numbers (dates, ranges) used to lose all but the last part
# ---------------------------------------------------------------------------


class TestHyphenSeparatedNumbers:
    """
    '11-08-1998' used to return '1998' and '1939-45' used to return '45'
    because hyphens between digits were treated as word-number separators.
    """

    def test_full_date(self):
        assert convert("11-08-1998") == "11-08-1998"

    def test_year_range(self):
        assert convert("1939-45") == "1939-45"

    def test_iso_date(self):
        assert convert("2020-01-15") == "2020-01-15"

    def test_hyphenated_word_numbers_still_work(self):
        """Hyphens between letters should still be treated as separators."""
        assert convert("forty-two") == "42"
        assert convert("twenty-one") == "21"

    def test_hyphen_between_digit_and_letter_unchanged(self):
        assert convert("0.5-1") == "0.5-1"


# ---------------------------------------------------------------------------
# Comma-separated numbers in a list are not combined
# ---------------------------------------------------------------------------


class TestCommaListOfNumbers:
    """
    'three, four, 500' inside a sentence used to be merged into a single
    large number on some versions.  Each number should be converted
    independently because the commas break the token stream.
    """

    def test_comma_separated_small_numbers(self):
        result = convert("So we would have three, four, 500 black farmers")
        assert result == "So we would have 3, 4, 500 black farmers"

    def test_comma_list_not_multiplied(self):
        """Ensure no large-scale multiplication occurs (old bug: 6*2020=12120)."""
        assert convert("three, four, 500") == "3, 4, 500"

    def test_two_comma_numbers_unchanged(self):
        assert convert("6, 2020") == "6, 2020"

    def test_two_comma_numbers_unchanged_variant(self):
        assert convert("6, 1010") == "6, 1010"


# ---------------------------------------------------------------------------
# Known limitation: non-standard English without scale word "hundred"
# ---------------------------------------------------------------------------


class TestNonStandardEnglishLimitation:
    """
    'fifty one thousand two forty eight' is non-standard English for 51 248.
    Standard English requires the word 'hundred': 'fifty one thousand
    two hundred forty eight'.  The algorithm produces 51 050 for the
    non-standard form; this test documents the current behaviour so that
    any future improvement is intentional.
    """

    def test_standard_form_correct(self):
        assert convert("fifty one thousand two hundred forty eight") == "51248"

    def test_non_standard_form_current_behaviour(self):
        # Non-standard English: no 'hundred' between 'two' and 'forty eight'.
        # Documents current output; update this if the algorithm is improved.
        assert convert("fifty one thousand two forty eight") == "51050"
