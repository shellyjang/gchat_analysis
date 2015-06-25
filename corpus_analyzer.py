import matplotlib.pyplot as plt
import getpass, os
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import seaborn as sns
from copy import copy
from collections import OrderedDict
import nltk
# nltk.download('punkt')
from nltk.collocations import BigramCollocationFinder, TrigramCollocationFinder # QuadgramCollocationFinder
from nltk.collocations import BigramAssocMeasures, TrigramAssocMeasures
from nltk.tokenize import RegexpTokenizer
import operator, pickle

bigram_measures = BigramAssocMeasures()
trigram_measures = TrigramAssocMeasures()
tokenizer = RegexpTokenizer(r'\w+')

def word_bag(filename):
    f = open(filename, 'rb')
    words = []
    for line in f:
        line = line.split('|')[-1]
            
        words.append(line)
    f.close()
    
    words = ' '.join(words).lower()
    words = words.replace('\n','')
    return words

def tokens_(filename):
    words = word_bag(filename)
    tmp = tokenizer.tokenize(words)
    return tmp

def single_word_freq(filename):
    tmp = tokens_(filename)
    fd = nltk.FreqDist(tmp)
    fd_sorted = OrderedDict(sorted(fd.items(), key=lambda t: t[1], reverse=True))
    return fd_sorted

    
def bi_tri_gram(filename):
    tmp = tokens_(filename)
    tokens = nltk.wordpunct_tokenize(' '.join(tmp))
#     bigram_finder = BigramCollocationFinder.from_words(tokens)
#     bigram_scored = bigram_finder.score_ngrams(bigram_measures.raw_freq)
# #     bigram_sorted = sorted(bigram_scored, key=lambda tup: tup[1], reverse=True)
#     bigram_sorted = dict((item[0], item[1]) for item in bigram_scored)
#     bigram_sorted = OrderedDict(sorted(bigram_sorted.items(), key=lambda t: t[1], reverse=True))

#     trigram_finder = TrigramCollocationFinder.from_words(tokens)
#     trigram_scored = trigram_finder.score_ngrams(trigram_measures.raw_freq)
# #     trigram_sorted = sorted(bigram_scored, key=lambda tup: tup[1], reverse=True)
#     trigram_sorted = dict((item[0], item[1]) for item in trigram_scored)
#     trigram_sorted = OrderedDict(sorted(trigram_sorted.items(), key=lambda t: t[1], reverse=True))
    bgs, tgs = nltk.bigrams(tokens), nltk.trigrams(tokens)
    bg, tg = nltk.FreqDist(bgs), nltk.FreqDist(tgs)

    bigram_sorted = OrderedDict(sorted(bg.items(), key=lambda t: t[1], reverse=True))
    trigram_sorted = OrderedDict(sorted(tg.items(), key=lambda t: t[1], reverse=True))
    return (bigram_sorted, trigram_sorted)

def ordered_freq(corpus, initial, ngram='word_freq'):
    c = corpus[initial]
    c = c[ngram]
    o = OrderedDict(sorted(c.items(), key=lambda t: t[1], reverse=True))
    return o

def common_words(corpus, initial1, initial2, ngram='word'):
    '''
    corpus are a dictionary with keys 'word', 'bg', 'tg'
    Each value corresponding to the key are OrderedDict with 
    key = word/bg/tg
    value = raw_frequency/relative_frequency(for bg and tg)
    '''
    w1, w2 = ordered_freq(corpus, initial1, ngram), ordered_freq(corpus, initial2, ngram)
    return set.intersection(set(w1.keys()), set(w2.keys()))

def consolidate_freq_dict(corpus, list_of_freq_dicts, ngram='word'):
    ans = corpus[list_of_freq_dicts[0]][ngram]
    for item in list_of_freq_dicts[1:]:
        d = corpus[item][ngram]
        for (k, v) in d.iteritems():
            if k in ans:
                ans[k] += v
            else:
                ans[k] = v

    return ans

def common_words_v1(corpus, list1, list2, ngram='word'):
    '''
    corpus are a dictionary with keys 'word', 'bg', 'tg'
    Each value corresponding to the key are OrderedDict with 
    key = word/bg/tg
    value = raw_frequency/relative_frequency(for bg and tg)
    '''
    if type(list1) != list:
        list1 = [list1]
    if type(list2) != list:
        list2 = [list2]

    consolidated_dict1 = consolidate_freq_dict(corpus, list1, ngram)
    consolidated_dict2 = consolidate_freq_dict(corpus, list2, ngram)

    words1 = set(consolidated_dict1.keys())
    words2 = set(consolidated_dict2.keys())

    return set.intersection(words1, words2)

def word_rank(corpus, set_of_words, list1, ngram='word'):
    c = consolidate_freq_dict(corpus, list1, ngram)
    o = dict((word, c[word]) for word in set_of_words)
    o = OrderedDict(sorted(o.items(), key=lambda t: t[1]))
    o_rank = {}
    for (ii, k) in enumerate(o.iterkeys()):
        o_rank[k] = ii
    return o_rank

def word_rank_v1(corpus, set_of_words, list1, ngram='word'):
    c = consolidate_freq_dict(corpus, list1, ngram)
    k = pd.DataFrame.from_dict(c, orient='index')
    k = k.loc[list(set_of_words), :]
    k['rank'] = k.rank().astype(int)
    o_rank = k['rank'].to_dict()
    return o_rank

def compare_word_rank(corpus, list1, list2, set_of_words, ngram='word', threshold=0):
    o1, o2 = word_rank_v1(corpus, set_of_words, list1, ngram), word_rank_v1(corpus, set_of_words, list2, ngram)
    df = pd.DataFrame(columns=['word','o1_rank','o2_rank'])
    for (ii, word) in enumerate(set_of_words):
        df.loc[ii] = [word, o1[word], o2[word]]
    top_ = df[(df.o1_rank>threshold)&(df.o2_rank>threshold)]
    return top_

def biggest_divider(corpus, list1, list2, ngram='word', threshold=0, df=pd.DataFrame()):
    if df.shape == (0, 0):
        df = compare_word_rank_v1(corpus, list1, list2, common_words_v1(corpus, list1, list2, ngram), ngram, threshold)
    df['change'] = abs(df['o1_rank'] - df['o2_rank'])
    df['distance']= ( np.sqrt(2) / 2 ) * df['change']
    return df.sort(['distance'], ascending=False)

def more_1_than_2(bd):
    df = bd[bd['o1_rank'] > bd['o2_rank']]
    df = df.sort(['o1_rank'], ascending=True)
    return df

def more_2_than_1(bd):
    df = bd[bd['o1_rank'] < bd['o2_rank']]
    df = df.sort(['o2_rank'], ascending=True)
    return df

def plot_ranks(df, year, ax):
#     fig = plt.figure(figsize=(6,6))
#     ax = fig.add_subplot(111)

    l = plt.plot(df['o1_rank'],df['o2_rank'],'.', color='white')
    xmax = df['o1_rank'].max()
    xmin = xmax - 2000
    
    l = ax.set_xlim((xmin, xmax))
    l = ax.set_ylim((xmin, xmax))

    l = ax.set_xlabel('%d' %year)
    l = ax.set_ylabel('other years')

def off_diagonals(corpus, year, ngram='word'):
    nc = one_year_vs_other(corpus, year)
    cw = common_words(nc, '%d' %year, '%d_comp' %year, ngram=ngram)
    df = compare_word_rank(nc, '%d' %year, '%d_comp' %year, cw, ngram=ngram, threshold=0)
    bd = biggest_divider(nc, '%d' %year, '%d_comp' %year, ngram=ngram, threshold=0, df=df)
    bd['e'] = bd['change'].apply(lambda x: x**2)
    return np.sqrt(bd['e'].sum())


if __name__ == '__main__':
    # list1 = ['so_2009']
    # list2 = ['so_2010', 'so_2011', 'so_2012', 'so_2013']

    cw = common_words_v1(corpus, list1, list2, ngram='bg')
    df = compare_word_rank(corpus, list1, list2, cw, ngram='bg')

    bd = biggest_divider(corpus, list1, list2, ngram='bg', threshold=0, df=df)

    print bd.head()



