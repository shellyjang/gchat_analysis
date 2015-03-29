import sys, os
import pandas as pd
from gchat_eml import Gchat 

work_dir = sys.argv[1]
corpus_folder = sys.argv[2]

subchats_folder = [work_dir + '/' + dir for dir in os.listdir(work_dir) if 'subchats' in dir]
files = []
for folder in subchats_folder:
	listdir = os.listdir(folder)
	listdir = [folder + '/' +  f for f in listdir if 'eml.gz' in f]
	files += listdir

l = len(files) / 5
for (ii, f) in enumerate(files):
	try: 
		gc = Gchat(f)
		my_logs = gc.logs[gc.logs.sender == 'me']
		their_logs = gc.logs[gc.logs.sender != 'me']
		gc.corpus_writer(corpus_folder + '/' + gc.msg_from_address)
	except:
		pass
	if ii % l == 0 and ii != 0:
		print ('%d percent finished..' % ((ii // l) * 20) )