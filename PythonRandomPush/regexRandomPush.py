## print(2) ## Quick test to check virtualenv's virtual environment.

'''
Stanford NLP main page: http://stanfordnlp.github.io/CoreNLP/
Setting up CoreNLP  Server: http://stanfordnlp.github.io/CoreNLP/corenlp-server.html#getting-started
Running pycorenlp: https://github.com/smilli/py-corenlp
'''

from pycorenlp import StanfordCoreNLP
import json
from pprint import pprint
from functools import reduce
import re
import os

'''
To run CoreNLP server:
cd to CoreNLP folder
java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer
'''

## Pass in the url of the server
nlp = StanfordCoreNLP('http://localhost:9000')


## Read the text file.
file = open('data/classBios2.txt')
inputText = file.read()
# print("filname is: {}".format(file))
# print(file.read())

## Seems like the text file is way too big, split sentences for every bio by itself
## It seems like a valid separator would be "==>"

inputText = re.sub(' +', ' ', inputText)
inputText = re.sub('==>', '*', inputText) ### Delimiter
inputText = re.sub('[^A-Za-z0-9\,\.\*]+', ' ', inputText) ### @TRY to remove optional characters - THAT WAS THE WHOLE DEAL?>?????
# print(inputText)
inputText = os.linesep.join([s for s in inputText.splitlines() if s])
listOfBios = inputText.split("*")
listOfBios = listOfBios[1:]
# listOfBios = listOfBios[0:2]
allBios = []
print(len(listOfBios))





for index, bio in enumerate(listOfBios):
    ### NLPCORE stuff
    print("************ RUNNING FOR BIO NUMBER {}************".format(index))
    # print(bio)
    jsonOutput = nlp.annotate(bio, properties={
      'annotators': 'ssplit',
      'outputFormat': 'json'
    })
    # print(jsonOutput)
    # print(type(jsonOutput))

    if type(jsonOutput) is str:
        print("IS OF TYPE STRING")
        print(json.loads(jsonOutput))

    print("\n\n\n")
    #
    sentences = jsonOutput.get("sentences")
    listCleanSentencesForOneBio = []
    # pprint(sentences)
    for i in range(0, len(sentences)):
        #### access the individual tokens and put that in a list (specific to current bio)
        listTokens = sentences[i].get('tokens')
        getValues = lambda key, inputSentence: [subDict[key] for subDict in inputSentence if key in subDict]
        listCleanSentencesForOneBio.append(' '.join(getValues('word', listTokens)))
        # print(getValues('word', listTokens))
        # print(i)
        # print('************')
    # print(listCleanSentences)
    ### Add list of sentences for this bio to the list of all bios (broken down to sentences)
    allBios.append(listCleanSentencesForOneBio)

# pprint(allBios)
# print(allBios[0])

"""
Regex comments:
    - (?...)
    This is an extension notation (a '?' following a '(' is not meaningful otherwise).
     The first character after the '?' determines what the meaning and further syntax of the construct is.


    - (?:...) ---> A non capturing version of regular parentheses. Matches whatever pattern is inside the
    parenth. Substring matched by the group cannot be retrieved after performing a match or referenced later in the pattern

    -(?=\D|$): Anything but a digit or end of sentence.



"""

#### Regex strings:
### Regex string has to be on the same line
# For monthAndYear, simplified so that Feb, February, Feb. and February. will be accepted.
# For simplification now, first letter of months has to be uppercase.

## To simplify things by quite a bite, could have instead transformed all the text to lower-case
## Instead of considering words that are both upper or lowercase.
seasonsAndPeriodRegex = r"(F|f)all|(S|s)ummer|(W|w)inter|(S|s)pring"
monthDayYearRegex = r"\b(?:(0?[1-9]|1[0-2])(/|-|:))(?:(0?[1-9]|[1-2][0-9]|3[0-1])(/|-|:))?(?:18|19[7-9]\d|2\d{3})(?=\D|$)\b"  ## Don't need to make non controlling groups
dayMonthYearRegex = r"\b(?:(0?[1-9]|[1-2][0-9]|3[0-1])(/|-|:))?(?:(0?[1-9]|1[0-2])(/|-|:))(?:18|19[7-9]\d|2\d{3})(?=\D|$)\b"  ## Don't need to make non controlling groups
monthAndYearRegex = r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|(Nov|Dec)(?:ember)?(\s)?)(?:(18|19[0-9]\d|2\d{3}))?"
yearRegex = r"(?:(18|19[0-9]\d|2\d{3}))"
dayRegex = r"\b((0?[1-9])|([1-2][0-9])|(3[0-1]))(st|th|rd|nd)?\b"
## For dayMonthYear and monthDayYear: day is optional, but month and year have to appear
timeRegex = r"((0?[0-9]|1[0-9]|2[0-3])|(0[0-9]|1[0-2])):[0-5][0-9]" #for both 24hr and 12hr formats - for HH:MM
relativeTimeRegex = r"(N|n)ow|(l|L)ater|(s|S)oon|(D|d)uring|(I|i)n\sa\s(bit|while)|((I|i)n\sthe\s)?(past|future|present)|(A|a)t\sthis\smoment|(C|c)urrently|(T|t)o(night|morrow|day)|(A|a)fter|(B|b)efore"
moreRelativeRegex = r"((a|one|two|three|four|five|six|seven|eight|nine|ten|[1-9]{2})\s)?(week(day|end)?|day|night|month|year)(s)?(\sago)?"
daysRegex = "(Mon|Tues|Wednes|Thurs|Fri|Satur|Sun)day"
timeWordsRegex = "time|period|date|long|short|quick(ly)?|slow(ly)?|minute(s)?|second(s)?|hour(s)?"
# fullMonthDayYearRegex = r"October\s*0?1(st)?|2(nd)?|3(rd)?|[4-9](th)?"



### Problematic regexes:
"""
monthAndYearRegex - fixed
"""
classBios_timepoints = ""
count = 0
for oneBio in allBios:
    #print("****NEW BIO*****")
    for eachSentence in oneBio:
        ## let's try regexing:
        for regex in (seasonsAndPeriodRegex,moreRelativeRegex,dayRegex,
        dayMonthYearRegex,monthDayYearRegex,timeRegex,relativeTimeRegex,
        daysRegex,timeWordsRegex, yearRegex, monthAndYearRegex):
            if re.search(regex, eachSentence):
                # print(eachSentence)
                classBios_timepoints += eachSentence + "\n"
                count = count + 1
                break
print("*** TIMEPOINTS *****")
print(classBios_timepoints)
print("There were {} timepoints".format(count))

with open("classbios_timepoints.txt", "w") as text_file:
    text_file.write(classBios_timepoints)


###### TESTING INDIVIDUAL REGEXES
# for oneBio in allBios[:5]:
#     #print("****NEW BIO*****")
#     for eachSentence in oneBio:
#         ## let's try regexing:
#         if re.search(yearRegex, eachSentence):
#             print(eachSentence)
#
#



################################################################################
######################### SOME TEST CODE #######################################
################################################################################

# allRegexConcatenated =

### Join the regexes together

### @todo check a good way to add regexes together with or conditions
### it seems that the order in which a regex is added affects the match
# listRegex = []
# for regex in (seasonsAndPeriodRegex,moreRelativeRegex,monthAndYearRegex, dayRegex,
#     dayMonthYearRegex,monthDayYearRegex,timeRegex,relativeTimeRegex,
#     daysRegex,timeWordsRegex):
#     # Add a parenthese at the beginning and end of every regex
#     regex = "(" + regex + ")"
#     listRegex.append(regex)
#     # print(regex)
#
# # pprint(listRegex)
# fullRegex = "|".join(listRegex)
# print(fullRegex)
#
# testRegex = re.search(fullRegex,"Spring")
# print(testRegex)
#

# classBios_timepoints = ""
# for oneBio in allBios[:5]:
#     #print("****NEW BIO*****")
#     for eachSentence in oneBio:
#         ## let's try regexing:
#         for regex in (seasonsAndPeriodRegex,moreRelativeRegex,monthAndYearRegex, dayRegex,
#             dayMonthYearRegex,monthDayYearRegex,timeRegex,relativeTimeRegex,
#             daysRegex,timeWordsRegex):
#             if re.search(regex, eachSentence):
#                 # print(eachSentence)
#                 classBios_timepoints += eachSentence + "\n"
#                 break
# print("*** TIMEPOINTS *****")
# print(classBios_timepoints)


# for i in listOfBios[0:1]:
#     # print(i)
#     print("******")
#     jsonOutput = nlp.annotate(i, properties={
#       'annotators': 'ssplit',
#       'outputFormat': 'json'
#     })
#     print(jsonOutput)

# jsonOutput = nlp.annotate(, properties={
#   'annotators': 'ssplit',
#   'outputFormat': 'json'
# })
#
# print(jsonOutput)

#
#
# #### if you were to use lambda
# # getSentences = lambda dictKey, inputDict: inputDict.get(dictKey)
# # getListTokens = lambda dictKey, inputList: [tokenDict[dictKey] for tokenDict in inputList if dictKey in tokenDict]
# # getTokens = lambda key, outerList: [subDict[key] for subList in outerList for subDict in subList if key in subDict]
#
# # print(getSentences('sentences', jsonOutput))
# # print(getListTokens('tokens', getSentences('sentences', jsonOutput)))
# # print(getTokens('word',getListTokens('tokens', getSentences('sentences', jsonOutput))))
# # pprint(getListTokens('tokens', getSentences('sentences', jsonOutput)))
#
# # test = getListTokens('tokens', getSentences('sentences', jsonOutput))
# # for i  in range(len(test)):
# #     print(test[i])
# #     print('****')
#
# # print(output)
# # pprint(output)
#
# ### Instead of pprint, could use json.dumps()
# # json.dumps() serializes an obj to a JSON formatted string
# # print(output)
# # print('*****')
# # printjson.dumps(output, sort_keys = True,
# #                 indent = 4))
#
#
#
# # print(output['sentences'][0]['parse'])
#
# #################################################################################
# #### Could do it this way, did not need to tokenize and then reform the sentences.
# # output2 = nlp.annotate(text, properties = {
# #     'annotators': 'ssplit',
# #     'outputFormat': 'text'
# # })
# # splitOutput = output2.split("\n")
# # sentences = []
# # for sentence in splitOutput:
# #     if len(sentence) > 0:
# #         if sentence[0] != '[' and 'Sentence #' not in sentence:
# #             print(sentence)
# #             sentences.append(sentence)
# # print(sentences)
# #################################################################################
#
#
#
# #
# # print(output[1])

#
# # Read input.
# file = open('data/text.txt')
# text = file.read()
#
# nlpSentenceSplit = nlp.annotate(text, properties = {
#     'annotators': 'ssplit'
# })
#
# print(nlpSentenceSplit['sentences'][0])



# # Test with text from https://github.com/smilli/py-corenlp
# text = (
#   'Pusheen and Smitha walked along the beach. '
#   'Pusheen wanted to surf, but fell off the surfboard.')

# file = open('data/classBios.txt')
# inputText = file.read()
# # print("filname is: {}".format(file))
# # print(file.read())
#
# ## Seems like the text file is way too big, split sentences for every bio by itself
# ## It seems like a valid separator would be "==>"
#
#
#
# jsonOutput = nlp.annotate(inputText, properties={
#   'annotators': 'ssplit',
#   'outputFormat': 'json'
# })
# print(jsonOutput)
