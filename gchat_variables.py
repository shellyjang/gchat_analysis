import os, sys
import numpy as np 
import pandas as pd 
from gchat_eml import Gchat 

work_dir = sys.argv[1]
output_file = sys.argv[2]

subchats_folder = [work_dir + '/' + dir for dir in os.listdir(work_dir) if 'subchats' in dir]
files = []
for folder in subchats_folder:
	listdir = os.listdir(folder)
	listdir = [folder + '/' + f for f in listdir if 'eml.gz' in f]
	files += listdir

df = pd.DataFrame(columns=['msg_id', 'gm_id', 'num_msgs_me', 'num_msgs_other', \
							'num_msgs_both', 'num_words_tot', \
							'min_num_words_per_msg','max_num_words_per_msg', \
							'avg_num_words','chat_duration','avg_frequency', \
							'initiator','max_cont_num_msgs_me','max_cont_num_msgs_other', \
							'max_delay_me','max_delay_other'])
l = len(files) / 10
corr = 0
for (ii, f) in enumerate(files):
	try: 
		gc = Gchat(f)
		gm_id = f.split('/')[-1]
		gm_id = gm_id.split('.')[0]
		msg_id = gc.msg_id
		num_msgs = gc.num_messages()
		num_msgs_me = num_msgs[0][1]
		num_msgs_other = num_msgs[1][1]
		num_msgs_both = num_msgs[2][1]
		num_words = gc.count_num_words()

		num_words_tot = sum(num_words)
		if num_words_tot == 0:
			min_num_words_per_msg, max_num_words_per_msg = 0, 0
			avg_num_words = 0
		else:
			min_num_words_per_msg, max_num_words_per_msg = min(num_words), max(num_words)
			avg_num_words = 1. * num_words_tot / len(num_words)

		chat_duration = gc.chat_duration()
		avg_frequency = gc.frequency_analysis()
		initiator = gc.initiator()
		longest_sequence = gc.longest_sequence()
		if longest_sequence[0][0] == 'me':
			max_cont_num_msgs_me = longest_sequence[0][1]
			max_cont_num_msgs_other = longest_sequence[1][1]
		else:
			max_cont_num_msgs_me = longest_sequence[1][1]
			max_cont_num_msgs_other = longest_sequence[0][1]

		gc.delay()
		my_logs = gc.logs[gc.logs.sender == 'me']
		other_logs = gc.logs[gc.logs.sender != 'me']
		try: 
			max_delay_me = my_logs.delay[my_logs.delay.idxmax()].total_seconds()
		except:
			max_delay_me = 0
		try:
			max_delay_other = other_logs.delay[other_logs.delay.idxmax()].total_seconds()
		except: 
			max_delay_other = 0

		df.loc[ii] = [msg_id, gm_id, num_msgs_me, num_msgs_other, num_msgs_both, \
						num_words_tot, min_num_words_per_msg, max_num_words_per_msg, \
						avg_num_words, chat_duration, avg_frequency, initiator, \
						max_cont_num_msgs_me, max_cont_num_msgs_other, max_delay_me, max_delay_other]

		if ii != 0 and ii % l == 0:
			print '%d0 percent finished..' % (ii/l)
	except:
		pass

df.to_csv(output_file, index=False, header=True)
 
# LOAD DATA LOCAL INFILE 
# '/private/tmp/gchat_variables.csv'
# REPLACE 
# INTO TABLE chats_variables
# FIELDS TERMINATED BY ','
# IGNORE 1 LINES; 