'''
Build a pickle file for corpus analysis (supports up to 1-, 2- and 3-grams)
'''
import operator, pickle, sys, os
from corpus_analyzer import *

def fun1(corpus_folder, output_file):
	'''
	whole directory ngrams
	'''
	if corpus_folder[-1] != '/':
		corpus_folder += '/'
	files = [corpus_folder + f for f in os.listdir(corpus_folder) if ('@' in f)]

	ngrams = {}
	for f in files:
		tmp = {}
		tmp['word'] = single_word_freq(f)
		(bg, tg) = bi_tri_gram(f)
		tmp['bg'] = bg
		tmp['tg'] = tg

		f_ = f.split('/')[-1]
		ngrams[f_] = tmp
	pickle.dump(ngrams, open(output_file, 'w'))
	print 'corpus object saved in %s' %output_file

if __name__ == '__main__':
	print len(sys.argv)
	if len(sys.argv) == 3:
		print sys.argv[1], ",", sys.argv[2]
		fun1(sys.argv[1], sys.argv[2])

	else:
		print 'please provide appropriate arguments'
		fun1('/Users/sj334u/Desktop/corpus_test/','/Users/sj334u/Desktop/tmp/ngrams.pkl')