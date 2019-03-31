## Installation
```
pip3 install text2digits
```

## Usage
Python 3 only!
```
from text2digits import text2digits
t2d = text2digits.Text2Digits()

print(t2d.convert("I was born in nineteen ninety two and am twenty six years old!"))
```

Output:
```
"i was born in 1992 and am 26 years old!"
```

I find this useful if using Alexa/Lex to convert audio to text and have to convert the text to digits.

## Improvements/Issues
- Still need to add support for decimal numbers
- Need to add support for negative numbers

## Acknowledgements
I have heavily used code from the SO answers from here: https://stackoverflow.com/questions/493174/is-there-a-way-to-convert-number-words-to-integers
and improved upon them