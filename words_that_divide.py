import operator, pickle, sys, os
from corpus_analyzer import *

def fun1(corpus, list1, list2, ngram='word', n=5):
	cw = common_words_v1(corpus, list1, list2, ngram=ngram)
	df = compare_word_rank(corpus, list1, list2, cw, ngram=ngram)
	# print df.head()
	bd = biggest_divider(corpus, list1, list2, ngram=ngram, threshold=0, df=df)
	# print bd
	bd_1 = bd[bd['o1_rank'] > bd['o2_rank']]
	bd_2 = bd[bd['o1_rank'] < bd['o2_rank']]

	return (bd_1, bd_2)

if __name__ == '__main__':
	# fun1()
	if len(sys.argv) < 4:
		print 'please provide 1) location of the pickle file, and two lists of corpus you would like to compare'
		corpus = pickle.load(open('/private/tmp/yoohoo.pkl','r'))
		list1 = ['seraphzz@aim.com_mywords', 'stfnrulz@aim.com_mywords']
		list2 = ['ichiromania666@gmail.com_mywords']
	
	else:
		corpus = pickle.load(open(sys.argv[1], 'r'))
		list1, list2 = eval(sys.argv[2]), eval(sys.argv[3])

	try:
		ngram, n = sys.argv[4], int(sys.argv[-1])
	except:
		ngram, n = 'word', 5

	(bd_1, bd_2) = fun1(corpus, list1, list2, ngram=ngram, n=n)

	print '-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-'
	print 'words that are used more in list1 than list2 are:'
	print bd_1.head(n)
	print '-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-'
	print 'words that are used more in list2 than list1 are:'
	print bd_2.head(n)
