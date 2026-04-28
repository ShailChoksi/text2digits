## Installation
```
pip3 install text2digits
```

## Usage
Python 3 only!
```
from text2digits import text2digits
t2d = text2digits.Text2Digits()
t2d.convert("twenty ten and twenty one")
> 2010 and 21
```

It can handle a variety of phrases. Spoken/Informal and formal language:

```
"A random string" -> 'A random string'
"I am thirty six years old with a child that is four. I would like to get him four cars!" -> 'I am 36 years old with a child that is 4. I would like to get him 4 cars!'
"I was born in twenty ten" -> 'I was born in 2010'
"I was born in nineteen sixty four" -> 'I was born in 1964'
"I am the fourth cousin" -> 'I am the 4 cousin'
"I am twenty nine" -> 'I am 29'
"it was twenty ten and was negative thirty seven degrees" -> 'it was 2010 and was negative 37 degrees'
"thirty twenty one" -> '3021'
"one thousand six hundred sixty six" -> '1666'
"one thousand and six hundred and sixty six" -> '1666'
"sixteen sixty six" -> '1666'
"eleven hundred twelve" -> '1112'
"Sixteen and seven" -> '16 and 7'
"twenty ten and twenty one" -> '2010 and 21'
"I was born in nineteen ninety two and am twenty six years old!" -> 'I was born in 1992 and am 26 years old!'
"three forty five" -> '345'
```

I find this useful if using Alexa/Lex to convert audio to text and have to convert the text to digits.

## Known Limitations
- **Negative numbers:** the word `"negative"` is preserved as-is rather than being converted to a unary minus (e.g. `"negative five"` → `"negative 5"`, not `"-5"`).
- **Ordinal-to-digit conversion is lossy by default:** ordinal suffixes are dropped unless `add_ordinal_ending=True` is passed (e.g. `"third"` → `"3"`, not `"3rd"`).

## What Is Supported
- Decimal literals adjacent to scale words: `"2.5 thousand"` → `"2500"`, `"1.2345 hundred"` → `"123.45"`
- Indian number system scales: lakh, crore, arab, kharab
- Ordinals: first, second, …, twentieth, hundredth, thousandth, …
- Spelling correction via `similarity_threshold` parameter
- Year-style concatenation: `"twenty ten"` → `"2010"`

## Acknowledgements
I have heavily used code from the SO answers from here: https://stackoverflow.com/questions/493174/is-there-a-way-to-convert-number-words-to-integers
and improved upon them