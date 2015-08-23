import sys, os, argparse
import pandas as pd
from gchat_eml import Gchat, locate_eml
from progress.bar import Bar

if __name__ == '__main__':
	'''
	parse arguments
	'''
	parser = argparse.ArgumentParser()
	parser.add_argument('-d','--work_dir', help='specify location of .eml.gz files created via gmvault')
	parser.add_argument('-o','--output_dir', help='specify the location to save the corpus')
	args = parser.parse_args()

	if args.work_dir:
		work_dir = args.work_dir
	else:
		work_dir = '/Users/Shell/gmvault-db/'

	if args.output_dir:
		output_dir = args.output_dir
	else:
		output_dir = '/private/tmp/'

	''' 
	locate the files and set up reporting bar
	'''
	work_dir = os.path.join(work_dir, 'db/chats/')
	files = locate_eml(work_dir)
	l = len(files)
	print 'located %d files in chats directory' %l
	bar = Bar('Processing', max=l, suffix='%(percent)d%%')

	succ = 0
	for (ii, f) in enumerate(files):
		try: 
			gc = Gchat(f)
			gc.corpus_writer_yearly(os.path.join(output_dir, gc.msg_from_address), mode='w')
			succ += 1
		except:
			print 'uwotmate'
			pass
		if ii % l == 0 and ii != 0:
			print ('%d percent finished..' % ((ii // l) * 20) )
		bar.next()
	bar.finish()
	print '%d chats successfully parsed and saved' % succ
