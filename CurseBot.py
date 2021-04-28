import discord
import os
from dotenv import load_dotenv
import numpy as np
import random

client = discord.Client()


class WORD:
    VERB = 0
    NOUN = 1
    ADJECTIVE = 2
    ADVERB = 3


class word:
    def __init__(self, Word, mType, before, after, GlDict):
        self.word = Word
        self.type = mType
        self.before = before
        self.after = after
        self.dict = GlDict

    def getbefore(self, desiredType):
        value = -1
        for i in self.before.keys():
            if value == -1 or (value > self.before[i] + random.randint(-5, 5) and self.dict[i].type == desiredType):
                word = i
                value = self.before[i]
        return word

    def getAfter(self, desiredType):
        value = -1
        for i in self.after.keys():
            if value == -1 or (value > self.after[i] + random.randint(-5, 5) and self.dict[i].type == desiredType):
                word = i
                value = self.after[i]
        return word

    def AddBefore(self, Word):
        if Word in self.before.keys():
            self.before[Word] = self.before[Word] + 1
        else:
            self.before[Word] = 1

    def AddAfter(self, Word):
        if Word in self.after.keys():
            self.after[Word] = self.after[Word] + 1
        else:
            self.after[Word] = 1



words_roast = open('words_roast.txt', encoding='utf8').read()
words_meme = open('words_meme.txt', encoding='utf8').read()
#words_jokes = open('Jokes2.txt', encoding='utf8').read()
curses = open('swears.txt', encoding='utf8').read()
corpus = words_meme.split()
corpus += words_roast.split()
#corpus += words_jokes.split()
curses = curses.split()

verbs = open('verbs.txt', encoding='utf8').read()
nouns = open('nouns.txt', encoding='utf8').read()
adjectives = open('adjectives.txt', encoding='utf8').read()
adverbs = open('adverbs.txt', encoding='utf8').read()

verbs = verbs.split()
for v in range(len(verbs)):
    verbs[v] = verbs[v].lower()

nouns = nouns.split()
for n in range(len(nouns)):
    nouns[n] = nouns[n].lower()

adjectives = adjectives.split()
for a in range(len(adjectives)):
    adjectives[a] = adjectives[a].lower()

adverbs = adverbs.split()
for a in range(len(adverbs)):
    adverbs[a] = adverbs[a].lower()

structure = [WORD.NOUN, WORD.ADVERB, WORD.VERB, WORD.ADJECTIVE]

# structure = [WORD.NOUN, WORD.ADVERB, WORD.VERB, WORD.ADJECTIVE, WORD.NOUN, WORD.VERB]
punc = '''!()-[]{};:'"“|\, <>./?@#$%^&*_~123456789'''
for i in range(len(corpus)):
    for j in corpus[i]:
        if j in punc:
            corpus[i] = corpus[i].replace(j, "")
    corpus[i] = corpus[i].lower().strip()
while "" in corpus:
    corpus.remove("")

def findWordType(word):
    global verbs,adjectives,nouns,adverbs

    wordType = -1
    if word in verbs:
        wordType = WORD.VERB
    elif word in adjectives:
        wordType = WORD.ADJECTIVE
    elif word in adverbs:
        wordType = WORD.ADVERB
    else:
        wordType = WORD.NOUN
    return wordType


def make_pairs(corpus):
    for i in range(len(corpus) - 1):
        yield (corpus[i], corpus[i + 1])


word_dict = {}
pairs = make_pairs(corpus)
for word_1, word_2 in pairs:
    if word_1 != 'page' and word_2 != 'page':
        if word_1 in word_dict.keys():
            word_dict[word_1].AddAfter(word_2)
        else:
            word_dict[word_1] = word(word_1, findWordType(word_1), {}, {}, word_dict)
            word_dict[word_1].AddAfter(word_2)

        if word_2 in word_dict.keys():
            word_dict[word_2].AddBefore(word_1)
        else:
            word_dict[word_2] = word(word_2, findWordType(word_2), {}, {}, word_dict)
            word_dict[word_2].AddBefore(word_1)


def talkback(sent):
    temp = sent.lower().split()

    if len(temp) > 1:
        myIn = make_pairs(temp)
        value = -1
        first_word = np.random.choice(corpus)

        for word_1, word_2 in myIn:
            if word_1 in word_dict.keys() and word_2 in word_dict[word_1].after.keys():
                if value == -1 or value > word_dict[word_1].after[word_2]:
                    first_word = word_2
                    value = word_dict[word_1].after[word_2]
    else:
        myIn = temp
        if myIn[0] in word_dict.keys():
            first_word = myIn[0]
        else:
            first_word = np.random.choice(corpus)

    chain = [first_word]

    prewords = random.randint(1, 10)
    postwords = random.randint(1, 10)

    for i in range(prewords):
        if chain[-1] in word_dict.keys() and len(word_dict[chain[-1]].before) > 0:
            temp = structure.index(word_dict[chain[-1]].type)
            word = word_dict[chain[-1]].getbefore(structure[(temp - 1) % len(structure)])
        else:
            word = np.random.choice(corpus)
        chain.append(word)
    chain.reverse()
    j = 0
    while True:

        if chain[-1] in word_dict.keys() and len(word_dict[chain[-1]].after) > 0:
            temp = structure.index(word_dict[chain[-1]].type)
            word = word_dict[chain[-1]].getAfter(structure[(temp + 1) % len(structure)])
        else:
            word = np.random.choice(corpus)
        chain.append(word)

        j += 1
        if (j > postwords and findWordType(word) == WORD.NOUN) or j > 50:
            break

    for i in range(len(chain)):
        for j in curses:
            chain[i] = chain[i].replace(j, "bleep")

    chain[0] = chain[0].capitalize()
    chain[-1] += '.'

    return (' '.join(chain))


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if(str(message.channel) != "general" and str(message.channel) != "memes-and-stuff"):
        roast = talkback(message.content)

        await message.channel.send(roast)





load_dotenv()

token = os.getenv('TOKEN')
client.run(token)
