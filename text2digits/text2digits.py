import re
import math

UNITS = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
TEENS = ['ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen']
TENS = ['ten', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety']
SCALES = ['hundred', 'thousand', 'million', 'billion', 'trillion']
ORDINAL_WORDS = {'oh': 0, 'first': 1, 'second': 2, 'third': 3, 'fifth': 5, 'eighth': 8, 'ninth': 9, 'twelfth': 12}
ORDINAL_ENDINGS = [('ieth', 'y'), ('th', '')]


class TextPreprocessor:
    @staticmethod
    def bigram(word1, word2):
        '''
        Returns the bigram similarity of 2 words
        '''
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

    @staticmethod
    def get_similarity(item1, item2):
        '''
        Returns a number within the range (0,1) determining how similar
        item1 is to item2. 0 indicates perfect dissimilarity while 1
        indicates equality.
        '''
        return TextPreprocessor.bigram(item1, item2)
    
    @staticmethod
    def get_match(word, collection, threshold):
        '''
        Returns the most syntactically similar word in the collection
        to the specified word.
        '''
        match = None
        max_similarity = 0
        
        for item in collection:
            similarity = TextPreprocessor.get_similarity(word, item)
            if similarity > max(max_similarity, threshold):
                match = item
                max_similarity = similarity
                
        return match

    @staticmethod
    def split_glues(string, separator=r'\s+'):
        '''
        Splits a string and preserves the glue, i.e. the separator fragments.
        This is useful when words of a sentence should be processed while still
        keeping the possibility to recover the original sentence.

        :param string: The string to be split.
        :param separator: The separator to use for splitting (defaults to
        whitespace).
        :return: A generator yielding (match, glue) pairs, e.g. the word and
                 the whitespace next to it. If no glue is left, an empty string
                 is returned.
        '''
        while True:
            match = re.search(separator, string)
            if not match:
                # The last word does not have a glue
                yield string, ''
                break

            yield string[:match.start()], match.group()

            # Proceed with the remaining string
            string = string[match.end():]


class Text2Digits():
    def __init__(self, excluded_chars="", similarity_threshold=0.5):
        self.excluded = excluded_chars
        self.accepted = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 "
        self.numwords = dict()
        self.threshold = similarity_threshold

        self.numwords['and'] = (1, 0)
        for idx, word in enumerate(UNITS): self.numwords[word] = (1, idx)
        for idx, word in enumerate(TEENS): self.numwords[word] = (1, idx + 10)
        for idx, word in enumerate(TENS): self.numwords[word] = (1, (idx + 1) * 10)
        for idx, word in enumerate(SCALES): self.numwords[word] = (10 ** (idx * 3 or 2), 0)

    def convert(self, phrase, spell_check=False):
        substr_arr, punctuation_arr = self.get_substr_punctuation(phrase)
        digits_arr = []

        for substr in substr_arr:
            digits_arr.append(self.convert_to_digits(substr, spell_check))

        # Recreate the phrase by zipping the converted phrases with the punctuations
        digits_phrase = "".join([sstr + punct for sstr, punct in zip(digits_arr, punctuation_arr)])

        return digits_phrase

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

    def convert_to_digits(self, textnum, spell_check=False):
        textnum = textnum.replace('-', ' ')
        current = result = word_count = 0
        curstring = ''
        onnumber = lastunit = lastscale = is_tens = False
        last_number_glue = ''

        for word, glue in TextPreprocessor.split_glues(textnum):
            word_count += 1
            word_original = word
            word = word.lower()
            if word in ORDINAL_WORDS:
                scale, increment = (1, ORDINAL_WORDS[word])
                current = current * scale + increment
                if scale > 100:
                    result += current
                    current = 0
                onnumber = True
                last_number_glue = glue
                lastunit = lastscale = is_tens = False

            else:
                # Handle endings
                for ending, replacement in ORDINAL_ENDINGS:
                    if word.endswith(ending) and (word[:-len(ending)] in UNITS or word[:-len(ending)] in TENS):
                        word = "%s%s" % (word[:-len(ending)], replacement)

                # Handle misspelt words
                if spell_check:
                    matched_num = TextPreprocessor.get_match(word, self.numwords.keys(), self.threshold)
                    if matched_num is not None:
                        word = matched_num
                
                # Is not a number word
                if (not self.is_numword(word)) or (word == 'and' and not lastscale):
                    if onnumber:
                        # Flush the current number we are building
                        curstring += repr(result + current) + last_number_glue
                    curstring += word_original + glue

                    result = current = 0
                    onnumber = False
                    lastunit = False
                    lastscale = False
                    is_tens = False

                # Is a number word
                else:
                    scale, increment = self.from_numword(word)
                    onnumber = True
                    last_number_glue = glue

                    # For cases such as twenty ten -> 2010, twenty nineteen -> 2019
                    if is_tens and word not in (UNITS + SCALES):
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
                    is_tens = False
                    if word in SCALES:
                        lastscale = True
                    elif word in (UNITS + TEENS):
                        lastunit = True
                    elif word in TENS:
                        is_tens = True

        # Flush remaining number (in case the last word of a sentence corresponds to a number)
        if onnumber:
            curstring += repr(result + current) + last_number_glue

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
            x = float(x)

            if math.isnan(x) or math.isinf(x):
                return False
        except:
            return False
        return True


if __name__ == '__main__':
    t2n = Text2Digits(similarity_threshold=0.7)
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
        "three forty five",
        "nineteen",
        "ninteen",
        "nintteen",
        "ninten",
        "ninetin",
        "ninteen nineti niine",
        "forty two,  two. 0.5-1",
        "sixty six hundred",
        "one two zero three",
        "one fifty one twenty one",
        "twenty nineteen",
        "sixty six ten",
        "ten thousand one",
        "ten thousand fifty",
        "ten thousand",
        "hundred thousand",
        "one hundred thousand",
        "fifty five thousand",
        "fifty five twelve",
        "asb is twenty two altogether fifty five twelve parrot",
        "fifty one thirty three",
        "thirty eleven",
        "twenty eleven zero three",
        "zero twelve",
        "twelve zero nine",
        "twenty eleven three"
    ]

    for test in tests:
        print("\"" + test + "\" -> '" + t2n.convert(test, spell_check=True) + "'")
