import pytest

from text2digits import text2digits


@pytest.mark.parametrize("ordinal_input,convert_ordinals,add_ordinal_ending,expected", [
    ('third', True, False, '3'),
    ('third', False, False, 'third'),
    ('third', True, True, '3rd'),
    # ordinal ending 'st'
    ('twenty-first', True, False, '21'),
    ('twenty-first', False, False, 'twenty-first'),
    ('twenty-first', True, True, '21st'),
    # ordinal ending 'nd'
    ('thirty-second', True, False, '32'),
    ('thirty-second', False, False, 'thirty-second'),
    ('thirty-second', True, True, '32nd'),
    # ordinal ending 'rd'
    ('forty-third', True, False, '43'),
    ('forty-third', False, False, 'forty-third'),
    ('forty-third', True, True, '43rd'),
    # ordinal ending 'th'
    ('fifty-fourth', True, False, '54'),
    ('fifty-fourth', False, False, 'fifty-fourth'),
    ('fifty-fourth', True, True, '54th'),
])
def test_ordinal_conversion_switch_disabled(ordinal_input, convert_ordinals, add_ordinal_ending, expected):

    input_str = "she was the {} to finish the race"
    t2d_default = text2digits.Text2Digits(convert_ordinals=convert_ordinals, add_ordinal_ending=add_ordinal_ending)
    result = t2d_default.convert(input_str.format(ordinal_input))
    assert result == input_str.format(expected)


@pytest.mark.parametrize("ordinal_input,convert_ordinals,add_ordinal_ending,expected", [
    ('eighth', True, False, '8'),
    ('eighth', False, False, 'eighth'),
    ('eighth', True, True, '8th'),
    ('ninety-seventh', True, False, '97'),
    ('ninety-seventh', False, False, 'ninety-seventh'),
    ('ninety-seventh', True, True, '97th'),
])
def test_ordinal_at_the_end_of_the_sentence(ordinal_input, convert_ordinals, add_ordinal_ending, expected):
    input_str = "she finished {}"
    t2d_default = text2digits.Text2Digits(convert_ordinals=convert_ordinals, add_ordinal_ending=add_ordinal_ending)
    result = t2d_default.convert(input_str.format(ordinal_input))
    assert result == input_str.format(expected)


def test_ordinal_multi_occurence_and_cardinal():
    # using two ordinal numbers with different endings ('th' and 'nd')
    # and a cardinal number in the middle
    input_str = "she finished sixty-fourth on race number six and he finished forty-second"
    t2d_default = text2digits.Text2Digits(convert_ordinals=True, add_ordinal_ending=True)
    result = t2d_default.convert(input_str)
    assert result == "she finished 64th on race number 6 and he finished 42nd"

