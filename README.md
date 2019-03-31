## Installation
```
pip3 install text2digits
```

## Usage
Python 3 only!
```
from text2digits import text2digits
t2d = text2digits.Text2Digits()
tests = [
    "A random string",
    "I am thirty six years old with a child that is four. I would like to get him four cars!",
    "I was born in twenty ten",
    "I was born in nineteen sixty four",
    "I am the fourth cousin",
    "I am twenty nine",
    "it was twenty ten and was negative thirty seven degrees",
    "thirty twenty one",
    "one thousand six hundred sixty six",
    "one thousand and six hundred and sixty six",
    "sixteen sixty six",
    "eleven hundred twelve",
    "Sixteen and seven",
    "twenty ten and twenty one",
    "I was born in nineteen ninety two and am twenty six years old!",
    "three forty five"
]

for test in tests:
    print("output: '{}'".format(t2d.convert(test)))
```

Output:
```
output: 'a random string'
output: 'i am 36 years old with a child that is 4. i would like to get him 4 cars!'
output: 'i was born in 2010'
output: 'i was born in 1964'
output: 'i am the 4 cousin'
output: 'i am 29'
output: 'it was 2010 and was negative 37 degrees'
output: '3021'
output: '1666'
output: '1666'
output: '1666'
output: '1112'
output: '16 and 7'
output: '2010 and 21'
output: 'i was born in 1992 and am 26 years old!'
output: '345'
```

I find this useful if using Alexa/Lex to convert audio to text and have to convert the text to digits.

## Improvements/Issues
- Still need to add support for decimal numbers
- Need to add support for negative numbers

## Acknowledgements
I have heavily used code from the SO answers from here: https://stackoverflow.com/questions/493174/is-there-a-way-to-convert-number-words-to-integers
and improved upon them