'''

'''
from sklearn.feature_extraction.text import TfidfVectorizer
from corpus_analyzer import word_bag
import os, sys

def tfidf_scores(work_dir, ngram_range=(1,1), num_results=5):
	tf = TfidfVectorizer(analyzer='word', ngram_range=ngram_range, min_df = 0, stop_words = 'english')

	if work_dir[-1] != '/':
		work_dir += '/'
	files = [work_dir + f for f in os.listdir(work_dir) if '@' in f]

	corpus = []
	for f in files:
		corpus.append(word_bag(f))

	print '-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-'
	print 'fitting the corpus to generate TfIdf matrix'
	tfidf_matrix = tf.fit_transform(corpus)
	print 'finished!'
	print '-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-'
	feature_names = tf.get_feature_names()

	dense = tfidf_matrix.todense()

	for (ii, f) in enumerate(files):
		chat = dense[ii].tolist()[0]
		phrase_scores = [pair for pair in enumerate(chat) if pair[1] > 0]

		sorted_phrase_scores = sorted(phrase_scores, key=lambda x: x[1] * -1)
		print 'words most used in %s' %(f.split('/')[-1])
		for phrase, score in [(feature_names[word_id], score) for (word_id, score) in sorted_phrase_scores][:num_results]:
			print('{0: <20} {1}'.format(phrase, score))

if __name__ == '__main__':
	if len(sys.argv) == 4:
		tfidf_scores(sys.argv[1], eval(sys.argv[2]), int(sys.argv[3]))
	elif len(sys.argv) == 3:
		tfidf_scores(sys.argv[1], eval(sys.argv[2]))
	elif len(sys.argv) == 2:
		tfidf_scores(sys.argv[1])
	else:
		tfidf_scores('/Users/sj334u/Desktop/corpus/')
