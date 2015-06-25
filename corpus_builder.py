import sys, os
import pandas as pd
from gchat_eml import Gchat, locate_eml

work_dir = sys.argv[1]
corpus_folder = sys.argv[2]

files = locate_eml(work_dir)

if corpus_folder[-1] != '/':
	corpus_folder += '/'
print corpus_folder

l = len(files) / 5
for (ii, f) in enumerate(files[:10]):
	try:
		gc = Gchat(f)
		gc.corpus_writer_yearly(corpus_folder + gc.msg_from_address)
	except:
		print 'uwotmate'
		pass
	if ii % l == 0 and ii != 0:
		print ('%d percent finished..' % ((ii // l) * 20) )