UNITS = [
    'zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight',
    'nine', 'ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen',
    'sixteen', 'seventeen', 'eighteen', 'nineteen',
]
TENS = [
    'ten', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety'
]
SCALES = ['hundred', 'thousand', 'million', 'billion', 'trillion']
ORDINAL_WORDS = {'oh': 0, 'first': 1, 'second': 2, 'third': 3, 'fifth': 5, 'eighth': 8, 'ninth': 9, 'twelfth': 12}
ORDINAL_ENDINGS = [('ieth', 'y'), ('th', '')]


class Text2Digits():
    def __init__(self, excluded_chars=""):
        self.excluded = excluded_chars
        self.accepted = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 "
        self.numwords = dict()

        self.numwords['and'] = (1, 0)
        for idx, word in enumerate(UNITS): self.numwords[word] = (1, idx)
        for idx, word in enumerate(TENS): self.numwords[word] = (1, (idx+1) * 10)
        for idx, word in enumerate(SCALES): self.numwords[word] = (10 ** (idx * 3 or 2), 0)

        print(self.numwords)


    def convert(self, phrase):
        substr_arr, punctuation_arr = self.get_substr_punctuation(phrase)
        digits_arr = []

        for substr in substr_arr:
            digits_arr.append(self.convert_to_digits(substr))

        # Recreate the phrase by zipping the converted phrases with the punctuations
        digits_phrase = "".join([sstr + punct + " " for sstr, punct in zip(digits_arr, punctuation_arr)])

        return digits_phrase.strip()

    """
    This function takes in a phrase and outputs an array of substring split by punctuation and an array of
    all the punctuations that were stripped out
    """
    def get_substr_punctuation(self, phrase):
        substr_arr = []
        punctuation_arr = []
        substr = ""
        strlen = len(phrase)
        count = 0

        for char in phrase:
            count += 1
            if char in (self.accepted + self.excluded):
                substr += char
            else:
                substr_arr.append(substr)
                punctuation_arr.append(char)
                substr = ""

            # when there is no punctuation in a sentence
            if count == strlen and substr:
                substr_arr.append(substr)
                punctuation_arr.append("")

        return substr_arr, punctuation_arr

    """
    Modified version of answers from: 
    https://stackoverflow.com/questions/493174/is-there-a-way-to-convert-number-words-to-integers
    """

    def convert_to_digits(self, textnum):
        textnum = textnum.replace('-', ' ')
        current = result = word_count = 0
        curstring = ''
        onnumber = lastunit = lastscale = is_tens = False
        total_words = len(textnum.split())

        for word in textnum.split():
            word_count += 1
            word = word.lower()
            if word in ORDINAL_WORDS:
                scale, increment = (1, ORDINAL_WORDS[word])
                current = current * scale + increment
                if scale > 100:
                    result += current
                    current = 0
                onnumber = True
                lastunit = lastscale = is_tens = False

            else:
                for ending, replacement in ORDINAL_ENDINGS:
                    if word.endswith(ending) and (word[:-len(ending)] in UNITS or word[:-len(ending)] in TENS):
                        word = "%s%s" % (word[:-len(ending)], replacement)

                # Is not a number word
                if (not self.is_numword(word)) or (word == 'and' and not lastscale):
                    if onnumber:
                        # Flush the current number we are building
                        curstring += repr(result + current) + " "
                    curstring += word

                    if word_count != total_words:
                        curstring += " "

                    result = current = 0
                    onnumber = False
                    lastunit = False
                    lastscale = False
                    is_tens = False

                # Is a number word
                else:
                    scale, increment = self.from_numword(word)
                    onnumber = True

                    # For cases such as twenty ten -> 2010, twenty nineteen -> 2019

                    if is_tens and (word not in UNITS or word == "ten"):
                        curstring += repr(result + current)
                        result = current = 0

                    if lastunit and (word not in SCALES):
                        # Assume this is part of a string of individual numbers to
                        # be flushed, such as a zipcode "one two three four five"
                        curstring += repr(result + current)
                        result = current = 0

                    if scale > 1:
                        current = max(1, current)

                    current = current * scale + increment
                    if scale > 100:
                        result += current
                        current = 0

                    lastscale = False
                    lastunit = False
                    if word in SCALES:
                        lastscale = True
                    elif word in UNITS:
                        lastunit = True
                    elif word in TENS:
                        is_tens = True


        if onnumber:
            curstring += repr(result + current)

        return curstring

    def is_numword(self, x):
        if self.is_number(x):
            return True
        if x in self.numwords:
            return True
        return False

    def from_numword(self, x):
        if self.is_number(x):
            scale = 0
            increment = int(x.replace(',', ''))
            return scale, increment
        return self.numwords[x]

    def is_number(self, x):
        if type(x) == str:
            x = x.replace(',', '')
        try:
            float(x)
        except:
            return False
        return True

if __name__ == '__main__':
    t2n = Text2Digits()
    tests = [
        # "A random string",
        "I am thirty six years old with a child that is four. I would like to get him four cars!",
        "I was born in twenty ten",
        "I was born in nineteen sixty four",
        "I am the fourth cousin",
        "I am twenty nine",
        "it was twenty ten and was negative thirty seven degrees",
        "thirty twenty one",
        "one thousand six hundred sixty six",
        "one thousand and six hundred and sixty six",
        "Sixteen and seven",
        "twenty ten and twenty one",
        "I was born in nineteen ninety two and am twenty six years old!"
    ]

    for test in tests:
        print("output: '{}'".format(t2n.convert(test)))