'''
Build a pickle file for corpus analysis (supports up to 1-, 2- and 3-grams)
'''
import operator, pickle, sys, os
from corpus_analyzer import *

def fun1(corpus_folder, output_file):
	'''
	whole directory ngrams
	'''
	if corpus_folder[-1] == '/':
		corpus_folder = corpus_folder[:-1]
	# files = [corpus_folder + '/' + f for f in os.listdir(corpus_folder) if ('@' in f) and ('mywords' in f)]
	files = [corpus_folder + '/' + f for f in os.listdir(corpus_folder) if ('@' in f)]
	# print files

	ngrams = {}
	for f in files:
		tmp = {}
		tmp['word'] = single_word_freq(f)
		(bg, tg) = bi_tri_gram(f)
		tmp['bg'] = bg
		tmp['tg'] = tg

		f_ = f.split('/')[-1]
		ngrams[f_] = tmp
	
	f = open(output_file, 'w')
	pickle.dump(ngrams, f)
	print 'corpus object saved in %s' %output_file

if __name__ == '__main__':
	if len(sys.argv) == 3:
		# corpus_folder = '/Users/sj334u/Desktop/corpus/'
		# output_file = '/private/tmp/yoohoo.pkl'
		fun1(sys.argv[1], sys.argv[2])
	else:


		corpus = pickle.load(open('/private/tmp/yoohoo.pkl','r'))

		list1 = ['seraphzz@aim.com_mywords']
		list2 = ['stfnrulz@aim.com_mywords']

		cw = common_words_v1(corpus, list1, list2, ngram='word')
		# print cw
		df = compare_word_rank(corpus, list1, list2, cw, ngram='word')
		# print df.head()
		bg = biggest_divider(corpus, list1, list2, ngram='word', threshold=0, df=df)
		print bg.head()