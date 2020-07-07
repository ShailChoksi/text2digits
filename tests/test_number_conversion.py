import pytest

from text2digits import text2digits


@pytest.mark.parametrize("input_text", [
    "A random string",
    "Hello world. How are you?",
])
def test_str_unchanged_if_no_numbers(input_text):
    t2d_default = text2digits.Text2Digits()
    result = t2d_default.convert(input_text)
    assert result == input_text  # unchanged


@pytest.mark.parametrize("input_text,expected", [
    ("one thousand six hundred sixty six", "1666"),
    ("one thousand and six hundred and sixty six", "1666"),
    ("ten thousand one", "10001"),
    ("ten thousand fifty", "10050"),
    ("ten thousand", "10000"),
    ("hundred thousand", "100000"),
    ("one hundred thousand", "100000"),
    ("fifty five thousand", "55000"),
    ("thousand million", "1000000000"),
    ("two thousand hundred", "2000100"),
    ("I am twenty nine", "I am 29"),
    ("I am thirty six years old with a child that is four. I would like to get him four cars!", "I am 36 years old with a child that is 4. I would like to get him 4 cars!"),
    ("I am the fourth cousin", "I am the 4 cousin"),
    ("forty-two", "42"),
    ("forty_two", "42"),
])
def test_positive_integers(input_text, expected):
    t2d_default = text2digits.Text2Digits()
    result = t2d_default.convert(input_text)
    assert result == expected


@pytest.mark.parametrize("input_text,expected", [
    ("I was born in twenty ten", "I was born in 2010"),
    ("I was born in nineteen sixty four", "I was born in 1964"),
    ("thirty twenty one", "3021"),
    ("sixteen sixty six", "1666"),
    ("twenty nineteen", "2019"),
    ("twenty twenty", "2020"),
    ("fifty one thirty three", "5133"),
    ("fifty five twelve", "5512"),
    ("thirty eleven", "3011"),
    ("sixty six ten", "6610"),
])
def test_years(input_text, expected):
    t2d_default = text2digits.Text2Digits()
    result = t2d_default.convert(input_text)
    assert result == expected


@pytest.mark.parametrize("input_text, expected", [
    ("it was twenty ten and was negative thirty seven degrees", "it was 2010 and was negative 37 degrees"),
    ("I was born in nineteen ninety two and I am twenty six years old!", "I was born in 1992 and I am 26 years old!"),
    ("asb is twenty two altogether fifty five twelve parrot", "asb is 22 altogether 5512 parrot"),
    ("twenty eleven zero three", "201103"),
])
def test_multiple_types_of_numbers(input_text, expected):
    t2d_default = text2digits.Text2Digits()
    result = t2d_default.convert(input_text)
    assert result == expected


@pytest.mark.parametrize("input_text,expected", [
    ("eleven hundred twelve", "1112"),
    ("Sixteen and seven", "16 and 7"),
    ("twenty ten and twenty one", "2010 and 21"),
    ("three forty five", "345"),
    ("nineteen", "19"),
    ("ninteen", "ninteen"),
    ("nintteen", "nintteen"),
    ("ninten", "ninten"),
    ("ninetin", "ninetin"),
    ("ninteen nineti niine", "ninteen nineti niine"),
    ("sixty six hundred", "6600"),
    ("one two zero three", "1203"),
    ("one fifty one twenty one", "15121"),
    ("zero twelve", "012"),
    ("twelve zero nine", "1209"),
    ("twenty eleven three", "20113"),
    ("hundred and two", "102"),
])
def test_others(input_text, expected):
    t2d_default = text2digits.Text2Digits()
    result = t2d_default.convert(input_text)
    assert result == expected


@pytest.mark.parametrize("input_text,expected", [
    ("ninteen", "19"),
    ("nintteen", "19"),
    ("ninten", "ninten"),
    ("ninetin", "90"),
    ("ninteen nineti niine", "1999"),
])
def test_spelling_correction(input_text, expected):
    t2d_default = text2digits.Text2Digits(similarity_threshold=0.7)
    result = t2d_default.convert(input_text)
    assert result == expected


@pytest.mark.parametrize("input_text,expected", [
    ("forty two,  two. 0.5-1", "42,  2. 0.5-1"),
    ("1,000 million", "1000000000"),
    ("1,000", "1,000"),
    ("1,000 pounds", "1,000 pounds"),
    ("10,  20 2.0", "10,  20 2.0"),
    ("2.5 thousand", "2500"),
    ("1.2345 hundred", "123.45"),
    ("twenty 1.0", "20 1.0"),
    ("100 and two", "102"),
    ('6 2020', '6 2020'),
])
def test_number_literals(input_text, expected):
    t2d_default = text2digits.Text2Digits()
    result = t2d_default.convert(input_text)
    assert result == expected


@pytest.mark.parametrize("ordinal_input,convert_ordinals,add_ordinal_ending,expected", [
    ("third", True, False, "3"),
    ("third", False, False, "third"),
    ("third", True, True, "3rd"),
    # ordinal ending "st"
    ("twenty-first", True, False, "21"),
    ("twenty-first", False, False, "twenty-first"),
    ("twenty-first", True, True, "21st"),
    # ordinal ending "nd"
    ("thirty-second", True, False, "32"),
    ("thirty-second", False, False, "thirty-second"),
    ("thirty-second", True, True, "32nd"),
    # ordinal ending "rd"
    ("forty-third", True, False, "43"),
    ("forty-third", False, False, "forty-third"),
    ("forty-third", True, True, "43rd"),
    # ordinal ending "th"
    ("tenth", True, False, "10"),
    ("tenth", False, False, "tenth"),
    ("tenth", True, True, "10th"),
    ("fifty-fourth", True, False, "54"),
    ("fifty-fourth", False, False, "fifty-fourth"),
    ("fifty-fourth", True, True, "54th"),
    # ordinal ending "ieth"
    ("twentieth", True, False, "20"),
    ("twentieth", False, False, "twentieth"),
    ("twentieth", True, True, "20th"),
    ("seventieth", True, False, "70"),
    ("seventieth", False, False, "seventieth"),
    ("seventieth", True, True, "70th"),
    # 100, 1000, 10000, etc.
    ("hundredth", True, False, "100"),
    ("hundredth", False, False, "hundredth"),
    ("hundredth", True, True, "100th"),
    ("seven-hundredth", True, False, "700"),
    ("seven-hundredth", False, False, "seven-hundredth"),
    ("seven-hundredth", True, True, "700th"),
    ("thousandth", True, False, "1000"),
    ("thousandth", False, False, "thousandth"),
    ("thousandth", True, True, "1000th"),
    ("ten-thousandth", True, False, "10000"),
    ("ten-thousandth", False, False, "ten-thousandth"),
    ("ten-thousandth", True, True, "10000th"),
    ("two-hundred-thousandth", True, False, "200000"),
    ("two-hundred-thousandth", False, False, "two-hundred-thousandth"),
    ("two-hundred-thousandth", True, True, "200000th"),
    ("millionth", True, False, "1000000"),
    ("millionth", False, False, "millionth"),
    ("millionth", True, True, "1000000th"),
    ("millionth", False, True, "1000000th"),
])
def test_ordinal_conversion_switch_disabled(ordinal_input, convert_ordinals, add_ordinal_ending, expected):
    input_str = "she was the {} to finish the race"
    t2d_default = text2digits.Text2Digits(convert_ordinals=convert_ordinals, add_ordinal_ending=add_ordinal_ending)
    result = t2d_default.convert(input_str.format(ordinal_input))
    assert result == input_str.format(expected)


@pytest.mark.parametrize("ordinal_input,convert_ordinals,add_ordinal_ending,expected", [
    ("eighth", True, False, "8"),
    ("eighth", False, False, "eighth"),
    ("eighth", True, True, "8th"),
    ("ninety-seventh", True, False, "97"),
    ("ninety-seventh", False, False, "ninety-seventh"),
    ("ninety-seventh", True, True, "97th"),
])
def test_ordinal_at_the_end_of_the_sentence(ordinal_input, convert_ordinals, add_ordinal_ending, expected):
    input_str = "she finished {}"
    t2d_default = text2digits.Text2Digits(convert_ordinals=convert_ordinals, add_ordinal_ending=add_ordinal_ending)
    result = t2d_default.convert(input_str.format(ordinal_input))
    assert result == input_str.format(expected)


def test_ordinal_multi_occurrence_and_cardinal():
    # using two ordinal numbers with different endings ("th" and "nd")
    # and a cardinal number in the middle
    input_str = "she finished sixty-fourth on race number six and he finished forty-second"
    t2d_default = text2digits.Text2Digits(convert_ordinals=True, add_ordinal_ending=True)
    result = t2d_default.convert(input_str)
    assert result == "she finished 64th on race number 6 and he finished 42nd"


@pytest.mark.parametrize("input_text,expected_output", [
    ('its 07', 'its 07'),
    ('its 007', 'its 007'),
    ('its 15:01', 'its 15:01'),
    ('when I was eleven, I used to sleep at 23:01', 'when I was 11, I used to sleep at 23:01'),
    ('when I was eleven, I used to sleep at 02:01', 'when I was 11, I used to sleep at 02:01'),
    ('at 00:00 I will turn 15', 'at 00:00 I will turn 15'),
    ('at 03:03 I will turn 15', 'at 03:03 I will turn 15'),
])
def test_time_formats(input_text, expected_output):
    t2d_default = text2digits.Text2Digits()
    result = t2d_default.convert(input_text)
    assert result == expected_output


@pytest.mark.parametrize("input_text,expected_output", [
    ('it is january or jan for short', 'it is 1 or 1 for short'),
    ('it is february or feb for short', 'it is 2 or 2 for short'),
    ('it is march or mar for short', 'it is 3 or 3 for short'),
    ('it is april or apr for short', 'it is 4 or 4 for short'),
    ('it is may or may for short', 'it is 5 or 5 for short'),
    ('it is june or jun for short', 'it is 6 or 6 for short'),
    ('it is july or jul for short', 'it is 7 or 7 for short'),
    ('it is august or aug for short', 'it is 8 or 8 for short'),
    ('it is september or sep for short', 'it is 9 or 9 for short'),
    ('it is october or oct for short', 'it is 10 or 10 for short'),
    ('it is november or nov for short', 'it is 11 or 11 for short'),
    ('it is december or dec for short', 'it is 12 or 12 for short'),
    ('i was born on july four, 1776', 'i was born on 7 4, 1776'),
])
def test_month_formats(input_text, expected_output):
    t2d_default = text2digits.Text2Digits()
    result = t2d_default.convert(input_text)
    assert result == expected_output